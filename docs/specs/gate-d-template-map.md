# Gate D — Plant 7 → template-map classification

Maps every Plant 7 artifact category to one of five Gate D actions:

- **`template`** — copied to `templates/plant_template/...j2` with placeholders; rendered per plant.
- **`generate from profile`** — produced by Python code (`agent_factory.emit_agent_card`, `scripts/generate_plant_content.py`, etc.) from `profile.yaml`. Never templated.
- **`derive from CSV`** — content is a structured transform of plant CSVs (column-stable jitter, ID substitution). The CSV is templated; downstream fixtures/JSON are generated.
- **`shared as-is`** — lives under `shared/` or `enterprise/`. Plant 4 uses the same file, not a copy.
- **`do not copy`** — Plant 7-only artifact; Plant 4 should not get a counterpart.

Sources for this map:

- `git ls-files plants/plant7/` (39 files)
- `git ls-files enterprise/` (54 files)
- `git ls-files shared/` (8 files)
- `plants/plant7/profile.yaml` (113 lines, 6 roles)

---

## Plant 7 artifact classification

| Artifact category | Path pattern | Action | Notes |
|---|---|---|---|
| Plant profile | `plants/plant7/profile.yaml` | **template** | One file → `templates/plant_template/profile.yaml.j2`. Hand-authored per plant (Plant 4 overrides legacy SQL-table names and language). |
| Agent cards | `plants/plant7/cards/*.json` (5 files: `ehs`, `maintenance`, `quality`, `shiftops`, `training`) | **generate from profile** | Per Gate D plan: cards come from `agent_factory.emit_agent_card(profile, role, ...)`, not templates. **Side-observation:** `plant7-external-auditor.json` is missing from disk despite being a 6th role in `profile.yaml`. Plant 4's generation pass should emit all six cards including `plant4-external-auditor.json`. |
| Narrative KB — EHS Internal | `plants/plant7/kb/02_EHS_Internal/*.md` (4 files: LOTO SOP, PPE matrix, machine guarding SOP, safety program overview) | **template** | Render to Spanish for Plant 4 (Option A scope). Plant identity tokens substituted; standards swapped (OSHA → NOM-STPS for Plant 4 — see §Regulatory below). |
| Narrative KB — EHS Restricted | `plants/plant7/kb/02_EHS_Internal_Restricted/*.md` (1 file: confidential incident) | **template** | Plant 4 needs an equivalent confidential brief to make the sensitivity-demo work for both plants. Generate in Spanish; mark explicitly as restricted. |
| Narrative KB — Maintenance | `plants/plant7/kb/03_Maintenance/*.md` (4 files: PM program, jam-clear WI, conveyor manual excerpt, BOM L1) | **template** | Render to Spanish. BOM L1 stays brake-caliper themed (Plant 4 also builds calipers per Gate D plan); line and equipment-prefix tokens swap to Plant 4's `L1-CMM-` / `L2-PNT-`. |
| Narrative KB — Quality | `plants/plant7/kb/04_Quality/*.md` (3 files: NCR/CAPA process, brake caliper QA spec, quality policy) | **template** | Render to Spanish. ISO-9001 stays (international standard); cross-reference to Plant 4 enterprise QMS. |
| Narrative KB — Ops/Shift | `plants/plant7/kb/05_Ops_Shift/*.md` (2 files: standard work changeover, shift handover guidelines) | **template** | Render to Spanish. Shift IDs swap (Plant 4 has 2 shifts vs Plant 7's 3 — per plan: A=06:00-14:00, B=14:00-22:00). |
| Narrative KB — Logs (MD) | `plants/plant7/kb/08_Logs_Data/MMC_P7_L1_Build_Schedule.md` | **template** | Render to Spanish; line/equipment tokens swap. |
| CSV KB — Logs | `plants/plant7/kb/08_Logs_Data/*.csv` (3 files: Incident, PM, Training) | **derive from CSV** | English column headers preserved (Option A — schema-identical). Free-text values (incident description, asset name) generated in Spanish via deterministic LLM prompt or jittered from Plant 7. CSVs are templated; values are content-generated. |
| Fixtures | `plants/plant7/fixtures/*.json` (6 files: lms, cmms, capa, qms, mes, scada) | **derive from CSV** | Programmatically produced from the corresponding CSV in `data/` via existing `scripts/derive_fixtures.py` pattern. No template, no LLM — pure deterministic transform. |
| System data CSVs | `plants/plant7/data/*.csv` (6 files: scada, qms, mes, lms, cmms, capa) | **template** | Schema-identical templates with jittered values; same Spanish-free-text treatment as the Logs CSVs. Asset IDs jittered with `plant_code` prefix (`P7-` → `P4-`). |
| Shared OEM manuals | `shared/kb/oem-manuals/*.pdf` (HAAS CNC, Fanuc robot) | **shared as-is** | OEM equipment is global; Plant 4 references the same PDFs via profile `kb.sources.maintenance.paths`. |
| Shared regulatory (OSHA) | `shared/kb/regulatory-reference/OSHA/*.pdf` (6 files) | **do not copy** for Plant 4 | US-specific. Plant 4 needs a Mexican equivalent — see §Regulatory below. |
| Enterprise content | `enterprise/**` (all subtrees: supply-chain, enterprise-quality, procurement, demand-program, engineering-plm) | **shared as-is** | Enterprise agents stay singular; they compose across plants. No Plant 4 fork. (Gate D plan does extend `enterprise/supply-chain/data/bom_where_used.csv` with a Plant 4 row — that's a content edit, not a structural fork.) |

### Regulatory-reference treatment (new shared subtree)

The Gate D plan implicitly assumed shared OSHA references would apply to
Plant 4. They don't — Mexico operates under NOM-STPS (Normas Oficiales
Mexicanas, Secretaría del Trabajo y Previsión Social). Three options
considered:

- **(a) Stub Mexican regulatory references** — author `shared/kb/regulatory-reference/MEX/NOM_overview.md`, a 1-2 page Spanish summary referencing NOM-001-STPS (workplace safety), NOM-029-STPS (machinery), NOM-017-STPS (PPE), NOM-019-STPS (LOTO equivalent). No real PDFs; demo-plausible.
- (b) Skip regulatory entirely for Plant 4 — `kb.sources.ehs.paths` points only at plant-local content.
- (c) Reuse OSHA in Plant 4's profile — inauthentic.

**Pick (a).** Add `shared/kb/regulatory-reference/MEX/` to the **`do not template`** list — it's hand-authored content, but produced fresh as part of Gate D rather than derived from Plant 7. Treat it as new shared content, parallel to OSHA, that any future Mexico-region plant can reference.

---

## Templating placeholders

Every placeholder used in `templates/plant_template/**/*.j2` is enumerated
below with its source, type, and an example value for both plants. The
template engine (`scripts/clone_plant.py`) MUST refuse to render if any
required placeholder is missing.

### Placeholders from the original Gate D plan

| Placeholder | Type | Plant 7 (legacy) | Plant 4 (Gate D) | Source |
|---|---|---|---|---|
| `plant_id` | str | `plant7` | `plant4` | `profile.plant_id` |
| `plant_code` | str | `P7` | `P4` | derived: `'P' + plant_id[-1]` |
| `plant_name` | str | `Plant 7` | `Plant 4` | derived from `plant_code` |
| `plant_display_name` | str | `MMC Plant 7 (Illinois)` | `MMC Plant 4 (Monterrey)` | `profile.display_name` |
| `location_city` | str | (n/a; Plant 7 omits) | `Monterrey` | `profile.location.city` |
| `location_state` | str | `IL` | `NL` | `profile.location.state` |
| `location_country` | str | `US` | `MX` | `profile.location.country` |
| `primary_lines` | str | `brake-caliper assy + conveyor pack-out` | `brake-caliper assy + paint/final finish` | derived from `profile.lines` |
| `kb_id_env` | str | `FOUNDRY_IQ_KB_PLANT7_ID` | `FOUNDRY_IQ_KB_PLANT4_ID` | `profile.kb.kb_id_env` |
| `agent_display_prefix` | str | `Plant 7` | `Plant 4` | derived |
| `shifts` | list[dict] | A/B/C (8h each) | A/B (8h each) | `profile.shifts` |
| `lines` | list[dict] | L1/L2/L3 | L1/L2 | `profile.lines` |

### New placeholders from Gate D sign-off scope expansion

| Placeholder | Type | Plant 7 (legacy) | Plant 4 (Gate D) | Source / Decision |
|---|---|---|---|---|
| `language` | str | `en` (implicit / default) | `es` | Multi-language Option A — `profile.language` |
| `foundry_project` | str | `mmc-plant` | `mmc-plant4` | Decision 3 — `profile.foundry_project` |
| `plant_sql_suffix` | str | `''` (empty — legacy un-suffixed tables) | `_p4` | Decision 1 — `profile.plant_sql_suffix`; Plant 7 keeps `dbo.training_log`, Plant 4 gets `dbo.training_log_p4` |
| `search_service` | str | `srch-mmc-plant` | `srch-mmc-plant4` | Decision 2 — `profile.kb.search_service` |
| `kb_connection_env` | str | `PLANT_KB_CONNECTION_ID` | `PLANT4_KB_CONNECTION_ID` | Decision 2 — derived from `plant_id` |
| `kb_mcp_url_env` | str | `PLANT_KB_MCP_URL` | `PLANT4_KB_MCP_URL` | Decision 2 — derived from `plant_id` |
| `regulatory_reference_path` | str | `shared/kb/regulatory-reference/OSHA` | `shared/kb/regulatory-reference/MEX` | new — `profile.kb.regulatory_reference_path` |

### Placeholders that look generic but are NOT templated

Called out so nobody tries to "improve" them:

- **Brake-caliper part numbers (`BRK-CAL-XYZ`, `BRK-CAL-001`, etc.)** — stay literal across plants. Both plants build the same caliper; cross-plant where-used joins depend on the part numbers matching.
- **Supplier IDs (`SUP-001`)** — enterprise-scoped; stay literal.
- **OEM equipment models (HAAS, Fanuc, brand names in PDFs)** — global; not templated.
- **Magentic manager / orchestrator prompts** — English regardless of plant `language`. The manager comprehends Spanish via the model; only plant agent instructions get language-conditioned.

---

## Task evidence

```
git --no-pager log gate-c..HEAD --oneline
6dfdf3a docs(gate-d): record per-plant infra decisions at sign-off
87a7602 docs: gate d pre-review
374e23d docs: add PRODUCT.md, DESIGN.md, critique snapshot, and presentation deck
7b56e5d feat(trace): first-class agent_no_data event for empty agent responses
4fd036b (tag: gate-c) Gate C close: restricted source, hot-add, identity bicep, run-of-show

git ls-files plants/plant7/ | Measure-Object -Line  →  39 files
git ls-files enterprise/    | Measure-Object -Line  →  54 files
git ls-files shared/        | Measure-Object -Line  →  8 files
```

Plant 7 has 39 tracked files spread across 5 KB groups, 6 system-data CSVs,
6 fixture JSONs, 5 agent cards, and 1 profile. Of those: 1 templates to
`profile.yaml.j2`, ~15 narrative MDs template to `*.md.j2`, 9 CSVs
template to `*.csv.j2`, 6 fixtures derive from CSVs, 5 agent cards generate
from profile, 1 stays do-not-copy (`MMC_P7_Confidential_Incident.md`
parallel pattern only — Plant 4 gets its own incident brief, not a copy).

After Gate D: Plant 4 mirrors Plant 7's file count (~39) with all narrative
content in Spanish, English schema preserved, and per-plant SQL/Foundry
isolation.

---

## Open questions deferred to later tasks

These are not blockers for Task 3 (template extraction) but need decisions
before the tasks that touch them:

1. **NOM stub content authorship** — who writes `NOM_overview.md`? Recommend: generate via LLM during `scripts/generate_plant_content.py` Plant 4 run. (Resolve in Task 11.)
2. **Plant 4 confidential incident** — the narrative needs a plausible Spanish-language incident scenario. Recommend: LLM-generated, manually reviewed, mirrors Plant 7's pattern (near-miss → CAPA). (Resolve in Task 11.)
3. **`plant7-external-auditor.json` gap** — should Gate D backfill the missing card on disk for Plant 7, or leave the asymmetry? Recommend: backfill during Task 23 (cards generation) so the catalog is internally consistent. Low risk; no test currently asserts the gap. (Resolve in Task 23.)
4. **Existing `provision_sql.py` table creation** — does it already accept a suffix, or do we add the parameter? (Resolve in Task 17 SQL sub-task.)
