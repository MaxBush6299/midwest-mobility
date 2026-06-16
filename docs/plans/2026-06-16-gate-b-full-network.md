# Gate B — Full Network Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete Gate B: full enterprise content, all 10 agents, reliable brake-caliper backtracking, and Safety/LOTO end-to-end.

**Architecture:** Build directly on Gate A paths and seams: `src/mmc_agents/...`, `scripts/...`, `enterprise/<node>/{data,fixtures,agent.json}`, `AgentCard` from `registry/base.py`, CSVs as source of truth, fixtures derived by `scripts/derive_fixtures.py`, and Magentic as the only coordination code. Enterprise nodes share one Foundry IQ KB with 5 sources per D15.

**Tech Stack:** Python 3.11+, Microsoft Agent Framework SDK, Foundry Agent Service, Foundry IQ, Azure AI Search, Azure Storage, Bicep, pytest, PyYAML, CSV/JSON fixtures, Azure CLI.

**Verify against Microsoft Learn before coding:** Agent Framework Magentic, A2A, `@tool`, Foundry IQ Python SDK/MCP connector, Foundry Agent Service Python SDK, and Bicep resource types for Foundry projects + Foundry IQ KB.

---

## Reference docs

- `docs/specs/2026-06-16-mmc-agent-network-implementation-design.md` — source of truth for §8a, D5, D6, D8, D10, D15, and Gate B.
- `DEMO_BUILD_HANDOFF.md` — especially §4 (5 enterprise agents/tools) and §5 (brake-caliper composition).
- `docs/plans/2026-06-16-gate-a-thin-slice.md` — exact Gate A file paths, fixture pattern, TDD cadence, and commit style.
- `docs/MMC_Plant7_Company_Profile_v1.md` — Plant 7 names: `MMC_P7`, `L1/L2/L3`, `L1-PRS-001`, `LOTO-L1-001`, `HAZ_001`–`HAZ_099`.
- `docs/specs/gate-a-status.md` — actual Gate A implementation status.

---

## File Structure

| Path | Responsibility |
|---|---|
| `docs/specs/gate-b-pre-review.md` | Mandatory Gate A drift review and sign-off checkpoint. |
| `docs/specs/gate-b-status.md` | Final Gate B evidence summary and tag checkpoint. |
| `infra/bicep/modules/foundry-project.bicep` | Verified Foundry project resource/API or documented fallback. |
| `infra/bicep/modules/foundry-iq-kb.bicep` | Verified Foundry IQ KB resource/API or output-only manifest. |
| `src/mmc_agents/kb_client.py` | Verified Foundry IQ / Agent Service connector. |
| `src/mmc_agents/agent_factory.py` | Enterprise profile card generation and parity support. |
| `src/mmc_agents/orchestrator/model_config.py` | Verified Agent Framework chat client imports. |
| `src/mmc_agents/orchestrator/manager.py` | Magentic backtrack tuning and max-step guard handling. |
| `src/mmc_agents/orchestrator/scenarios/loto_cluster.py` | Safety/LOTO scenario. |
| `enterprise/scenario_seed.yaml` | Cross-link facts for Acme, `BRK-CAL-XYZ`, Plant 7 L1, and LOTO. |
| `enterprise/profile.yaml` | Factory input for 5 enterprise agents. |
| `enterprise/supply-chain/{data,kb,fixtures,agent.json}` | Supply Chain content, fixtures, card. |
| `enterprise/procurement/{data,kb,fixtures,agent.json}` | Procurement & Cost content, fixtures, card. |
| `enterprise/engineering-plm/{data,kb,fixtures,agent.json}` | Engineering / PLM content, fixtures, card. |
| `enterprise/enterprise-quality/{data,kb,fixtures,agent.json}` | Enterprise Quality content, fixtures, card. |
| `enterprise/demand-program/{data,kb,fixtures,agent.json}` | Demand / Program content, fixtures, card. |
| `plants/plant7/kb/08_Logs_Data/MMC_P7_Incident_Log.csv` | Add L1 LOTO rows if needed. |
| `plants/plant7/kb/08_Logs_Data/MMC_P7_PM_Schedule.csv` | Add L1 brake/LOTO PM context if needed. |
| `plants/plant7/fixtures/*.json` | CAPA, CMMS, QMS, SCADA, MES, LMS fixtures. |
| `scripts/generate_enterprise_data.py` | Deterministic CSV generator from scenario seed. |
| `scripts/generate_narrative_docs.py` | LLM-capable narrative generator with deterministic fallback. |
| `scripts/validate_naming.py` | Plant 7 naming and standards validator. |
| `scripts/derive_fixtures.py` | All enterprise and Plant 7 fixture derivation. |
| `scripts/seed_foundry_iq.py` | Upload enterprise data + narrative docs to KB sources. |
| `src/mmc_agents/tools/procurement.py` | Contracts, PO impact, should-cost tools. |
| `src/mmc_agents/tools/plm.py` | Part master, ECO, effectivity tools. |
| `src/mmc_agents/tools/warranty.py` | Warranty, field failure, recall tools. |
| `src/mmc_agents/tools/demand.py` | Order signal, program, allocation tools. |
| `src/mmc_agents/tools/capa.py` | Plant 7 CAPA tracker tool. |
| `src/mmc_agents/tools/cmms.py` | Plant 7 CMMS tool. |
| `src/mmc_agents/tools/qms.py` | Plant 7 QMS tool. |
| `src/mmc_agents/tools/scada.py` | Plant 7 telemetry stub. |
| `src/mmc_agents/tools/mes.py` | Plant 7 MES schedule stub. |
| `src/mmc_agents/tools/lms.py` | Plant 7 LMS / competency stub. |
| `tests/test_*.py` | TDD, validators, factory, hardening, smoke tests. |
| `agents/catalog.json` | Generated 10-agent local catalog. |

---

## Task 1: Gate A review checkpoint

**Files:**
- Create: `docs/specs/gate-b-pre-review.md`
- Read: `docs/specs/gate-a-status.md`, `docs/plans/2026-06-16-gate-a-thin-slice.md`, actual repo tree

- [ ] **Step 1: Inspect Gate A status**

```pwsh
Get-Content docs\specs\gate-a-status.md
git --no-pager log --oneline gate-a..HEAD
Get-ChildItem src\mmc_agents,scripts,enterprise,plants\plant7 -Recurse -File
```
Expected: implementation state and any drift are visible.

- [ ] **Step 2: Inspect unresolved Learn markers**

```pwsh
Select-String -Path infra\bicep\*.bicep,infra\bicep\modules\*.bicep,src\mmc_agents\*.py,src\mmc_agents\orchestrator\*.py,scripts\*.py -Pattern "TODO\(verify-on-Learn\)|TODO\(verify\)"
```
Expected: marker list is captured for Task 2.

- [ ] **Step 3: Write pre-review document**

```markdown
# Gate B pre-review — 2026-06-16

## Inputs reviewed
- `docs/specs/gate-a-status.md`
- `docs/plans/2026-06-16-gate-a-thin-slice.md`
- `git log gate-a..HEAD`
- Current file tree under `src/mmc_agents/`, `scripts/`, `enterprise/`, `plants/plant7/`

## Gate A actual state
- Working: record observed working items from status and tests.
- Deferred: record deferred items from Gate A status.
- Drift from Gate A plan: list exact path/API changes, or write `None observed`.

## Gate B plan adjustments
- List task numbers requiring adjustment, or write `No adjustment required`.

## Sign-off checkpoint
Gate B implementation must pause here. The user must explicitly approve this pre-review before Task 2 starts.
```
Expected: document has concrete observed values, not guesses.

- [ ] **Step 4: Commit**

```pwsh
git add docs\specs\gate-b-pre-review.md
git commit -m "docs: Gate B pre-review checkpoint"
```
Expected: commit succeeds.

- [ ] **Step 5: Stop for sign-off**

Do not continue until the user approves `docs/specs/gate-b-pre-review.md`.

---

## Task 2: Resolve Microsoft Learn verification markers

**Files:**
- Modify: `infra/bicep/modules/foundry-project.bicep`, `infra/bicep/modules/foundry-iq-kb.bicep`
- Modify: `src/mmc_agents/kb_client.py`, `src/mmc_agents/agent_factory.py`, `src/mmc_agents/orchestrator/model_config.py`, `src/mmc_agents/orchestrator/manager.py`
- Modify: `scripts/seed_foundry_iq.py`
- Create: `tests/test_learn_verification_cleanup.py`

- [ ] **Step 1: Write failing cleanup test**

```python
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def test_no_verify_markers_remain():
    offenders = []
    for base in [ROOT / "infra" / "bicep", ROOT / "src" / "mmc_agents", ROOT / "scripts"]:
        for path in base.rglob("*"):
            if path.suffix in {".py", ".bicep", ".bicepparam"}:
                text = path.read_text(encoding="utf-8")
                if "TODO(verify-on-Learn)" in text or "TODO(verify)" in text:
                    offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
```
Expected: test fails before markers are resolved.

- [ ] **Step 2: Run failing test**

```pwsh
pytest tests\test_learn_verification_cleanup.py -v
```
Expected: FAIL with offender file list.

- [ ] **Step 3: Verify official Microsoft surfaces**

```text
Verify and record exact package/import/API versions for:
- Agent Framework Python `@tool` decorator
- Agent Framework Python Magentic manager and result shape
- A2A hydration from agent-card URL
- Foundry Agent Service prompt-agent constructor
- Foundry IQ KB connector / MCP tool binding
- Bicep resource type/API for Foundry project
- Bicep resource type/API for Foundry IQ KB or data-plane-only fallback
```
Expected: every verification marker has a documented replacement.

- [ ] **Step 4: Update code and infra**

```pwsh
az bicep build --file infra\bicep\main.bicep
pytest tests\test_learn_verification_cleanup.py tests\test_agent_factory.py -v
```
Expected: Bicep build succeeds and cleanup test passes.

- [ ] **Step 5: Re-run Gate A live smoke**

```pwsh
$env:MMC_LIVE = "1"
pytest tests\test_brake_caliper_smoke.py -v -s
```
Expected: PASS; Gate A flow still works.

- [ ] **Step 6: Commit**

```pwsh
git add infra\bicep src\mmc_agents scripts\seed_foundry_iq.py tests\test_learn_verification_cleanup.py
git commit -m "chore: resolve verified Microsoft SDK and Bicep surfaces"
```
Expected: commit succeeds.

---

## Task 3: Scenario seed and naming validator

**Files:**
- Create: `enterprise/scenario_seed.yaml`
- Create: `scripts/validate_naming.py`
- Create: `tests/test_validate_naming.py`

- [ ] **Step 1: Create scenario seed**

```yaml
version: 1
company: Midwest Mobility Components
brake_caliper:
  supplier_id: SUP-001
  supplier_name: Acme Brakes
  part_id: BRK-CAL-XYZ
  part_name: Brake Caliper Assembly
  plant_id: plant7
  plant_code: MMC_P7
  line_id: L1
  primary_equipment_id: L1-PRS-001
  disruption_days: 21
  no_alt_path_key: BRK-CAL-XYZ:NO_ALT_DIRECT
loto_cluster:
  plant_id: plant7
  plant_code: MMC_P7
  line_id: L1
  equipment_ids: [L1-PRS-001, L1-PRS-002]
  loto_procedure_ids: [LOTO-L1-001, LOTO-L1-002]
  hazard_ids: [HAZ_011, HAZ_014, HAZ_019]
  min_incidents_last_60_days: 3
allowed_standards: [OSHA 29 CFR 1910, ISO 45001, ISO 9001, ANSI/RIA R15.06, NFPA 70E]
```
Expected: seed pins all cross-link facts.

- [ ] **Step 2: Write failing tests**

```python
from scripts.validate_naming import validate_text, validate_part_id, validate_equipment_id

def test_validate_text_accepts_plant7_terms():
    assert validate_text("MMC_P7 L1 L1-PRS-001 OSHA 29 CFR 1910 ISO 45001") == []

def test_validate_text_rejects_wrong_terms():
    assert validate_text("MMC_P8 L4 PRESS-1")

def test_part_and_equipment_ids():
    assert validate_part_id("BRK-CAL-XYZ") == []
    assert validate_equipment_id("L1-PRS-001") == []
```
Expected: ImportError before implementation.

- [ ] **Step 3: Run failing tests**

```pwsh
pytest tests\test_validate_naming.py -v
```
Expected: FAIL.

- [ ] **Step 4: Implement validator**

```python
import re
VALID_LINES = {"L1", "L2", "L3"}
def validate_part_id(value: str) -> list[str]:
    return [] if re.match(r"^[A-Z]{3}-[A-Z0-9]{2,4}-[A-Z0-9]{2,4}$", value) else [value]
def validate_equipment_id(value: str) -> list[str]:
    return [] if re.match(r"^L[123]-(PRS|ROB|CNV)-\d{3}$", value) else [value]
def validate_text(text: str) -> list[str]:
    errors = []
    errors += [p for p in re.findall(r"MMC_P\d+", text) if p != "MMC_P7"]
    errors += [l for l in re.findall(r"\bL\d+\b", text) if l not in VALID_LINES]
    return errors
```
Expected: CLI also validates supplied files/directories and exits 1 on errors.

- [ ] **Step 5: Verify and commit**

```pwsh
pytest tests\test_validate_naming.py -v
git add enterprise\scenario_seed.yaml scripts\validate_naming.py tests\test_validate_naming.py
git commit -m "feat(data): scenario seed and naming validator"
```
Expected: tests pass; commit succeeds.

---

## Task 4: Deterministic enterprise CSV generator

**Files:**
- Create: `scripts/generate_enterprise_data.py`
- Create: `tests/test_generate_enterprise_data.py`

- [ ] **Step 1: Write failing tests**

```python
from pathlib import Path
import csv, yaml
from scripts.generate_enterprise_data import generate_node, NODE_SPECS

def rows(path): return list(csv.DictReader(path.open(encoding="utf-8")))
def test_specs_cover_all_nodes():
    assert set(NODE_SPECS) == {"supply-chain", "procurement", "engineering-plm", "enterprise-quality", "demand-program"}
def test_supply_chain_contains_brake_cross_link(tmp_path):
    seed = yaml.safe_load(Path("enterprise/scenario_seed.yaml").read_text())
    generate_node("supply-chain", tmp_path, seed)
    assert len(rows(tmp_path / "supplier_master.csv")) >= 25
    bom = rows(tmp_path / "bom_where_used.csv")
    assert any(r["Part_ID"] == "BRK-CAL-XYZ" and r["Plant_ID"] == "plant7" and r["Line_ID"] == "L1" for r in bom)
```
Expected: ImportError before implementation.

- [ ] **Step 2: Run failing tests**

```pwsh
pytest tests\test_generate_enterprise_data.py -v
```
Expected: FAIL.

- [ ] **Step 3: Implement generator contracts**

```python
NODE_SPECS = {
  "supply-chain": ["supplier_master.csv", "bom_where_used.csv", "erp_inventory.csv", "tms_freight.csv"],
  "procurement": ["contracts.csv", "po_spend.csv", "should_cost_model.csv"],
  "engineering-plm": ["plm_part_master.csv", "eco_log.csv", "effectivity.csv"],
  "enterprise-quality": ["warranty_claims.csv", "field_failure_feed.csv", "recall_ruleset.csv"],
  "demand-program": ["order_crm_feed.csv", "program_plan.csv", "allocation_model.csv"],
}
```
Expected: each generator writes deterministic rows from `enterprise/scenario_seed.yaml`.

- [ ] **Step 4: Verify and commit**

```pwsh
pytest tests\test_generate_enterprise_data.py -v
git add scripts\generate_enterprise_data.py tests\test_generate_enterprise_data.py
git commit -m "feat(scripts): deterministic enterprise CSV generator"
```
Expected: tests pass; commit succeeds.

---

## Task 5: Narrative doc generator

**Files:**
- Create: `scripts/generate_narrative_docs.py`
- Modify: `scripts/validate_naming.py`
- Modify: `tests/test_validate_naming.py`

- [ ] **Step 1: Add failing narrative test**

```python
from scripts.generate_narrative_docs import render_doc

def test_render_doc_includes_plant7_and_seed_part():
    text = render_doc("supply-chain", "supplier_qualification_policy.md")
    assert "MMC_P7" in text
    assert "BRK-CAL-XYZ" in text
    assert validate_text(text) == []
```
Expected: ImportError before implementation.

- [ ] **Step 2: Implement deterministic fallback**

```python
DOCS = {
  "supply-chain": ["supplier_qualification_policy.md", "logistics_sop.md", "disruption_playbook.md"],
  "procurement": ["procurement_policy.md", "expedite_cost_methodology.md", "supplier_tier_definitions.md"],
  "engineering-plm": ["eco_workflow.md", "part_numbering_standard.md", "cross_plant_change_procedure.md"],
  "enterprise-quality": ["warranty_handling_sop.md", "recall_threshold_policy.md", "cross_plant_defect_trend_methodology.md"],
  "demand-program": ["launch_readiness_checklist.md", "demand_allocation_policy.md", "oem_program_definitions.md"],
}
def render_doc(node, filename):
    return f"# {filename}\n\nApplies to MMC_P7 L1, Acme Brakes SUP-001, and BRK-CAL-XYZ. Use OSHA 29 CFR 1910, ISO 45001, and ISO 9001 names."
```
Expected: optional LLM mode may be added, but output must pass `validate_naming.py`.

- [ ] **Step 3: Verify and commit**

```pwsh
pytest tests\test_validate_naming.py -v
git add scripts\generate_narrative_docs.py scripts\validate_naming.py tests\test_validate_naming.py
git commit -m "feat(scripts): enterprise narrative doc generator"
```
Expected: tests pass; commit succeeds.

---
## Task 6: Supply Chain full enterprise content

**Files:**
- Modify: `enterprise/supply-chain/data/supplier_master.csv`
- Modify: `enterprise/supply-chain/data/bom_where_used.csv`
- Create: `enterprise/supply-chain/data/erp_inventory.csv`, `enterprise/supply-chain/data/tms_freight.csv`
- Create: `enterprise/supply-chain/kb/supplier_qualification_policy.md`, `enterprise/supply-chain/kb/logistics_sop.md`, `enterprise/supply-chain/kb/disruption_playbook.md`
- Modify: `enterprise/supply-chain/fixtures/*.json`

- [ ] **Step 1: CSV schema and 5-row samples**

`supplier_master.csv` — expand to ≥25 rows:
```csv
Supplier_ID,Supplier_Name,Tier,Country,Primary_Commodity,Qualification_Status,Lead_Time_Days,Disruption_Flag,Disruption_Days,Risk_Score,Preferred_Alt_Supplier_ID,Notes
SUP-001,Acme Brakes,1,US,Brake Systems,Critical,14,Y,21,High,,No direct alternate source for BRK-CAL-XYZ; requires manager backtrack
SUP-002,Midwest Stampings,2,US,Stamped Components,Approved,10,N,0,Low,SUP-006,Approved backup for L1 stampings
SUP-003,Globex Robotics,1,DE,Robotics,Approved,28,N,0,Medium,SUP-008,L2 robot-cell components
SUP-004,Initech Fasteners,2,US,Fasteners,Approved,7,N,0,Low,SUP-009,Common M8/M10 packs
SUP-005,Hooli Castings,1,MX,Castings,Approved,21,N,0,Medium,SUP-010,General cast housings
```

`bom_where_used.csv` — expand to ≥40 rows:
```csv
Part_ID,Part_Name,Supplier_ID,Plant_ID,Plant_Code,Line_ID,Equipment_ID,Qty_Per_Assy,Effective_Date,Safety_Critical,Alt_Source_Status
BRK-CAL-XYZ,Brake Caliper Assembly,SUP-001,plant7,MMC_P7,L1,L1-PRS-001,1,2025-01-01,Y,NO_DIRECT_ALT
STM-PNL-A1,Stamped Panel A1,SUP-002,plant7,MMC_P7,L1,L1-PRS-001,2,2025-01-01,N,APPROVED_ALT_AVAILABLE
ROB-ARM-G3,Robot Arm Gen3,SUP-003,plant7,MMC_P7,L2,L2-ROB-001,1,2025-01-01,N,APPROVED_ALT_AVAILABLE
FST-M8-100,M8 Fastener Pack,SUP-004,plant7,MMC_P7,L1,L1-PRS-002,50,2025-01-01,N,APPROVED_ALT_AVAILABLE
CST-HSG-04,Cast Housing 04,SUP-005,plant7,MMC_P7,L3,L3-CNV-001,1,2025-01-01,N,APPROVED_ALT_AVAILABLE
```

`erp_inventory.csv`:
```csv
Part_ID,Plant_ID,Stocking_Location,On_Hand_Qty,Allocated_Qty,Days_Of_Supply,Reorder_Point
BRK-CAL-XYZ,plant7,MMC_P7-CRIB,32,28,4,50
STM-PNL-A1,plant7,MMC_P7-CRIB,210,80,14,100
ROB-ARM-G3,plant7,MMC_P7-CRIB,6,2,30,3
FST-M8-100,plant7,MMC_P7-CRIB,5000,1200,45,2000
CST-HSG-04,plant7,MMC_P7-CRIB,75,25,20,40
```

`tms_freight.csv`:
```csv
Shipment_ID,Supplier_ID,Part_ID,Carrier,Origin,Destination,ETA_Date,Status,Delay_Days
TMS-0001,SUP-001,BRK-CAL-XYZ,NorthStar Logistics,Acme Dock,MMC_P7 Receiving,2026-02-20,Delayed,21
TMS-0002,SUP-002,STM-PNL-A1,Lake Freight,Chicago IL,MMC_P7 Receiving,2026-02-03,On Time,0
TMS-0003,SUP-003,ROB-ARM-G3,EuroLink Air,Hamburg DE,MMC_P7 Receiving,2026-02-12,On Time,0
TMS-0004,SUP-004,FST-M8-100,Midwest LTL,Indianapolis IN,MMC_P7 Receiving,2026-02-02,On Time,0
TMS-0005,SUP-005,CST-HSG-04,Borderline Freight,Monterrey MX,MMC_P7 Receiving,2026-02-08,Watch,2
```

- [ ] **Step 2: Generate data**

```pwsh
python scripts\generate_enterprise_data.py --node supply-chain
```
Expected: all 4 CSVs exist; Acme/BRK-CAL-XYZ/plant7/L1 rows are exact.

- [ ] **Step 3: Generate docs and validate**

```pwsh
python scripts\generate_narrative_docs.py --node supply-chain
python scripts\validate_naming.py enterprise\supply-chain\kb
```
Expected: 3 docs generated and validator exits 0.

- [ ] **Step 4: Derive fixtures and seed KB**

```pwsh
python scripts\derive_fixtures.py --node supply-chain
python scripts\seed_foundry_iq.py --enterprise --source supply-chain
```
Expected: `supplier_master.json`, `bom_where_used.json`, `erp_inventory.json`, `tms_freight.json` are derived and uploaded.

- [ ] **Step 5: Commit**

```pwsh
git add enterprise\supply-chain\data enterprise\supply-chain\kb enterprise\supply-chain\fixtures
git commit -m "feat(supply-chain): full enterprise content and fixtures"
```
Expected: commit succeeds.

---

## Task 7: Procurement & Cost content

**Files:**
- Create: `enterprise/procurement/data/contracts.csv`, `enterprise/procurement/data/po_spend.csv`, `enterprise/procurement/data/should_cost_model.csv`
- Create: `enterprise/procurement/kb/procurement_policy.md`, `enterprise/procurement/kb/expedite_cost_methodology.md`, `enterprise/procurement/kb/supplier_tier_definitions.md`
- Create: `enterprise/procurement/fixtures/*.json`

- [ ] **Step 1: CSV schema and 5-row samples**

`contracts.csv` — expand to ≥30 rows:
```csv
Contract_ID,Supplier_ID,Part_ID,Contract_Type,Incoterms,Expedite_Allowed,Expedite_Cost_Per_Unit,Currency,Payment_Terms,Effective_Date,Expiration_Date
CON-0001,SUP-001,BRK-CAL-XYZ,LTA,FCA,Y,18.50,USD,Net 45,2025-01-01,2026-12-31
CON-0002,SUP-002,STM-PNL-A1,LTA,DAP,N,0.00,USD,Net 60,2025-01-01,2026-12-31
CON-0003,SUP-003,ROB-ARM-G3,LTA,FCA,Y,145.00,USD,Net 45,2025-01-01,2026-12-31
CON-0004,SUP-004,FST-M8-100,Blanket,DAP,N,0.00,USD,Net 60,2025-01-01,2026-12-31
CON-0005,SUP-005,CST-HSG-04,Spot,FCA,Y,35.00,USD,Net 30,2025-07-01,2026-06-30
```

`po_spend.csv`:
```csv
PO_ID,Supplier_ID,Part_ID,Plant_ID,Order_Date,Need_Date,Open_Qty,Unit_Price,Extended_Value,Status
PO-00001,SUP-001,BRK-CAL-XYZ,plant7,2026-01-05,2026-02-04,480,142.00,68160.00,At Risk
PO-00002,SUP-002,STM-PNL-A1,plant7,2026-01-04,2026-02-02,900,18.25,16425.00,Open
PO-00003,SUP-003,ROB-ARM-G3,plant7,2026-01-07,2026-02-18,4,18500.00,74000.00,Open
PO-00004,SUP-004,FST-M8-100,plant7,2026-01-06,2026-02-01,12000,0.18,2160.00,Open
PO-00005,SUP-005,CST-HSG-04,plant7,2026-01-09,2026-02-08,120,86.50,10380.00,Watch
```

`should_cost_model.csv`:
```csv
Part_ID,Material_Cost,Labor_Cost,Overhead_Cost,Freight_Cost,Should_Cost,Current_Unit_Price,Variance_Percent
BRK-CAL-XYZ,82.00,12.00,18.00,6.00,118.00,142.00,20.34
STM-PNL-A1,10.00,2.00,3.00,1.00,16.00,18.25,14.06
ROB-ARM-G3,12100.00,700.00,2600.00,450.00,15850.00,18500.00,16.72
FST-M8-100,0.09,0.02,0.03,0.01,0.15,0.18,20.00
CST-HSG-04,53.00,9.00,14.00,4.00,80.00,86.50,8.13
```

- [ ] **Step 2: Generate, validate, derive, seed**

```pwsh
python scripts\generate_enterprise_data.py --node procurement
python scripts\generate_narrative_docs.py --node procurement
python scripts\validate_naming.py enterprise\procurement\kb
python scripts\derive_fixtures.py --node procurement
python scripts\seed_foundry_iq.py --enterprise --source procurement
```
Expected: 3 CSVs, 3 docs, `contracts.json`, `po.json`, `should_cost_model.json` created and uploaded.

- [ ] **Step 3: Commit**

```pwsh
git add enterprise\procurement\data enterprise\procurement\kb enterprise\procurement\fixtures
git commit -m "feat(procurement): enterprise content and fixtures"
```
Expected: commit succeeds.

---

## Task 8: Engineering / PLM content

**Files:**
- Create: `enterprise/engineering-plm/data/plm_part_master.csv`, `enterprise/engineering-plm/data/eco_log.csv`, `enterprise/engineering-plm/data/effectivity.csv`
- Create: `enterprise/engineering-plm/kb/eco_workflow.md`, `enterprise/engineering-plm/kb/part_numbering_standard.md`, `enterprise/engineering-plm/kb/cross_plant_change_procedure.md`
- Create: `enterprise/engineering-plm/fixtures/*.json`

- [ ] **Step 1: CSV schema and 5-row samples**

`plm_part_master.csv`:
```csv
Part_ID,Part_Name,Revision,Lifecycle_State,Material,Safety_Critical,Program_Code,Owning_Engineer
BRK-CAL-XYZ,Brake Caliper Assembly,C,Released,Ductile Iron,Y,EV-BRK-26,Dana Patel
STM-PNL-A1,Stamped Panel A1,B,Released,HSLA Steel,N,MMC-BODY-25,Riley Chen
ROB-ARM-G3,Robot Arm Gen3,A,Released,Aluminum,N,MMC-AUTO-24,Jordan Lee
FST-M8-100,M8 Fastener Pack,A,Released,Steel,N,MMC-GEN,Sam Rivera
CST-HSG-04,Cast Housing 04,B,Released,Aluminum,N,MMC-CAST-25,Dana Patel
```

`eco_log.csv`:
```csv
ECO_ID,Part_ID,Revision_From,Revision_To,Status,Reason,Opened_Date,Approved_Date,Safety_Review_Required
ECO-2026-014,BRK-CAL-XYZ,B,C,Released,Supplier casting process update,2025-12-15,2026-01-10,Y
ECO-2026-015,STM-PNL-A1,A,B,Released,Die wear compensation,2025-12-18,2026-01-08,N
ECO-2026-016,ROB-ARM-G3,A,B,In Review,Robot cable routing update,2026-01-12,,Y
ECO-2026-017,FST-M8-100,A,A,Closed,No revision change,2026-01-03,2026-01-09,N
ECO-2026-018,CST-HSG-04,A,B,Released,Wall thickness optimization,2025-11-21,2025-12-19,N
```

`effectivity.csv`:
```csv
Effectivity_ID,Part_ID,Revision,Plant_ID,Line_ID,Effective_From,Effective_To,Program_Code
EFF-0001,BRK-CAL-XYZ,C,plant7,L1,2026-01-15,,EV-BRK-26
EFF-0002,STM-PNL-A1,B,plant7,L1,2026-01-12,,MMC-BODY-25
EFF-0003,ROB-ARM-G3,A,plant7,L2,2025-09-01,,MMC-AUTO-24
EFF-0004,FST-M8-100,A,plant7,L1,2025-01-01,,MMC-GEN
EFF-0005,CST-HSG-04,B,plant7,L3,2025-12-20,,MMC-CAST-25
```

- [ ] **Step 2: Generate, validate, derive, seed**

```pwsh
python scripts\generate_enterprise_data.py --node engineering-plm
python scripts\generate_narrative_docs.py --node engineering-plm
python scripts\validate_naming.py enterprise\engineering-plm\kb
python scripts\derive_fixtures.py --node engineering-plm
python scripts\seed_foundry_iq.py --enterprise --source engineering-plm
```
Expected: PLM data/docs/fixtures are generated and uploaded.

- [ ] **Step 3: Commit**

```pwsh
git add enterprise\engineering-plm\data enterprise\engineering-plm\kb enterprise\engineering-plm\fixtures
git commit -m "feat(plm): enterprise content and fixtures"
```
Expected: commit succeeds.

---

## Task 9: Enterprise Quality content

**Files:**
- Create: `enterprise/enterprise-quality/data/warranty_claims.csv`, `enterprise/enterprise-quality/data/field_failure_feed.csv`, `enterprise/enterprise-quality/data/recall_ruleset.csv`
- Create: `enterprise/enterprise-quality/kb/warranty_handling_sop.md`, `enterprise/enterprise-quality/kb/recall_threshold_policy.md`, `enterprise/enterprise-quality/kb/cross_plant_defect_trend_methodology.md`
- Create: `enterprise/enterprise-quality/fixtures/*.json`

- [ ] **Step 1: CSV schema and required warranty rows**

`warranty_claims.csv` — include ≥8 `BRK-CAL-XYZ` rows:
```csv
Claim_ID,Part_ID,Plant_ID,Line_ID,Customer,Failure_Mode,Severity,Claim_Date,Status
WCL-2026-0001,BRK-CAL-XYZ,plant7,L1,Northstar EV,Brake drag,High,2026-01-05,Open
WCL-2026-0002,BRK-CAL-XYZ,plant7,L1,Northstar EV,Caliper seal leak,High,2026-01-08,Open
WCL-2026-0003,BRK-CAL-XYZ,plant7,L1,Great Lakes Fleet,Brake noise,Medium,2026-01-11,Open
WCL-2026-0004,BRK-CAL-XYZ,plant7,L1,Northstar EV,Brake drag,High,2026-01-14,Open
WCL-2026-0005,BRK-CAL-XYZ,plant7,L1,Northstar EV,Caliper binding,High,2026-01-18,Open
```

`field_failure_feed.csv`:
```csv
Feed_ID,Part_ID,Source,Signal_Date,Symptom_Text,Potential_Safety,Linked_Claim_ID
FFF-0001,BRK-CAL-XYZ,OEM Portal,2026-01-05,Brake drag after cold start,Y,WCL-2026-0001
FFF-0002,BRK-CAL-XYZ,Dealer Report,2026-01-08,Fluid at caliper seal,Y,WCL-2026-0002
FFF-0003,BRK-CAL-XYZ,OEM Portal,2026-01-11,Audible brake noise,N,WCL-2026-0003
FFF-0004,BRK-CAL-XYZ,Fleet Telematics,2026-01-14,Right front brake drag,Y,WCL-2026-0004
FFF-0005,BRK-CAL-XYZ,Dealer Report,2026-01-18,Caliper binding during inspection,Y,WCL-2026-0005
```

`recall_ruleset.csv`:
```csv
Rule_ID,Part_Family,Metric,Threshold_Count,Window_Days,Action,Applies_To_Safety_Critical
REC-001,Brake,High severity claims,5,60,Open safety review,Y
REC-002,Brake,Potential safety field failures,3,60,Escalate to recall council,Y
REC-003,General,Repeat cosmetic claims,20,90,Quality trend review,N
REC-004,Robot,Unexpected motion reports,2,30,EHS engineering review,Y
REC-005,Conveyor,Jam-related injuries,3,90,Containment review,Y
```

- [ ] **Step 2: Generate, validate, derive, seed**

```pwsh
python scripts\generate_enterprise_data.py --node enterprise-quality
python scripts\generate_narrative_docs.py --node enterprise-quality
python scripts\validate_naming.py enterprise\enterprise-quality\kb
python scripts\derive_fixtures.py --node enterprise-quality
python scripts\seed_foundry_iq.py --enterprise --source enterprise-quality
```
Expected: warranty rows for `BRK-CAL-XYZ` exist; source uploads.

- [ ] **Step 3: Commit**

```pwsh
git add enterprise\enterprise-quality\data enterprise\enterprise-quality\kb enterprise\enterprise-quality\fixtures
git commit -m "feat(quality): enterprise warranty content and fixtures"
```
Expected: commit succeeds.

---

## Task 10: Demand / Program content

**Files:**
- Create: `enterprise/demand-program/data/order_crm_feed.csv`, `enterprise/demand-program/data/program_plan.csv`, `enterprise/demand-program/data/allocation_model.csv`
- Create: `enterprise/demand-program/kb/launch_readiness_checklist.md`, `enterprise/demand-program/kb/demand_allocation_policy.md`, `enterprise/demand-program/kb/oem_program_definitions.md`
- Create: `enterprise/demand-program/fixtures/*.json`

- [ ] **Step 1: CSV schema and 5-row samples**

`order_crm_feed.csv`:
```csv
Order_ID,Customer,Program_Code,Part_ID,Requested_Week,Order_Qty,Signal_Type,Priority
CRM-ORD-0001,Northstar EV,EV-BRK-26,BRK-CAL-XYZ,2026-W06,250,Pull-ahead,High
CRM-ORD-0002,Northstar EV,EV-BRK-26,BRK-CAL-XYZ,2026-W07,275,Firm,High
CRM-ORD-0003,Great Lakes Fleet,EV-BRK-26,BRK-CAL-XYZ,2026-W08,180,Firm,High
CRM-ORD-0004,Northstar EV,EV-BRK-26,BRK-CAL-XYZ,2026-W09,300,Forecast,Normal
CRM-ORD-0005,AgriMotion,MMC-BODY-25,STM-PNL-A1,2026-W09,900,Firm,Normal
```

`program_plan.csv`:
```csv
Program_Code,Milestone,Owner,Due_Date,Status,Risk
EV-BRK-26,Brake system launch readiness,Program Mgmt,2026-03-01,At Risk,Supplier disruption affects L1 brake caliper build
EV-BRK-26,Customer PPAP confirmation,Quality,2026-02-20,At Risk,Warranty claims under review
MMC-BODY-25,Panel refresh launch,Engineering,2026-04-15,Green,No material risk
MMC-AUTO-24,Robot cell sustaining,Ops,2026-03-30,Green,No material risk
MMC-GEN,General service parts,Supply Chain,2026-02-28,Green,No material risk
```

`allocation_model.csv`:
```csv
Allocation_ID,Program_Code,Part_ID,Plant_ID,Line_ID,Allocated_Qty,Capacity_Status
ALLOC-0001,EV-BRK-26,BRK-CAL-XYZ,plant7,L1,250,Constrained
ALLOC-0002,EV-BRK-26,BRK-CAL-XYZ,plant7,L1,275,Constrained
ALLOC-0003,EV-BRK-26,BRK-CAL-XYZ,plant7,L1,180,Constrained
ALLOC-0004,MMC-BODY-25,STM-PNL-A1,plant7,L1,900,Available
ALLOC-0005,MMC-AUTO-24,ROB-ARM-G3,plant7,L2,4,Available
```

- [ ] **Step 2: Generate, validate, derive, seed**

```pwsh
python scripts\generate_enterprise_data.py --node demand-program
python scripts\generate_narrative_docs.py --node demand-program
python scripts\validate_naming.py enterprise\demand-program\kb
python scripts\derive_fixtures.py --node demand-program
python scripts\seed_foundry_iq.py --enterprise --source demand-program
```
Expected: demand/program data/docs/fixtures are generated and uploaded.

- [ ] **Step 3: Commit**

```pwsh
git add enterprise\demand-program\data enterprise\demand-program\kb enterprise\demand-program\fixtures
git commit -m "feat(demand): enterprise demand-program content and fixtures"
```
Expected: commit succeeds.

---
## Task 11: Cross-link integrity test

**Files:**
- Create: `tests/test_cross_link_integrity.py`
- Modify: `plants/plant7/kb/08_Logs_Data/MMC_P7_PM_Schedule.csv` if needed
- Modify: `plants/plant7/kb/08_Logs_Data/MMC_P7_Incident_Log.csv` if needed

- [ ] **Step 1: Write failing pytest**

```python
from pathlib import Path
import csv
ROOT = Path(__file__).resolve().parents[1]
def load_csv(path): return list(csv.DictReader(path.open(encoding="utf-8-sig")))
def test_brake_caliper_resolves_enterprise_to_plant7_records():
    suppliers = load_csv(ROOT / "enterprise" / "supply-chain" / "data" / "supplier_master.csv")
    bom = load_csv(ROOT / "enterprise" / "supply-chain" / "data" / "bom_where_used.csv")
    pm = load_csv(ROOT / "plants" / "plant7" / "kb" / "08_Logs_Data" / "MMC_P7_PM_Schedule.csv")
    incidents = load_csv(ROOT / "plants" / "plant7" / "kb" / "08_Logs_Data" / "MMC_P7_Incident_Log.csv")
    acme = next(r for r in suppliers if r["Supplier_ID"] == "SUP-001")
    brake = next(r for r in bom if r["Part_ID"] == "BRK-CAL-XYZ")
    assert acme["Supplier_Name"] == "Acme Brakes"
    assert brake["Plant_ID"] == "plant7" and brake["Line_ID"] == "L1"
    assert any(r.get("Asset_ID") == brake["Equipment_ID"] or r.get("Location") == "L1" for r in pm)
    assert any(r.get("Location") == "L1" or r.get("Area") == "L1" for r in incidents)
def test_loto_cluster_has_three_l1_near_misses():
    incidents = load_csv(ROOT / "plants" / "plant7" / "kb" / "08_Logs_Data" / "MMC_P7_Incident_Log.csv")
    hits = [r for r in incidents if (r.get("Location") == "L1" or r.get("Area") == "L1") and "LOTO" in (r.get("Description", "") + r.get("Root_Cause", "")).upper()]
    assert len(hits) >= 3
```
Expected: fails if Plant 7 lacks cross-link rows.

- [ ] **Step 2: Run test**

```pwsh
pytest tests\test_cross_link_integrity.py -v
```
Expected: PASS or targeted failure explaining missing rows.

- [ ] **Step 3: Add PM row only if needed**

```csv
PM-081,L1-PRS-001,L1 Brake Caliper Press Fixture,L1,Mechanical Inspection,Weekly,2026-01-24,2026-01-24,Completed,Alex Morgan,2.0,Y,Brake caliper fixture alignment checked for BRK-CAL-XYZ,WO-7721,Added for Gate B brake-caliper cross-link
```
Expected: row uses existing PM header exactly.

- [ ] **Step 4: Add incident row only if needed**

```csv
INC-061,2026-01-20,09:12,A,L1,Stamping/Forming,Near Miss,Medium,Operator reported unexpected fixture movement during BRK-CAL-XYZ brake caliper setup,Incomplete energy isolation during setup,LOTO verification gap,None,None,First Aid,0,0,Line Lead,EHS Manager,CAPA-061,Open,
```
Expected: row uses existing Incident_Log header exactly.

- [ ] **Step 5: Verify and commit**

```pwsh
pytest tests\test_cross_link_integrity.py -v
git add tests\test_cross_link_integrity.py plants\plant7\kb\08_Logs_Data\MMC_P7_PM_Schedule.csv plants\plant7\kb\08_Logs_Data\MMC_P7_Incident_Log.csv
git commit -m "test(data): brake-caliper and LOTO cross-link integrity"
```
Expected: 2 passed; commit succeeds.

---

## Task 12: Procurement tools (TDD)

**Files:**
- Create: `tests/test_procurement_tool.py`
- Create: `src/mmc_agents/tools/procurement.py`

- [ ] **Step 1: Write failing tests**

```python
from mmc_agents.tools.procurement import contract_terms, po_impact, should_cost

def test_contract_terms_for_acme_brake_part():
    result = contract_terms("SUP-001", "BRK-CAL-XYZ")
    assert result["Contract_ID"] == "CON-0001"
    assert result["Expedite_Allowed"] == "Y"
def test_po_impact_returns_at_risk_pos_for_part():
    rows = po_impact("BRK-CAL-XYZ")
    assert rows and any(r["Status"] == "At Risk" for r in rows)
def test_should_cost_known_part():
    result = should_cost("BRK-CAL-XYZ")
    assert float(result["Current_Unit_Price"]) >= float(result["Should_Cost"])
def test_unknown_contract_returns_not_found():
    assert contract_terms("SUP-999", "NOPE") == {"status": "not_found", "supplier_id": "SUP-999", "part_id": "NOPE"}
```
Expected: ImportError before implementation.

- [ ] **Step 2: Run failing tests**

```pwsh
pytest tests\test_procurement_tool.py -v
```
Expected: FAIL.

- [ ] **Step 3: Implement tools**

```python
from pathlib import Path
from mmc_agents.tools.fixtures_loader import _read, load_fixture
from mmc_agents.tools.tool_decorator import tool
ROOT = Path(__file__).resolve().parents[3]
_FIX = ROOT / "enterprise" / "procurement" / "fixtures"
@tool(description="Look up contract terms for supplier and part.")
def contract_terms(supplier_id: str, part_id: str) -> dict:
    for row in _read(str(_FIX / "contracts.json")).values():
        if row["Supplier_ID"] == supplier_id and row["Part_ID"] == part_id: return row
    return {"status": "not_found", "supplier_id": supplier_id, "part_id": part_id}
@tool(description="Return open purchase-order impact for a part.")
def po_impact(part_id: str) -> list[dict]:
    return [r for r in _read(str(_FIX / "po.json")).values() if r["Part_ID"] == part_id]
@tool(description="Return should-cost model for a part.")
def should_cost(part_id: str) -> dict:
    return load_fixture(_FIX / "should_cost_model.json", part_id) or {"status": "not_found", "part_id": part_id}
```
Expected: uses fixtures only; no network calls.

- [ ] **Step 4: Verify and commit**

```pwsh
pytest tests\test_procurement_tool.py -v
git add src\mmc_agents\tools\procurement.py tests\test_procurement_tool.py
git commit -m "feat(tools): procurement fixture-backed tools"
```
Expected: tests pass; commit succeeds.

---

## Task 13: PLM tools (TDD)

**Files:**
- Create: `tests/test_plm_tool.py`
- Create: `src/mmc_agents/tools/plm.py`

- [ ] **Step 1: Write failing tests**

```python
from mmc_agents.tools.plm import part_master, eco_status, effectivity

def test_part_master_brake_caliper():
    assert part_master("BRK-CAL-XYZ")["Revision"] == "C"
def test_eco_status_for_part():
    assert eco_status("BRK-CAL-XYZ")[0]["ECO_ID"] == "ECO-2026-014"
def test_effectivity_for_part_and_plant():
    assert effectivity("BRK-CAL-XYZ", "plant7")[0]["Line_ID"] == "L1"
def test_unknown_part_master():
    assert part_master("NOPE") == {"status": "not_found", "part_id": "NOPE"}
```
Expected: ImportError.

- [ ] **Step 2: Implement PLM tools**

```python
from pathlib import Path
from mmc_agents.tools.fixtures_loader import _read, load_fixture
from mmc_agents.tools.tool_decorator import tool
ROOT = Path(__file__).resolve().parents[3]
_FIX = ROOT / "enterprise" / "engineering-plm" / "fixtures"
@tool(description="Look up PLM part master.")
def part_master(part_id: str) -> dict:
    return load_fixture(_FIX / "plm.json", part_id) or {"status": "not_found", "part_id": part_id}
@tool(description="Return ECO rows for part.")
def eco_status(part_id: str) -> list[dict]:
    return [r for r in _read(str(_FIX / "eco.json")).values() if r["Part_ID"] == part_id]
@tool(description="Return effectivity by part and optional plant.")
def effectivity(part_id: str, plant_id: str | None = None) -> list[dict]:
    return [r for r in _read(str(_FIX / "effectivity.json")).values() if r["Part_ID"] == part_id and (plant_id is None or r["Plant_ID"] == plant_id)]
```
Expected: functions return deterministic records.

- [ ] **Step 3: Verify and commit**

```pwsh
pytest tests\test_plm_tool.py -v
git add src\mmc_agents\tools\plm.py tests\test_plm_tool.py
git commit -m "feat(tools): PLM fixture-backed tools"
```
Expected: tests pass; commit succeeds.

---

## Task 14: Warranty and recall tools (TDD)

**Files:**
- Create: `tests/test_warranty_tool.py`
- Create: `src/mmc_agents/tools/warranty.py`

- [ ] **Step 1: Write failing tests**

```python
from mmc_agents.tools.warranty import warranty_claims, field_failures, recall_thresholds

def test_warranty_claims_for_brake_caliper():
    assert len(warranty_claims("BRK-CAL-XYZ")) >= 5
def test_field_failures_include_potential_safety():
    assert any(r["Potential_Safety"] == "Y" for r in field_failures("BRK-CAL-XYZ"))
def test_recall_thresholds_for_brake_family():
    assert any(r["Action"] == "Open safety review" for r in recall_thresholds("Brake"))
```
Expected: ImportError.

- [ ] **Step 2: Implement warranty tools**

```python
from pathlib import Path
from mmc_agents.tools.fixtures_loader import _read
from mmc_agents.tools.tool_decorator import tool
ROOT = Path(__file__).resolve().parents[3]
_FIX = ROOT / "enterprise" / "enterprise-quality" / "fixtures"
@tool(description="Return warranty claims for part.")
def warranty_claims(part_id: str) -> list[dict]:
    return [r for r in _read(str(_FIX / "warranty.json")).values() if r["Part_ID"] == part_id]
@tool(description="Return field failure rows for part.")
def field_failures(part_id: str) -> list[dict]:
    return [r for r in _read(str(_FIX / "field_failure.json")).values() if r["Part_ID"] == part_id]
@tool(description="Return recall thresholds by family.")
def recall_thresholds(part_family: str) -> list[dict]:
    return [r for r in _read(str(_FIX / "recall.json")).values() if r["Part_Family"].lower() == part_family.lower()]
```
Expected: functions return deterministic rows.

- [ ] **Step 3: Verify and commit**

```pwsh
pytest tests\test_warranty_tool.py -v
git add src\mmc_agents\tools\warranty.py tests\test_warranty_tool.py
git commit -m "feat(tools): warranty and recall fixture-backed tools"
```
Expected: tests pass; commit succeeds.

---

## Task 15: Demand and allocation tools (TDD)

**Files:**
- Create: `tests/test_demand_tool.py`
- Create: `src/mmc_agents/tools/demand.py`

- [ ] **Step 1: Write failing tests**

```python
from mmc_agents.tools.demand import order_signal, program_status, allocation

def test_order_signal_for_brake_caliper():
    assert any(r["Priority"] == "High" for r in order_signal("BRK-CAL-XYZ"))
def test_program_status_at_risk():
    assert any(r["Status"] == "At Risk" for r in program_status("EV-BRK-26"))
def test_allocation_constrained_on_plant7_l1():
    rows = allocation("BRK-CAL-XYZ", "plant7")
    assert rows and all(r["Line_ID"] == "L1" for r in rows)
```
Expected: ImportError.

- [ ] **Step 2: Implement demand tools**

```python
from pathlib import Path
from mmc_agents.tools.fixtures_loader import _read
from mmc_agents.tools.tool_decorator import tool
ROOT = Path(__file__).resolve().parents[3]
_FIX = ROOT / "enterprise" / "demand-program" / "fixtures"
@tool(description="Return OEM order signals for part.")
def order_signal(part_id: str) -> list[dict]:
    return [r for r in _read(str(_FIX / "demand.json")).values() if r["Part_ID"] == part_id]
@tool(description="Return program plan status.")
def program_status(program_code: str) -> list[dict]:
    return [r for r in _read(str(_FIX / "program_plan.json")).values() if r["Program_Code"] == program_code]
@tool(description="Return allocation by part and optional plant.")
def allocation(part_id: str, plant_id: str | None = None) -> list[dict]:
    return [r for r in _read(str(_FIX / "allocation.json")).values() if r["Part_ID"] == part_id and (plant_id is None or r["Plant_ID"] == plant_id)]
```
Expected: deterministic fixture-backed behavior.

- [ ] **Step 3: Verify and commit**

```pwsh
pytest tests\test_demand_tool.py -v
git add src\mmc_agents\tools\demand.py tests\test_demand_tool.py
git commit -m "feat(tools): demand and allocation fixture-backed tools"
```
Expected: tests pass; commit succeeds.

---

## Task 16: Plant 7 fixture derivation

**Files:**
- Modify: `scripts/derive_fixtures.py`
- Create: `plants/plant7/fixtures/capa.json`, `plants/plant7/fixtures/cmms.json`, `plants/plant7/fixtures/qms.json`, `plants/plant7/fixtures/scada.json`, `plants/plant7/fixtures/mes.json`, `plants/plant7/fixtures/lms.json`

- [ ] **Step 1: Extend derivation mappings**

```python
ENTERPRISE_MAPPINGS = {
  "supply-chain": [("supplier_master.csv", "supplier_master.json", "Supplier_ID"), ("bom_where_used.csv", "bom_where_used.json", "Part_ID")],
  "procurement": [("contracts.csv", "contracts.json", "Contract_ID"), ("po_spend.csv", "po.json", "PO_ID")],
}
PLANT7_FIXTURES = ["capa.json", "cmms.json", "qms.json", "scada.json", "mes.json", "lms.json"]
```
Expected: actual implementation includes all mappings from the File Structure table.

- [ ] **Step 2: Generate fixtures**

```pwsh
python scripts\derive_fixtures.py --plant plant7
python scripts\derive_fixtures.py --node all
python scripts\derive_fixtures.py --node all
git --no-pager diff --stat enterprise plants\plant7\fixtures
```
Expected: no diff after second derivation.

- [ ] **Step 3: Commit**

```pwsh
git add scripts\derive_fixtures.py plants\plant7\fixtures enterprise\supply-chain\fixtures enterprise\procurement\fixtures enterprise\engineering-plm\fixtures enterprise\enterprise-quality\fixtures enterprise\demand-program\fixtures
git commit -m "feat(fixtures): derive full enterprise and Plant 7 tool fixtures"
```
Expected: commit succeeds.

---

## Task 17: Plant 7 CAPA tool (TDD)

**Files:**
- Create: `tests/test_plant_tools.py`
- Create: `src/mmc_agents/tools/capa.py`

- [ ] **Step 1: Write failing tests**

```python
from mmc_agents.tools.capa import capa_status, capa_by_incident

def test_capa_status_known_loto_capa():
    assert capa_status("CAPA-061")["CAPA_ID"] == "CAPA-061"
def test_capa_by_incident_known_incident():
    assert capa_by_incident("INC-061")["Incident_ID"] == "INC-061"
```
Expected: ImportError.

- [ ] **Step 2: Implement CAPA tool**

```python
from pathlib import Path
from mmc_agents.tools.fixtures_loader import _read, load_fixture
from mmc_agents.tools.tool_decorator import tool
ROOT = Path(__file__).resolve().parents[3]
_FIX = ROOT / "plants" / "plant7" / "fixtures" / "capa.json"
@tool(description="Look up Plant 7 CAPA by CAPA ID.")
def capa_status(capa_id: str) -> dict:
    return load_fixture(_FIX, capa_id) or {"status": "not_found", "capa_id": capa_id}
@tool(description="Look up CAPA by incident ID.")
def capa_by_incident(incident_id: str) -> dict:
    for row in _read(str(_FIX)).values():
        if row.get("Incident_ID") == incident_id: return row
    return {"status": "not_found", "incident_id": incident_id}
```
Expected: uses Plant 7 fixture only.

- [ ] **Step 3: Verify and commit**

```pwsh
pytest tests\test_plant_tools.py -v
git add src\mmc_agents\tools\capa.py tests\test_plant_tools.py
git commit -m "feat(tools): Plant 7 CAPA fixture-backed tool"
```
Expected: tests pass; commit succeeds.

---

## Task 18: Plant 7 CMMS and QMS tools (TDD)

**Files:**
- Modify: `tests/test_plant_tools.py`
- Create: `src/mmc_agents/tools/cmms.py`, `src/mmc_agents/tools/qms.py`

- [ ] **Step 1: Add failing tests**

```python
from mmc_agents.tools.cmms import pm_status, asset_history
from mmc_agents.tools.qms import ncr_status, quality_signals_for_part

def test_pm_status_for_l1_press():
    assert any(r["LOTO_Required"] == "Y" for r in pm_status("L1-PRS-001"))
def test_asset_history_unknown_returns_empty():
    assert asset_history("NO-ASSET") == []
def test_quality_signals_for_brake_caliper():
    assert any(r["Line_ID"] == "L1" for r in quality_signals_for_part("BRK-CAL-XYZ"))
def test_ncr_status_known_record():
    assert ncr_status("NCR-BRK-001")["Part_ID"] == "BRK-CAL-XYZ"
```
Expected: ImportError.

- [ ] **Step 2: Implement CMMS and QMS**

```python
# cmms.py
@tool(description="Return PM status rows for a Plant 7 asset.")
def pm_status(asset_id: str) -> list[dict]:
    return [r for r in _read(str(_FIX)).values() if r.get("Asset_ID") == asset_id]
def asset_history(asset_id: str) -> list[dict]:
    return pm_status(asset_id)
# qms.py
@tool(description="Look up QMS/NCR status by NCR ID.")
def ncr_status(ncr_id: str) -> dict:
    return load_fixture(_FIX, ncr_id) or {"status": "not_found", "ncr_id": ncr_id}
def quality_signals_for_part(part_id: str) -> list[dict]:
    return [r for r in _read(str(_FIX)).values() if r.get("Part_ID") == part_id]
```
Expected: actual files include imports/root/fixture paths.

- [ ] **Step 3: Verify and commit**

```pwsh
pytest tests\test_plant_tools.py -v
git add src\mmc_agents\tools\cmms.py src\mmc_agents\tools\qms.py tests\test_plant_tools.py
git commit -m "feat(tools): Plant 7 CMMS and QMS fixture-backed tools"
```
Expected: tests pass; commit succeeds.

---

## Task 19: Plant 7 SCADA, MES, and LMS stub tools (TDD)

**Files:**
- Modify: `tests/test_plant_tools.py`
- Create: `src/mmc_agents/tools/scada.py`, `src/mmc_agents/tools/mes.py`, `src/mmc_agents/tools/lms.py`

- [ ] **Step 1: Add failing tests**

```python
from mmc_agents.tools.scada import telemetry_snapshot
from mmc_agents.tools.mes import line_schedule
from mmc_agents.tools.lms import qualified_employees, training_status

def test_scada_snapshot_for_l1_press():
    assert telemetry_snapshot("L1-PRS-001")["Asset_ID"] == "L1-PRS-001"
def test_mes_line_schedule_l1():
    assert all(r["Line_ID"] == "L1" for r in line_schedule("L1"))
def test_lms_qualified_for_loto_l1():
    assert qualified_employees("LOTO-L1")
def test_training_status_known_employee():
    assert training_status("EMP-001")["Employee_ID"] == "EMP-001"
```
Expected: ImportError.

- [ ] **Step 2: Implement stubs**

```python
# scada.py: telemetry_snapshot(asset_id) -> load_fixture(scada.json, asset_id) or not_found
# mes.py: line_schedule(line_id) -> rows from mes.json matching Line_ID
# lms.py: qualified_employees(course_query) -> completed rows; training_status(employee_id) -> fixture hit
```
Expected: each module imports the verified `tool` decorator and `fixtures_loader`; no network calls.

- [ ] **Step 3: Verify and commit**

```pwsh
pytest tests\test_plant_tools.py -v
git add src\mmc_agents\tools\scada.py src\mmc_agents\tools\mes.py src\mmc_agents\tools\lms.py tests\test_plant_tools.py
git commit -m "feat(tools): Plant 7 SCADA MES LMS fixture stubs"
```
Expected: tests pass; commit succeeds.

---
## Task 20: Procurement agent card

**Files:**
- Create: `enterprise/procurement/agent.json`

- [ ] **Step 1: Author card**

```json
{
  "name": "ent-procurement",
  "display_name": "Procurement & Cost",
  "description": "Enterprise procurement and cost agent for should-cost, PO impact, contract terms, expedite options, and spend rollups.",
  "endpoint": "http://localhost:8080/ent-procurement/.well-known/agent-card.json",
  "skills": [
    {"id": "should_cost_analysis", "description": "Should-cost and PO-impact analysis"},
    {"id": "contract_terms", "description": "Contract terms and expedite-cost lookup"},
    {"id": "spend_rollup", "description": "Spend and supplier-tier rollup"}
  ],
  "tier": "enterprise",
  "metadata": {"kb_sources": ["procurement"], "tools": ["procurement"]}
}
```
Expected: schema matches `AgentCard`.

- [ ] **Step 2: Validate and commit**

```pwsh
python -c "import json; from pathlib import Path; from mmc_agents.registry.base import AgentCard; AgentCard.model_validate(json.loads(Path('enterprise/procurement/agent.json').read_text())); print('ok')"
git add enterprise\procurement\agent.json
git commit -m "feat(procurement): A2A agent card"
```
Expected: `ok`; commit succeeds.

---

## Task 21: Engineering / PLM agent card

**Files:**
- Create: `enterprise/engineering-plm/agent.json`

- [ ] **Step 1: Author card**

```json
{
  "name": "ent-engineering-plm",
  "display_name": "Engineering / PLM",
  "description": "Enterprise engineering and PLM agent for ECO/ECN status, part revisions, effectivity, and where-installed impact.",
  "endpoint": "http://localhost:8080/ent-engineering-plm/.well-known/agent-card.json",
  "skills": [
    {"id": "eco_status", "description": "ECO / ECN status and impact"},
    {"id": "part_revision_lookup", "description": "Part revision and effectivity lookup"},
    {"id": "where_installed", "description": "Cross-plant where-installed lookup"}
  ],
  "tier": "enterprise",
  "metadata": {"kb_sources": ["engineering_plm"], "tools": ["plm"]}
}
```
Expected: schema matches `AgentCard`.

- [ ] **Step 2: Validate and commit**

```pwsh
python -c "import json; from pathlib import Path; from mmc_agents.registry.base import AgentCard; AgentCard.model_validate(json.loads(Path('enterprise/engineering-plm/agent.json').read_text())); print('ok')"
git add enterprise\engineering-plm\agent.json
git commit -m "feat(plm): A2A agent card"
```
Expected: `ok`; commit succeeds.

---

## Task 22: Enterprise Quality agent card

**Files:**
- Create: `enterprise/enterprise-quality/agent.json`

- [ ] **Step 1: Author card**

```json
{
  "name": "ent-quality",
  "display_name": "Enterprise Quality",
  "description": "Enterprise quality agent for warranty clustering, cross-plant defect trends, recall thresholds, and safety escalation.",
  "endpoint": "http://localhost:8080/ent-quality/.well-known/agent-card.json",
  "skills": [
    {"id": "warranty_clustering", "description": "Warranty-claim clustering"},
    {"id": "cross_plant_defect_trends", "description": "Cross-plant defect trends"},
    {"id": "recall_threshold", "description": "Recall-threshold and safety call"}
  ],
  "tier": "enterprise",
  "metadata": {"kb_sources": ["enterprise_quality"], "tools": ["warranty"]}
}
```
Expected: schema matches `AgentCard`.

- [ ] **Step 2: Validate and commit**

```pwsh
python -c "import json; from pathlib import Path; from mmc_agents.registry.base import AgentCard; AgentCard.model_validate(json.loads(Path('enterprise/enterprise-quality/agent.json').read_text())); print('ok')"
git add enterprise\enterprise-quality\agent.json
git commit -m "feat(quality): enterprise A2A agent card"
```
Expected: `ok`; commit succeeds.

---

## Task 23: Demand / Program agent card

**Files:**
- Create: `enterprise/demand-program/agent.json`

- [ ] **Step 1: Author card**

```json
{
  "name": "ent-demand-program",
  "display_name": "Demand / Program",
  "description": "Enterprise demand and program agent for OEM order signals, launch readiness, and plant allocation decisions.",
  "endpoint": "http://localhost:8080/ent-demand-program/.well-known/agent-card.json",
  "skills": [
    {"id": "order_signal", "description": "OEM order signal and build-mix lookup"},
    {"id": "launch_readiness", "description": "Launch-program readiness"},
    {"id": "demand_allocation", "description": "Demand to plant allocation"}
  ],
  "tier": "enterprise",
  "metadata": {"kb_sources": ["demand_program"], "tools": ["demand"]}
}
```
Expected: schema matches `AgentCard`.

- [ ] **Step 2: Validate and commit**

```pwsh
python -c "import json; from pathlib import Path; from mmc_agents.registry.base import AgentCard; AgentCard.model_validate(json.loads(Path('enterprise/demand-program/agent.json').read_text())); print('ok')"
git add enterprise\demand-program\agent.json
git commit -m "feat(demand): A2A agent card"
```
Expected: `ok`; commit succeeds.

---

## Task 24: Refresh catalog to all 10 agents

**Files:**
- Modify: `agents/catalog.json`
- Modify: `tests/test_local_catalog.py`

- [ ] **Step 1: Add catalog count test**

```python
def test_gate_b_catalog_has_all_10_agents_after_refresh():
    agents = LocalCatalogSource(Path("agents/catalog.json")).list_agents()
    names = {a.name for a in agents}
    assert len(names) == 10
    assert {"ent-supply-chain", "ent-procurement", "ent-engineering-plm", "ent-quality", "ent-demand-program"}.issubset(names)
```
Expected: fails before catalog refresh if only Gate A cards exist.

- [ ] **Step 2: Refresh and verify**

```pwsh
python scripts\refresh_catalog.py
pytest tests\test_local_catalog.py -v
```
Expected: script prints catalog with 10 agents; tests pass.

- [ ] **Step 3: Commit**

```pwsh
git add agents\catalog.json tests\test_local_catalog.py
git commit -m "feat(registry): catalog includes full 10-agent pool"
```
Expected: commit succeeds.

---

## Task 25: Enterprise profile and factory refactor (TDD)

**Files:**
- Create: `enterprise/profile.yaml`
- Create: `tests/test_enterprise_agent_factory.py`
- Modify: `src/mmc_agents/agent_factory.py`

- [ ] **Step 1: Create profile**

```yaml
enterprise_id: enterprise
display_name: MMC Enterprise Nodes
kb:
  kb_id_env: FOUNDRY_IQ_KB_ENTERPRISE_ID
  sources:
    supply_chain: { node: supply-chain, paths: ["enterprise/supply-chain/data", "enterprise/supply-chain/kb"] }
    procurement: { node: procurement, paths: ["enterprise/procurement/data", "enterprise/procurement/kb"] }
    engineering_plm: { node: engineering-plm, paths: ["enterprise/engineering-plm/data", "enterprise/engineering-plm/kb"] }
    enterprise_quality: { node: enterprise-quality, paths: ["enterprise/enterprise-quality/data", "enterprise/enterprise-quality/kb"] }
    demand_program: { node: demand-program, paths: ["enterprise/demand-program/data", "enterprise/demand-program/kb"] }
agents:
  - { role: supply-chain, name: ent-supply-chain, display_name: Supply Chain, kb_sources: [supply_chain], tools: [erp, supplier, tms], skills: [{ id: supplier_health, description: Supplier health & disruption impact }, { id: bom_where_used, description: BOM explode & where-used }, { id: alt_source_lookup, description: Alternate-source and inbound-logistics ETA }] }
  - { role: procurement, name: ent-procurement, display_name: Procurement & Cost, kb_sources: [procurement], tools: [procurement], skills: [{ id: should_cost_analysis, description: Should-cost and PO-impact analysis }, { id: contract_terms, description: Contract terms and expedite-cost lookup }, { id: spend_rollup, description: Spend and supplier-tier rollup }] }
  - { role: engineering-plm, name: ent-engineering-plm, display_name: Engineering / PLM, kb_sources: [engineering_plm], tools: [plm], skills: [{ id: eco_status, description: ECO / ECN status and impact }, { id: part_revision_lookup, description: Part revision and effectivity lookup }, { id: where_installed, description: Cross-plant where-installed lookup }] }
  - { role: enterprise-quality, name: ent-quality, display_name: Enterprise Quality, kb_sources: [enterprise_quality], tools: [warranty], skills: [{ id: warranty_clustering, description: Warranty-claim clustering }, { id: cross_plant_defect_trends, description: Cross-plant defect trends }, { id: recall_threshold, description: Recall-threshold and safety call }] }
  - { role: demand-program, name: ent-demand-program, display_name: Demand / Program, kb_sources: [demand_program], tools: [demand], skills: [{ id: order_signal, description: OEM order signal and build-mix lookup }, { id: launch_readiness, description: Launch-program readiness }, { id: demand_allocation, description: Demand to plant allocation }] }
```
Expected: profile mirrors Plant profile shape.

- [ ] **Step 2: Write failing factory test**

```python
def test_emit_enterprise_card(tmp_path):
    profile = yaml.safe_load(Path("enterprise/profile.yaml").read_text())
    card = emit_enterprise_agent_card(profile, role="procurement", endpoint_base="http://localhost:8080", out_path=tmp_path / "agent.json")
    assert card["name"] == "ent-procurement"
    assert card["tier"] == "enterprise"
    assert card["metadata"]["kb_sources"] == ["procurement"]
```
Expected: missing function fails.

- [ ] **Step 3: Implement and verify**

```python
def emit_enterprise_agent_card(profile, role, endpoint_base, out_path):
    agent_def = next(a for a in profile["agents"] if a["role"] == role)
    name = agent_def["name"]
    card = {"name": name, "display_name": agent_def["display_name"], "description": f"{agent_def['display_name']} enterprise agent.", "endpoint": f"{endpoint_base.rstrip('/')}/{name}/.well-known/agent-card.json", "skills": agent_def["skills"], "tier": "enterprise", "metadata": {"kb_sources": agent_def["kb_sources"], "tools": agent_def["tools"]}}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(card, indent=2), encoding="utf-8")
    return card
```

```pwsh
pytest tests\test_enterprise_agent_factory.py tests\test_agent_factory.py -v
git add enterprise\profile.yaml src\mmc_agents\agent_factory.py tests\test_enterprise_agent_factory.py
git commit -m "feat(factory): enterprise agent cards from profile"
```
Expected: factory tests pass; commit succeeds.

---

## Task 26: Factory parity snapshots and replacement

**Files:**
- Create: `tests/snapshots/enterprise_agent_cards/*.json`
- Modify: `tests/test_enterprise_agent_factory.py`, `scripts/generate_cards.py`, `enterprise/*/agent.json`

- [ ] **Step 1: Snapshot hand cards**

```pwsh
New-Item -ItemType Directory -Force tests\snapshots\enterprise_agent_cards
Copy-Item enterprise\supply-chain\agent.json tests\snapshots\enterprise_agent_cards\supply-chain.agent.json
Copy-Item enterprise\procurement\agent.json tests\snapshots\enterprise_agent_cards\procurement.agent.json
Copy-Item enterprise\engineering-plm\agent.json tests\snapshots\enterprise_agent_cards\engineering-plm.agent.json
Copy-Item enterprise\enterprise-quality\agent.json tests\snapshots\enterprise_agent_cards\enterprise-quality.agent.json
Copy-Item enterprise\demand-program\agent.json tests\snapshots\enterprise_agent_cards\demand-program.agent.json
```
Expected: five snapshots exist.

- [ ] **Step 2: Add parity test**

```python
def test_factory_emitted_enterprise_cards_match_snapshots(tmp_path):
    for role, snapshot in mapping.items():
        emitted = emit_enterprise_agent_card(profile, role, "http://localhost:8080", tmp_path / role / "agent.json")
        expected = json.loads((Path("tests/snapshots/enterprise_agent_cards") / snapshot).read_text())
        assert emitted == expected
```
Expected: fails until factory and snapshots align exactly.

- [ ] **Step 3: Extend card generation and verify**

```pwsh
python scripts\generate_cards.py
python scripts\refresh_catalog.py
pytest tests\test_enterprise_agent_factory.py tests\test_local_catalog.py -v
```
Expected: factory cards equal snapshots and catalog remains 10 agents.

- [ ] **Step 4: Commit**

```pwsh
git add scripts\generate_cards.py enterprise\supply-chain\agent.json enterprise\procurement\agent.json enterprise\engineering-plm\agent.json enterprise\enterprise-quality\agent.json enterprise\demand-program\agent.json agents\catalog.json tests\test_enterprise_agent_factory.py tests\snapshots\enterprise_agent_cards
git commit -m "refactor(factory): replace enterprise hand cards with profile output"
```
Expected: commit succeeds.

---

## Task 27: Magentic backtrack tuning for brake-caliper

**Files:**
- Modify: `src/mmc_agents/orchestrator/manager.py`, `src/mmc_agents/orchestrator/scenarios/brake_caliper.py`
- Modify: `enterprise/supply-chain/data/supplier_master.csv`, `enterprise/supply-chain/fixtures/supplier_master.json`
- Create: `tests/test_manager_hardening.py`

- [ ] **Step 1: Write failing backtrack test**

```python
from mmc_agents.orchestrator.manager import RunResult, summarize_guarded_result

def test_run_result_exposes_backtrack_reason():
    result = RunResult(answer="alternate source requires procurement review", hops=["ent-supply-chain", "plant7-maintenance", "plant7-quality", "ent-procurement", "ent-supply-chain"], backtracks=1, raw_ledgers={"progress": {"backtrack_reason": "NO_DIRECT_ALT for BRK-CAL-XYZ"}})
    summary = summarize_guarded_result(result)
    assert "NO_DIRECT_ALT" in summary
    assert "ent-supply-chain" in summary
```
Expected: missing helper fails.

- [ ] **Step 2: Update scenario bounds**

```python
EXPECTED_BOUNDS = {
    "min_distinct_agents": 5,
    "min_backtracks": 1,
    "must_include_agents": {"ent-supply-chain", "plant7-maintenance", "plant7-quality", "ent-procurement"},
    "must_observe_ledger_terms": {"NO_DIRECT_ALT", "BRK-CAL-XYZ"},
}
```
Expected: smoke now requires the backtrack evidence.

- [ ] **Step 3: Tune manager instructions and helper**

```python
MANAGER_INSTRUCTIONS = "When a tool or agent reports NO_DIRECT_ALT, treat it as a dead-end, backtrack, and ask procurement, PLM, demand, or enterprise quality for another mitigation dimension. Record the dead-end phrase in the progress ledger."
def summarize_guarded_result(result: RunResult) -> str:
    return f"answer={result.answer}\nhops={result.hops}\nbacktracks={result.backtracks}\nledgers={result.raw_ledgers}"
```
Expected: instructions are passed through verified Magentic API from Task 2.

- [ ] **Step 4: Verify and commit**

```pwsh
python scripts\derive_fixtures.py --node supply-chain
pytest tests\test_manager_hardening.py -v
git add src\mmc_agents\orchestrator\manager.py src\mmc_agents\orchestrator\scenarios\brake_caliper.py enterprise\supply-chain\data\supplier_master.csv enterprise\supply-chain\fixtures\supplier_master.json tests\test_manager_hardening.py
git commit -m "feat(orchestrator): tune brake-caliper backtracking"
```
Expected: tests pass; commit succeeds.

---

## Task 28: Max-step guard handling

**Files:**
- Modify: `src/mmc_agents/orchestrator/manager.py`
- Modify: `tests/test_manager_hardening.py`

- [ ] **Step 1: Add failing guard test**

```python
def test_max_step_guard_returns_partial_answer_and_ledgers():
    result = RunResult(answer="Partial answer: supply impact known.", hops=["ent-supply-chain", "plant7-maintenance"], backtracks=0, raw_ledgers={"task": {"solved": False}, "progress": {"guard": "max_steps"}})
    assert "max_steps" in summarize_guarded_result(result)
    assert "Partial answer" in summarize_guarded_result(result)
```
Expected: fails if guard details are discarded.

- [ ] **Step 2: Implement guard normalization**

```python
try:
    result = manager.run(problem_statement)
except MaxStepsExceeded as exc:
    return RunResult(answer=f"Partial answer: manager reached max_steps={self.max_steps} before full resolution.", hops=getattr(exc, "hops", []), backtracks=getattr(exc, "backtracks", 0), raw_ledgers={"task": getattr(exc, "task_ledger", {}), "progress": {"guard": "max_steps", **getattr(exc, "progress_ledger", {})}})
```
Expected: use the verified SDK exception/result type from Task 2.

- [ ] **Step 3: Verify and commit**

```pwsh
pytest tests\test_manager_hardening.py -v
git add src\mmc_agents\orchestrator\manager.py tests\test_manager_hardening.py
git commit -m "feat(orchestrator): return ledgers on max-step guard"
```
Expected: tests pass; commit succeeds.

---

## Task 29: Safety/LOTO data augmentation and scenario file

**Files:**
- Modify: `plants/plant7/kb/08_Logs_Data/MMC_P7_Incident_Log.csv`
- Modify: `plants/plant7/fixtures/capa.json`
- Create: `src/mmc_agents/orchestrator/scenarios/loto_cluster.py`

- [ ] **Step 1: Append LOTO rows only if missing**

```csv
INC-062,2026-01-22,10:18,A,L1,Stamping/Forming,Near Miss,High,Maintenance opened L1-PRS-001 guard before all LOTO points were verified,Verification step skipped,LOTO verification gap,None,None,None,0,0,Operator,EHS Manager,CAPA-062,Open,
INC-063,2026-01-29,15:42,B,L1,Stamping/Forming,Near Miss,Medium,Contractor staged work at L1-PRS-002 with tag applied to wrong disconnect,Wrong energy isolation point,LOTO procedure mismatch,None,None,None,0,0,Supervisor,EHS Manager,CAPA-063,Open,
INC-064,2026-02-06,07:55,A,L1,Stamping/Forming,Near Miss,High,Operator attempted jam clear before LOTO verification signoff on press feed,Production pressure,LOTO signoff bypass,None,None,First Aid,0,0,Line Lead,EHS Manager,CAPA-064,In Progress,
```
Expected: existing Incident_Log header remains unchanged.

- [ ] **Step 2: Create scenario**

```python
PROBLEM_STATEMENT = "We've had 3 LOTO-related near-misses on Plant 7 L1 in the last 60 days. What's the pattern, who is qualified to address it, what corrective actions are open, and is there any enterprise quality or customer exposure?"
EXPECTED_BOUNDS = {
  "min_distinct_agents": 4,
  "min_backtracks": 0,
  "must_include_agents": {"plant7-ehs", "plant7-maintenance", "plant7-training"},
  "optional_agents": {"plant7-quality", "ent-quality"},
  "must_observe_terms": {"LOTO", "L1", "CAPA"},
}
```
Expected: scenario is distinct from brake-caliper.

- [ ] **Step 3: Re-derive and commit**

```pwsh
python scripts\derive_fixtures.py --plant plant7
pytest tests\test_cross_link_integrity.py tests\test_plant_tools.py -v
git add plants\plant7\kb\08_Logs_Data\MMC_P7_Incident_Log.csv plants\plant7\fixtures\capa.json src\mmc_agents\orchestrator\scenarios\loto_cluster.py
git commit -m "feat(scenarios): Safety LOTO cluster scenario and data"
```
Expected: tests pass; commit succeeds.

---

## Task 30: Safety/LOTO live-gated smoke test

**Files:**
- Create: `tests/test_loto_cluster_smoke.py`

- [ ] **Step 1: Write smoke test**

```python
import os, pytest
from mmc_agents.orchestrator.manager import MmcMagenticManager
from mmc_agents.orchestrator.scenarios.loto_cluster import PROBLEM_STATEMENT, EXPECTED_BOUNDS
LIVE = os.environ.get("MMC_LIVE", "0") == "1"
@pytest.mark.skipif(not LIVE, reason="Requires deployed Foundry + KBs; set MMC_LIVE=1.")
def test_loto_cluster_composes_distinct_flow():
    result = MmcMagenticManager(max_steps=14).run(PROBLEM_STATEMENT)
    distinct = set(result.hops)
    assert len(distinct) >= EXPECTED_BOUNDS["min_distinct_agents"]
    assert EXPECTED_BOUNDS["must_include_agents"].issubset(distinct)
    for term in EXPECTED_BOUNDS["must_observe_terms"]:
        assert term in result.answer.upper()
```
Expected: skipped without live environment.

- [ ] **Step 2: Seed and run live**

```pwsh
python scripts\seed_foundry_iq.py --plant plant7
python scripts\seed_foundry_iq.py --enterprise
$env:MMC_LIVE = "1"
pytest tests\test_loto_cluster_smoke.py -v -s
```
Expected: PASS; hops include EHS, Maintenance, Training, plus Quality or Enterprise Quality.

- [ ] **Step 3: Commit**

```pwsh
git add tests\test_loto_cluster_smoke.py
git commit -m "test(smoke): Safety LOTO cluster composition bounds"
```
Expected: commit succeeds.

---

## Task 31: Full enterprise KB seed and brake-caliper live smoke

**Files:**
- Modify: `scripts/seed_foundry_iq.py`
- Modify: `tests/test_brake_caliper_smoke.py`

- [ ] **Step 1: Update seeder**

```python
for subdir in ["data", "kb"]:
    for f in (node_dir / subdir).rglob("*"):
        if f.is_file():
            source.upload(str(f))
```
Expected: `--enterprise` uploads all 5 sources; `--source <node>` refreshes one source.

- [ ] **Step 2: Tighten brake-caliper smoke**

```python
for term in EXPECTED_BOUNDS.get("must_observe_ledger_terms", set()):
    assert term in str(result.raw_ledgers) or term in result.answer
```
Expected: smoke verifies `NO_DIRECT_ALT` evidence.

- [ ] **Step 3: Run live smokes**

```pwsh
python scripts\seed_foundry_iq.py --enterprise
$env:MMC_LIVE = "1"
pytest tests\test_brake_caliper_smoke.py tests\test_loto_cluster_smoke.py -v -s
```
Expected: both live tests pass.

- [ ] **Step 4: Commit**

```pwsh
git add scripts\seed_foundry_iq.py tests\test_brake_caliper_smoke.py
git commit -m "test(smoke): Gate B brake-caliper bounds against full network"
```
Expected: commit succeeds.

---

## Task 32: Full regression and generated artifact audit

**Files:**
- Modify only direct regression fixes caused by Gate B work.

- [ ] **Step 1: Run non-live tests**

```pwsh
pytest -v -m "not live"
```
Expected: all non-live tests pass; live tests skip.

- [ ] **Step 2: Run Bicep build**

```pwsh
az bicep build --file infra\bicep\main.bicep
```
Expected: build succeeds.

- [ ] **Step 3: Run validators and fixture audit**

```pwsh
python scripts\validate_naming.py enterprise\supply-chain\kb enterprise\procurement\kb enterprise\engineering-plm\kb enterprise\enterprise-quality\kb enterprise\demand-program\kb
python scripts\derive_fixtures.py --node all
python scripts\derive_fixtures.py --plant plant7
git --no-pager diff --stat enterprise plants\plant7\fixtures
```
Expected: validator exits 0; no fixture diff.

- [ ] **Step 4: Run both live smokes**

```pwsh
$env:MMC_LIVE = "1"
pytest tests\test_brake_caliper_smoke.py tests\test_loto_cluster_smoke.py -v -s
```
Expected: both pass.

- [ ] **Step 5: Commit only if fixes were required**

```pwsh
git status --short\n# If direct regression fixes changed files, add only those files shown by git status.
git commit -m "fix: Gate B regression cleanup"
```
Expected: skip this commit if there are no changes.

---

## Task 33: Gate B status checkpoint and tag

**Files:**
- Create: `docs/specs/gate-b-status.md`

- [ ] **Step 1: Write status**

```markdown
# Gate B status — 2026-06-16

**Working:** Full 10-agent pool is discoverable in `agents/catalog.json`. All 5 enterprise nodes have CSV data, narrative docs, derived fixtures, and KB sources under `kb-enterprise`. Plant 7 has CAPA, CMMS, QMS, SCADA, MES, and LMS fixture-backed tool seams. Brake-caliper resolves across enterprise and Plant 7 with at least one manager backtrack. Safety/LOTO composes a distinct flow across EHS, maintenance, training, and quality/enterprise exposure.

**Verification:**
- `pytest -v -m "not live"` — PASS
- `az bicep build --file infra\bicep\main.bicep` — PASS
- `python scripts\validate_naming.py enterprise\supply-chain\kb enterprise\procurement\kb enterprise\engineering-plm\kb enterprise\enterprise-quality\kb enterprise\demand-program\kb` — PASS
- `MMC_LIVE=1 pytest tests\test_brake_caliper_smoke.py tests\test_loto_cluster_smoke.py -v -s` — PASS

**Demo notes:**
- Brake-caliper trigger: `BRK-CAL-XYZ` / `SUP-001` / `NO_DIRECT_ALT`.
- LOTO trigger: at least three L1 near-misses in 60 days with open CAPAs.
- Foundry portal threads show KB citations and Magentic ledgers.

**Deferred to Gate C:** custom trace UI, hot-add visual choreography, governance overlay / Entra Agent ID blast-radius view.
```
Expected: status reflects actual command output.

- [ ] **Step 2: Commit and tag**

```pwsh
git add docs\specs\gate-b-status.md
git commit -m "docs: Gate B checkpoint"
git tag gate-b
```
Expected: `git tag --list gate-b` prints `gate-b`.

---

## Done criteria for Gate B

- Gate A pre-review exists at `docs/specs/gate-b-pre-review.md` and user sign-off occurred before Task 2.
- No `TODO(verify-on-Learn)` or `TODO(verify)` markers remain in infra, scripts, or `src/mmc_agents`.
- `enterprise/scenario_seed.yaml` pins Acme Brakes, `BRK-CAL-XYZ`, `plant7`, `MMC_P7`, `L1`, `L1-PRS-001`, and LOTO cluster facts.
- Supply Chain has ≥25 suppliers and ≥40 BOM rows.
- All 5 enterprise nodes have required CSVs, narrative docs, and derived deterministic fixtures.
- Enterprise Quality warranty data includes multiple `BRK-CAL-XYZ` rows and recall rules.
- `scripts/derive_fixtures.py --node all` and `scripts/derive_fixtures.py --plant plant7` are deterministic.
- `scripts/seed_foundry_iq.py --enterprise` updates one enterprise KB with 5 sources per D15.
- Cross-link integrity test resolves supplier → BOM → Plant 7 PM → Plant 7 incident context.
- Procurement, PLM, warranty/recall, demand/allocation, CAPA, CMMS, QMS, SCADA, MES, and LMS tools are fixture-backed and tested.
- Remaining 4 enterprise cards validate with `AgentCard` before factory refactor.
- Factory-emitted enterprise cards match the hand-authored snapshots and replace them.
- `agents/catalog.json` contains exactly 10 agents.
- Brake-caliper live smoke passes with ≥1 backtrack and `NO_DIRECT_ALT` evidence.
- Safety/LOTO live smoke passes with a distinct flow including Plant 7 EHS, Maintenance, and Training.
- `pytest -v -m "not live"` passes.
- `az bicep build --file infra\bicep\main.bicep` passes.
- `docs/specs/gate-b-status.md` is committed and `gate-b` tag exists.
