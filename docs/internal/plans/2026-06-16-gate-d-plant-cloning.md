# Gate D — Plant Cloning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clone Plant 7 into Plant 4 to prove the reusable-pattern thesis end-to-end: same code, new plant profile + content, and existing enterprise agents composing with both plants.

**Architecture:** Gate D adds a template tree, a clone CLI, a hybrid content generator, and a validator in front of Foundry IQ seeding. Plant agents remain generated from `plants/<plant_id>/profile.yaml` via `agent_factory.build_plant_agent(...)` / card-emission helpers, while enterprise agents and the Magentic manager remain unchanged.

**Tech Stack:** Python 3.11+, pytest, PyYAML, Jinja2-style templates, deterministic CSV transforms with stdlib `csv`/`hashlib`/`random`, Azure OpenAI chat client from `mmc_agents.config.get_chat_client()`, Microsoft Agent Framework SDK, Foundry Agent Service, Foundry IQ, Azure AI Search, Bicep, Azure CLI.

**Reference docs (read these before starting):**
- `docs/specs/2026-06-16-mmc-agent-network-implementation-design.md` — source of truth for D10, D11, D15, §8 plant cloning, §4 repo layout, and Gate D scope.
- `DEMO_BUILD_HANDOFF.md` — naming conventions, agent rosters, the brake-caliper composition thesis, and Plant 7/enterprise vocabulary.
- `docs/plans/2026-06-16-gate-a-thin-slice.md` — required plan style, paths, `agent_factory.py`, `seed_foundry_iq.py`, `refresh_catalog.py`, catalog shape, and scenario smoke-test style.
- `docs/MMC_Plant7_Company_Profile_v1.md` — canonical Plant 7 naming and content tone; Plant 4 must use `plant4` / `P4` IDs with different location and equipment specifics.
- `docs/specs/gate-c-status.md` — Gate C trace UI + governance overlay status; Task 1 documents drift before Gate D begins.

**Verify against Microsoft Learn before Azure-specific coding:** Foundry IQ KB/source provisioning, Agent Framework chat-client API, Foundry Agent Service deployment, A2A card schema, and current Bicep resource types. Keep model/client choices configurable and do not hardcode a vendor beyond the existing `get_chat_client()` seam.

---

## File Structure

| Path | Responsibility |
|---|---|
| `docs/specs/gate-d-pre-review.md` | Mandatory Gate C review output and sign-off checkpoint before coding Gate D. |
| `docs/specs/gate-d-template-map.md` | Records which Plant 7 artifacts became templates versus plant-specific generated output. |
| `templates/plant_template/profile.yaml.j2` | Reusable plant profile template using `{{ plant_id }}`, `{{ plant_code }}`, `{{ plant_name }}`, `{{ primary_lines }}`, and KB env placeholders. |
| `templates/plant_template/kb/**/*.md.j2` | Narrative templates copied from Plant 7 structure and rewritten by the LLM for Plant 4. |
| `templates/plant_template/kb/08_Logs_Data/*.csv.j2` | Schema-identical CSV templates for PM, incident, training, and any Gate B/C plant CSVs. |
| `templates/plant_template/fixtures/*.json.j2` | Optional plant-local fixture templates only if Gate B/C added plant fixtures that cannot derive from CSVs. |
| `scripts/clone_plant.py` | CLI that renders templates into `plants/<plant_id>/`, refusing overwrite unless `--force`. |
| `scripts/generate_plant_content.py` | Hybrid generator: mechanical CSV substitution/jitter and LLM narrative regeneration. |
| `scripts/validate_plant.py` | Structured validator for required files, CSV schemas, naming, source-plant remnants, and enterprise cross-links. |
| `plants/plant4/profile.yaml` | Hand-authored Plant 4 profile for Monterrey, MX; L1 brake-caliper assembly and L2 paint/final finish. |
| `plants/plant4/kb/**` | Generated Plant 4 KB content after clone + content generation. |
| `plants/plant4/agents/*.agent.json` | Generated cards from `agent_factory` helpers, not hand-authored templates. |
| `tests/test_clone_plant.py` | CLI render/overwrite tests. |
| `tests/test_generate_plant_content.py` | Determinism, ID substitution, LLM rewrite, and shared-token guard tests. |
| `tests/test_validate_plant.py` | Schema, naming, and cross-link validator tests. |
| `tests/test_multi_plant_catalog.py` | Catalog count and Plant 4 registration test. |
| `tests/test_multi_plant_warranty_smoke.py` | Live scenario test for enterprise + Plant 7 + Plant 4 composition. |
| `enterprise/supply-chain/data/bom_where_used.csv` | Add Plant 4 where-used row for `BRK-CAL-XYZ` while preserving `Acme Brakes`. |
| `src/mmc_agents/orchestrator/scenarios/brake_caliper.py` | Update expected bounds so a Plant 4 hop is accepted/required when present. |
| `src/mmc_agents/orchestrator/scenarios/multi_plant_warranty.py` | Explicit cross-plant warranty spike scenario. |
| `infra/bicep/main.bicep` | Add Plant 4 KB module with the same three-source shape as Plant 7. |
| `infra/bicep/parameters/dev.bicepparam` | Add `plant4KbName = 'kb-plant4'`. |
| `.env.example` | Add `FOUNDRY_IQ_KB_PLANT4_ID=`, plus per-plant KB MCP wiring `PLANT4_KB_CONNECTION_ID=` and `PLANT4_KB_MCP_URL=` (mirrors the global `PLANT_KB_*` pattern from Gate A). |
| `governance/blast_radius.json` | Regenerated Gate C artifact including Plant 4 agents. |
| `docs/specs/gate-d-status.md` | Gate D verification evidence and v1.0 tag readiness. |

**Decision:** Strongly prefer **not** templating agent cards. Agent cards should come from `agent_factory.build_plant_agent(profile, role, ...)` / `emit_agent_card(...)`; templates handle profile, KB documents, CSV data, and optional fixtures only.

---

## Task 1: Gate C review before Gate D

**Files:**
- Create: `docs/specs/gate-d-pre-review.md`
- Read: `docs/specs/gate-c-status.md`
- Inspect: `git log gate-c..HEAD`

- [ ] **Step 1: Collect Gate C drift evidence**

Run:
```pwsh
git status --short
git --no-pager log gate-c..HEAD --oneline --decorate
Get-ChildItem docs\specs\gate-c-status.md
Get-ChildItem plants, enterprise, src\mmc_agents, scripts, infra\bicep, governance -Recurse -File | Select-Object FullName
```
Expected: current tree and commits after `gate-c` are known; missing `gate-c-status.md` is captured as a blocker.

- [ ] **Step 2: Write pre-review**

Create `docs/specs/gate-d-pre-review.md` with sections: Inputs reviewed, Gate C delivered baseline, Blocking drift, Non-blocking drift, Sign-off request. Replace every finding with actual command evidence.

- [ ] **Step 3: Stop for user sign-off**

Expected: after this task is committed, do not create templates/scripts/Plant 4 files until the user replies with explicit approval such as `Approved to start Gate D`.

- [ ] **Step 4: Commit**

```pwsh
git add docs\specs\gate-d-pre-review.md
git commit -m "docs: gate d pre-review"
```

- [ ] **Step 5: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 2: Map Plant 7 template responsibilities

**Files:**
- Create: `docs/specs/gate-d-template-map.md`
- Read: `plants/plant7/**`
- Read: `enterprise/**`

- [ ] **Step 1: Inventory Plant 7**

Run:
```pwsh
Get-ChildItem plants\plant7 -Recurse -File | Sort-Object FullName | Select-Object FullName
Get-ChildItem enterprise -Recurse -File -ErrorAction SilentlyContinue | Sort-Object FullName | Select-Object FullName
```
Expected: all profile, KB, CSV, fixture, and card files are listed.

- [ ] **Step 2: Classify artifacts**

Create a table mapping each Plant 7 artifact category to one action: `template`, `generate from profile`, `derive from CSV`, `shared as-is`, or `do not copy`. Explicitly mark `agents/*.agent.json` as `generate from profile`, not template.

- [ ] **Step 3: Define placeholders**

Document required placeholders: `plant_id`, `plant_code`, `plant_name`, `plant_display_name`, `location_city`, `location_state`, `location_country`, `primary_lines`, `kb_id_env`, `agent_display_prefix`, `shifts`, and `lines`.

- [ ] **Step 4: Commit**

```pwsh
git add docs\specs\gate-d-template-map.md
git commit -m "docs: map plant7 content to reusable template"
```

- [ ] **Step 5: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 3: Extract profile and narrative templates

**Files:**
- Create: `templates/plant_template/profile.yaml.j2`
- Create: `templates/plant_template/kb/**/*.md.j2`

- [ ] **Step 1: Create template folders**

Run:
```pwsh
New-Item -ItemType Directory -Force templates\plant_template\kb\02_EHS_Internal | Out-Null
New-Item -ItemType Directory -Force templates\plant_template\kb\03_Maintenance | Out-Null
New-Item -ItemType Directory -Force templates\plant_template\kb\04_Quality | Out-Null
New-Item -ItemType Directory -Force templates\plant_template\kb\05_Ops_Shift | Out-Null
New-Item -ItemType Directory -Force templates\plant_template\kb\08_Logs_Data | Out-Null
```
Expected: folder shape mirrors Plant 7 KB source groups.

- [ ] **Step 2: Author `profile.yaml.j2`**

Use the Plant 7 profile shape from Gate A, but replace plant identity, location, shifts, lines, display names, KB env var, and KB paths with placeholders. Include all five roles: `ehs`, `maintenance`, `quality`, `shiftops`, `training`.

- [ ] **Step 3: Copy narrative docs**

Run:
```pwsh
Copy-Item plants\plant7\kb\02_EHS_Internal\*.md templates\plant_template\kb\02_EHS_Internal\
Copy-Item plants\plant7\kb\03_Maintenance\*.md templates\plant_template\kb\03_Maintenance\
Copy-Item plants\plant7\kb\04_Quality\*.md templates\plant_template\kb\04_Quality\
Copy-Item plants\plant7\kb\05_Ops_Shift\*.md templates\plant_template\kb\05_Ops_Shift\
Get-ChildItem templates\plant_template\kb -Recurse -File -Filter *.md | ForEach-Object { Rename-Item $_.FullName ($_.FullName -replace '\.md$', '.md.j2') }
```
Expected: every narrative template keeps the original document purpose but replaces generated-output Plant 7 literals with placeholders.

- [ ] **Step 4: Verify literals**

Run:
```pwsh
Select-String -Path templates\plant_template\kb\**\*.md.j2 -Pattern 'MMC_P7|Plant 7|plant7|P7-L' -CaseSensitive
```
Expected: no matches except deliberate source-context comments for LLM prompting.

- [ ] **Step 5: Commit**

```pwsh
git add templates\plant_template docs\specs\gate-d-template-map.md
git commit -m "feat(templates): extract plant profile and narrative templates"
```

- [ ] **Step 6: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 4: Extract schema-identical CSV templates

**Files:**
- Create: `templates/plant_template/kb/08_Logs_Data/*.csv.j2`
- Create: `tests/test_plant_template_contract.py`

- [ ] **Step 1: Write failing contract test**

Create `tests/test_plant_template_contract.py` that asserts these paths exist: `MMC_{{ plant_code }}_Incident_Log.csv.j2`, `MMC_{{ plant_code }}_PM_Schedule.csv.j2`, `MMC_{{ plant_code }}_Training_Log.csv.j2`, and asserts no `templates/plant_template/agents/*.agent.json.j2` files exist.

- [ ] **Step 2: Run failing test**

Run:
```pwsh
pytest tests\test_plant_template_contract.py -v
```
Expected: FAIL until CSV templates exist.

- [ ] **Step 3: Create CSV templates**

Copy Plant 7 CSVs into `templates/plant_template/kb/08_Logs_Data/`, rename filenames to `MMC_{{ plant_code }}_*`, preserve headers byte-for-byte, and replace plant-local row IDs with placeholders where safe.

- [ ] **Step 4: Verify schemas**

Run:
```pwsh
pytest tests\test_plant_template_contract.py -v
python -c "from pathlib import Path; [print(p.name, p.read_text(encoding='utf-8').splitlines()[0]) for p in Path('templates/plant_template/kb/08_Logs_Data').glob('*.csv.j2')]"
```
Expected: test passes and printed headers match the schemas in `DEMO_BUILD_HANDOFF.md`.

- [ ] **Step 5: Commit**

```pwsh
git add templates\plant_template\kb\08_Logs_Data tests\test_plant_template_contract.py
git commit -m "feat(templates): add plant CSV templates"
```

- [ ] **Step 6: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 5: TDD for clone_plant CLI

**Files:**
- Create: `tests/test_clone_plant.py`

- [ ] **Step 1: Write failing tests**

Create tests covering mini-template rendering and overwrite refusal. Use `subprocess.run([sys.executable, 'scripts/clone_plant.py', '--profile', profile, '--template', template, '--output-root', out])` and assert rendered `plants/plantx/profile.yaml` plus `MMC_PX_Doc.md` output.

- [ ] **Step 2: Include expected mini profile**

The test profile must include `plant_id: plantx`, `plant_code: PX`, `display_name`, `lines: [{id: L1, name: Test Line, equipment_prefix: L1-TST-}]`, `agents: []`, and `kb.kb_id_env`.

- [ ] **Step 3: Run failure**

Run:
```pwsh
pytest tests\test_clone_plant.py -v
```
Expected: FAIL because `scripts/clone_plant.py` does not exist.

- [ ] **Step 4: Commit**

```pwsh
git add tests\test_clone_plant.py
git commit -m "test(clone): define plant clone CLI behavior"
```

- [ ] **Step 5: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 6: Implement clone_plant CLI

**Files:**
- Create: `scripts/clone_plant.py`
- Modify: `tests/test_clone_plant.py` if validation fixture needs keys

- [ ] **Step 1: Implement renderer**

Create a CLI with `--profile`, `--template`, `--output-root`, and `--force`. Load YAML, build context defaults (`plant_code`, `plant_name`, `primary_lines`, `kb_id_env`), render `{{ token }}` placeholders in filenames and file content, and strip `.j2` suffixes.

- [ ] **Step 2: Implement overwrite protection**

If `plants/<plant_id>` exists and `--force` is not set, print `Refusing to overwrite existing plant directory: <path>` to stderr and exit 1. With `--force`, overwrite rendered files.

- [ ] **Step 3: Implement profile validation**

Require `plant_id`, `display_name`, `lines`, `agents`, and `kb`; reject plant IDs that do not match `plant<n>`.

- [ ] **Step 4: Run tests**

Run:
```pwsh
pytest tests\test_clone_plant.py -v
python scripts\clone_plant.py --help
```
Expected: clone tests pass and help lists all CLI flags.

- [ ] **Step 5: Commit**

```pwsh
git add scripts\clone_plant.py tests\test_clone_plant.py
git commit -m "feat(scripts): render plant template from profile"
```

- [ ] **Step 6: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 7: TDD for generate_plant_content mechanical phase

**Files:**
- Create: `tests/test_generate_plant_content.py`

- [ ] **Step 1: Write deterministic CSV test**

Create a temp Plant 4 with `profile.yaml` and a CSV row containing `PM-P7-001`, `P7-L1-CMM-04`, `2026-01-10`, `2.0`, and `BRK-CAL-XYZ stays shared`. Run the script twice with `--mechanical-only` and assert bytes are identical.

- [ ] **Step 2: Assert substitutions**

The test must assert `P4-L1-CMM-04` appears, `P7-L1-CMM-04` does not, and `BRK-CAL-XYZ` still appears.

- [ ] **Step 3: Run failure**

Run:
```pwsh
pytest tests\test_generate_plant_content.py -v
```
Expected: FAIL because `scripts/generate_plant_content.py` does not exist.

- [ ] **Step 4: Commit**

```pwsh
git add tests\test_generate_plant_content.py
git commit -m "test(content): define deterministic plant content generation"
```

- [ ] **Step 5: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 8: Implement mechanical CSV generation

**Files:**
- Create: `scripts/generate_plant_content.py`
- Modify: `tests/test_generate_plant_content.py`

- [ ] **Step 1: Implement CLI**

Add `--plant`, `--plants-root`, `--enterprise-root`, and `--mechanical-only`. Load `plants/<plant>/profile.yaml`; derive `plant_code` from profile or `plant_id`.

- [ ] **Step 2: Implement substitutions**

For CSVs under `kb/08_Logs_Data`, replace `MMC_P7 -> MMC_P4`, `P7-L<n>-... -> P4-L<n>-...`, `PM-P7- -> PM-P4-`, `INC-P7- -> INC-P4-`, and `TRN-P7- -> TRN-P4-`. Do not replace `BRK-CAL-XYZ` or `Acme Brakes`.

- [ ] **Step 3: Implement deterministic jitter**

Use `hashlib.sha256(f'{plant_id}:{path.name}:{row_index}')` as the seed. Jitter date columns by a small deterministic day offset and numeric quantity columns by a small deterministic factor.

- [ ] **Step 4: Run tests**

Run:
```pwsh
pytest tests\test_generate_plant_content.py -v
python scripts\generate_plant_content.py --help
```
Expected: deterministic mechanical test passes; help lists all flags.

- [ ] **Step 5: Commit**

```pwsh
git add scripts\generate_plant_content.py tests\test_generate_plant_content.py
git commit -m "feat(content): deterministic mechanical plant CSV generation"
```

- [ ] **Step 6: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 9: Implement narrative LLM regeneration

**Files:**
- Modify: `scripts/generate_plant_content.py`
- Modify: `tests/test_generate_plant_content.py`

- [ ] **Step 1: Add fake-client test**

Extend tests with a `FakeChatClient.complete(prompt)` that returns Plant 4 text. Assert the prompt contains the original Plant 7 source doc and the output file contains Plant 4 text with no `MMC_P7`, `Plant 7`, `plant7`, or `P7-L`.

- [ ] **Step 2: Implement prompt**

Add `build_narrative_prompt(source_doc, profile)` instructing the model to rewrite the same document as Plant 4, preserve standards references, use profile location/lines/equipment, keep shared tokens unchanged, and never emit Plant 7 identifiers.

- [ ] **Step 3: Call chat client**

Use `mmc_agents.config.get_chat_client()` by default. Accept client methods named `complete(prompt)` or `invoke(prompt)` so tests can use a fake client.

- [ ] **Step 4: Validate output**

After each `.md` rewrite, scan for forbidden source-plant remnants and raise a structured error naming the file if any remain.

- [ ] **Step 5: Run tests**

Run:
```pwsh
pytest tests\test_generate_plant_content.py -v
```
Expected: generator tests pass without live Azure.

- [ ] **Step 6: Commit**

```pwsh
git add scripts\generate_plant_content.py tests\test_generate_plant_content.py
git commit -m "feat(content): regenerate plant narratives with chat client"
```

- [ ] **Step 7: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 10: Add cross-link guard for shared scenario IDs

**Files:**
- Modify: `scripts/generate_plant_content.py`
- Modify: `tests/test_generate_plant_content.py`
- Later modifies: `enterprise/supply-chain/data/bom_where_used.csv`

- [ ] **Step 1: Add failing BOM test**

Create a temp `bom_where_used.csv` with Plant 7 row `BRK-CAL-XYZ,Acme Brakes,plant7,L1,P7-L1-CMM-04`. Call `ensure_cross_plant_bom_link(...)`; assert a Plant 4 row is added with `P4-L1-CMM-04` and shared tokens unchanged.

- [ ] **Step 2: Implement helper**

Add `ensure_cross_plant_bom_link(bom_path, plant_id, plant_code)` that is idempotent, copies the Plant 7 `BRK-CAL-XYZ` row, changes only plant-local fields, and reduces volume deterministically if an annual volume column exists.

- [ ] **Step 3: Wire CLI**

After mechanical phase, call the helper for `enterprise/supply-chain/data/bom_where_used.csv`. Ensure repeated generator runs do not duplicate Plant 4 rows.

- [ ] **Step 4: Run tests**

Run:
```pwsh
pytest tests\test_generate_plant_content.py -v
```
Expected: all tests pass and deterministic bytes remain stable.

- [ ] **Step 5: Commit**

```pwsh
git add scripts\generate_plant_content.py tests\test_generate_plant_content.py
git commit -m "feat(content): preserve shared scenario IDs and add plant4 BOM link"
```

- [ ] **Step 6: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 11: TDD for validate_plant

**Files:**
- Create: `tests/test_validate_plant.py`

- [ ] **Step 1: Write success test**

Create a temp `plants/plant4` with `profile.yaml` and non-empty `MMC_P4_Incident_Log.csv`, `MMC_P4_PM_Schedule.csv`, and `MMC_P4_Training_Log.csv` using exact headers from `DEMO_BUILD_HANDOFF.md`. Run `scripts/validate_plant.py <plant_dir>` and assert JSON `status == ok`.

- [ ] **Step 2: Write failure test**

Replace `P4-L1-CMM-04` with `P7-L1-CMM-04` in a CSV and assert nonzero exit plus JSON error code `forbidden_source_plant_id`.

- [ ] **Step 3: Run failure**

Run:
```pwsh
pytest tests\test_validate_plant.py -v
```
Expected: FAIL because validator does not exist.

- [ ] **Step 4: Commit**

```pwsh
git add tests\test_validate_plant.py
git commit -m "test(validate): define plant validator behavior"
```

- [ ] **Step 5: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 12: Implement validate_plant schema and naming checks

**Files:**
- Create: `scripts/validate_plant.py`
- Modify: `tests/test_validate_plant.py`

- [ ] **Step 1: Implement required CSV checks**

Require exact headers and at least one row for Incident Log, PM Schedule, and Training Log. Emit errors with `code`, `path`, and `message`.

- [ ] **Step 2: Implement naming checks**

For non-Plant 7 plants, reject `MMC_P7`, `Plant 7`, `plant7`, and `P7-L`. Validate any `P<n>-L<n>-...` local ID matches the current plant code.

- [ ] **Step 3: Implement JSON report**

Always print JSON to stdout: `{'status': 'ok'|'error', 'plant_id': '<id>', 'errors': [...]}`. Return 0 only when status is ok.

- [ ] **Step 4: Run tests**

Run:
```pwsh
pytest tests\test_validate_plant.py -v
python scripts\validate_plant.py --help
```
Expected: tests pass and help lists `plant_dir` plus `--enterprise-root`.

- [ ] **Step 5: Commit**

```pwsh
git add scripts\validate_plant.py tests\test_validate_plant.py
git commit -m "feat(validate): schema and naming checks for cloned plants"
```

- [ ] **Step 6: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 13: Enforce enterprise cross-link validation

**Files:**
- Modify: `scripts/validate_plant.py`
- Modify: `tests/test_validate_plant.py`

- [ ] **Step 1: Add cross-link tests**

Add tests where `bom_where_used.csv` references `plant4,L9` and assert `bad_cross_link`; add another where enterprise data exists but no `BRK-CAL-XYZ` Plant 4 row exists and assert `missing_brake_caliper_cross_link`.

- [ ] **Step 2: Implement cross-link validation**

Load `enterprise/supply-chain/data/bom_where_used.csv` when present. For this plant, every `line_id` must exist in profile. For cloned plants, require at least one row with `part_id == BRK-CAL-XYZ`, `supplier_name == Acme Brakes`, and `plant_id == plant4`.

- [ ] **Step 3: Run tests**

Run:
```pwsh
pytest tests\test_validate_plant.py -v
```
Expected: all validator tests pass.

- [ ] **Step 4: Commit**

```pwsh
git add scripts\validate_plant.py tests\test_validate_plant.py
git commit -m "feat(validate): enforce enterprise cross-links for cloned plants"
```

- [ ] **Step 5: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 14: Author Plant 4 profile

**Files:**
- Create: `plants/plant4/profile.yaml`

- [ ] **Step 1: Write profile**

Create a hand-authored profile for `plant4` / `P4`: Monterrey, Nuevo Leon, MX; ~190 employees; two shifts; L1 Brake-Caliper Assembly with prefix `L1-CMM-`; L2 Paint and Final Finish with prefix `L2-PNT-`; standards matching Plant 7; same five roles as Plant 7.

- [ ] **Step 2: Use this YAML core**

```yaml
plant_id: plant4
plant_code: P4
display_name: MMC Plant 4 (Monterrey, MX)
location:
  city: Monterrey
  state: Nuevo Leon
  country: MX
employees: 190
operating_model: 2-shift 24/5 with Saturday maintenance window
shifts:
  - { id: A, hours: "06:00-14:00" }
  - { id: B, hours: "14:00-22:00" }
lines:
  - { id: L1, name: Brake-Caliper Assembly, equipment_prefix: L1-CMM-, primary_products: [BRK-CAL-XYZ] }
  - { id: L2, name: Paint and Final Finish, equipment_prefix: L2-PNT-, primary_products: [painted caliper brackets] }
kb:
  kb_id_env: FOUNDRY_IQ_KB_PLANT4_ID
  sources:
    ehs:
      paths: ["plants/plant4/kb/02_EHS_Internal", "shared/kb/regulatory-reference/OSHA"]
    maintenance:
      paths: ["plants/plant4/kb/03_Maintenance", "shared/kb/oem-manuals"]
    quality_ops:
      paths: ["plants/plant4/kb/04_Quality", "plants/plant4/kb/05_Ops_Shift", "plants/plant4/kb/08_Logs_Data"]
```
Then append all five `agents:` entries from Plant 7 with display names changed to `Plant 4 ...`.

- [ ] **Step 3: Verify**

Run:
```pwsh
python -c "import yaml, pathlib; p=yaml.safe_load(pathlib.Path('plants/plant4/profile.yaml').read_text()); assert p['plant_id']=='plant4'; assert p['plant_code']=='P4'; assert len(p['agents'])==5; print('plant4 profile ok')"
```
Expected: prints `plant4 profile ok`.

- [ ] **Step 4: Commit**

```pwsh
git add plants\plant4\profile.yaml
git commit -m "feat(plant4): author Monterrey plant profile"
```

- [ ] **Step 5: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 15: Run clone_plant for Plant 4 scaffold

**Files:**
- Modify/Create: `plants/plant4/kb/**`
- Read: `templates/plant_template/**`

- [ ] **Step 1: Run clone**

Run:
```pwsh
python scripts\clone_plant.py --profile plants\plant4\profile.yaml --template templates\plant_template --force
```
Expected: renders `plants\plant4` and preserves the hand-authored profile values.

- [ ] **Step 2: Inspect tree**

Run:
```pwsh
Get-ChildItem plants\plant4 -Recurse -File | Sort-Object FullName | Select-Object FullName
```
Expected: KB folder structure mirrors Plant 7 and CSV filenames use `MMC_P4`.

- [ ] **Step 3: Check source remnants**

Run:
```pwsh
Select-String -Path plants\plant4\kb\**\* -Pattern 'MMC_P7|Plant 7|plant7|P7-L' -CaseSensitive
```
Expected: before narrative generation, any match is in source-like narrative text only; CSVs should already be plant-local after template rendering.

- [ ] **Step 4: Commit**

```pwsh
git add plants\plant4
git commit -m "feat(plant4): scaffold plant content from reusable template"
```

- [ ] **Step 5: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 16: Generate final Plant 4 content

**Files:**
- Modify: `plants/plant4/kb/**`
- Modify: `enterprise/supply-chain/data/bom_where_used.csv`

- [ ] **Step 1: Run hybrid generator**

Run:
```pwsh
python scripts\generate_plant_content.py --plant plant4
```
Expected: CSVs are mechanically transformed and narratives are LLM-rewritten as Plant 4 documents.

- [ ] **Step 2: Inspect Plant 4 content**

Run:
```pwsh
Select-String -Path plants\plant4\kb\**\* -Pattern 'MMC_P7|Plant 7|plant7|P7-L' -CaseSensitive
Select-String -Path plants\plant4\kb\**\* -Pattern 'MMC_P4|Plant 4|P4-L|Monterrey' -CaseSensitive | Select-Object -First 40
```
Expected: no forbidden Plant 7 remnants; Plant 4 naming appears throughout.

- [ ] **Step 3: Verify BOM cross-link**

Run:
```pwsh
Select-String -Path enterprise\supply-chain\data\bom_where_used.csv -Pattern 'BRK-CAL-XYZ|Acme Brakes|plant4|P4-L1-CMM-04'
```
Expected: Plant 7 and Plant 4 rows exist for `BRK-CAL-XYZ`; shared supplier/part tokens are unchanged.

- [ ] **Step 4: Commit**

```pwsh
git add plants\plant4\kb enterprise\supply-chain\data\bom_where_used.csv
git commit -m "feat(plant4): generate cloned content and cross-plant BOM link"
```

- [ ] **Step 5: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 17: Validate Plant 4 content

**Files:**
- Run: `scripts/validate_plant.py plants/plant4`
- Read/modify if needed: `plants/plant4/**`

- [ ] **Step 1: Run validator**

Run:
```pwsh
python scripts\validate_plant.py plants\plant4
```
Expected: exit code 0 and JSON status `ok` with empty errors.

- [ ] **Step 2: Run regression tests**

Run:
```pwsh
pytest tests\test_clone_plant.py tests\test_generate_plant_content.py tests\test_validate_plant.py tests\test_plant_template_contract.py -v
```
Expected: all tests pass.

- [ ] **Step 3: Fix reported rows only**

If validator fails, edit only the file/row named in the structured error and rerun the validator plus related test. Do not broaden schemas or rename shared enterprise tokens.

- [ ] **Step 4: Commit if fixes were needed**

If validation fixes changed tracked files, run:
```pwsh
git add plants\plant4 enterprise\supply-chain\data\bom_where_used.csv
git commit -m "fix(plant4): satisfy cloned plant validation"
```
Expected: skip this commit if Task 17 already validates cleanly.

- [ ] **Step 5: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 18: Add Plant 4 Foundry IQ KB to Bicep

**Files:**
- Modify: `infra/bicep/main.bicep`
- Modify: `infra/bicep/parameters/dev.bicepparam`
- Modify: `.env.example`

- [ ] **Step 1: Add parameter**

Add `param plant4KbName string = 'kb-plant4'` to `main.bicep` and `param plant4KbName = 'kb-plant4'` to `dev.bicepparam` if parameters are split.

- [ ] **Step 2: Add module**

Instantiate `modules/foundry-iq-kb.bicep` as `kbPlant4` with plant search resource and `sourceNames: ['ehs','maintenance','quality_ops']`, mirroring Plant 7.

- [ ] **Step 3: Update env example**

Append three lines to `.env.example` (the KB id is used by the seeder; the
connection id + MCP url are baked into agent versions by the factory):
```
FOUNDRY_IQ_KB_PLANT4_ID=
PLANT4_KB_CONNECTION_ID=
PLANT4_KB_MCP_URL=
```
The connection id pattern is `kb-<kb-name>-<5-char-suffix>` and the MCP URL is
`https://<search>.search.windows.net/knowledgebases/<kb-name>/mcp?api-version=2026-05-01-preview`
(see Gate A `gate-a-status.md` for the exact format).

- [ ] **Step 4: Build**

Run:
```pwsh
az bicep build --file infra\bicep\main.bicep
```
Expected: build succeeds.

- [ ] **Step 5: Commit**

```pwsh
git add infra\bicep\main.bicep infra\bicep\parameters\dev.bicepparam .env.example
git commit -m "infra: add plant4 Foundry IQ KB"
```

- [ ] **Step 6: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 19: Deploy and seed Plant 4 KB

**Files:**
- Run: `infra/bicep/**`
- Run: `scripts/seed_foundry_iq.py --plant plant4`
- Do not commit: `.env`

- [ ] **Step 1: Deploy**

Run:
```pwsh
az deployment group create --resource-group rg-magentictest --template-file infra\bicep\main.bicep --parameters infra\bicep\parameters\dev.bicepparam
```
Expected: deployment succeeds in `rg-magentictest`.

- [ ] **Step 2: Seed**

Run:
```pwsh
python scripts\seed_foundry_iq.py --plant plant4
```
Expected: `kb-plant4` is created/updated with EHS, maintenance, and quality_ops sources from Plant 4 profile paths.

- [ ] **Step 3: Store local env**

Add the printed KB id to untracked `.env` as `FOUNDRY_IQ_KB_PLANT4_ID=<id>`,
**plus** the MCP connection id and URL so the factory can bake the tool into
plant4 agent versions:
```
PLANT4_KB_CONNECTION_ID=kb-kb-plant4-<5-char-suffix>
PLANT4_KB_MCP_URL=https://srch-mmc-plant.search.windows.net/knowledgebases/kb-plant4/mcp?api-version=2026-05-01-preview
```
Expected: `.env` remains untracked and is not committed.

> **Factory change needed before Task 21:** `agent_factory._kb_tool()` currently
> reads global `PLANT_KB_CONNECTION_ID` / `PLANT_KB_MCP_URL`. For Gate D,
> generalize it to look up `<PLANT_ID_UPPER>_KB_CONNECTION_ID` /
> `<PLANT_ID_UPPER>_KB_MCP_URL` first, falling back to the globals (so Plant 7
> keeps working without rename). Add a unit test
> `tests/test_agent_factory.py::test_kb_tool_uses_per_plant_env`.

- [ ] **Step 4: Smoke retrieval**

Run a brake-caliper scenario scoped to plant4:
```pwsh
$env:MMC_LIVE = "1"
python scripts\run_scenario.py --plant plant4   # add --plant flag if not present
```
Open App Insights (`mmc-plant-appinsights-5430`) → Transaction search →
`magentic.scenario.plant4`. Expected: citations in agent spans come from
Plant 4 sources and shared OSHA/OEM sources only — **no Plant 7 leakage**.

- [ ] **Step 5: Commit if fixes needed**

If seeding required code fixes, commit with `git add scripts src infra && git commit -m "fix(seed): support plant4 Foundry IQ seeding"`; otherwise no commit.

- [ ] **Step 6: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 20: Generate Plant 4 agent cards and refresh catalog

**Files:**
- Create: `plants/plant4/agents/*.agent.json`
- Modify: `agents/catalog.json`
- Create: `tests/test_multi_plant_catalog.py`

- [ ] **Step 1: Generate cards**

Use the same Gate A path that generated Plant 7 cards. If no wrapper script exists, run a Python one-liner that loads `plants/plant4/profile.yaml` and calls `emit_agent_card(profile, role, endpoint, plants/plant4/agents/<plant4-role>.agent.json)` for all five roles.

- [ ] **Step 2: Refresh catalog**

Run:
```pwsh
python scripts\refresh_catalog.py
python -c "import json, pathlib; c=json.loads(pathlib.Path('agents/catalog.json').read_text()); print(len(c['agents'])); print(sorted(a['name'] for a in c['agents'] if a.get('metadata',{}).get('plant_id')=='plant4'))"
```
Expected: prints `15` and the five Plant 4 names.

- [ ] **Step 3: Add catalog test**

Create `tests/test_multi_plant_catalog.py` asserting 15 unique names and presence of all Plant 7, Plant 4, and `ent-*` agents.

- [ ] **Step 4: Run test**

Run:
```pwsh
pytest tests\test_multi_plant_catalog.py -v
```
Expected: 1 passed.

- [ ] **Step 5: Commit**

```pwsh
git add plants\plant4\agents agents\catalog.json tests\test_multi_plant_catalog.py
git commit -m "feat(plant4): register generated plant agents in catalog"
```

- [ ] **Step 6: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 21: Deploy and smoke Plant 4 agents

**Files:**
- Run: existing Gate B/C agent deployment scripts
- Read: `plants/plant4/profile.yaml`
- Read: `plants/plant4/agents/*.agent.json`

- [ ] **Step 1: Deploy agents**

Run the Gate B/C plant-agent deployment command, expected shape
`python scripts\deploy_agents.py --plant plant4` if that script exists.
The factory must read `PLANT4_KB_CONNECTION_ID` / `PLANT4_KB_MCP_URL` (set
in Task 19 Step 3) so the Foundry IQ MCP tool is baked into each of the five
agent versions at create time — no portal action required (mirrors Plant 7).
Expected: five agents are deployed to `mmc-foundry-plant`, each version's
tools list includes the plant4 KB MCP tool, and `FOUNDRY_IQ_KB_PLANT4_ID`
is referenced by the seeder run in Task 19.

> **Quota note (from Gate A):** the manager runs on its own
> `FOUNDRY_MANAGER_DEPLOYMENT` (`gpt-5.4`) so it does not consume the
> agent-pool TPM. If you plan to run plant7 and plant4 scenarios in parallel,
> request a quota bump on `gpt-5.4-mini` before Task 24's live composition
> test — Gate A is currently provisioned at 500 TPM, which is the operational
> floor for a single 5-agent loop.

- [ ] **Step 2: Smoke role questions**

Ask: EHS LOTO for `P4-L1-CMM-04`; maintenance PM history for `P4-L1-CMM-04`; quality containment for `BRK-CAL-XYZ`; shiftops L1 handover; training qualifications for L1 LOTO. Expected: each answer cites Plant 4 KB or shared references.

- [ ] **Step 3: Verify no code fork**

Run `git diff src/mmc_agents/orchestrator` and confirm no Plant 4-specific routing code was added. Expected: orchestrator remains registry-driven.

- [ ] **Step 4: Commit if fixes needed**

If deployment required source fixes, commit with `git add scripts src && git commit -m "fix(agents): support plant4 profile-driven deployment"`; otherwise no commit.

- [ ] **Step 5: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 22: Update brake-caliper scenario for cross-plant composition

**Files:**
- Modify: `src/mmc_agents/orchestrator/scenarios/brake_caliper.py`
- Modify: brake-caliper smoke test under `tests/`

- [ ] **Step 1: Update bounds**

Set bounds to require enterprise + Plant 7 and at least one Plant 4 plant-local hop. Include `must_mention_plants: {'Plant 7','Plant 4'}` and allow Gate B/C role naming drift (`plant4-shiftops` or `plant4-production`).

- [ ] **Step 2: Update assertions**

Add helper logic for `must_include_any`: for each set of alternatives, at least one must appear in `result.hops`. Assert final answer mentions both plants.

- [ ] **Step 3: Run non-live tests**

Run:
```pwsh
pytest tests -k "brake_caliper or catalog" -v
```
Expected: non-live tests pass; live smoke remains skipped unless `MMC_LIVE=1`.

- [ ] **Step 4: Commit**

```pwsh
git add src\mmc_agents\orchestrator\scenarios\brake_caliper.py tests
git commit -m "test(scenarios): require cross-plant brake-caliper bounds"
```

- [ ] **Step 5: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 23: Add explicit multi-plant warranty scenario

**Files:**
- Create: `src/mmc_agents/orchestrator/scenarios/multi_plant_warranty.py`
- Create: `tests/test_multi_plant_warranty_smoke.py`

- [ ] **Step 1: Create scenario file**

Define `PROBLEM_STATEMENT`: `BRK-CAL-XYZ warranty claims are spiking. Which MMC plants are affected, what qualified maintenance and production response should each plant take, and what enterprise quality or supply-chain actions are needed?`

- [ ] **Step 2: Define bounds**

Require `ent-quality`, `ent-supply-chain`, `plant7-quality`, `plant4-quality`, one Plant 7 maintenance/shiftops/production agent, one Plant 4 maintenance/shiftops/production agent, both plant names, `BRK-CAL-XYZ`, and `Acme Brakes`.

- [ ] **Step 3: Create live smoke**

Create a pytest skipped unless `MMC_LIVE=1`; run `MmcMagenticManager().run(PROBLEM_STATEMENT)` and assert the bounds above against `result.hops`, `result.answer`, and `result.backtracks`.

- [ ] **Step 4: Run non-live**

Run:
```pwsh
pytest tests\test_multi_plant_warranty_smoke.py -v
```
Expected: skipped by default.

- [ ] **Step 5: Commit**

```pwsh
git add src\mmc_agents\orchestrator\scenarios\multi_plant_warranty.py tests\test_multi_plant_warranty_smoke.py
git commit -m "feat(scenarios): add multi-plant warranty spike smoke"
```

- [ ] **Step 6: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 24: Verify cross-plant scenario composition live

**Files:**
- Run: `tests/test_brake_caliper_smoke.py`
- Run: `tests/test_multi_plant_warranty_smoke.py`
- Read: Gate C trace artifacts/logs

- [ ] **Step 1: Run brake-caliper live**

Run:
```pwsh
$env:MMC_LIVE = "1"
pytest tests\test_brake_caliper_smoke.py -v -s
```
Expected: PASS with enterprise + Plant 7 + Plant 4 hops and final answer naming both plants.

- [ ] **Step 2: Run warranty live**

Run:
```pwsh
$env:MMC_LIVE = "1"
pytest tests\test_multi_plant_warranty_smoke.py -v -s
```
Expected: PASS with enterprise quality/supply-chain and both plant quality/local-response agents.

- [ ] **Step 3: Inspect ledgers**

Verify at least one manager ledger entry mentions both Plant 7 and Plant 4 in the same decision. Expected: evidence supports reusable cross-plant composition rather than a hardcoded route.

- [ ] **Step 4: Commit if fixes needed**

If live tests required fixes, commit with `git add src tests enterprise plants && git commit -m "fix(scenarios): stabilize cross-plant composition"`; otherwise no commit.

- [ ] **Step 5: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 25: Verify Plant 4 in trace UI and blast radius

**Files:**
- Modify: `governance/blast_radius.json`
- Run: Gate C trace UI
- Run: Gate C governance generator

- [ ] **Step 1: Check trace UI**

Start the Gate C trace UI using its existing command. Expected: sidebar lists five Plant 4 agents from `agents/catalog.json` with no Plant 4-specific UI code.

- [ ] **Step 2: Run UI/governance tests**

Run:
```pwsh
pytest tests -k "trace_ui or blast_radius" -v
```
Expected: tests pass or unrelated live tests are skipped.

- [ ] **Step 3: Regenerate blast radius**

Run the Gate C generator, expected shape `python scripts\generate_blast_radius.py --catalog agents\catalog.json --out governance\blast_radius.json`. Then assert Plant 4 IDs exist in JSON.

- [ ] **Step 4: Commit**

```pwsh
git add governance\blast_radius.json
git commit -m "chore(governance): include plant4 in blast radius"
```

- [ ] **Step 5: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 26: Write Gate D status checkpoint

**Files:**
- Create: `docs/specs/gate-d-status.md`

- [ ] **Step 1: Create status doc**

Write sections: Summary, Evidence table, Final agent roster, Known limitations, Tag plan. Include command evidence for pre-review approval, clone, generation, validation, unit tests, catalog 15, Bicep, deploy, seed, live scenarios, trace UI, and blast radius.

- [ ] **Step 2: Remove placeholders**

Run:
```pwsh
Select-String -Path docs\specs\gate-d-status.md -Pattern '<|>'
```
Expected: no placeholder matches remain.

- [ ] **Step 3: Commit**

```pwsh
git add docs\specs\gate-d-status.md
git commit -m "docs: gate d status checkpoint"
```

- [ ] **Step 4: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Task 27: Final verification and tags

**Files:**
- Run: full repo tests
- Tag: `gate-d`
- Tag: `mmc-demo-v1.0`

- [ ] **Step 1: Run final non-live verification**

Run:
```pwsh
pytest -v
az bicep build --file infra\bicep\main.bicep
python scripts\validate_plant.py plants\plant4
python scripts\refresh_catalog.py
```
Expected: tests pass or live tests skip; Bicep builds; Plant 4 validates; catalog prints 15 agents.

- [ ] **Step 2: Run final live verification**

Run:
```pwsh
$env:MMC_LIVE = "1"
pytest tests\test_brake_caliper_smoke.py tests\test_multi_plant_warranty_smoke.py -v -s
```
Expected: both pass and show enterprise + Plant 7 + Plant 4 hops.

- [ ] **Step 3: Create annotated tags**

Run:
```pwsh
git tag -a gate-d -m "Gate D: Plant 4 cloning complete"
git tag -a mmc-demo-v1.0 -m "MMC demo v1.0: reusable agent network with Plant 4 clone"
```
Expected: local annotated tags exist.

- [ ] **Step 4: Verify tags**

Run:
```pwsh
git --no-pager tag --list "gate-d" "mmc-demo-v1.0" -n
```
Expected: prints both tags. Do not push unless the user explicitly asks.

- [ ] **Step 5: Record task evidence**

- Record the exact command output in the task notes or the eventual `docs/specs/gate-d-status.md` evidence table.
- If a command fails, fix the smallest directly related issue and rerun the same command before moving on.
- Do not commit secrets, `.env`, Azure IDs that are not already safe to document, or unrelated formatting changes.

---

## Cross-task execution guardrails

Use this checklist while executing the numbered tasks. It is intentionally repetitive so each task can be handed to a fresh agent without relying on hidden context.

### Task 1 guardrails
- Confirm Task 1 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 1 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 1.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 1 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 1 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 1 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 2 guardrails
- Confirm Task 2 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 2 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 2.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 2 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 2 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 2 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 3 guardrails
- Confirm Task 3 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 3 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 3.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 3 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 3 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 3 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 4 guardrails
- Confirm Task 4 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 4 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 4.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 4 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 4 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 4 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 5 guardrails
- Confirm Task 5 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 5 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 5.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 5 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 5 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 5 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 6 guardrails
- Confirm Task 6 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 6 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 6.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 6 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 6 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 6 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 7 guardrails
- Confirm Task 7 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 7 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 7.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 7 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 7 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 7 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 8 guardrails
- Confirm Task 8 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 8 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 8.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 8 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 8 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 8 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 9 guardrails
- Confirm Task 9 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 9 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 9.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 9 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 9 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 9 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 10 guardrails
- Confirm Task 10 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 10 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 10.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 10 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 10 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 10 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 11 guardrails
- Confirm Task 11 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 11 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 11.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 11 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 11 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 11 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 12 guardrails
- Confirm Task 12 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 12 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 12.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 12 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 12 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 12 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 13 guardrails
- Confirm Task 13 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 13 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 13.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 13 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 13 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 13 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 14 guardrails
- Confirm Task 14 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 14 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 14.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 14 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 14 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 14 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 15 guardrails
- Confirm Task 15 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 15 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 15.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 15 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 15 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 15 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 16 guardrails
- Confirm Task 16 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 16 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 16.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 16 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 16 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 16 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 17 guardrails
- Confirm Task 17 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 17 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 17.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 17 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 17 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 17 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 18 guardrails
- Confirm Task 18 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 18 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 18.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 18 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 18 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 18 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 19 guardrails
- Confirm Task 19 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 19 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 19.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 19 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 19 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 19 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 20 guardrails
- Confirm Task 20 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 20 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 20.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 20 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 20 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 20 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 21 guardrails
- Confirm Task 21 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 21 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 21.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 21 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 21 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 21 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 22 guardrails
- Confirm Task 22 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 22 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 22.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 22 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 22 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 22 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 23 guardrails
- Confirm Task 23 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 23 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 23.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 23 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 23 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 23 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 24 guardrails
- Confirm Task 24 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 24 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 24.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 24 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 24 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 24 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 25 guardrails
- Confirm Task 25 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 25 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 25.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 25 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 25 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 25 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 26 guardrails
- Confirm Task 26 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 26 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 26.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 26 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 26 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 26 for `docs/specs/gate-d-status.md` if the task contributes final verification.

### Task 27 guardrails
- Confirm Task 27 starts from a clean understanding of the files listed in its **Files** block.
- Run the exact command shown in Task 27 before changing later-task files.
- Preserve Gate A naming: plant IDs use `plant<n>` and plant codes use `P<n>`.
- Preserve shared enterprise tokens unless the task explicitly says to add a new cross-link.
- Do not introduce Plant 4-specific code into the Magentic manager or registry.
- Prefer profile-driven generation over copied JSON whenever agent cards are involved.
- Keep CSV headers identical to their source schemas unless a prior committed Gate B/C schema change requires otherwise.
- Keep validation errors structured with stable machine-readable `code` values.
- Re-run the task-specific pytest target after every code change in Task 27.
- Re-run `python scripts\validate_plant.py plants\plant4` after any Plant 4 content change once the validator exists.
- Inspect `git diff --stat` before the Task 27 commit and remove unrelated edits.
- Ensure generated files are deterministic when the task claims deterministic output.
- Ensure no `.env` values, KB IDs, access tokens, or local secrets are staged.
- Use the commit message specified in Task 27 unless a no-commit step explicitly says to skip it.
- Record concise evidence from Task 27 for `docs/specs/gate-d-status.md` if the task contributes final verification.


## Done criteria for Gate D

- `docs/specs/gate-d-pre-review.md` exists, reflects `docs/specs/gate-c-status.md` and `git log gate-c..HEAD`, and was approved by the user before Gate D coding started.
- `templates/plant_template/` mirrors Plant 7 content structure for profile, narrative docs, CSV logs, and optional fixtures.
- Agent cards are generated from `profile.yaml` using the Gate A factory path; they are not hand-templated.
- `scripts/clone_plant.py --profile plants/plant4/profile.yaml --template templates/plant_template` renders `plants/plant4/` and refuses overwrite unless `--force`.
- `scripts/generate_plant_content.py --plant plant4` performs deterministic mechanical CSV generation and LLM narrative regeneration.
- Shared scenario identifiers remain shared: `Acme Brakes` and `BRK-CAL-XYZ` are not renamed.
- Enterprise where-used data includes both Plant 7 and Plant 4 rows for `BRK-CAL-XYZ`.
- `scripts/validate_plant.py plants/plant4` returns exit code 0 and structured JSON with `status: ok`.
- `infra/bicep/main.bicep` includes `kb-plant4` with three sources matching Plant 7's pattern.
- `scripts/seed_foundry_iq.py --plant plant4` seeds Plant 4 into Foundry IQ and `FOUNDRY_IQ_KB_PLANT4_ID` is stored only in local `.env`.
- `plants/plant4/agents/` contains five generated cards: EHS, maintenance, quality, shiftops/production, training.
- `scripts/refresh_catalog.py` produces a 15-agent catalog: 5 enterprise + 5 Plant 7 + 5 Plant 4.
- Brake-caliper and/or multi-plant warranty live scenario traces show enterprise hops plus Plant 7 and Plant 4 hops.
- Gate C trace UI lists Plant 4 agents without Plant 4-specific UI code.
- `governance/blast_radius.json` includes Plant 4 nodes and scopes.
- `docs/specs/gate-d-status.md` records command evidence and live verification results.
- Local annotated tag `gate-d` exists.

## Demo v1.0 done criteria

- Gate A, Gate B, Gate C, and Gate D status documents exist and show completed verification evidence.
- The repo demonstrates the reusable thesis: same manager, same registry, same factory, same enterprise agents, new plant profile/content only.
- The live catalog has 15 agents and the manager discovers them at run start.
- The brake-caliper / warranty demo can answer which plants are affected, what each plant should do, and what enterprise actions are needed.
- The trace UI makes the dynamic plan visible: manager ledgers, agent hops, citations, backtrack, and both plant nodes.
- Governance overlay/blast-radius view includes all 15 agents.
- Azure resources are deployed in `rg-magentictest` with Plant 7, Plant 4, and enterprise KBs seeded.
- Full tests pass, with live tests passing when `MMC_LIVE=1` and non-live tests passing without Azure.
- Local annotated tag `mmc-demo-v1.0` exists after final verification.
