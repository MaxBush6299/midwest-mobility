# Midwest Mobility Components (MMC): Multi-Agent Manufacturing Demo

**What if every specialist in your company could be summoned to the table the moment a problem needed them, and something intelligent decided who to call, in what order, and when to change the plan?**

This repository is an exploration of that idea. It demonstrates a way of building AI systems that breaks from the two patterns most automation falls into today: rigid, pre-wired workflows and brittle robotic process automation. Instead, it shows what becomes possible when you **develop agents independently, in their own silos, and orchestrate them generatively at runtime.**

### The concept

Real organizations don't solve hard problems with a flowchart. When a brake-caliper line goes down, a person doesn't run a fixed script; they reason about *who* to pull in: maybe quality, then procurement to check the supplier, then engineering to confirm the part revision, then demand planning to understand what's at risk downstream. The path isn't known in advance. It emerges from the problem.

This demo reproduces that dynamic with software:

- **Agents are built in silos.** Ten specialist agents live in two separate domains: five on the **plant floor** (maintenance, quality, training, operations, safety) and five across the **enterprise** (procurement, supply chain, engineering/PLM, demand, warranty). Each is developed, grounded, and owned independently, as if by different teams. None of them knows the others exist.
- **Orchestration is generative, not deterministic.** There is no hard-coded workflow connecting them. A **Magentic manager** reads the question, forms a plan, decides which specialists to bring in, dispatches them, reads what comes back, and **replans on the fly**, pulling in whoever the evolving situation demands. Change the question and the whole collaboration reshapes itself. No pipeline was rewired; the system reasoned its way there.
- **Every specialist is grounded in truth.** Each agent is backed by a Foundry IQ knowledge base that blends policy documents (markdown / PDF) with **live row data indexed straight from Azure SQL**: training records, PM schedules, incidents, suppliers, purchase orders. Answers are traceable to real data, not improvised.

The result is a system that assembles a cross-company team of experts on demand and reasons its way to a solution, the way an organization actually works, not the way a script pretends it does.

### Why it's the art of the possible

Because the agents are decoupled from the orchestration, the whole thing is **composable and extensible in ways a fixed workflow never is.** A **plant-cloning path** proves the point: a brand-new facility (**Plant 4**) is stood up as a copy of Plant 7 and immediately participates in orchestration with **zero changes to the manager's code**. Add a specialist, add a site, swap the reasoning model: the collaboration adapts, because nothing about *how* the experts work together was hard-wired in the first place.

The entire run streams to a small FastAPI + SSE trace UI, so you can *watch* the manager think: the plan it forms, every specialist it calls, every hop, and every mid-course replan in real time.

> 📐 **Looking for the deep dive?** See **[`docs/SOLUTION_ARCHITECTURE.md`](docs/SOLUTION_ARCHITECTURE.md)**: full component map, request flow, configuration surface, profile→KB→agent mapping, and gotchas.
>
> 📊 Looking for the source dataset? See **[`docs/DATASET.md`](docs/DATASET.md)**: the original Plant 7 knowledge base contents (markdown SOPs + CSV operational logs).

---

## At a glance

A reference implementation built on **Microsoft Agent Framework** (Magentic orchestration), **Azure AI Foundry** (Agents Service + Foundry IQ), and **Azure SQL**.

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

## Prerequisites

- **Python 3.11+**
- **Azure subscription** with access to Azure AI Foundry, Azure AI Search, and Azure SQL Database
- **Azure CLI ≥ 2.60** with the Bicep CLI (`az bicep version`)
- **Microsoft ODBC Driver 18 for SQL Server**: required by `pyodbc` for the SQL data-load scripts
- Sign in once so `AzureCliCredential` works: `az login`

All Azure access is **passwordless** (Microsoft Entra ID via `AzureCliCredential` /
`DefaultAzureCredential`) with no SQL passwords or shared keys. Real endpoints and
IDs live only in your local, git-ignored `.env` (copy [`.env.example`](.env.example)).

---

## Provision from scratch

Already have the environment stood up? Skip to [Run the demo](#run-the-demo).

```powershell
# 0. Python env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
copy .env.example .env        # fill in as you capture outputs below

# 1. Deploy the Azure infrastructure (2x Search, 2 Foundry projects, SQL, storage)
az login
az group create -n rg-magentictest -l eastus
az deployment group create `
  --resource-group rg-magentictest `
  --template-file infra/bicep/main.bicep `
  --parameters infra/bicep/parameters/dev.bicepparam
# Capture outputs into .env (project endpoints, SQL FQDN, search MI object ids):
az deployment group show -g rg-magentictest -n main --query properties.outputs

# 2. Load the CSV operational data into Azure SQL (change tracking on),
#    then grant each Search managed identity db_datareader
python scripts/provision_sql.py
python scripts/grant_sql_access.py

# 3. Seed the Foundry IQ knowledge bases (docs + IndexedSql sources)
python scripts/seed_foundry_iq.py --plant plant7
python scripts/seed_foundry_iq.py --enterprise

# 4. In the Foundry portal, create the IQ project connection for each KB, then set
#    PLANT_KB_CONNECTION_ID / PLANT_KB_MCP_URL (+ enterprise equivalents) in .env.
#    This step is portal-only; see infra/bicep/README.md for why.

# 5. Create / update the portal-managed prompt-agent versions from profile.yaml
python scripts/refresh_catalog.py
```

> Full component map, the profile→KB→agent mapping, and every gotcha are in
> [`docs/SOLUTION_ARCHITECTURE.md`](docs/SOLUTION_ARCHITECTURE.md); infra details
> are in [`infra/bicep/README.md`](infra/bicep/README.md).

---

## Run the demo

```powershell
# Trace UI: scenario picker + live event stream
$env:MMC_TRACE_UI_PORT="8000"
python -m mmc_agents.trace_ui
# Open http://127.0.0.1:8000 and pick a scenario
```

Prefer the CLI? The hero scenario has a standalone runner; other scenarios are
launched from the trace UI's scenario picker.

```powershell
python scripts/run_scenario.py        # runs the brake_caliper fan-out
```

---

## Demo scenarios

| Scenario | What it shows | Agents | Roughly |
|---|---|---|---|
| `training_gap` | SQL spot-check: Plant 7 employees whose LOTO Authorized Person cert expires before 2026-12-31 | 1 | ~3-5 hops |
| `po_status` | SQL spot-check: open Acme Brakes POs flagged At Risk / Watch, cite `po_spend` rows | 1 | ~3-5 hops |
| `pm_check` | SQL spot-check: Line 1 PM tasks that generated follow-up WOs this quarter | 1 | ~3-5 hops |
| **`supplier_risk_pm`** | **Cross-KB SQL story: at-risk PO → which Plant 7 PMs depend on the part → backup supplier in `supplier_master`** | **3** | **~6-10 hops** |
| `multi_plant_training` | Cross-plant rollup: Plant 7 + Plant 4 LOTO expirations, enterprise rolls up the refresher load | 3 | ~8-12 hops |
| `loto_cluster` | Plant + enterprise: cluster L1 Press near-misses, check competency, escalate to enterprise quality | 5-6 | ~15 hops |
| `brake_caliper` | Full fan-out: supplier delay impact, mitigation, cost; triggers `NO_DIRECT_ALT` replan | All 10 | ~30 hops |
| `multi_plant_warranty` | Cross-plant warranty spike on `BRK-CAL-XYZ`: both plants + enterprise coordinate with the supplier | All | ~60 hops |

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
│   ├── demo/                       ← run-of-show + hot-add runbook
│   └── internal/                   ← build-tracking docs (plans, specs, results, handoff)
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
├── plants/                         ← one folder per plant
│   ├── plant7/                     ← origin plant (profile.yaml + kb/)
│   └── plant4/                     ← clone produced by Gate D plant-cloning
│
├── templates/plant_template/       ← Jinja templates used by clone_plant.py
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
│   ├── run_scenario.py             ← CLI runner (brake_caliper hero scenario)
│   ├── clone_plant.py              ← Gate D, clone a plant from the template
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
└── tests/                          ← 154 tests, all Azure calls mocked
    └── snapshots/                  ← pinned factory output snapshots
```

---

## Key design choices (one-line each)

* **Portal-managed prompt agents, not local SDK agents:** the user wanted them visible/editable in the Foundry portal.
* **Foundry IQ MCP tool baked into every agent version:** KB grounding is the agent's default behavior, not an orchestrator concern.
* **`IndexedSqlKnowledgeSource` for row data, doc indexer for procedures:** when both held the same data the agent paraphrased instead of citing rows. Splitting them fixed it.
* **Separate manager + worker LLM deployments:** sharing one deployment 429s reliably because the manager invokes the model every round on top of every worker call.
* **Per-scenario `participants` whitelist + `max_rounds` cap:** keeps narrow scenarios narrow.
* **Single source of truth = `profile.yaml`:** agents, KB sources, tools, and skills all live there; everything else (cards, KB seed, agent versions, snapshots) derives from it.

---

## License & contributing

Licensed under the [MIT License](LICENSE). Contributions are welcome; see
[`CONTRIBUTING.md`](CONTRIBUTING.md), the [Code of Conduct](CODE_OF_CONDUCT.md),
and the [security policy](SECURITY.md).

The dataset is entirely **fictional**. Any resemblance to actual companies,
facilities, or individuals is coincidental.
