# Identity Propagation & Data Security — Forward Architecture

**Status:** Forward-looking design doc. Not yet implemented.
**Author:** MMC Demo team
**Last updated:** 2026-06-17

---

## 1. Why this matters

The MMC demo's current security posture is **zero**:

| Layer                               | Today                                                          |
| ----------------------------------- | -------------------------------------------------------------- |
| Trace UI (front door)               | Local-only, no auth                                            |
| Orchestrator → Foundry              | `AzureCliCredential` — runs as whoever ran `az login`          |
| Manager → sub-agent (A2A)           | No identity passed; agent runs as the orchestrator's principal |
| Knowledge base retrieval            | No security trim — every retrieval returns everything indexed  |
| Per-agent permissions               | All agents share one dev identity                              |
| Behavioral scope (`kb_sources`)     | **Soft prompt hint only** — not enforced                       |

For a *demo* this is fine. For a customer pilot or production rollout it isn't.
Microsoft's identity stack has matured to the point where the full end-to-end
story is now buildable with first-party building blocks. This document captures
that target architecture so we have a clear "here → there" path the next time a
customer asks "how would this respect our existing data boundaries?".

---

## 2. The 5-layer blueprint

```
 ┌──────────────┐  user token   ┌──────────────┐  OBO token   ┌──────────────┐
 │   Browser    │ ─────────────▶│ Trace UI API │ ────────────▶│ Orchestrator │
 │ (signed in)  │               │ (Easy Auth)  │              │ (as user)    │
 └──────────────┘               └──────────────┘              └──────┬───────┘
                                                                     │ OBO + A2A
                                                                     ▼
                                                              ┌──────────────┐
                                                              │ Foundry Agent│  ◀── Entra Agent ID
                                                              │ (plant7-...) │      (per-blueprint RBAC,
                                                              └──────┬───────┘       Conditional Access)
                                                                     │ user token
                                                                     ▼
                                                              ┌──────────────┐
                                                              │  Foundry IQ  │  ◀── ACL / group_ids
                                                              │ knowledge KB │      trimming at query time
                                                              └──────────────┘
```

### Layer 1 — Front door: user → API

Put the trace UI behind **Microsoft Entra ID** using one of:

- **Easy Auth** on Azure App Service / Container Apps — zero code, identity headers injected.
- **MSAL** in the SPA — explicit, more control over scopes and consent.

The API receives the user's access token on every request (in
`Authorization: Bearer <jwt>`).

### Layer 2 — API → Foundry: On-Behalf-Of (OBO)

Replace `AzureCliCredential` with **`OnBehalfOfCredential`** (`azure-identity`).
When the API receives the user's token, exchange it via OAuth 2.0 OBO for a
downstream token scoped to Foundry (`https://ai.azure.com/.default`).

Microsoft Foundry calls this the **"attended"** flow:

> The agent operates on behalf of a human user, using the OAuth 2.0
> on-behalf-of (OBO) flow. The user first authenticates to the application,
> and the application passes the user's token to Agent Service. Agent Service
> then exchanges that token for one that carries both the agent identity and
> the user's delegated permissions.
>
> — [Agent identity concepts in Microsoft Foundry][foundry-agent-identity]

**Result:** every Foundry call now executes as the user, not as the
orchestrator's shared identity.

### Layer 3 — Manager → sub-agent: A2A with OBO pass-through

When the Magentic manager dispatches to a Foundry agent via the **Agent-to-Agent
(A2A) protocol** (preview), the user's identity travels with the call.

> The calling agent passes through the end user's identity. Your agent
> receives a token that represents the actual user, so you can scope actions
> to that user's permissions. This pattern is appropriate when your agent
> needs to enforce per-user access control.
>
> — [Enable incoming A2A on a Foundry agent (preview)][a2a-incoming]

This is what makes statements like *"the auditor sees a redacted view; the
plant manager sees the full record"* actually true end-to-end, not just
true at the prompt layer.

### Layer 4 — Knowledge base: security trimming (hard data boundary)

Today our `kb_sources` field in `plants/plant7/profile.yaml` is just a list
that gets templated into the agent's instructions:

```python
# src/mmc_agents/agent_factory.py
f"You have access to a Foundry IQ knowledge base covering: {kb_sources}."
```

The agent **can** retrieve anything in the unified KB; it just *agrees* not to.
That's behavioral, not enforced.

The hard version uses Azure AI Search's built-in document-level ACLs or the
security-filter pattern:

1. At seed time, tag every KB doc with a `group_ids` field carrying the
   Entra group OIDs allowed to see it:

   ```json
   { "name": "group_ids", "type": "Collection(Edm.String)", "filterable": true }
   ```

2. Foundry IQ applies the filter at retrieval time using the propagated user
   token:

   > Permission enforcement varies by knowledge source. Depending on the data
   > source, indexed knowledge sources can support document-level security
   > through ACLs, role-based access control, or both. At query time, results
   > are filtered based on the user's identity.
   >
   > — [Foundry IQ FAQ — How does Foundry IQ handle permissions?][foundryiq-faq]

3. Remote SharePoint sources enforce permissions natively via the Copilot
   Retrieval API and respect **Microsoft Purview sensitivity labels**.

4. For non-Search sources, see the security-filter pattern in
   [Security filters for trimming results in Azure AI Search][search-trim]
   (`search.in(group_ids, '<csv-of-user-OIDs>')`).

**Result:** SOX-restricted POs, PII-bearing training records, or
confidential-tier procurement docs simply do not appear in retrieval for
users who lack the group — without the agent having to know about it.

### Layer 5 — Per-agent RBAC: Microsoft Entra Agent ID

Each Foundry agent gets a first-class **service principal** via an
[Agent identity blueprint][entra-agent-id]:

- **Type classification**: a blueprint like `"MMC Plant7 Operations Agent"`
  is the template; each spun-up agent inherits its RBAC + Conditional Access.
- **Least-privilege RBAC**: `plant7-quality` agent identity gets
  `Search Index Data Reader` on `kb-plant7` only — *not* on `kb-enterprise`.
  This is the **hard boundary** that complements our soft `kb_sources` prompt
  scoping.
- **Conditional Access** applies per blueprint: device compliance, geofencing,
  sign-in frequency, blocked countries, MFA.
- **Lifecycle workflows**: deprovision when an agent is no longer needed
  (sponsor sign-off, expiration dates) — see
  [Entra ID governance for agents][entra-id-governance].

---

## 3. What stays from current design (defense in depth)

The hardened architecture *adds* layers; it doesn't replace what we have.
Keep these behavioral controls — they're independent guardrails:

| Control                                            | Why keep it                                                    |
| -------------------------------------------------- | -------------------------------------------------------------- |
| Prompt-level `kb_sources` in `_instructions()`     | Steers the model even when RBAC technically permits more       |
| Manager `participants` filter per scenario         | Narrows the pool — fewer hops, more deterministic demos        |
| Magentic stall/round/reset caps                    | Prevents runaway loops even if every layer above is correct    |
| Network isolation (VNet, private endpoints)        | Stops data exfil even if a token is leaked                     |
| `kb_sources` declared in profile.yaml              | Single source of truth; mirror it into RBAC at provision time  |

---

## 4. Audit & observability

The whole point of "identity all the way down" is **a single per-user pane**:

- **Application Insights**: Foundry agent runs include the user OID in
  tracing. Every hop is correlated.
- **Entra sign-in logs**: every OBO exchange is logged — see exactly which
  user → which agent → which downstream resource.
- **Azure AI Search query logs**: the principal that issued each retrieval is
  captured. Combine with the doc's `group_ids` field to prove the trim
  applied correctly.
- **Microsoft Purview**: if SharePoint + sensitivity labels are in scope, all
  retrievals + agent actions show up in the unified audit + Insider Risk
  pipelines.

---

## 5. Demo path (Gate D candidate — cheap mock of the real story)

Building the full stack above is a multi-week pilot. For a **demo beat** that
shows the *narrative* of identity propagation without standing up Entra:

1. Add an **"Acting as:"** dropdown in the trace UI:
   `[Plant Manager | Quality Auditor | External Contractor]`.
2. Each persona maps to a fake `x-user-groups` header sent on `/runs`.
3. Orchestrator filters KB results client-side by group membership (mock the
   trim that the real `search.in()` would do).
4. Run the same scenario as each persona — the manager sees full PO values
   and supplier risk notes, the auditor sees redacted financial fields, the
   contractor gets a "no documents matched your access" response.

This is **demo-grade** but tells the right story in under a day's work. A
follow-up Gate E would replace each mock with the real building block
(Easy Auth → OBO → A2A → Search ACL → Entra Agent ID blueprint).

---

## 6. Buy-vs-build summary

Everything in the blueprint above is a **first-party Microsoft building
block**. Nothing here requires custom IdP code, custom token brokers, or
custom policy engines.

| Need                                  | Service                                                     |
| ------------------------------------- | ----------------------------------------------------------- |
| User auth at the front door           | Entra ID (Easy Auth or MSAL)                                |
| Token exchange to downstream services | `OnBehalfOfCredential` in `azure-identity`                  |
| Agent-to-agent identity pass-through  | Foundry A2A (preview) with OBO                              |
| Document-level data trimming          | Azure AI Search ACL / `search.in()` security filter         |
| Per-agent identity + RBAC + CA        | Microsoft Entra Agent ID + Agent identity blueprints        |
| SharePoint/M365 doc security          | Copilot Retrieval API + Microsoft Purview sensitivity labels|
| Cross-cutting audit                   | Application Insights + Entra sign-in logs + Purview         |

---

## 7. References

- [Agent identity concepts in Microsoft Foundry][foundry-agent-identity]
- [Enable incoming A2A on a Foundry agent (preview)][a2a-incoming]
- [What is Microsoft Entra Agent ID?][entra-agent-id]
- [Foundry IQ FAQ — How does Foundry IQ handle permissions?][foundryiq-faq]
- [Security filters for trimming results in Azure AI Search][search-trim]
- [Document-level access control for Azure OpenAI On Your Data][on-your-data-acl]
- [Microsoft Entra ID governance for agents][entra-id-governance]
- [What are workload identities? — Agent identities for AI workloads][workload-identities]

[foundry-agent-identity]: https://learn.microsoft.com/azure/foundry/agents/concepts/agent-identity
[a2a-incoming]: https://learn.microsoft.com/azure/foundry/agents/how-to/a2a-incoming
[entra-agent-id]: https://learn.microsoft.com/entra/agent-id/what-is-microsoft-entra-agent-id
[foundryiq-faq]: https://learn.microsoft.com/azure/foundry/agents/concepts/foundry-iq-faq#how-does-foundry-iq-handle-permissions
[search-trim]: https://learn.microsoft.com/azure/search/search-security-trimming-for-azure-search
[on-your-data-acl]: https://learn.microsoft.com/azure/ai-foundry/openai/how-to/on-your-data-configuration#document-level-access-control
[entra-id-governance]: https://learn.microsoft.com/entra/id-governance/agent-id-governance-overview
[workload-identities]: https://learn.microsoft.com/entra/workload-id/workload-identities-overview#agent-identities-for-ai-workloads
