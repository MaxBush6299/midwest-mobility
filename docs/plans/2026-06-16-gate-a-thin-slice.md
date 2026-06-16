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

## Task 10: `seed_foundry_iq.py` — upload Plant 7 content into Azure AI Search KB

**Architecture clarification (per SDK addendum D16):** "Foundry IQ KB" = Azure AI Search knowledge base, created via the `azure-search-documents` preview SDK against our existing `srch-mmc-plant` Search service. There is no separate Foundry IQ resource. The seeder:
1. For each KB source in `profile.yaml`, walks the source's file paths and parses them into `{id, content, source_path}` records.
2. Creates one Search **index** per source (e.g. `ks-plant7-ehs-index`).
3. Pushes documents into each index via `SearchClient.upload_documents`.
4. Registers each index as a **knowledge source** on the Search service.
5. Creates the **knowledge base** referencing all sources.

**Files:**
- Create: `scripts/seed_foundry_iq.py`

- [ ] **Step 1: Capture Search endpoints into `.env`**

Run:
```pwsh
$plantEp = "https://srch-mmc-plant.search.windows.net"
$entEp = "https://srch-mmc-enterprise.search.windows.net"
Add-Content .env "SEARCH_PLANT_ENDPOINT=$plantEp"
Add-Content .env "SEARCH_ENTERPRISE_ENDPOINT=$entEp"
```

- [ ] **Step 2: Grant yourself `Search Service Contributor` on both Search services**

```pwsh
$me = (az account show --query user.name -o tsv)
$myOid = (az ad user show --id $me --query id -o tsv)
$sub = (az account show --query id -o tsv)
foreach ($name in @("srch-mmc-plant","srch-mmc-enterprise")) {
  az role assignment create `
    --assignee $myOid `
    --role "Search Service Contributor" `
    --scope "/subscriptions/$sub/resourceGroups/rg-magentictest/providers/Microsoft.Search/searchServices/$name"
}
```

- [ ] **Step 3: Write the seeder**

```python
# scripts/seed_foundry_iq.py
"""Seed Foundry IQ KBs (= Azure AI Search KBs) per profile.yaml.

Per D16: a Foundry IQ KB is an Azure AI Search knowledge base. For each KB
source in the profile, we create a Search index, push parsed docs into it,
register it as a knowledge source, then create the KB referencing all sources.

Run:
  python scripts/seed_foundry_iq.py --plant plant7
  python scripts/seed_foundry_iq.py --enterprise
"""
from __future__ import annotations
import argparse
import hashlib
import os
import sys
from pathlib import Path

import yaml
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    KnowledgeBase,
    KnowledgeSourceReference,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
)

ROOT = Path(__file__).resolve().parent.parent
TEXT_SUFFIXES = {".md", ".txt", ".csv", ".json", ".yaml", ".yml"}


def _doc_id(path: Path) -> str:
    return hashlib.sha1(str(path).encode("utf-8")).hexdigest()


def _index_name(scope: str, source: str) -> str:
    return f"ks-{scope}-{source}".lower().replace("_", "-")


def _ks_name(scope: str, source: str) -> str:
    return f"ks-{scope}-{source}".lower().replace("_", "-")


def _build_index(name: str) -> SearchIndex:
    return SearchIndex(
        name=name,
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SimpleField(name="source_path", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="source_name", type=SearchFieldDataType.String, filterable=True),
        ],
    )


def _walk_docs(paths: list[str]) -> list[dict]:
    docs = []
    for rel in paths:
        base = ROOT / rel
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in TEXT_SUFFIXES:
                # Non-text (PDFs, etc.) get a stub record so they are discoverable;
                # binary extraction is a Gate B concern.
                docs.append({
                    "id": _doc_id(p),
                    "content": f"[binary file: {p.name}]",
                    "source_path": str(p.relative_to(ROOT)).replace("\\", "/"),
                })
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = p.read_text(encoding="latin-1")
            docs.append({
                "id": _doc_id(p),
                "content": text,
                "source_path": str(p.relative_to(ROOT)).replace("\\", "/"),
            })
    return docs


def _seed(search_endpoint: str, scope: str, sources: dict[str, dict], kb_name: str) -> None:
    cred = DefaultAzureCredential()
    idx_client = SearchIndexClient(endpoint=search_endpoint, credential=cred)

    ks_refs: list[KnowledgeSourceReference] = []
    for source_key, src in sources.items():
        idx_name = _index_name(scope, source_key)
        ks_name = _ks_name(scope, source_key)

        print(f"  [{source_key}] creating index '{idx_name}'...")
        idx_client.create_or_update_index(_build_index(idx_name))

        docs = _walk_docs(src["paths"])
        for d in docs:
            d["source_name"] = source_key
        print(f"  [{source_key}] uploading {len(docs)} docs...")
        if docs:
            SearchClient(
                endpoint=search_endpoint, index_name=idx_name, credential=cred
            ).upload_documents(documents=docs)

        # Knowledge source creation is API-version-dependent; the high-level helper
        # is not yet stable in the SDK preview. We treat the Search index itself as
        # the source for KB references (the KB resolves index_name → KS by name
        # when names match in the 2026-04-01 GA path). If your SDK version requires
        # explicit KS objects, see KnowledgeSource model.
        ks_refs.append(KnowledgeSourceReference(name=idx_name))

    print(f"  creating knowledge base '{kb_name}' with {len(ks_refs)} sources...")
    kb = KnowledgeBase(
        name=kb_name,
        description=f"MMC {scope} grounding KB (auto-seeded)",
        knowledge_sources=ks_refs,
    )
    idx_client.create_or_update_knowledge_base(kb)
    print(f"  done. KB '{kb_name}' is ready.")


def seed_plant(plant_id: str) -> None:
    profile = yaml.safe_load((ROOT / "plants" / plant_id / "profile.yaml").read_text(encoding="utf-8"))
    search_ep = os.environ["SEARCH_PLANT_ENDPOINT"]
    kb_name = f"kb-{plant_id}"
    print(f"Seeding plant '{plant_id}' → {search_ep}")
    _seed(search_ep, plant_id, profile["kb"]["sources"], kb_name)
    print(f"Set FOUNDRY_IQ_KB_PLANT7_ID={kb_name} in your .env")


def seed_enterprise() -> None:
    search_ep = os.environ["SEARCH_ENTERPRISE_ENDPOINT"]
    nodes = {
        "supply_chain": {"paths": ["enterprise/supply-chain/data"]},
        # Gate B adds the other 4 nodes.
    }
    nodes = {k: v for k, v in nodes.items() if (ROOT / v["paths"][0]).exists()}
    if not nodes:
        print("No enterprise data found yet (Gate B populates remaining nodes).")
        return
    print(f"Seeding enterprise → {search_ep}")
    _seed(search_ep, "enterprise", nodes, "kb-enterprise")
    print("Set FOUNDRY_IQ_KB_ENTERPRISE_ID=kb-enterprise in your .env")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plant")
    ap.add_argument("--enterprise", action="store_true")
    args = ap.parse_args()
    if not args.plant and not args.enterprise:
        ap.error("specify --plant <id> or --enterprise")
    if args.plant:
        seed_plant(args.plant)
    if args.enterprise:
        seed_enterprise()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run for Plant 7**

```pwsh
.\.venv\Scripts\python.exe scripts/seed_foundry_iq.py --plant plant7
```
Expected: 3 indexes created (`ks-plant7-ehs`, `ks-plant7-maintenance`, `ks-plant7-quality-ops`), ~14 docs uploaded, KB `kb-plant7` created.

- [ ] **Step 5: Add KB id to `.env`**

```pwsh
Add-Content .env "FOUNDRY_IQ_KB_PLANT7_ID=kb-plant7"
```

- [ ] **Step 6: Commit**

```
git add scripts/seed_foundry_iq.py
git commit -m "feat(scripts): seed Azure AI Search KBs (Foundry IQ) from profile`n`nCo-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
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

## Task 21: Foundry project → Search connection (Bicep) ✏️ **REVISED for portal-managed agents**

The Azure AI Search tool consumes a **project connection** by ID. Add one connection per project pointing at the matching Search service, using `AAD` auth so the project's system-assigned MI is used at query time.

- [ ] **Step 1: New module `infra/bicep/modules/search-connection.bicep`**

```bicep
param foundryAccountName string
param projectName string
param connectionName string
param searchName string

resource search 'Microsoft.Search/searchServices@2024-03-01-preview' existing = {
  name: searchName
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' existing = {
  name: '${foundryAccountName}/${projectName}'
}

resource conn 'Microsoft.CognitiveServices/accounts/projects/connections@2025-04-01-preview' = {
  parent: project
  name: connectionName
  properties: {
    category: 'CognitiveSearch'
    target: 'https://${searchName}.search.windows.net/'
    authType: 'AAD'
    isSharedToAll: true
    metadata: {
      ApiType: 'Azure'
      ResourceId: search.id
      Location: search.location
    }
  }
}

output connectionId string = conn.id
output connectionName string = conn.name
```

- [ ] **Step 2: Wire in `main.bicep`** — after the foundry module, add two `search-connection` module deployments (plant project → plant search, enterprise project → enterprise search). Output `plantSearchConnectionName` and `enterpriseSearchConnectionName` (these get added to `.env`).

- [ ] **Step 3: Redeploy**: `az deployment group create -g rg-magentictest -f infra/bicep/main.bicep -p infra/bicep/parameters/dev.bicepparam`

- [ ] **Step 4: Grant project MI `Search Index Data Reader`** on `srch-mmc-plant` (and enterprise search). Get each project's MI principalId from deployment output or `az resource show`, then:

```powershell
az role assignment create --role "Search Index Data Reader" --assignee-object-id <projectMIPrincipalId> --assignee-principal-type ServicePrincipal --scope $(az search service show -g rg-magentictest -n srch-mmc-plant --query id -o tsv)
```

- [ ] **Step 5: Append to `.env`**: `PLANT_SEARCH_CONNECTION_NAME=srch-mmc-plant`, `ENTERPRISE_SEARCH_CONNECTION_NAME=srch-mmc-enterprise`.

- [ ] **Step 6: Commit**: `infra: project→Search connection for AI Search tool`

---

## Task 22: `agent_factory.py` — Foundry Agents Service upsert ✏️ **REVISED**

Idempotent factory that reads `plants/{plant}/profile.yaml` and creates/updates one portal-managed Foundry agent per profile entry. Returns `FoundryAgent` wrappers for Magentic.

**Files:**
- Create: `src/mmc_agents/agent_factory.py`
- Create: `tests/test_agent_factory.py` (smoke test — gated on `MMC_LIVE=1`)

- [ ] **Step 1: TDD smoke test** (`tests/test_agent_factory.py`)

```python
import os, pytest
pytestmark = pytest.mark.skipif(os.getenv("MMC_LIVE") != "1", reason="live Azure test")

def test_upsert_plant7_ehs_agent():
    from mmc_agents.agent_factory import upsert_plant_agents
    from azure.identity import AzureCliCredential
    agents = upsert_plant_agents("plant7", project_endpoint=os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"],
                                  credential=AzureCliCredential())
    names = {a.name for a in agents}
    assert "plant7-ehs" in names
    assert len(agents) == 5
```

- [ ] **Step 2: Implementation** (`src/mmc_agents/agent_factory.py`)

```python
"""Create/update portal-managed Foundry agents from profile.yaml (Task 22)."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Any

import yaml
from agent_framework.foundry import FoundryAgent, FoundryAgentOptions
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType
from azure.ai.projects import AIProjectClient
from azure.core.credentials import TokenCredential

from mmc_agents.tools import erp, supplier

ROOT = Path(__file__).resolve().parent.parent.parent
MODEL = os.environ.get("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4o-mini")

# Map profile tool names to Python callables
LOCAL_TOOLS: dict[str, Any] = {
    "erp.bom_where_used": erp.bom_where_used,
    "supplier.lookup": supplier.lookup,
    "supplier.alternates": supplier.alternates,
}


def _load_profile(plant_id: str) -> dict:
    with open(ROOT / "plants" / plant_id / "profile.yaml") as fh:
        return yaml.safe_load(fh)


def _index_name(plant_id: str, source_key: str) -> str:
    return f"ks-{plant_id}-{source_key}".lower().replace("_", "-")


def _build_search_tool_defs(project: AIProjectClient, connection_name: str,
                              plant_id: str, sources: list[str]) -> list[dict]:
    conn_id = project.connections.get(connection_name).id
    defs: list[dict] = []
    for s in sources:
        tool = AzureAISearchTool(
            index_connection_id=conn_id,
            index_name=_index_name(plant_id, s),
            query_type=AzureAISearchQueryType.SEMANTIC,
            top_k=5,
        )
        defs.extend(tool.definitions)
    return defs


def upsert_plant_agents(plant_id: str, project_endpoint: str,
                          credential: TokenCredential) -> list[FoundryAgent]:
    profile = _load_profile(plant_id)
    project = AIProjectClient(endpoint=project_endpoint, credential=credential)
    conn_name = os.environ["PLANT_SEARCH_CONNECTION_NAME"]

    agents: list[FoundryAgent] = []
    for agent_def in profile["agents"]:
        name = f"{plant_id}-{agent_def['id']}"
        search_defs = _build_search_tool_defs(project, conn_name, plant_id,
                                                agent_def.get("kb_sources", []))
        local_tools = [LOCAL_TOOLS[t] for t in agent_def.get("tools", []) if t in LOCAL_TOOLS]

        agents.append(FoundryAgent(
            project_endpoint=project_endpoint,
            credential=credential,
            name=name,
            description=agent_def.get("description", ""),
            instructions=agent_def["instructions"],
            tools=local_tools,
            default_options=FoundryAgentOptions(
                model=MODEL,
                tools=search_defs,
            ),
        ))
    return agents
```

- [ ] **Step 3: Run** `MMC_LIVE=1 pytest tests/test_agent_factory.py -v` — must pass. Verify agents appear in Foundry portal → Agents.

- [ ] **Step 4: Commit**: `feat(agents): Foundry Agents Service upsert factory`

---

## Task 23: Agent cards point at portal agents ✏️ **REVISED**

Cards are emitted by a one-off script that runs the factory once, then writes one `agent.json` per agent containing the **real Foundry agent id**. This is what `LocalCatalogSource` reads.

- [ ] **Step 1: Script `scripts/generate_cards.py`**

```python
"""Emit AgentCard JSON for each plant agent created in Foundry (Task 23)."""
from __future__ import annotations
import json, os
from pathlib import Path

from azure.identity import AzureCliCredential
from dotenv import load_dotenv

from mmc_agents.agent_factory import upsert_plant_agents

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    plant_id = "plant7"
    endpoint = os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"]
    agents = upsert_plant_agents(plant_id, endpoint, AzureCliCredential())

    out_dir = ROOT / "plants" / plant_id / "cards"
    out_dir.mkdir(parents=True, exist_ok=True)
    for a in agents:
        card = {
            "schema_version": "1",
            "name": a.name,
            "description": a.description or "",
            "endpoint": endpoint,
            "agent_id": a.id,
            "skills": [],
            "metadata": {"plant_id": plant_id, "project": "mmc-plant"},
        }
        (out_dir / f"{a.name}.json").write_text(json.dumps(card, indent=2))
        print(f"wrote {a.name}.json (id={a.id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run** `.\.venv\Scripts\python.exe scripts/generate_cards.py` — 5 files in `plants/plant7/cards/`.

- [ ] **Step 3: Commit**: `feat(cards): emit Plant 7 cards from live Foundry agent IDs`

---

## Task 24: Supply Chain agent card (hand-authored for thin slice)

Same as before — hand-authored `enterprise/supply-chain/agent.json` pointing at a placeholder Foundry agent. Gate B will upgrade it through the factory.

- [ ] **Step 1: Author** `enterprise/supply-chain/agent.json`:

```json
{
  "schema_version": "1",
  "name": "supply-chain",
  "description": "Enterprise supply-chain operations (BOM, supplier risk)",
  "endpoint": "stub://supply-chain",
  "agent_id": "stub-supply-chain",
  "skills": ["erp.bom_where_used", "supplier.lookup", "supplier.alternates"],
  "metadata": {"project": "mmc-enterprise", "stub": true}
}
```

- [ ] **Step 2: Commit**: `feat(cards): supply-chain stub agent card`

---

## Task 25: `orchestrator/model_config.py` — manager model only ✏️ **REVISED**

Agents carry their own model now. We only need a `FoundryChatClient` for the **Magentic manager** (lightweight planner over the same gpt-4o-mini deployment).

**Files:**
- Create: `src/mmc_agents/orchestrator/__init__.py` (empty)
- Create: `src/mmc_agents/orchestrator/model_config.py`

- [ ] **Step 1:** `src/mmc_agents/orchestrator/model_config.py`

```python
"""Manager-side model client (Magentic planner)."""
from __future__ import annotations
import os
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential


def manager_chat_client() -> FoundryChatClient:
    return FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"],
        model=os.environ.get("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4o-mini"),
        credential=AzureCliCredential(),
    )
```

- [ ] **Step 2: Commit**: `feat(orchestrator): manager chat client`

---

## Task 26: `orchestrator/manager.py` — Magentic over Foundry agents ✏️ **REVISED**

- [ ] **Step 1:** `src/mmc_agents/orchestrator/manager.py`

```python
"""Magentic orchestration over portal-managed Foundry agents (Task 26)."""
from __future__ import annotations
import os
from typing import AsyncIterator

from agent_framework import AgentResponseUpdate
from agent_framework.orchestrations import MagenticBuilder
from azure.identity import AzureCliCredential

from mmc_agents.agent_factory import upsert_plant_agents
from mmc_agents.orchestrator.model_config import manager_chat_client


async def run_plant_scenario(plant_id: str, task: str) -> AsyncIterator[dict]:
    cred = AzureCliCredential()
    endpoint = os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"]
    participants = upsert_plant_agents(plant_id, endpoint, cred)

    workflow = (
        MagenticBuilder(
            participants=participants,
            manager_chat_client=manager_chat_client(),
            max_round_count=10,
            max_stall_count=3,
            max_reset_count=2,
        )
        .build()
    )

    async for event in workflow.run(task, stream=True):
        kind = getattr(event, "kind", "event")
        data = getattr(event, "data", None)
        if isinstance(data, AgentResponseUpdate):
            yield {"kind": kind, "agent": data.agent_name, "text": data.text}
        else:
            yield {"kind": kind, "data": repr(data)[:200]}
```

- [ ] **Step 2: Commit**: `feat(orchestrator): Magentic over Foundry agents`

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
