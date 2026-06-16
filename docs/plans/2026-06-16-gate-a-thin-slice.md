# Gate A — Thin Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up `rg-magentictest` from scratch and demonstrate the Magentic manager composing a multi-agent flow over 5 Plant 7 agents + 1 Supply Chain stub for the brake-caliper scenario, traced via the Foundry portal.

**Architecture:** Bicep-provisioned Azure resources (2 Foundry projects, 1 Plant 7 Foundry IQ KB with 3 sources, 1 enterprise Foundry IQ KB stub, storage, AI Search). Python package `mmc_agents` with: prompt-based Foundry agent factory, Foundry IQ MCP wrapper, local-catalog A2A registry, Magentic orchestrator (model-agnostic via Agent Framework `ChatClient`), one scripted scenario.

**Tech Stack:** Python 3.11+, Microsoft Agent Framework SDK (Python), Foundry Agent Service, Foundry IQ, Azure AI Search, Azure Storage, Bicep, pytest, Azure CLI.

**Reference docs (read these before starting):**
- `DEMO_BUILD_HANDOFF.md` — architecture, agent rosters, KB→agent mapping, naming conventions.
- `docs/specs/2026-06-16-mmc-agent-network-implementation-design.md` — implementation decisions (D1–D15) that govern this plan.
- `docs/MMC_Plant7_Company_Profile_v1.md` — source of truth for MMC content (naming, IDs, standards).

**Verify against Microsoft Learn before coding** (per spec D2/handoff §2): Agent Framework Magentic API surface, Foundry IQ MCP connect path, A2A card schema, Foundry Agent Service Python SDK. Pin SDK versions; Magentic is flagged experimental.

---

## File Structure

**Repo additions / migrations:**

| Path | Responsibility |
|---|---|
| `pyproject.toml` | Python package metadata, deps (`agent-framework`, `httpx`, `pydantic`, `pyyaml`, `pytest`). |
| `.env.example` | Required env vars (Azure tenant/subscription, model endpoint, RG name). |
| `.gitignore` | Add `.venv/`, `__pycache__/`, `.env`, `agents/catalog.json` (auto-generated). |
| `infra/bicep/main.bicep` | Top-level deployment for `rg-magentictest`. |
| `infra/bicep/modules/storage.bicep` | Storage account for KB raw documents. |
| `infra/bicep/modules/ai-search.bicep` | Two Azure AI Search instances (plant + enterprise). |
| `infra/bicep/modules/foundry-project.bicep` | Parameterized Foundry project; instantiated twice. |
| `infra/bicep/modules/foundry-iq-kb.bicep` | Foundry IQ KB + named sources (parameterized list). |
| `infra/bicep/parameters/dev.bicepparam` | RG, region, resource names. |
| `infra/bicep/README.md` | Deploy + tear-down commands. |
| `plants/plant7/profile.yaml` | Plant 7 metadata: lines, equipment IDs, shifts, KB-source manifest, agent skills. |
| `plants/plant7/kb/**` | Migrated from `kb/Internal/**`. |
| `plants/plant7/agents/*.agent.json` | 5 generated A2A cards. |
| `shared/kb/oem-manuals/`, `shared/kb/regulatory-reference/` | Migrated from `kb/oem-manuals/`, `kb/regulatory-reference/`. |
| `enterprise/supply-chain/data/supplier_master.csv` | Seed: 25 suppliers incl. Acme Brakes. |
| `enterprise/supply-chain/data/bom_where_used.csv` | Seed: maps `BRK-CAL-XYZ` → Plant 7 L1. |
| `enterprise/supply-chain/fixtures/*.json` | Derived from CSVs by `derive_fixtures.py`. |
| `enterprise/supply-chain/agent.json` | Generated A2A card. |
| `agents/catalog.json` | Auto-generated; aggregated A2A catalog. |
| `src/mmc_agents/agent_factory.py` | `build_agent(profile, role) -> FoundryAgent` + emits A2A card JSON. |
| `src/mmc_agents/kb_client.py` | `FoundryIQClient.connect(kb_id, source_ids)` → tool binding for an agent. |
| `src/mmc_agents/tools/fixtures_loader.py` | `load_fixture(path, key) -> dict | None`. |
| `src/mmc_agents/tools/erp.py` | `@tool bom_where_used(part_id)`, `@tool inventory(part_id)`. |
| `src/mmc_agents/tools/supplier.py` | `@tool lookup(supplier_id)`, `@tool alternates(part_id)`. |
| `src/mmc_agents/registry/base.py` | `RegistrySource` Protocol; `list_agents() -> list[AgentCard]`. |
| `src/mmc_agents/registry/local_catalog.py` | Reads `agents/catalog.json`; `WatchedLocalCatalogSource` re-reads on every call. |
| `src/mmc_agents/registry/agent365.py` | Stub raising `NotImplementedError` with TODO. |
| `src/mmc_agents/orchestrator/manager.py` | `MagenticManager.run(problem_statement) -> RunResult`. |
| `src/mmc_agents/orchestrator/model_config.py` | `load_chat_client() -> ChatClient` from env+YAML. |
| `src/mmc_agents/orchestrator/scenarios/brake_caliper.py` | Problem-statement constant + expected-bounds assertions. |
| `scripts/refresh_catalog.py` | Walks `plants/*/agents/` + `enterprise/*/agent.json`, writes `agents/catalog.json`. |
| `scripts/seed_foundry_iq.py` | Uploads plant/enterprise content into provisioned KBs. |
| `scripts/derive_fixtures.py` | Generates `fixtures/*.json` from `data/*.csv` for each enterprise node. |
| `tests/test_fixtures_loader.py` | Determinism + missing-key behavior. |
| `tests/test_local_catalog.py` | Read, watch, hot-add. |
| `tests/test_agent_factory.py` | Card generation matches A2A schema. |
| `tests/test_brake_caliper_smoke.py` | Manager hops ≥4 agents, backtracks ≥1 time (skipped if `MMC_LIVE=0`). |

---

## Task 1: Repo bootstrap

**Files:**
- Create: `pyproject.toml`, `.env.example`, `.gitignore` (modify if exists)

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "mmc_agents"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "agent-framework>=1.0.0",   # pin actual experimental Magentic-supporting version after Microsoft Learn check
  "httpx>=0.27",
  "pydantic>=2.7",
  "pyyaml>=6.0",
  "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-asyncio>=0.23", "ruff>=0.5"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 2: Create `.env.example`**

```
# Azure
AZURE_TENANT_ID=
AZURE_SUBSCRIPTION_ID=
AZURE_RESOURCE_GROUP=rg-magentictest
AZURE_LOCATION=eastus

# Foundry projects (set after Bicep deploy)
FOUNDRY_PLANT_PROJECT_ENDPOINT=
FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT=

# Foundry IQ KBs (set after seed)
FOUNDRY_IQ_KB_PLANT7_ID=
FOUNDRY_IQ_KB_ENTERPRISE_ID=

# Reasoning model (D2: configurable)
MMC_MODEL_PROVIDER=azure_openai
MMC_MODEL_DEPLOYMENT=gpt-5-reasoning
MMC_MODEL_ENDPOINT=
MMC_MODEL_FALLBACK_DEPLOYMENT=gpt-4o
```

- [ ] **Step 3: Update `.gitignore`**

Append:
```
.venv/
__pycache__/
*.pyc
.env
agents/catalog.json
.pytest_cache/
htmlcov/
```

- [ ] **Step 4: Create venv + install**

Run: `python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -e .[dev]`
Expected: install succeeds; `pytest --version` prints a version.

- [ ] **Step 5: Commit**

```
git add pyproject.toml .env.example .gitignore
git commit -m "chore: bootstrap Python package + dev tooling"
```

---

## Task 2: Migrate KB content into new layout

**Files:**
- Move: `kb/Internal/**` → `plants/plant7/kb/**`
- Move: `kb/oem-manuals/` → `shared/kb/oem-manuals/`
- Move: `kb/regulatory-reference/` → `shared/kb/regulatory-reference/`

- [ ] **Step 1: Create destination directories**

```
mkdir plants\plant7\kb, plants\plant7\fixtures, plants\plant7\agents
mkdir shared\kb
mkdir enterprise\supply-chain\data, enterprise\supply-chain\fixtures
mkdir agents
```

- [ ] **Step 2: Move files (use `git mv` to preserve history)**

```
git mv kb/Internal/* plants/plant7/kb/
git mv kb/oem-manuals shared/kb/oem-manuals
git mv kb/regulatory-reference shared/kb/regulatory-reference
Remove-Item kb -Recurse
```

- [ ] **Step 3: Verify**

Run: `Get-ChildItem plants\plant7\kb -Recurse -File | Measure-Object | Select Count`
Expected: file count matches what was in `kb/Internal/` before the move.

- [ ] **Step 4: Commit**

```
git add -A
git commit -m "refactor: migrate kb/ to plants/plant7/kb and shared/kb per spec"
```

---

## Task 3: Plant 7 profile

**Files:**
- Create: `plants/plant7/profile.yaml`

- [ ] **Step 1: Author `profile.yaml`**

```yaml
plant_id: plant7
display_name: MMC Plant 7 (Illinois)
location:
  state: IL
  country: US
shifts:
  - { id: A, hours: "06:00-14:00" }
  - { id: B, hours: "14:00-22:00" }
  - { id: C, hours: "22:00-06:00" }
lines:
  - { id: L1, name: Stamping/Forming, equipment_prefix: L1-PRS- }
  - { id: L2, name: Assembly/Robot Cells, equipment_prefix: L2-ROB- }
  - { id: L3, name: Conveyor/Pack-Out, equipment_prefix: L3-CNV- }
standards: [OSHA-29CFR1910, ISO-45001, ISO-9001, ANSI-RIA-R15.06, NFPA-70E]

kb:
  kb_id_env: FOUNDRY_IQ_KB_PLANT7_ID
  sources:
    ehs:
      paths: ["plants/plant7/kb/02_EHS_Internal", "shared/kb/regulatory-reference/OSHA"]
    maintenance:
      paths: ["plants/plant7/kb/03_Maintenance", "shared/kb/oem-manuals"]
    quality_ops:
      paths: ["plants/plant7/kb/04_Quality", "plants/plant7/kb/05_Ops_Shift", "plants/plant7/kb/08_Logs_Data"]

agents:
  - role: ehs
    display_name: Plant 7 EHS / Safety
    kb_sources: [ehs]
    tools: [capa]
    skills:
      - id: hazard_loto_lookup
        description: Hazard & LOTO requirement lookup
      - id: incident_clustering
        description: Incident clustering & repeat-cause analysis
      - id: osha_iso_compliance_check
        description: OSHA / ISO 45001 compliance check
  - role: maintenance
    display_name: Plant 7 Maintenance & Reliability
    kb_sources: [maintenance]
    tools: [cmms, scada]
    skills:
      - id: pm_status
        description: PM status & overdue work-order lookup
      - id: asset_history
        description: Asset history & jam-clear procedure
      - id: spare_part_lookup
        description: Spare-part lookup & OEE / downtime
  - role: quality
    display_name: Plant 7 Quality
    kb_sources: [quality_ops]
    tools: [qms]
    skills:
      - id: ncr_capa_status
        description: NCR / CAPA status & 8D containment
      - id: defect_safety_linkage
        description: Defect → safety-issue linkage
      - id: first_piece_inspection
        description: First-piece / changeover inspection
  - role: shiftops
    display_name: Plant 7 Shift Ops
    kb_sources: [quality_ops]
    tools: [mes]
    skills:
      - id: handover_summary
        description: Shift-handover summary & open items
      - id: changeover_guidance
        description: Changeover / SMED step guidance
      - id: line_stop_support
        description: Line-stop decision support
  - role: training
    display_name: Plant 7 Training / Competency
    kb_sources: [quality_ops]
    tools: [lms]
    skills:
      - id: cert_status
        description: Certification status & expiration lookup
      - id: qualified_for_task
        description: "Who is qualified for this task?"
      - id: training_gap_link
        description: Training-gap vs. incident linkage
```

- [ ] **Step 2: Commit**

```
git add plants/plant7/profile.yaml
git commit -m "feat(plant7): add profile.yaml driving agent generation"
```

---

## Task 4: Bicep — storage module

**Files:**
- Create: `infra/bicep/modules/storage.bicep`

- [ ] **Step 1: Write module**

```bicep
param location string
param storageName string

resource sa 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

output storageAccountId string = sa.id
output storageAccountName string = sa.name
```

- [ ] **Step 2: Lint**

Run: `az bicep build --file infra/bicep/modules/storage.bicep`
Expected: success, emits `.json` next to it.

- [ ] **Step 3: Commit**

```
git add infra/bicep/modules/storage.bicep
git commit -m "infra: storage module"
```

---

## Task 5: Bicep — AI Search module

**Files:**
- Create: `infra/bicep/modules/ai-search.bicep`

- [ ] **Step 1: Write module**

```bicep
param location string
param searchName string
@allowed(['basic','standard'])
param sku string = 'standard'

resource search 'Microsoft.Search/searchServices@2024-03-01-preview' = {
  name: searchName
  location: location
  sku: { name: sku }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    semanticSearch: 'standard'
    authOptions: { aadOrApiKey: { aadAuthFailureMode: 'http401WithBearerChallenge' } }
  }
}

output searchId string = search.id
output searchName string = search.name
```

- [ ] **Step 2: Lint + commit**

```
az bicep build --file infra/bicep/modules/ai-search.bicep
git add infra/bicep/modules/ai-search.bicep
git commit -m "infra: AI Search module"
```

---

## Task 6: Bicep — Foundry project module

**Verify against Microsoft Learn:** the exact resource type for "Foundry project" (likely `Microsoft.MachineLearningServices/workspaces` with kind=`Project` or the newer `Microsoft.AIFoundry/...` namespace as of 2026). Pin the right one before writing.

**Files:**
- Create: `infra/bicep/modules/foundry-project.bicep`

- [ ] **Step 1: Write module (template — replace resource type once verified)**

```bicep
param location string
param projectName string
param tier string  // 'plant' | 'enterprise'

// TODO(verify-on-Learn): confirm resource type + apiVersion for Foundry project
resource project 'Microsoft.MachineLearningServices/workspaces@2024-10-01' = {
  name: projectName
  location: location
  kind: 'Project'
  identity: { type: 'SystemAssigned' }
  properties: {
    friendlyName: 'MMC ${tier} Foundry Project'
  }
}

output projectId string = project.id
output projectName string = project.name
output projectEndpoint string = project.properties.discoveryUrl
```

- [ ] **Step 2: Lint + commit**

```
az bicep build --file infra/bicep/modules/foundry-project.bicep
git add infra/bicep/modules/foundry-project.bicep
git commit -m "infra: Foundry project module"
```

---

## Task 7: Bicep — Foundry IQ KB module

**Verify on Microsoft Learn first:** Foundry IQ KB resource type and whether KB+sources are deployable in ARM/Bicep today, or must be created via the data-plane SDK at seed time. If data-plane only, this module becomes a no-op and `seed_foundry_iq.py` (Task 10) does the creation.

**Files:**
- Create: `infra/bicep/modules/foundry-iq-kb.bicep`

- [ ] **Step 1: Write module skeleton (control-plane variant if available)**

```bicep
param location string
param kbName string
param searchResourceId string
param sourceNames array  // e.g. ['ehs','maintenance','quality_ops']

// TODO(verify-on-Learn): Foundry IQ KB resource type. If only data-plane, leave this
// file as a placeholder that emits the names as outputs for the seed script to consume.

output kbName string = kbName
output sourceNames array = sourceNames
```

- [ ] **Step 2: Commit**

```
git add infra/bicep/modules/foundry-iq-kb.bicep
git commit -m "infra: Foundry IQ KB module (control-plane skeleton)"
```

---

## Task 8: Bicep — main + parameters + README

**Files:**
- Create: `infra/bicep/main.bicep`, `infra/bicep/parameters/dev.bicepparam`, `infra/bicep/README.md`

- [ ] **Step 1: Write `main.bicep`**

```bicep
targetScope = 'resourceGroup'

param location string = 'eastus'
param storageName string
param searchPlantName string
param searchEnterpriseName string
param foundryPlantProjectName string
param foundryEnterpriseProjectName string
param plant7KbName string = 'kb-plant7'
param enterpriseKbName string = 'kb-enterprise'

module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: { location: location, storageName: storageName }
}

module searchPlant 'modules/ai-search.bicep' = {
  name: 'searchPlant'
  params: { location: location, searchName: searchPlantName }
}

module searchEnt 'modules/ai-search.bicep' = {
  name: 'searchEnt'
  params: { location: location, searchName: searchEnterpriseName }
}

module foundryPlant 'modules/foundry-project.bicep' = {
  name: 'foundryPlant'
  params: { location: location, projectName: foundryPlantProjectName, tier: 'plant' }
}

module foundryEnt 'modules/foundry-project.bicep' = {
  name: 'foundryEnt'
  params: { location: location, projectName: foundryEnterpriseProjectName, tier: 'enterprise' }
}

module kbPlant7 'modules/foundry-iq-kb.bicep' = {
  name: 'kbPlant7'
  params: {
    location: location
    kbName: plant7KbName
    searchResourceId: searchPlant.outputs.searchId
    sourceNames: ['ehs','maintenance','quality_ops']
  }
}

module kbEnterprise 'modules/foundry-iq-kb.bicep' = {
  name: 'kbEnterprise'
  params: {
    location: location
    kbName: enterpriseKbName
    searchResourceId: searchEnt.outputs.searchId
    sourceNames: ['supply_chain','procurement','engineering_plm','enterprise_quality','demand_program']
  }
}

output foundryPlantEndpoint string = foundryPlant.outputs.projectEndpoint
output foundryEnterpriseEndpoint string = foundryEnt.outputs.projectEndpoint
```

- [ ] **Step 2: Write `parameters/dev.bicepparam`**

```bicep
using '../main.bicep'

param location = 'eastus'
param storageName = 'stmmcdemo${uniqueString(resourceGroup().id)}'
param searchPlantName = 'srch-mmc-plant'
param searchEnterpriseName = 'srch-mmc-enterprise'
param foundryPlantProjectName = 'mmc-foundry-plant'
param foundryEnterpriseProjectName = 'mmc-foundry-enterprise'
```

- [ ] **Step 3: Write `infra/bicep/README.md`**

```markdown
# Bicep deployment

Target: resource group `rg-magentictest` in `eastus`.

## Deploy

```pwsh
az login
az account set --subscription <your-sub-id>
az deployment group create `
  --resource-group rg-magentictest `
  --template-file main.bicep `
  --parameters parameters/dev.bicepparam
```

## Tear down

```pwsh
az group delete --name rg-magentictest --yes --no-wait
```
```

- [ ] **Step 4: Lint + commit**

```
az bicep build --file infra/bicep/main.bicep
git add infra/bicep/main.bicep infra/bicep/parameters/dev.bicepparam infra/bicep/README.md
git commit -m "infra: top-level main + dev params + deploy README"
```

---

## Task 9: Deploy to `rg-magentictest`

- [ ] **Step 1: Verify RG exists**

Run: `az group show -n rg-magentictest --query location -o tsv`
Expected: `eastus`

- [ ] **Step 2: Deploy**

Run: `az deployment group create -g rg-magentictest -f infra/bicep/main.bicep -p infra/bicep/parameters/dev.bicepparam -o table`
Expected: deployment succeeds; `Succeeded` provisioning state.

- [ ] **Step 3: Capture outputs into `.env`**

```pwsh
$out = az deployment group show -g rg-magentictest -n main --query properties.outputs -o json | ConvertFrom-Json
Add-Content .env "FOUNDRY_PLANT_PROJECT_ENDPOINT=$($out.foundryPlantEndpoint.value)"
Add-Content .env "FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT=$($out.foundryEnterpriseEndpoint.value)"
```

- [ ] **Step 4: Verify in portal**

Open the RG in the Azure Portal. Confirm: 1 storage, 2 Search, 2 Foundry projects.

No commit (no file changes from this task).

---

## Task 10: `seed_foundry_iq.py` — upload Plant 7 content

**Files:**
- Create: `scripts/seed_foundry_iq.py`

- [ ] **Step 1: Write seeder**

```python
"""Seed Foundry IQ KBs from disk per profile.yaml mappings.

Uses the Foundry IQ data-plane SDK to:
  1. Create the KB (if Bicep didn't already) and its sources.
  2. Upload files under each profile-mapped path into the matching source.
  3. Trigger indexer / ingestion.

Run:
  python scripts/seed_foundry_iq.py --plant plant7
  python scripts/seed_foundry_iq.py --enterprise
"""
from __future__ import annotations
import argparse, os, yaml
from pathlib import Path

# TODO(verify-on-Learn): swap to the actual Foundry IQ Python SDK client
# (likely under azure.ai.foundry or azure.ai.projects as of 2026).
from foundry_iq import FoundryIQClient  # placeholder import

ROOT = Path(__file__).resolve().parent.parent

def seed_plant(plant_id: str) -> None:
    profile = yaml.safe_load((ROOT / "plants" / plant_id / "profile.yaml").read_text())
    kb_id_env = profile["kb"]["kb_id_env"]
    client = FoundryIQClient.from_env(project_endpoint=os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"])
    kb = client.kbs.get_or_create(name=f"kb-{plant_id}")
    for source_name, src in profile["kb"]["sources"].items():
        source = kb.sources.get_or_create(name=source_name)
        for rel in src["paths"]:
            for f in (ROOT / rel).rglob("*"):
                if f.is_file():
                    source.upload(str(f))
        source.start_indexer()
    print(f"Set {kb_id_env}={kb.id} in your .env")

def seed_enterprise() -> None:
    client = FoundryIQClient.from_env(project_endpoint=os.environ["FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT"])
    kb = client.kbs.get_or_create(name="kb-enterprise")
    nodes = ["supply-chain","procurement","engineering-plm","enterprise-quality","demand-program"]
    for node in nodes:
        node_dir = ROOT / "enterprise" / node
        if not node_dir.exists():
            continue
        source = kb.sources.get_or_create(name=node.replace("-","_"))
        for f in (node_dir / "data").rglob("*"):
            if f.is_file():
                source.upload(str(f))
        source.start_indexer()
    print(f"Set FOUNDRY_IQ_KB_ENTERPRISE_ID={kb.id} in your .env")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plant")
    ap.add_argument("--enterprise", action="store_true")
    args = ap.parse_args()
    if args.plant: seed_plant(args.plant)
    if args.enterprise: seed_enterprise()
```

- [ ] **Step 2: Run for Plant 7**

Run: `python scripts/seed_foundry_iq.py --plant plant7`
Expected: completes; prints KB id to add to `.env`.

- [ ] **Step 3: Add `FOUNDRY_IQ_KB_PLANT7_ID` to `.env`**

- [ ] **Step 4: Commit**

```
git add scripts/seed_foundry_iq.py
git commit -m "feat(scripts): seed Foundry IQ KBs from profile + enterprise data"
```

---

## Task 11: Verify Plant 7 KB grounds a sample question

- [ ] **Step 1: In the Foundry portal**, open the Plant 7 project → KB → "Test retrieval" → query:

> "What LOTO procedure applies to L1-PRS-001?"

Expected: results cite files from `plants/plant7/kb/02_EHS_Internal/`.

No commit.

---

## Task 12: Supply Chain seed data (minimal for thin slice)

**Files:**
- Create: `enterprise/supply-chain/data/supplier_master.csv`, `enterprise/supply-chain/data/bom_where_used.csv`

- [ ] **Step 1: `supplier_master.csv`** (5 rows is enough for thin slice; include Acme)

```csv
Supplier_ID,Name,Tier,Country,Lead_Time_Days,Disruption_Flag,Disruption_Days,Risk_Score
SUP-001,Acme Brakes,1,US,14,Y,21,High
SUP-002,Midwest Stampings,2,US,7,N,0,Low
SUP-003,Globex Robotics,1,DE,28,N,0,Medium
SUP-004,Initech Fasteners,2,US,5,N,0,Low
SUP-005,Hooli Castings,1,MX,21,N,0,Medium
```

- [ ] **Step 2: `bom_where_used.csv`**

```csv
Part_ID,Part_Name,Supplier_ID,Plant_ID,Line_ID,Qty_Per_Assy,Effective_Date
BRK-CAL-XYZ,Brake Caliper Assembly,SUP-001,plant7,L1,1,2025-01-01
STM-PNL-A1,Stamped Panel A1,SUP-002,plant7,L1,2,2025-01-01
ROB-ARM-G3,Robot Arm Gen3,SUP-003,plant7,L2,1,2025-01-01
FST-M8-100,M8 Fastener Pack,SUP-004,plant7,L1,50,2025-01-01
CST-HSG-04,Cast Housing 04,SUP-005,plant7,L3,1,2025-01-01
```

- [ ] **Step 3: Commit**

```
git add enterprise/supply-chain/data/
git commit -m "feat(supply-chain): seed supplier_master + bom_where_used for brake-caliper scenario"
```

---

## Task 13: `derive_fixtures.py`

**Files:**
- Create: `scripts/derive_fixtures.py`

- [ ] **Step 1: Write derivation**

```python
"""Derive tool fixtures (JSON keyed by lookup field) from enterprise CSVs.

Single source of truth: CSVs in enterprise/<node>/data/.
Fixtures in enterprise/<node>/fixtures/ are regenerable byte-identically.
"""
from __future__ import annotations
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (csv_path, fixture_path, key_column)
MAPPINGS = [
    (
        "enterprise/supply-chain/data/supplier_master.csv",
        "enterprise/supply-chain/fixtures/supplier_master.json",
        "Supplier_ID",
    ),
    (
        "enterprise/supply-chain/data/bom_where_used.csv",
        "enterprise/supply-chain/fixtures/bom_where_used.json",
        "Part_ID",
    ),
]

def derive(csv_path: Path, fixture_path: Path, key: str) -> None:
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    out: dict[str, dict] = {}
    for row in rows:
        out[row[key]] = row
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_text(
        json.dumps(out, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )

def main() -> None:
    for csv_rel, fix_rel, key in MAPPINGS:
        derive(ROOT / csv_rel, ROOT / fix_rel, key)
    print(f"Derived {len(MAPPINGS)} fixtures.")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run**

Run: `python scripts/derive_fixtures.py`
Expected: `enterprise/supply-chain/fixtures/supplier_master.json` + `bom_where_used.json` created.

- [ ] **Step 3: Run again — confirm deterministic**

Run: `python scripts/derive_fixtures.py; git diff --stat enterprise/supply-chain/fixtures`
Expected: no diff.

- [ ] **Step 4: Commit**

```
git add scripts/derive_fixtures.py enterprise/supply-chain/fixtures/
git commit -m "feat(scripts): derive_fixtures + supply-chain initial fixtures"
```

---

## Task 14: `fixtures_loader.py` (TDD)

**Files:**
- Create: `src/mmc_agents/__init__.py` (empty), `src/mmc_agents/tools/__init__.py` (empty)
- Create: `tests/test_fixtures_loader.py`, then `src/mmc_agents/tools/fixtures_loader.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_fixtures_loader.py
from pathlib import Path
import json, pytest
from mmc_agents.tools.fixtures_loader import load_fixture

def test_load_existing_key(tmp_path: Path):
    p = tmp_path / "f.json"
    p.write_text(json.dumps({"K1": {"a": 1}, "K2": {"a": 2}}))
    assert load_fixture(p, "K1") == {"a": 1}

def test_missing_key_returns_none(tmp_path: Path):
    p = tmp_path / "f.json"
    p.write_text(json.dumps({"K1": {"a": 1}}))
    assert load_fixture(p, "NOPE") is None

def test_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_fixture(tmp_path / "missing.json", "K1")
```

- [ ] **Step 2: Run — confirm failure**

Run: `pytest tests/test_fixtures_loader.py -v`
Expected: ImportError / collection failure.

- [ ] **Step 3: Implement**

```python
# src/mmc_agents/tools/fixtures_loader.py
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=64)
def _read(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)
    return json.loads(p.read_text(encoding="utf-8"))

def load_fixture(path: str | Path, key: str) -> dict | None:
    return _read(str(path)).get(key)
```

- [ ] **Step 4: Run — confirm pass**

Run: `pytest tests/test_fixtures_loader.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```
git add src/mmc_agents/__init__.py src/mmc_agents/tools/__init__.py src/mmc_agents/tools/fixtures_loader.py tests/test_fixtures_loader.py
git commit -m "feat(tools): fixtures_loader with cache + tests"
```

---

## Task 15: `tools/erp.py` (TDD)

**Files:**
- Create: `tests/test_erp_tool.py`, `src/mmc_agents/tools/erp.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_erp_tool.py
from mmc_agents.tools.erp import bom_where_used

def test_bom_where_used_finds_known_part():
    result = bom_where_used("BRK-CAL-XYZ")
    assert result is not None
    assert result["Plant_ID"] == "plant7"
    assert result["Line_ID"] == "L1"
    assert result["Supplier_ID"] == "SUP-001"

def test_bom_where_used_unknown_part_returns_not_found():
    result = bom_where_used("DOES-NOT-EXIST")
    assert result == {"status": "not_found", "part_id": "DOES-NOT-EXIST"}
```

- [ ] **Step 2: Run — confirm failure**

Run: `pytest tests/test_erp_tool.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement**

```python
# src/mmc_agents/tools/erp.py
from __future__ import annotations
from pathlib import Path
from mmc_agents.tools.fixtures_loader import load_fixture

# Agent Framework's @tool decorator. Verify exact import on Microsoft Learn.
from agent_framework import tool  # TODO(verify): exact module path

_FIX = Path(__file__).resolve().parents[3] / "enterprise" / "supply-chain" / "fixtures" / "bom_where_used.json"

@tool(description="Look up where a part is used: returns supplier, plant, line, qty.")
def bom_where_used(part_id: str) -> dict:
    hit = load_fixture(_FIX, part_id)
    if hit is None:
        return {"status": "not_found", "part_id": part_id}
    return hit
```

- [ ] **Step 4: Run — confirm pass**

Run: `pytest tests/test_erp_tool.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```
git add src/mmc_agents/tools/erp.py tests/test_erp_tool.py
git commit -m "feat(tools): erp.bom_where_used backed by fixture"
```

---

## Task 16: `tools/supplier.py` (TDD)

**Files:**
- Create: `tests/test_supplier_tool.py`, `src/mmc_agents/tools/supplier.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_supplier_tool.py
from mmc_agents.tools.supplier import lookup, alternates

def test_lookup_acme():
    s = lookup("SUP-001")
    assert s is not None
    assert s["Name"] == "Acme Brakes"
    assert s["Disruption_Flag"] == "Y"
    assert int(s["Disruption_Days"]) == 21

def test_lookup_unknown():
    assert lookup("SUP-999") == {"status": "not_found", "supplier_id": "SUP-999"}

def test_alternates_returns_other_supplier_when_part_known():
    # For the thin slice, alternates is keyed by part_id; returns ALL other suppliers
    # of parts at the same plant/line as a deterministic placeholder.
    alts = alternates("BRK-CAL-XYZ")
    assert isinstance(alts, list)
    assert all(a["Supplier_ID"] != "SUP-001" for a in alts)
```

- [ ] **Step 2: Run — confirm failure**

Run: `pytest tests/test_supplier_tool.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement**

```python
# src/mmc_agents/tools/supplier.py
from __future__ import annotations
from pathlib import Path
from mmc_agents.tools.fixtures_loader import load_fixture, _read
from agent_framework import tool  # TODO(verify)

_FIX_SUP = Path(__file__).resolve().parents[3] / "enterprise" / "supply-chain" / "fixtures" / "supplier_master.json"
_FIX_BOM = Path(__file__).resolve().parents[3] / "enterprise" / "supply-chain" / "fixtures" / "bom_where_used.json"

@tool(description="Look up a supplier by ID; returns master record incl. disruption flag.")
def lookup(supplier_id: str) -> dict:
    hit = load_fixture(_FIX_SUP, supplier_id)
    if hit is None:
        return {"status": "not_found", "supplier_id": supplier_id}
    return hit

@tool(description="Find alternate suppliers for a given part. Returns list (possibly empty).")
def alternates(part_id: str) -> list[dict]:
    bom = load_fixture(_FIX_BOM, part_id)
    if bom is None:
        return []
    incumbent = bom["Supplier_ID"]
    plant = bom["Plant_ID"]; line = bom["Line_ID"]
    all_bom = _read(str(_FIX_BOM))
    all_sup = _read(str(_FIX_SUP))
    other_sup_ids = {r["Supplier_ID"] for r in all_bom.values()
                     if r["Plant_ID"] == plant and r["Line_ID"] == line and r["Supplier_ID"] != incumbent}
    return [all_sup[sid] for sid in other_sup_ids if sid in all_sup]
```

- [ ] **Step 4: Run — confirm pass**

Run: `pytest tests/test_supplier_tool.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```
git add src/mmc_agents/tools/supplier.py tests/test_supplier_tool.py
git commit -m "feat(tools): supplier.lookup + alternates"
```

---

## Task 17: `registry/base.py`

**Files:**
- Create: `src/mmc_agents/registry/__init__.py` (empty), `src/mmc_agents/registry/base.py`

- [ ] **Step 1: Write**

```python
# src/mmc_agents/registry/base.py
from __future__ import annotations
from typing import Protocol
from pydantic import BaseModel

class AgentSkill(BaseModel):
    id: str
    description: str

class AgentCard(BaseModel):
    name: str                       # unique id, e.g. "plant7-ehs"
    display_name: str
    description: str
    endpoint: str                   # A2A endpoint (e.g. https://.../.well-known/agent-card.json)
    skills: list[AgentSkill]
    tier: str                       # "plant" | "enterprise"
    metadata: dict = {}

class RegistrySource(Protocol):
    def list_agents(self) -> list[AgentCard]: ...
```

- [ ] **Step 2: Commit**

```
git add src/mmc_agents/registry/__init__.py src/mmc_agents/registry/base.py
git commit -m "feat(registry): AgentCard + RegistrySource protocol"
```

---

## Task 18: `registry/local_catalog.py` (TDD)

**Files:**
- Create: `tests/test_local_catalog.py`, `src/mmc_agents/registry/local_catalog.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_local_catalog.py
import json
from pathlib import Path
from mmc_agents.registry.local_catalog import LocalCatalogSource, WatchedLocalCatalogSource

CARD = {
    "name": "x-agent",
    "display_name": "X",
    "description": "demo",
    "endpoint": "https://example/.well-known/agent-card.json",
    "skills": [{"id": "do_x", "description": "do X"}],
    "tier": "plant",
}

def write_catalog(p: Path, cards):
    p.write_text(json.dumps({"agents": cards}))

def test_local_catalog_reads_file(tmp_path: Path):
    cat = tmp_path / "catalog.json"
    write_catalog(cat, [CARD])
    src = LocalCatalogSource(cat)
    agents = src.list_agents()
    assert len(agents) == 1
    assert agents[0].name == "x-agent"

def test_watched_picks_up_new_card(tmp_path: Path):
    cat = tmp_path / "catalog.json"
    write_catalog(cat, [CARD])
    src = WatchedLocalCatalogSource(cat)
    assert len(src.list_agents()) == 1
    second = {**CARD, "name": "y-agent"}
    write_catalog(cat, [CARD, second])
    assert {a.name for a in src.list_agents()} == {"x-agent", "y-agent"}
```

- [ ] **Step 2: Run — confirm failure**

Run: `pytest tests/test_local_catalog.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement**

```python
# src/mmc_agents/registry/local_catalog.py
from __future__ import annotations
import json
from pathlib import Path
from mmc_agents.registry.base import AgentCard

class LocalCatalogSource:
    def __init__(self, catalog_path: Path):
        self.path = Path(catalog_path)
        self._cache: list[AgentCard] | None = None

    def list_agents(self) -> list[AgentCard]:
        if self._cache is None:
            self._cache = self._read()
        return self._cache

    def _read(self) -> list[AgentCard]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [AgentCard.model_validate(a) for a in data["agents"]]

class WatchedLocalCatalogSource(LocalCatalogSource):
    """Re-reads catalog.json on every list_agents() call. Powers hot-add demo."""
    def list_agents(self) -> list[AgentCard]:
        return self._read()
```

- [ ] **Step 4: Run — confirm pass**

Run: `pytest tests/test_local_catalog.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```
git add src/mmc_agents/registry/local_catalog.py tests/test_local_catalog.py
git commit -m "feat(registry): LocalCatalogSource + WatchedLocalCatalogSource"
```

---

## Task 19: `registry/agent365.py` stub

**Files:**
- Create: `src/mmc_agents/registry/agent365.py`

- [ ] **Step 1: Write stub**

```python
# src/mmc_agents/registry/agent365.py
"""End-state registry source: Microsoft Agent 365 (Graph API, preview).

Not implemented in the thin slice (D9). Keep this seam in the code so swapping
to Agent 365 later is purely additive.
"""
from __future__ import annotations
from mmc_agents.registry.base import AgentCard

class Agent365Source:
    def __init__(self, tenant_id: str | None = None):
        self.tenant_id = tenant_id

    def list_agents(self) -> list[AgentCard]:
        # TODO(swap-in): replace with Graph API call to Agent 365 registry once tenant access is available.
        raise NotImplementedError("Agent365Source is a documented future swap-in. Use LocalCatalogSource.")
```

- [ ] **Step 2: Commit**

```
git add src/mmc_agents/registry/agent365.py
git commit -m "feat(registry): Agent365Source stub (future swap-in)"
```

---

## Task 20: `scripts/refresh_catalog.py`

**Files:**
- Create: `scripts/refresh_catalog.py`

- [ ] **Step 1: Write**

```python
"""Aggregate all *.agent.json files under plants/ and enterprise/ into agents/catalog.json."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main() -> None:
    cards = []
    for p in sorted(ROOT.glob("plants/*/agents/*.agent.json")):
        cards.append(json.loads(p.read_text(encoding="utf-8")))
    for p in sorted(ROOT.glob("enterprise/*/agent.json")):
        cards.append(json.loads(p.read_text(encoding="utf-8")))
    out = ROOT / "agents" / "catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"agents": cards}, indent=2), encoding="utf-8")
    print(f"Wrote {out} with {len(cards)} agents.")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```
git add scripts/refresh_catalog.py
git commit -m "feat(scripts): refresh_catalog aggregator"
```

---

## Task 21: `kb_client.py` — Foundry IQ wrapper

**Verify on Microsoft Learn:** the first-party "Connect a Foundry IQ KB to Foundry Agent Service" Python API. Adjust class/method names accordingly.

**Files:**
- Create: `src/mmc_agents/kb_client.py`

- [ ] **Step 1: Write**

```python
"""Wrap the Foundry IQ MCP connector so agents bind to KB sources by name."""
from __future__ import annotations
import os
from dataclasses import dataclass

# TODO(verify-on-Learn): real import path likely azure.ai.projects or azure.ai.foundry
from foundry_iq import FoundryIQClient  # placeholder

@dataclass
class KBBinding:
    kb_id: str
    source_names: list[str]
    project_endpoint: str

def kb_binding_for(profile_kb: dict, source_names: list[str], tier: str) -> KBBinding:
    """Return a binding for an agent given its scoped sources.

    tier='plant'      -> uses FOUNDRY_PLANT_PROJECT_ENDPOINT + FOUNDRY_IQ_KB_PLANT*_ID
    tier='enterprise' -> uses FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT + FOUNDRY_IQ_KB_ENTERPRISE_ID
    """
    if tier == "plant":
        endpoint = os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"]
        kb_id = os.environ[profile_kb["kb_id_env"]]
    elif tier == "enterprise":
        endpoint = os.environ["FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT"]
        kb_id = os.environ["FOUNDRY_IQ_KB_ENTERPRISE_ID"]
    else:
        raise ValueError(tier)
    return KBBinding(kb_id=kb_id, source_names=source_names, project_endpoint=endpoint)

def attach_kb_tool(agent, binding: KBBinding) -> None:
    """Attach the Foundry IQ KB to an agent as a tool, scoped to its source_names."""
    client = FoundryIQClient(project_endpoint=binding.project_endpoint)
    client.connect_kb_to_agent(
        agent=agent,
        kb_id=binding.kb_id,
        source_filter=binding.source_names,
        output_mode="extractive",
        retrieval_reasoning_effort="medium",
    )
```

- [ ] **Step 2: Commit**

```
git add src/mmc_agents/kb_client.py
git commit -m "feat(kb): FoundryIQClient wrapper + per-agent source-scoped binding"
```

---

## Task 22: `agent_factory.py` (TDD)

**Files:**
- Create: `tests/test_agent_factory.py`, `src/mmc_agents/agent_factory.py`

- [ ] **Step 1: Write failing test (card-emission only — agent instantiation is integration)**

```python
# tests/test_agent_factory.py
import json, yaml
from pathlib import Path
from mmc_agents.agent_factory import emit_agent_card

PROFILE = yaml.safe_load("""
plant_id: plant7
display_name: MMC Plant 7
kb:
  kb_id_env: FOUNDRY_IQ_KB_PLANT7_ID
  sources:
    ehs: { paths: [] }
agents:
  - role: ehs
    display_name: Plant 7 EHS / Safety
    kb_sources: [ehs]
    tools: [capa]
    skills:
      - { id: hazard_loto_lookup, description: Hazard & LOTO requirement lookup }
""")

def test_emit_card(tmp_path: Path):
    out = tmp_path / "plant7-ehs.agent.json"
    emit_agent_card(PROFILE, role="ehs", endpoint_base="https://demo.local", out_path=out)
    card = json.loads(out.read_text())
    assert card["name"] == "plant7-ehs"
    assert card["tier"] == "plant"
    assert card["endpoint"].endswith("/plant7-ehs/.well-known/agent-card.json")
    assert card["skills"] == [{"id": "hazard_loto_lookup", "description": "Hazard & LOTO requirement lookup"}]
```

- [ ] **Step 2: Run — confirm failure**

Run: `pytest tests/test_agent_factory.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement card emission + agent build**

```python
# src/mmc_agents/agent_factory.py
"""Builds Foundry agents (prompt-based) and emits A2A cards from profile.yaml."""
from __future__ import annotations
import json, os
from pathlib import Path
from mmc_agents.kb_client import kb_binding_for, attach_kb_tool
# from agent_framework import FoundryAgent, ChatClient   # TODO(verify-on-Learn)

PROMPT_TEMPLATE = """You are {display_name} for MMC ({plant_id}).
Scope: {scope}.
Always ground factual claims in your knowledge base sources: {sources}.
If retrieval returns nothing, reply 'No grounded answer available' rather than speculating.
You may call your registered tools when a question needs structured lookup.
Respond concisely and cite source filenames you used.
"""

def _agent_name(plant_id: str, role: str) -> str:
    return f"{plant_id}-{role}"

def emit_agent_card(profile: dict, role: str, endpoint_base: str, out_path: Path) -> dict:
    agent_def = next(a for a in profile["agents"] if a["role"] == role)
    name = _agent_name(profile["plant_id"], role)
    card = {
        "name": name,
        "display_name": agent_def["display_name"],
        "description": f"{agent_def['display_name']} grounded in {', '.join(agent_def['kb_sources'])} KB sources.",
        "endpoint": f"{endpoint_base.rstrip('/')}/{name}/.well-known/agent-card.json",
        "skills": agent_def["skills"],
        "tier": "plant",
        "metadata": {
            "plant_id": profile["plant_id"],
            "kb_sources": agent_def["kb_sources"],
            "tools": agent_def["tools"],
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(card, indent=2), encoding="utf-8")
    return card

def build_plant_agent(profile: dict, role: str, chat_client, tool_registry: dict):
    """Build a live Foundry agent for the given role from profile + tool registry."""
    agent_def = next(a for a in profile["agents"] if a["role"] == role)
    name = _agent_name(profile["plant_id"], role)
    prompt = PROMPT_TEMPLATE.format(
        display_name=agent_def["display_name"],
        plant_id=profile["plant_id"],
        scope=", ".join(s["description"] for s in agent_def["skills"]),
        sources=", ".join(agent_def["kb_sources"]),
    )
    tools = [tool_registry[t] for t in agent_def["tools"] if t in tool_registry]
    # TODO(verify-on-Learn): real constructor for prompt-based Foundry agent.
    from agent_framework import FoundryAgent  # placeholder
    agent = FoundryAgent(name=name, instructions=prompt, chat_client=chat_client, tools=tools)
    binding = kb_binding_for(profile["kb"], agent_def["kb_sources"], tier="plant")
    attach_kb_tool(agent, binding)
    return agent
```

- [ ] **Step 4: Run — confirm pass**

Run: `pytest tests/test_agent_factory.py -v`
Expected: 1 passed.

- [ ] **Step 5: Commit**

```
git add src/mmc_agents/agent_factory.py tests/test_agent_factory.py
git commit -m "feat(factory): emit_agent_card + build_plant_agent"
```

---

## Task 23: Generate 5 Plant 7 agent cards

- [ ] **Step 1: One-off generation script**

```python
# scripts/generate_cards.py  (commit this too)
from __future__ import annotations
import os, yaml
from pathlib import Path
from mmc_agents.agent_factory import emit_agent_card

ROOT = Path(__file__).resolve().parent.parent
PROFILE = yaml.safe_load((ROOT / "plants" / "plant7" / "profile.yaml").read_text())
endpoint_base = os.environ.get("MMC_AGENT_ENDPOINT_BASE", "http://localhost:8080")

for agent in PROFILE["agents"]:
    role = agent["role"]
    out = ROOT / "plants" / "plant7" / "agents" / f"plant7-{role}.agent.json"
    emit_agent_card(PROFILE, role=role, endpoint_base=endpoint_base, out_path=out)
print("Generated 5 cards.")
```

- [ ] **Step 2: Run**

Run: `python scripts/generate_cards.py`
Expected: 5 files in `plants/plant7/agents/`.

- [ ] **Step 3: Commit cards + script**

```
git add scripts/generate_cards.py plants/plant7/agents/
git commit -m "feat(plant7): generate 5 A2A cards from profile"
```

---

## Task 24: Supply Chain agent card (thin-slice stub)

**Files:**
- Create: `enterprise/supply-chain/agent.json` (hand-authored for the thin slice — Task 24 of Gate B replaces with factory)

- [ ] **Step 1: Author**

```json
{
  "name": "ent-supply-chain",
  "display_name": "Supply Chain",
  "description": "Enterprise supply chain agent. Resolves supplier health, BOM where-used, and alt-source lookups.",
  "endpoint": "http://localhost:8080/ent-supply-chain/.well-known/agent-card.json",
  "skills": [
    {"id": "supplier_health", "description": "Supplier health & disruption impact"},
    {"id": "bom_where_used", "description": "BOM explode & where-used"},
    {"id": "alt_source_lookup", "description": "Alternate-source & inbound-logistics ETA"}
  ],
  "tier": "enterprise",
  "metadata": {
    "kb_sources": ["supply_chain"],
    "tools": ["erp", "supplier"]
  }
}
```

- [ ] **Step 2: Refresh catalog**

Run: `python scripts/refresh_catalog.py`
Expected: `agents/catalog.json` contains 6 agents.

- [ ] **Step 3: Commit**

```
git add enterprise/supply-chain/agent.json
git commit -m "feat(supply-chain): A2A card (thin-slice stub)"
```

---

## Task 25: `orchestrator/model_config.py`

**Files:**
- Create: `src/mmc_agents/orchestrator/__init__.py` (empty), `src/mmc_agents/orchestrator/model_config.py`

- [ ] **Step 1: Write**

```python
# src/mmc_agents/orchestrator/model_config.py
"""D2: configurable, model-agnostic reasoning client w/ fallback."""
from __future__ import annotations
import os
# from agent_framework.openai import AzureOpenAIChatClient   # TODO(verify-on-Learn)

def load_chat_client(prefer: str | None = None):
    provider = (prefer or os.environ.get("MMC_MODEL_PROVIDER", "azure_openai")).lower()
    if provider == "azure_openai":
        from agent_framework.openai import AzureOpenAIChatClient  # placeholder import
        return AzureOpenAIChatClient(
            endpoint=os.environ["MMC_MODEL_ENDPOINT"],
            deployment=os.environ["MMC_MODEL_DEPLOYMENT"],
        )
    raise ValueError(f"Unsupported provider: {provider}")

def load_fallback_client():
    saved = os.environ.get("MMC_MODEL_DEPLOYMENT")
    fallback = os.environ.get("MMC_MODEL_FALLBACK_DEPLOYMENT")
    if not fallback:
        return None
    os.environ["MMC_MODEL_DEPLOYMENT"] = fallback
    try:
        return load_chat_client()
    finally:
        if saved: os.environ["MMC_MODEL_DEPLOYMENT"] = saved
```

- [ ] **Step 2: Commit**

```
git add src/mmc_agents/orchestrator/__init__.py src/mmc_agents/orchestrator/model_config.py
git commit -m "feat(orchestrator): model_config loader + fallback"
```

---

## Task 26: `orchestrator/manager.py`

**Verify on Microsoft Learn:** exact Magentic manager class name + run signature in Agent Framework Python.

**Files:**
- Create: `src/mmc_agents/orchestrator/manager.py`

- [ ] **Step 1: Write**

```python
# src/mmc_agents/orchestrator/manager.py
"""Magentic manager wiring: registry → A2A agent handles → Magentic orchestration."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from mmc_agents.registry.local_catalog import WatchedLocalCatalogSource
from mmc_agents.registry.base import AgentCard, RegistrySource
from mmc_agents.orchestrator.model_config import load_chat_client

# TODO(verify-on-Learn): correct Magentic + A2A imports for Agent Framework Python.
from agent_framework.magentic import MagenticManager  # placeholder
from agent_framework.a2a import A2AAgent             # placeholder

@dataclass
class RunResult:
    answer: str
    hops: list[str]
    backtracks: int
    raw_ledgers: dict

class MmcMagenticManager:
    def __init__(self, registry: RegistrySource | None = None, max_steps: int = 12):
        repo_root = Path(__file__).resolve().parents[3]
        self.registry = registry or WatchedLocalCatalogSource(repo_root / "agents" / "catalog.json")
        self.chat_client = load_chat_client()
        self.max_steps = max_steps

    def _hydrate(self, cards: list[AgentCard]):
        return [A2AAgent.from_card_url(c.endpoint) for c in cards]

    def run(self, problem_statement: str) -> RunResult:
        cards = self.registry.list_agents()
        agents = self._hydrate(cards)
        manager = MagenticManager(chat_client=self.chat_client, agents=agents, max_steps=self.max_steps)
        result = manager.run(problem_statement)
        return RunResult(
            answer=result.final_message,
            hops=[step.agent_name for step in result.history],
            backtracks=sum(1 for s in result.history if s.is_backtrack),
            raw_ledgers={"task": result.task_ledger, "progress": result.progress_ledger},
        )
```

- [ ] **Step 2: Commit**

```
git add src/mmc_agents/orchestrator/manager.py
git commit -m "feat(orchestrator): MmcMagenticManager wired to local registry"
```

---

## Task 27: `scenarios/brake_caliper.py`

**Files:**
- Create: `src/mmc_agents/orchestrator/scenarios/__init__.py` (empty), `src/mmc_agents/orchestrator/scenarios/brake_caliper.py`

- [ ] **Step 1: Write**

```python
# src/mmc_agents/orchestrator/scenarios/brake_caliper.py
"""Reference scenario from DEMO_BUILD_HANDOFF.md §5."""

PROBLEM_STATEMENT = (
    "A tier-1 supplier flagged a 3-week delay on brake calipers (part BRK-CAL-XYZ). "
    "What's the impact on our plants, what mitigations are available, and what's the cost picture?"
)

EXPECTED_BOUNDS = {
    "min_distinct_agents": 4,    # supply-chain, plant7-maintenance, plant7-quality, plus one of (procurement | alt-source loop)
    "min_backtracks": 1,         # spec D6 + handoff §5: "no alt source → backtrack"
    "must_include_agents": {"ent-supply-chain", "plant7-maintenance", "plant7-quality"},
}
```

- [ ] **Step 2: Commit**

```
git add src/mmc_agents/orchestrator/scenarios/
git commit -m "feat(scenarios): brake_caliper problem statement + expected bounds"
```

---

## Task 28: Smoke test — brake-caliper end-to-end

**Files:**
- Create: `tests/test_brake_caliper_smoke.py`

- [ ] **Step 1: Write test (skipped unless live env wired)**

```python
# tests/test_brake_caliper_smoke.py
import os, pytest
from mmc_agents.orchestrator.manager import MmcMagenticManager
from mmc_agents.orchestrator.scenarios.brake_caliper import PROBLEM_STATEMENT, EXPECTED_BOUNDS

LIVE = os.environ.get("MMC_LIVE", "0") == "1"

@pytest.mark.skipif(not LIVE, reason="Requires deployed Foundry + KBs; set MMC_LIVE=1.")
def test_brake_caliper_composes_multi_agent_flow():
    mgr = MmcMagenticManager()
    result = mgr.run(PROBLEM_STATEMENT)
    distinct = set(result.hops)
    assert len(distinct) >= EXPECTED_BOUNDS["min_distinct_agents"], (
        f"Manager only hopped {len(distinct)} agents: {distinct}"
    )
    assert EXPECTED_BOUNDS["must_include_agents"].issubset(distinct), (
        f"Missing required agents: {EXPECTED_BOUNDS['must_include_agents'] - distinct}"
    )
    assert result.backtracks >= EXPECTED_BOUNDS["min_backtracks"], (
        f"No backtrack observed; ledgers: {result.raw_ledgers}"
    )
    assert result.answer, "Empty final answer"
```

- [ ] **Step 2: Run unit suite (fast — does not require live)**

Run: `pytest -v -m "not live"`
Expected: all non-live tests pass; smoke test SKIPPED.

- [ ] **Step 3: Run smoke against live env**

```pwsh
$env:MMC_LIVE = "1"
pytest tests/test_brake_caliper_smoke.py -v -s
```
Expected: passes; you see hops including `ent-supply-chain`, `plant7-maintenance`, `plant7-quality`, plus at least one backtrack.

- [ ] **Step 4: Commit test**

```
git add tests/test_brake_caliper_smoke.py
git commit -m "test(smoke): brake-caliper composition bounds (live-gated)"
```

---

## Task 29: Foundry portal trace verification (manual)

- [ ] **Step 1:** In the Foundry portal, open the `mmc-foundry-plant` project → Threads → find the most recent run from Task 28. Confirm hops are visible and KB citations appear on agent responses.
- [ ] **Step 2:** Take a screenshot for the demo deck (optional). No commit.

---

## Task 30: Gate A checkpoint

**Files:**
- Create: `docs/specs/gate-a-status.md` (one-paragraph what's working / what's deferred to Gate B)

- [ ] **Step 1: Write checkpoint**

```markdown
# Gate A status — <YYYY-MM-DD>

**Working:** Bicep-deployed rg-magentictest (2 Foundry projects, 1 plant KB, 1 enterprise KB shell, 2 Search, storage). 5 Plant 7 agents grounded against Foundry IQ KB sources. 1 Supply Chain enterprise stub agent backed by deterministic fixtures. Magentic manager composes the brake-caliper flow with ≥4 hops including ≥1 backtrack. Trace visible in Foundry portal.

**Deferred to Gate B:** Remaining 4 enterprise agents, full enterprise content generation (CSVs + narrative docs for all 5 nodes), Safety/LOTO scenario, cross-link validators against the full enterprise dataset.

**Known TODOs flagged in code:** `# TODO(verify-on-Learn)` markers in `kb_client.py`, `agent_factory.py`, `model_config.py`, `manager.py`, `seed_foundry_iq.py`, `infra/bicep/modules/foundry-project.bicep`, `foundry-iq-kb.bicep`. Resolve before or during Gate B Task 1.
```

- [ ] **Step 2: Commit + tag**

```
git add docs/specs/gate-a-status.md
git commit -m "docs: Gate A checkpoint"
git tag gate-a
```

---

## Done criteria for Gate A

- `pytest -v -m "not live"` is green.
- `MMC_LIVE=1 pytest tests/test_brake_caliper_smoke.py` is green.
- Foundry portal shows the multi-agent flow with KB-grounded citations.
- All artifacts committed; `gate-a` tag exists.
