# MMC Demo · Run of Show

> Single source of truth for the live demo. Pre-flight, story beats, narration cues, fallback plans.

**Audience**: Manufacturing IT + plant ops leadership.
**Duration**: ~25 minutes (15 min live · 10 min Q&A).
**Stack on stage**: Trace UI (`uvicorn ... mmc_agents.trace_ui.app:app`), single browser tab.

---

## 0 · Pre-flight checklist (do this 30 min before the demo)

### Capacity & quota

- [ ] **gpt-5.4 quota**: confirm at least **200K TPM** and **100 RPM** available in the Foundry region (eastus). Run:
      ```pwsh
      az cognitiveservices account deployment show --name <foundry-account> --resource-group mmc-demo --deployment-name gpt-5.4 --query "{model:properties.model.name, capacity:sku.capacity}"
      ```
      If capacity < 10 → file a quota increase (24h SLA) **before** demoing, or fall back to gpt-5.4-mini.
- [ ] **gpt-5.4-mini quota** (worker model): same check, target ≥ 100K TPM.
- [ ] **SQL DTU headroom**: `mmcops` (centralus) at < 50 % DTU. Heavy run can spike to 70 % on the joins.

### Foundry IQ KB connection (manual step from Gate B)

- [ ] In the Foundry portal, open the **mmc-plant** project → **Knowledge** → **Connections**, confirm the `kb-plant7` IQ connection exists and points to AI Search service `mmc-plant-search` (eastus).
- [ ] Repeat for **mmc-enterprise** project → `kb-enterprise` → `mmc-enterprise-search`.
- [ ] If missing: re-create via portal (Bicep can't do this — Foundry IQ connections are portal-only as of this writing). See `docs/specs/gate-b-status.md` §Deferred.

### Data freshness

- [ ] Confirm `governance/blast_radius.json` matches live computation:
      ```pwsh
      .\.venv\Scripts\python scripts\generate_blast_radius.py
      git diff --quiet governance/blast_radius.json
      ```
      Non-zero exit → re-commit the regenerated snapshot before the demo (otherwise the freshness test would have already failed in CI).
- [ ] SQL change-tracking up to date — the IQ indexers run on a schedule. If you edited a CSV recently:
      ```pwsh
      .\.venv\Scripts\python scripts\sync_sql_from_csv.py
      ```

### Trace UI sanity

- [ ] Start the trace UI:
      ```pwsh
      .\.venv\Scripts\uvicorn mmc_agents.trace_ui.app:app --reload --port 8080
      ```
- [ ] Open http://localhost:8080 → confirm 11 agents visible (6 plant including external-auditor + 5 enterprise).
- [ ] Run the **training_gap** scenario as a smoke test. Expect 1 hop, ~35 s, 5 employees listed.
- [ ] Reset hot-add state: `curl -X POST http://localhost:8080/demo/hot-add/reset`.

---

## 1 · Opening (2 min)

> "We're going to walk through a multi-agent assistant for a manufacturing org — Midwest Mobility Corporation. One factory floor, one enterprise back-office, eleven specialized agents, all orchestrated by a Foundry-hosted manager that we never wrote line-by-line. Let's see what it can do, and then we'll peel back the layers."

Show the trace UI. Point out:
- **Left rail**: agents organized by tier (Plant 7 / Enterprise).
- **Center**: empty trace pane.
- **Right**: empty synthesis pane.

---

## 2 · Scenario 1 — Training compliance (3 min) · proves: real data, narrow scope

> "Front line problem: who do we need to recertify before the end of the year?"

1. Pick **training_gap** scenario.
2. Click **Run scenario**.
3. **Narrate the streaming trace** as events arrive:
   - "Manager built a plan in one round."
   - "Dispatched to plant7-training. One hop."
   - "Got real rows from the SQL-backed Training_Log table."
4. Read the final synthesis aloud — 5 employee names, TRN-IDs, expiration dates.

**Talking points**:
- This is Foundry IQ + Azure SQL — the indexer follows change-tracking on `dbo.training_log`.
- Narrow scope = single-agent dispatch. The manager is parsimonious by design.

---

## 3 · Scenario 2 — PO + maintenance + supplier (5 min) · proves: multi-agent routing

> "Now let's give it a harder problem. A specific PO is at risk. What does that mean for the plant?"

1. Pick **po_status** (or the cross-functional scenario if available).
2. **Run**.
3. Watch the manager:
   - Hop 1: `ent-procurement` confirms PO-00001.
   - Hop 2: `plant7-maintenance` lists tied PM tasks.
   - Hop 3: `ent-supply-chain` checks supplier_master for backup.
4. **Highlight in the synthesis**: the manager surfaces the `NO_DIRECT_ALT` flag — that's a real row from `supplier_master`, not a hallucination.

**Talking points**:
- Each hop is a true tool call to a Foundry agent, returning grounded citations.
- The synthesis is rendered as markdown — citations are stripped from the synthesis but **preserved** in the per-hop transcript above for auditability.

---

## 4 · Governance overlay (3 min) · proves: blast-radius transparency

> "OK, the agents work. But who can do what? In manufacturing, that's table stakes."

1. Click `plant7-ehs` in the left rail.
2. Modal opens — walk through the **Dependencies** list:
   - Foundry project · KB · KB sources (ehs, **ehs_restricted**, incident_data) · Search service · SQL server.
3. Hover the 🔒 **Revoke** call-outs: "Revoke this RBAC chain, this agent loses retrieval. The overlay is computed from the same JSON the deployment uses, so it can't drift."

Now the **sensitivity demo**:

1. Close the modal. Click `plant7-external-auditor`.
2. Modal shows: same Foundry project, same KB — but only **one** source: `ehs`. **No `ehs_restricted`, no `incident_data`**.
3. Narrate: "Same physical KB. Different per-agent readable-sources mapping. The boundary is the metadata, and the overlay makes it visible."

**Talking points**:
- This is the answer to "how do I know my external auditor agent can't see the incident brief?"
- Citation: `governance/kb_metadata.json` → `per_agent_readable_sources`.
- Sealed in tests: `test_external_auditor_blast_radius_omits_restricted_source`.

---

## 5 · Hot-add live (2 min) · proves: registry is hot-pluggable

> "What if mid-investigation we realize we need a new specialist? We don't redeploy."

Follow `docs/demo/hot-add-runbook.md`:

1. Click `+ Hot-add supplier-quality`.
2. Show toast + new dashed-amber agent row.
3. Click the row → modal says **"no governance metadata yet"** — narrate the seam.
4. Click **Reset**.

---

## 6 · Identity layer (2 min) · proves: per-agent UAMIs

Show `infra/bicep/modules/agent-identities.bicep` and `parameters/agent-identities.bicepparam`.

> "Every agent in the catalog — including the external-auditor — gets its own Entra principal via a User-Assigned Managed Identity. That's the Bicep that provisions them. The blast-radius overlay says 'revoke this UAMI', and *this* is the UAMI it's talking about. Same name, same scope, traceable end-to-end."

Talking points:
- Deploy is idempotent. Stand-alone module — does not touch `main.bicep`.
- Tags carry `mmc:agent` and `mmc:foundryProjectId` so an auditor can trace each UAMI back to its agent.

---

## 7 · Wrap (2 min)

Recap the four moments:
- **Live data** (training_gap)
- **Multi-agent routing with citations** (po_status)
- **Per-agent blast-radius with revocation transparency** (governance modal)
- **Hot-pluggable registry + per-agent identity** (hot-add + Bicep)

Close: "Built on Foundry, Foundry IQ over Azure SQL, FastAPI for the trace UI, ~100 tests gating the demo invariants. Everything visible on stage is in the repo."

---

## Fallback plans

| Failure                          | Recovery                                                                 |
|----------------------------------|--------------------------------------------------------------------------|
| Foundry 429 rate limit           | Re-run the scenario; manager retries on its own                          |
| SQL indexer stale                | `scripts\sync_sql_from_csv.py` + wait 60 s + retry                       |
| Scenario hits max_rounds         | The manager now accepts "could not find" — but if a regression occurs, switch to the **training_gap** scenario which is the most reliable |
| Trace UI port collision          | `--port 8081` and update the bookmark                                    |
| Foundry IQ connection broken     | Skip Scenario 2, demo only Scenario 1 + governance overlay + hot-add     |
| Hot-add button does nothing      | Hit `POST /demo/hot-add` via curl manually; check browser console        |
| Sensitivity modal shows restricted source on auditor | `pytest -q tests/test_governance.py` to confirm regression. If real → roll back governance/kb_metadata.json |

---

## Post-demo cleanup

- [ ] `POST /demo/hot-add/reset`
- [ ] Stop the trace UI
- [ ] (Optional) Re-run `pytest -q` to confirm no state mutation
