# Midwest Mobility Components (MMC) — Multi-Agent Manufacturing Demo

A reference implementation of a **multi-tier, multi-agent manufacturing assistant** built on Microsoft Agent Framework, Azure AI Foundry (Agents Service + Foundry IQ), and Azure SQL.

A user asks a real plant-floor question. A **Magentic manager** decomposes it into a plan, dispatches the right specialists from a pool of 10 portal-managed Foundry Prompt Agents (5 plant + 5 enterprise), each grounded in a Foundry IQ knowledge base that mixes policy documents (markdown / PDF) with **live row data indexed straight from Azure SQL**. The full run streams to a tiny FastAPI + SSE trace UI so you can watch the plan, every hop, and every replan in real time.

> 📐 **Looking for the deep dive?** See **[`docs/SOLUTION_ARCHITECTURE.md`](docs/SOLUTION_ARCHITECTURE.md)** — full component map, request flow, configuration surface, profile→KB→agent mapping, and gotchas.
>
> 📊 Looking for the source dataset? See **[`docs/DATASET.md`](docs/DATASET.md)** — the original Plant 7 knowledge base contents (markdown SOPs + CSV operational logs).

---

## At a glance

```
   Browser  ──►  FastAPI trace UI (SSE)  ──►  Magentic Orchestrator
                                                    │
                                  ┌─────────────────┼─────────────────┐
                                  ▼                                   ▼
                          mmc-plant (Foundry)                 mmc-enterprise (Foundry)
                          5 prompt agents                      5 prompt agents
                                  │                                   │
                                  ▼                                   ▼
                          kb-plant7 (Foundry IQ)            kb-enterprise (Foundry IQ)
                          docs + 3 SQL sources              docs + 2 SQL sources
                                  │                                   │
                                  └────────────┬──────────────────────┘
                                               ▼
                                  Azure SQL: mmcops (5 tables, CT on)
```

| Tier | Component | Tech |
|---|---|---|
| 🖥️ UI | Live event stream, scenario picker | FastAPI + SSE + single static HTML file |
| 🧠 Orchestrator | Magentic plan/dispatch/replan loop | `agent_framework.orchestrations.MagenticBuilder` |
| 🤖 Agents | 10 portal-managed prompt agents (2 Foundry projects) | `azure-ai-projects` ≥ 2.2 `PromptAgentDefinition` |
| 📚 Knowledge | Per-project KB; mix of doc-indexed + SQL-indexed sources | Foundry IQ (`azure-search-documents` ≥ 12.1.0b1) |
| 🗃️ Data | Row-truthful operational data (training, PM, incidents, suppliers, POs) | Azure SQL Database (serverless Gen5, change tracking on) |
| 🏗️ Infra | Reproducible deploy | Bicep modules under `infra/bicep/` |

---

## Quickstart (run the demo locally against your already-provisioned Azure)

> Assumes Bicep has been deployed (`infra/bicep/main.bicep`), Foundry IQ project-connections have been wired in the portal, and `.env` is populated. See the architecture doc for the full provision recipe.

```powershell
# 1. Set up Python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]

# 2. (One-time) load CSVs into Azure SQL and grant search MIs access
python scripts/provision_sql.py
python scripts/grant_sql_access.py

# 3. (One-time per profile change) seed Foundry IQ knowledge bases
python scripts/seed_foundry_iq.py --plant plant7
python scripts/seed_foundry_iq.py --enterprise

# 4. (One-time after KB+IQ-connection exist) create / update prompt agent versions
python scripts/refresh_catalog.py

# 5. Run the trace UI
$env:MMC_TRACE_UI_PORT="8000"
python -m mmc_agents.trace_ui
# Open http://127.0.0.1:8000
```

To run a scenario from the CLI without the UI:

```powershell
python -m scripts.run_scenario --scenario supplier_risk_pm
```

---

## Demo scenarios

| Scenario | What it shows | Agents | Roughly |
|---|---|---|---|
| `training_gap` | SQL spot-check — list employees with expiring LOTO cert, cite `Training_Log` rows | 1 | ~35s, 1 hop |
| `po_status` | SQL spot-check — open POs flagged At Risk / Watch, cite `po_spend` rows | 1 | ~15s, 1 hop |
| `pm_check` | SQL spot-check — Line 1 PMs with follow-up WOs this quarter | 1 | ~30s, 1 hop |
| **`supplier_risk_pm`** | **Cross-KB SQL story — at-risk PO → which Plant 7 PMs depend on the part → backup supplier in master** | **3** | **~6-10 hops** |
| `loto_cluster` | Plant + enterprise — cluster L1 Press near-misses, check competency, escalate to enterprise quality | 5-6 | ~15 hops |
| `brake_caliper` | Full fan-out — supplier delay impact, mitigation, cost; triggers `NO_DIRECT_ALT` replan | All 10 | ~30 hops |

---

## Repository layout

```
mmc_demo/
├── README.md                       ← you are here
├── pyproject.toml                  ← Python deps + package config
├── .env(.example)                  ← Azure + Foundry + SQL env wiring
│
├── docs/
│   ├── SOLUTION_ARCHITECTURE.md    ← deep-dive technical doc
│   ├── DATASET.md                  ← Plant 7 + enterprise dataset card
│   ├── plans/                      ← gate plans (A/B/C)
│   └── specs/                      ← gate status snapshots
│
├── infra/bicep/                    ← all Azure IaC
│   ├── main.bicep                  ← top-level deployment
│   └── modules/
│       ├── ai-search.bicep         ← Search services (one per Foundry project)
│       ├── foundry-iq-kb.bicep     ← Foundry IQ knowledge base
│       ├── foundry-project.bicep   ← Foundry project + identity
│       ├── search-connection.bicep
│       ├── sql.bicep               ← Azure SQL (serverless Gen5, AAD-only)
│       └── storage.bicep
│
├── plants/plant7/                  ← per-plant profile + docs
│   ├── profile.yaml                ← agents, kb sources, tool wiring
│   └── kb/                         ← markdown SOPs, OEM manuals, etc.
│
├── enterprise/                     ← per-node profiles + docs
│   ├── profile.yaml
│   ├── supply-chain/, procurement/, engineering-plm/, ...
│
├── shared/kb/                      ← cross-cutting docs (OSHA, manuals)
│
├── agents/catalog.json             ← snapshot of agent cards
├── governance/                     ← per-agent blast-radius cards (Gate C)
│
├── scripts/                        ← all the one-shots
│   ├── provision_sql.py            ← CSVs → SQL tables + change tracking
│   ├── grant_sql_access.py         ← Create DB users for both Search MIs
│   ├── seed_foundry_iq.py          ← Build KB sources (docs + indexedSql)
│   ├── refresh_catalog.py          ← Re-emit agent JSON cards
│   ├── run_scenario.py             ← CLI scenario runner
│   ├── verify_kb_retrieval.py
│   └── generate_*.py               ← synthetic data generators
│
├── src/mmc_agents/                 ← the actual Python package
│   ├── agent_factory.py            ← PromptAgentDefinition + IQ MCP tool
│   ├── orchestrator/
│   │   ├── manager.py              ← MagenticBuilder + TraceEvent emission
│   │   ├── trace.py                ← typed event vocabulary
│   │   ├── model_config.py         ← separate manager vs worker deployments
│   │   └── scenarios/              ← one .py per scenario + registry.py
│   ├── trace_ui/                   ← FastAPI app + SSE + static HTML
│   ├── registry/                   ← AgentCard schema, local catalog
│   └── tools/                      ← stubbed tool fixtures (capa/cmms/etc.)
│
└── tests/                          ← 88 tests, all mocked Azure
    └── snapshots/                  ← pinned factory output snapshots
```

---

## Key design choices (one-line each)

* **Portal-managed prompt agents, not local SDK agents** — the user wanted them visible/editable in the Foundry portal.
* **Foundry IQ MCP tool baked into every agent version** — KB grounding is the agent's default behavior, not an orchestrator concern.
* **`IndexedSqlKnowledgeSource` for row data, doc indexer for procedures** — when both held the same data the agent paraphrased instead of citing rows. Splitting them fixed it.
* **Separate manager + worker LLM deployments** — sharing one deployment 429s reliably because the manager invokes the model every round on top of every worker call.
* **Per-scenario `participants` whitelist + `max_rounds` cap** — keeps narrow scenarios narrow.
* **Single source of truth = `profile.yaml`** — agents, KB sources, tools, and skills all live there; everything else (cards, KB seed, agent versions, snapshots) derives from it.

---

## License

Fictional dataset; demo code. Any resemblance to actual companies, facilities, or individuals is coincidental.
