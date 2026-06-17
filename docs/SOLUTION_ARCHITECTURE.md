# MMC Demo — Solution Architecture

> A reference implementation of a **multi-tier, multi-agent manufacturing assistant** built on Microsoft Agent Framework, Azure AI Foundry (Agents Service + Foundry IQ), and Azure SQL — running over a synthetic Midwest Mobility Components (MMC) Plant 7 + enterprise dataset.

This document explains *what* was built, *why* each piece is there, and *how* the components connect. It is the companion to the operational `README.md` (which covers setup, demo prompts, and run instructions).

---

## 1. What the demo actually does

A user asks a manufacturing question (e.g. *"Our open PO PO-00001 for BRK-CAL-XYZ from SUP-001 is flagged At Risk. Which Plant 7 Line 1 PM tasks involve this part, and does the supplier master show any backup suppliers?"*).

A **Magentic manager** decomposes that question into a plan, picks the right agents from a pool of 10 specialists (5 plant + 5 enterprise), dispatches them in sequence/parallel, watches their outputs, and produces a cited, ledger-grounded answer.

Each specialist agent is a **portal-managed Azure Foundry Prompt Agent** with a **Foundry IQ knowledge base** attached as an MCP tool. The KB contains a mix of unstructured policy documents (markdown / PDF) and **structured rows pulled live from Azure SQL** via Foundry IQ's *Indexed Azure SQL knowledge source*.

The whole run is visible in real time through a **FastAPI + Server-Sent Events trace UI** that shows the plan, every agent hop, every replan/backtrack, and the final synthesis.

---

## 2. High-level architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          Browser (single HTML file)                      │
│   - Scenario picker  - Live event stream  - Plan / hop / agent cards     │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │  GET /scenarios  POST /runs  GET /runs/{id}/events (SSE)
┌───────────────────────────────▼──────────────────────────────────────────┐
│                FastAPI trace_ui  (src/mmc_agents/trace_ui)               │
│   - schemas.py     pydantic event + scenario models                      │
│   - runtime.py     async run registry, in-memory event bus               │
│   - app.py         REST + SSE endpoints, scenario registry adapter       │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │  ScenarioSpec + AsyncIterator[TraceEvent]
┌───────────────────────────────▼──────────────────────────────────────────┐
│      Magentic Orchestrator    (src/mmc_agents/orchestrator)              │
│   - manager.py      MagenticBuilder + StandardMagenticManager wrapper    │
│                     run_stream() emits TraceEvent for every plan/hop/    │
│                     replan/output. NO_DIRECT_ALT_RULE in instructions.   │
│   - scenarios/      problem statements + participant whitelist           │
│                     + per-scenario max_rounds                            │
│   - model_config.py separate manager (gpt-5.4) vs agent (gpt-5.4-mini)   │
│                     deployments — avoids 429 from shared model           │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │  build_foundry_agents() + build_enterprise_agents()
┌───────────────────────────────▼──────────────────────────────────────────┐
│       agent_factory.py        — portal-managed Foundry Prompt Agents     │
│                                                                          │
│   For each agent in profile.yaml:                                        │
│     PromptAgentDefinition(instructions=..., model=...)                   │
│       └─ MCPTool(server_label=KB_CONNECTION_ID,                          │
│                  server_url=KB_MCP_URL)        ← Foundry IQ baked in     │
│     AIProjectClient.agents.create_version(...)                           │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        │                                               │
┌───────▼────────────────────────┐         ┌────────────▼───────────────┐
│  Foundry Project: mmc-plant    │         │  Foundry Project: mmc-ent  │
│  ┌──────────────────────────┐  │         │  ┌──────────────────────┐  │
│  │ 5 plant prompt agents:   │  │         │  │ 5 ent prompt agents: │  │
│  │  plant7-ehs              │  │         │  │  ent-supply-chain    │  │
│  │  plant7-maintenance      │  │         │  │  ent-procurement     │  │
│  │  plant7-quality          │  │         │  │  ent-engineering-plm │  │
│  │  plant7-shiftops         │  │         │  │  ent-quality         │  │
│  │  plant7-training         │  │         │  │  ent-demand-program  │  │
│  └──────────┬───────────────┘  │         │  └──────────┬───────────┘  │
└─────────────┼──────────────────┘         └─────────────┼──────────────┘
              │ MCP tool call                            │ MCP tool call
              ▼                                          ▼
   ┌──────────────────────────┐              ┌──────────────────────────┐
   │  Foundry IQ: kb-plant7   │              │ Foundry IQ: kb-enterprise│
   │  6 knowledge sources:    │              │  7 knowledge sources:    │
   │   • ehs           (docs) │              │   • supply_chain  (docs) │
   │   • maintenance   (docs) │              │   • procurement   (docs) │
   │   • quality_ops   (docs) │              │   • engineering   (docs) │
   │   • training_data (SQL)  │              │   • ent_quality   (docs) │
   │   • pm_data       (SQL)  │              │   • demand_program(docs) │
   │   • incident_data (SQL)  │              │   • supplier_data (SQL)  │
   │                          │              │   • po_data       (SQL)  │
   └──────────┬───────────────┘              └──────────┬───────────────┘
              │                                         │
              └────────────────────┬────────────────────┘
                                   │  IndexedSqlKnowledgeSource
                                   │  (Database+ResourceId conn string,
                                   │   MI auth, SQL change tracking)
                                   ▼
                       ┌─────────────────────────┐
                       │  Azure SQL: mmcops      │
                       │   dbo.training_log      │
                       │   dbo.pm_schedule       │
                       │   dbo.incident_log      │
                       │   dbo.supplier_master   │
                       │   dbo.po_spend          │
                       │   (283 rows, CT on)     │
                       └─────────────────────────┘
```

---

## 3. The three tiers explained

### Tier 1 — Orchestrator (Magentic)

| File | Responsibility |
|------|----------------|
| `orchestrator/manager.py` | Builds the `MagenticBuilder` workflow, instantiates `StandardMagenticManager` with a manager chat client, runs `workflow.run(task, stream=True)`, and adapts framework events into typed `TraceEvent` objects via `run_stream()`. |
| `orchestrator/trace.py` | Defines `TraceEvent` (start / ledger_update / agent_call / agent_response / backtrack / complete) — the canonical event vocabulary that flows up to the UI. |
| `orchestrator/model_config.py` | Returns separate `ChatClient` instances for the manager vs. the agents so they hit different deployments and don't compete for the same per-minute token bucket. |
| `orchestrator/scenarios/registry.py` | Single source of truth for demoable prompts. Each `ScenarioSpec` carries the problem statement, a UI blurb, an optional `participants` whitelist (to scope the team), and a per-scenario `max_rounds` cap. |
| `orchestrator/scenarios/*.py` | One module per scenario: `PROBLEM_STATEMENT` constant + `EXPECTED_BOUNDS` dict for tests. |

The manager's behavior is tuned with two custom instruction extensions:

* `NO_DIRECT_ALT_RULE` — when a supply-chain or plant tool returns `NO_DIRECT_ALT`, treat it as a *signal to fan out*, not a stop condition.
* `participants` whitelist — narrow scenarios only see the agents they need (e.g. `training_gap` sees only `plant7-training`), preventing the manager from over-fanning for trivial questions.

### Tier 2 — Agents (Azure Foundry Prompt Agents)

Every specialist agent is a **portal-managed PromptAgentDefinition** created via `AIProjectClient.agents.create_version(...)`. This is intentional — the user explicitly wanted them visible in the Foundry portal, not local-only SDK agents.

`src/mmc_agents/agent_factory.py` is the single source of truth:

1. Reads `plants/plant7/profile.yaml` or `enterprise/profile.yaml`.
2. For each agent role, composes instructions from `display_name`, `description`, `skills`, and a standard footer about citing KB sources.
3. Attaches the **Foundry IQ MCP tool** (`MCPTool(server_label=PLANT_KB_CONNECTION_ID, server_url=PLANT_KB_MCP_URL)`) so the agent gets KB grounding for free.
4. Calls `agents.create_version(...)` — idempotent because Foundry versions are append-only.

The factory is split into two functions:

* `build_foundry_agents(profile, project_endpoint, kb_tool)` → plant agents
* `build_enterprise_agents(profile, project_endpoint, kb_tool)` → enterprise agents

The orchestrator calls both and merges them into one participant pool of up to 10.

### Tier 3 — Knowledge (Foundry IQ + Azure SQL)

Foundry IQ is Azure AI Search dressed up with knowledge-base + MCP semantics. We have two KBs (one per Foundry project), each composed of multiple **knowledge sources**:

| Source kind | Backing | Used for |
|---|---|---|
| `searchIndex` | Push-API uploaded text from markdown / PDF / CSV | Procedures, SOPs, regulatory docs, narrative reports |
| `indexedSql` | Live `IndexedSqlKnowledgeSource` over an Azure SQL table | Row-level operational data (training records, PM tasks, incidents, suppliers, POs) |

#### Why split docs vs rows?

Earlier iterations put CSVs through the document indexer. The agent could *paraphrase* the data but couldn't reliably retrieve specific rows — questions like *"list every employee whose LOTO cert expires before 2026-12-31"* hit `max_rounds` because the agent kept replanning when the doc chunks didn't contain the right rows.

Switching the row data to `IndexedSqlKnowledgeSource` (Pattern A from the agentic-retrieval docs) fixed this: each SQL column becomes an Edm field, the Search service indexes every row with PK as document key, and queries return discrete cited rows that the agent can list verbatim.

#### IndexedSqlKnowledgeSource setup gotchas (battle-tested)

1. **Connection string must be the MI form**, not the standard client form:
   ```
   Database={db};ResourceId=/subscriptions/.../servers/{server};Connection Timeout=30;
   ```
   *Not* `Server=tcp:...,1433;Database=...;User=...;Password=...;`.
2. **Search MI needs Contributor (not just Reader) on the SQL server resource.** The docs say Reader is sufficient for the server-endpoint lookup; in practice Contributor was required.
3. **Database-level user** must be created from external provider and granted `db_datareader` + `VIEW CHANGE TRACKING` on the schema:
   ```sql
   CREATE USER [search-svc-name] FROM EXTERNAL PROVIDER WITH OBJECT_ID = '<MI-principal-id>';
   ALTER ROLE db_datareader ADD MEMBER [search-svc-name];
   GRANT VIEW CHANGE TRACKING ON SCHEMA::dbo TO [search-svc-name];
   ```
4. **Enable SQL integrated change tracking** on every table (`ALTER TABLE ... ENABLE CHANGE_TRACKING`) so Foundry IQ can do incremental indexing instead of full re-ingest.
5. **API version 2026-05-01-preview** requires `retrievalReasoningEffort: {kind: "minimal"}` (object), not the bare string from earlier previews.

---

## 4. End-to-end request flow

Walking through the `training_gap` scenario from click to answer:

1. **Browser** posts `{ "scenario": "training_gap" }` to `POST /runs`.
2. **trace_ui.app** validates against the scenario registry, instantiates `MagenticRunner`, and returns a `run_id`. The runner spins up an async task that drives the orchestrator and pushes `TraceEvent` objects into an asyncio queue.
3. Browser opens `GET /runs/{run_id}/events` — an SSE stream that forwards each queued event as soon as it arrives.
4. **manager.run_stream** sends the prompt to `MagenticBuilder`, which calls the manager LLM (`gpt-5.4`) to produce a plan. We emit `ledger_update` with the plan text.
5. Manager dispatches `plant7-training`. We emit `agent_call(agent="plant7-training", hop=1)`.
6. The Prompt Agent receives the request in Foundry, calls its **Foundry IQ MCP tool**, which fans out to all attached knowledge sources. The `training_data` SQL source returns 5 cited rows (Marcus Chen, David Kowalski, Steven Garcia, Christopher White, Carlos Mendez).
7. Foundry composes an answer with `【source】` citations and returns it as an `AgentResponseUpdate`. We emit `agent_response`.
8. Manager sees the response is sufficient, asks for synthesis, and emits a final `complete` event with the full answer.
9. Browser closes the SSE stream and renders the final card.

Total elapsed time on the verified path: **~35 seconds for 1 hop, 1 agent, 5 cited row matches.**

---

## 5. Configuration surface

| Env var | Purpose | When set |
|---|---|---|
| `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `AZURE_LOCATION` | Bicep + Azure CLI defaults | Before `az deployment ... create` |
| `FOUNDRY_PLANT_PROJECT_ENDPOINT`, `FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT` | `services.ai.azure.com` endpoints for both Foundry projects | After Bicep deploy |
| `FOUNDRY_MODEL_DEPLOYMENT` | Agent LLM deployment name (e.g. `gpt-5.4-mini`) | Before factory run |
| `FOUNDRY_MANAGER_DEPLOYMENT` | Manager LLM deployment name (must be a **different** deployment from agent — typically `gpt-5.4`) | Before orchestrator run |
| `FOUNDRY_IQ_KB_PLANT7_ID`, `FOUNDRY_IQ_KB_ENTERPRISE_ID` | KB names emitted by `seed_foundry_iq.py` | After seed |
| `PLANT_KB_CONNECTION_ID`, `PLANT_KB_MCP_URL` | Foundry IQ MCP project-connection wiring for the plant KB | After operator creates the IQ connection in Foundry portal |
| `ENTERPRISE_KB_CONNECTION_ID`, `ENTERPRISE_KB_MCP_URL` | Same, for enterprise KB | Same |
| `SEARCH_PLANT_ENDPOINT`, `SEARCH_ENTERPRISE_ENDPOINT` | Direct Search endpoints used by the seeder | After Bicep deploy |
| `SQL_SERVER_FQDN`, `SQL_DATABASE_NAME`, `SQL_SERVER_NAME` | Used by `provision_sql.py` and seeder | After SQL Bicep deploy |
| `MMC_TRACE_UI_PORT` | Port for `python -m mmc_agents.trace_ui` (default 8000) | At UI start |

---

## 6. Profile → KB → Agent mapping (today's state)

### Plant 7 (`plants/plant7/profile.yaml`)

| KB Source | Kind | Backing |
|---|---|---|
| `ehs` | docs | `plants/plant7/kb/02_EHS_Internal` + `shared/kb/regulatory-reference/OSHA` |
| `maintenance` | docs | `plants/plant7/kb/03_Maintenance` + `shared/kb/oem-manuals` |
| `quality_ops` | docs | `plants/plant7/kb/04_Quality` + `plants/plant7/kb/05_Ops_Shift` |
| `training_data` | **SQL** | `dbo.training_log` |
| `pm_data` | **SQL** | `dbo.pm_schedule` |
| `incident_data` | **SQL** | `dbo.incident_log` |

| Agent | kb_sources |
|---|---|
| `plant7-ehs` | `[ehs, incident_data]` |
| `plant7-maintenance` | `[maintenance, pm_data]` |
| `plant7-quality` | `[quality_ops, incident_data]` |
| `plant7-shiftops` | `[quality_ops, pm_data, incident_data]` |
| `plant7-training` | `[quality_ops, training_data, incident_data]` |

### Enterprise (`enterprise/profile.yaml`)

| KB Source | Kind | Backing |
|---|---|---|
| `supply_chain` | docs | `enterprise/supply-chain/kb` |
| `procurement` | docs | `enterprise/procurement/kb` |
| `engineering_plm` | docs | `enterprise/engineering-plm/{data,kb}` |
| `enterprise_quality` | docs | `enterprise/enterprise-quality/{data,kb}` |
| `demand_program` | docs | `enterprise/demand-program/{data,kb}` |
| `supplier_data` | **SQL** | `dbo.supplier_master` |
| `po_data` | **SQL** | `dbo.po_spend` |

| Agent | kb_sources |
|---|---|
| `ent-supply-chain` | `[supply_chain, supplier_data]` |
| `ent-procurement` | `[procurement, po_data]` |
| `ent-engineering-plm` | `[engineering_plm]` |
| `ent-quality` | `[enterprise_quality]` |
| `ent-demand-program` | `[demand_program]` |

---

## 7. Scenarios

Each scenario lives in `src/mmc_agents/orchestrator/scenarios/`. They scale from single-agent SQL spot-checks to all-10-agent fan-outs.

| ID | Label | Agents | Notes |
|---|---|---|---|
| `training_gap` | LOTO refresher · expirations | 1 (training) | Pure SQL spot-check; cites `training_log` rows |
| `po_status` | At-risk POs · SUP-001 | 1 (procurement) | Pure SQL spot-check; cites `po_spend` row |
| `pm_check` | Line 1 PM · follow-up WOs | 1 (quality) | SQL spot-check on `pm_schedule` |
| **`supplier_risk_pm`** | At-risk PO · PM impact + alt supplier | **3** (procurement + maintenance + supply-chain) | Cross-KB SQL story across 3 tables |
| `loto_cluster` | LOTO cluster · L1 Press near-misses | ~5-6 | Mixes EHS, maintenance, training, quality, ent-quality |
| `brake_caliper` | Brake caliper · NO_DIRECT_ALT | All 10 | Full fan-out; triggers `NO_DIRECT_ALT` replan |

---

## 8. Operational scripts

| Script | What it does | Idempotent? |
|---|---|---|
| `scripts/provision_sql.py` | Connects to Azure SQL with AAD bearer token, creates 5 tables from the CSVs in `plants/plant7/kb/08_Logs_Data` and `enterprise/**`, enables change tracking. | Yes (drops + recreates tables) |
| `scripts/grant_sql_access.py` | Creates database users for both Search MIs, grants `db_datareader` + `VIEW CHANGE TRACKING`. | Yes |
| `scripts/seed_foundry_iq.py` | For each KB source in `profile.yaml`: builds either a doc-indexed `SearchIndex` (uploads docs via push API) or an `IndexedSqlKnowledgeSource` (registers + auto-ingests), then builds the `KnowledgeBase` over all sources. | Yes |
| `scripts/generate_cards.py` | Emits agent JSON cards for each profile entry — used by tests and by the Entra Agent ID overlay (Gate C). | Yes |
| `scripts/run_scenario.py` | CLI runner: `python -m scripts.run_scenario --scenario brake_caliper` — invokes the orchestrator and prints the trace. | Yes |

---

## 9. What's intentionally *not* in the demo

Documented to set expectations for future work — see also `docs/identity-propagation-strategy.md` if it exists.

* **End-user identity propagation.** The MI auth chain stops at the Search service → SQL. Real customer deployments need OBO flows or per-user tokens propagated all the way through the agents to data sources. Documented but not implemented.
* **Restricted-source / row-level security.** Foundry IQ has knowledge-source-level ACLs but we don't exercise them in the demo. Pattern would be to give each agent only the KB sources it's authorized for, optionally combined with SQL row-level security on the user's behalf.
* **Hot-add agent at demo time.** Plumbed but currently relies on rerunning `agent_factory` — the trace UI doesn't yet expose a hot-add button.
* **Entra Agent IDs.** The governance overlay (per-agent blast-radius cards) is in Gate C plan but not built yet.
* **Tools beyond KB.** Each profile lists tools (`capa`, `cmms`, `qms`, etc.); the stubs in `src/mmc_agents/tools/` return canned fixtures. They are wired into agent instructions but not yet attached as real Foundry tool definitions.

---

## 10. Hard-won learnings (worth knowing if you fork this)

* **Magentic manager and worker agents must use different deployments.** Sharing a single `gpt-5.4` deployment for both reliably 429-rate-limits because the manager calls the model every round for planning *plus* progress-ledger updates *on top of* the worker call. We use `gpt-5.4` for the manager and `gpt-5.4-mini` for the workers.
* **Foundry IQ knowledge sources are baked into Prompt Agent versions via the MCP tool.** You must create the agent versions *after* the KB exists, then create the IQ project-connection in the Foundry portal, then re-run the factory so the env vars (`PLANT_KB_CONNECTION_ID`, `PLANT_KB_MCP_URL`) cause every new version to include the binding.
* **`KnowledgeRetrievalMinimalReasoningEffort` type was removed from `azure-search-documents>=12.1.0b1`.** The current API expects an object `{kind: "minimal"}` instead.
* **East US SQL capacity is flaky for serverless Gen5.** We deployed SQL to `centralus` while everything else stayed in `eastus`. No measurable perf cost — Foundry IQ + indexer cross talk over Microsoft backbone.
* **Profile splits matter.** Removing `08_Logs_Data` CSV paths from `quality_ops` is what made the SQL sources actually win. If both the doc indexer and the SQL indexer hold the same data, the agent's retrieval often picks a doc chunk (paraphrase) instead of a SQL row (cited).
* **Manager terminal-phrase recognition is narrow.** Today the manager only treats literal *"I cannot assist"* as a terminal failure. Phrases like *"no records matched"* or *"could not find"* cause it to keep replanning to `max_rounds`. Tracked as `t-manager-broaden` follow-up.

---

## 11. Testing

* `pytest tests/` — 88 tests, 4 skipped. Covers scenario registry shape, agent factory snapshots, manager event mapping, trace UI schemas, and orchestrator integration smoke tests.
* `tests/snapshots/enterprise_agent_cards/` — pinned snapshots of factory-emitted JSON cards. If you change `profile.yaml`, refresh the snapshots with the loop in `scripts/refresh_catalog.py` or copy-paste from the failure diff.
* `tests/` does not invoke live Azure — all Foundry/Search/SQL clients are mocked or fixtured. Live verification is done by running scenarios through the trace UI.

---

## 12. Where to look next

| Topic | File |
|---|---|
| Add a new agent | `plants/plant7/profile.yaml` or `enterprise/profile.yaml` → re-run `scripts/seed_foundry_iq.py` → re-run agent factory |
| Add a new scenario | `src/mmc_agents/orchestrator/scenarios/*.py` + entry in `registry.py` + literal entry in `trace_ui/schemas.py` |
| Add a new SQL table | Drop CSV in `plants/...` or `enterprise/...` → update `provision_sql.py` table list → add `sql_table:` entry in profile → re-seed |
| Change manager behavior | `orchestrator/manager.py` — instruction extensions or `ScenarioSpec.max_rounds` |
| Inspect Bicep IaC | `infra/bicep/main.bicep` + `infra/bicep/modules/*.bicep` |
