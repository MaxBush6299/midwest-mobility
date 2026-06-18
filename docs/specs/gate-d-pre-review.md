# Gate D pre-review

Mandatory pre-flight before any Gate D implementation work, per the multi-gate
review convention. Compares Gate C's actual delivered surface against what the
Gate D plan (`docs/plans/2026-06-16-gate-d-plant-cloning.md`) assumes, records
the adjustments needed, and folds in a deliberate scope expansion
(multi-language) that the user requested at the start of Gate D.

## Inputs reviewed

- **Gate C status doc:** `docs/specs/gate-c-status.md` — closed at commit
  `4fd036b` (tag `gate-c`), 103 passed + 4 skipped.
- **Git baseline:** `git log gate-c..HEAD` returns 2 commits, both
  trace-UI / docs only and unrelated to Gate D scope:
  - `7b56e5d` — `feat(trace): first-class agent_no_data event for empty agent responses`
  - `374e23d` — `docs: add PRODUCT.md, DESIGN.md, critique snapshot, and presentation deck`
- **Working tree:** `docs/presentation/` has uncommitted deck-rebuild churn
  (slide-*.jpg removals, new agent-rings artifacts). Out of Gate D scope.
- **Tree inspection:** `plants/plant7/**`, `enterprise/**`, `governance/**`,
  `scripts/**`, `infra/bicep/**`, and `src/mmc_agents/**` enumerated against
  the Gate D plan's File Structure section.
- **Plant 7 profile:** `plants/plant7/profile.yaml` (113 lines) — six roles,
  not five; three SQL-backed sources alongside file-backed sources.
- **Test baseline (this branch):** `110 tests collected` (`pytest --collect-only`).

## Gate C delivered baseline (carries into Gate D)

| Surface | State at `gate-c` | Why Gate D cares |
|---|---|---|
| Plant roles per profile | **6** (`ehs`, `maintenance`, `quality`, `shiftops`, `training`, `external-auditor`) | Template extraction + Plant 4 generation must cover all six. |
| Plant 7 KB source types | File-backed (`paths: [...]`) **and** SQL-backed (`sql_table: dbo.<table>`) | Plant 4 needs a SQL-data story (see Blocking drift §2). |
| Governance metadata | `governance/kb_metadata.json` includes 11 agents + 12 sources; `governance/blast_radius.json` is snapshot-tested | Plant 4 onboarding must update both and re-run the generator before any test runs. |
| Trace UI event types | 7 lifecycle types, plus the new `agent_no_data` added today | Plant 4 smoke-test scenarios will trip `agent_no_data` if Plant 4 agents are dispatched outside their KB scope — already handled correctly. |
| Demo scenarios | `brake_caliper` + `loto_cluster` | Plant 4 needs a cross-plant warranty scenario (the plan already calls this out at Task 25). |
| Branch hygiene | `gate-c` tag at `4fd036b`; Gate D will land on `gate-a-thin-slice` like A/B/C did | No new branch needed; Gate D commits append to the same branch. |

## Blocking drift (must fix the plan before Task 2)

### 1. Plan says "five roles" — Plant 7 has six

The Gate D plan was written before Gate C's `external-auditor` role landed. Three plan locations need correcting:

- Line 156 (Task 3 Step 2 — author profile.yaml.j2): *"Include all five roles: `ehs`, `maintenance`, `quality`, `shiftops`, `training`."*
- Line 604 (Task 17 Step 2 — hand-author Plant 4 profile): *"same five roles as Plant 7"*
- Line 917 (Task 23 — generate Plant 4 cards): *"for all five roles"*

**Adjustment:** treat every "five" above as "six" and explicitly include `external-auditor` in:

- `templates/plant_template/profile.yaml.j2` agents block
- `plants/plant4/profile.yaml` agents block
- `plants/plant4/agents/plant4-external-auditor.agent.json` generation
- `governance/kb_metadata.json` Plant 4 entries
- The `tests/test_multi_plant_catalog.py` count assertion (Plant 4 contributes **6** agents, not 5; the manifest at Gate D close should be 11 plant-side + 5 enterprise-side = **16 agents**).

### 2. SQL-backed KB sources have no Plant 4 story in the plan

Plant 7's profile binds three sources to SQL tables:

```yaml
training_data: { sql_table: dbo.training_log, ... }
pm_data:       { sql_table: dbo.pm_schedule, ... }
incident_data: { sql_table: dbo.incident_log, ... }
```

The Gate D plan handles the **CSV layer** (`MMC_P4_Training_Log.csv` etc.) but is silent on what binds Plant 4's SQL sources. Two valid options, both require code work the current plan doesn't enumerate:

- **(a) Per-plant tables** — `dbo.training_log_p4`, `dbo.pm_schedule_p4`, etc. Cleanest isolation; requires `provision_sql.py` and `scripts/upsert_enterprise.py` to template the table name from `plant_id`, and the profile gains `{{ plant_sql_suffix }}` substitutions.
- **(b) Shared tables with a `plant_id` filter column** — single `dbo.training_log` with a `plant_id` column. Cheaper schema; requires every agent skill that reads these tables to filter `WHERE plant_id = '<this plant>'`, and the upsert script to derive `plant_id` per row.

**Adjustment:** add a sub-task to **Task 17** (Plant 4 profile authoring) that picks one of the two options and updates `provision_sql.py` accordingly, *before* `scripts/seed_foundry_iq.py --plant plant4` is attempted. **Recommended: option (a)** — keeps blast-radius reasoning clean ("revoke read on `dbo.training_log_p4` isolates Plant 4 only") and matches the per-plant KB pattern (`kb-plant7`, `kb-plant4`) already in the Bicep plan.

### 3. Catalog and governance counts in the plan need updating

The Gate D plan's `tests/test_multi_plant_catalog.py` task says "Catalog count and Plant 4 registration test" without a target number. The current `agents/catalog.json` count is **11** (6 plant + 5 enterprise). After Gate D it should be **17** (6 + 6 + 5).

`governance/kb_metadata.json` after Gate D: **16 agents, 18 sources** (Plant 4 adds 6 agents + 6 sources mirroring Plant 7's structure).

**Adjustment:** call these numbers out explicitly in Task 24 (catalog test) and Task 21 (governance metadata refresh) so the assertions are concrete, not "roughly more."

## Non-blocking drift (note and continue)

- **`docs/presentation/` working-tree churn** — unrelated to Gate D. Leave alone or commit separately; does not affect Gate D tasks.
- **`PRODUCT.md` / `DESIGN.md` / `.impeccable/`** — design-system context committed in `374e23d`. Has no impact on Gate D code paths but Plant 4 documentation can lean on DESIGN.md tokens if/when we touch UI for the cross-plant scenario.
- **`agent_no_data` event** — added today (commit `7b56e5d`). Plant 4 agents whose Spanish KBs return no match will now render with the distinct dashed-amber treatment automatically; no Gate D task changes needed.
- **`marked@12` CDN dependency in the trace UI** — flagged in the impeccable critique but out of Gate D scope. Re-raise during `/impeccable harden`.

## Scope addendum: multi-language Plant 4 (user-approved, Option A)

The user requested at Gate D kickoff that Plant 4 (Monterrey, MX) demonstrate multi-language operation. After reviewing the cost/benefit, scope is locked to **Option A: Spanish narrative, English schema.** This is a deliberate scope expansion that the original Gate D plan did not anticipate.

### What changes

| Layer | Treatment | Affected Gate D tasks |
|---|---|---|
| Plant 4 narrative KB (.md files) | Spanish prose | Tasks 3, 11, 16 (template + generator + render) |
| Plant 4 agent instructions | Spanish | Task 17 (profile), Task 23 (card generation) |
| Plant 4 profile | New top-level `language: es` field | Task 17 |
| Plant 4 CSV files | English column headers, Spanish free-text values where applicable | Task 11 (CSV generator), validator |
| Plant 4 SQL tables / columns | English schema (per Blocking drift §2 resolution) | Task 17 SQL sub-task |
| Magentic manager prompts | Unchanged (English) | None |
| Trace UI rendering | Unchanged — Spanish replies pass through verbatim | None |
| Final synthesis | English (manager-driven, audience-facing) | None |
| Validator "source-plant remnants" check | Language-aware: must allow Spanish translations of role/place names | Task 20 (`scripts/validate_plant.py`) |
| `agent_factory.build_plant_agent` | Reads `profile.language` and conditions instructions accordingly | New sub-task under Task 17 |

### New Gate D artifacts

- `plants/plant4/profile.yaml` — adds `language: es`, `location: { city: Monterrey, state: NL, country: MX }`
- `templates/plant_template/profile.yaml.j2` — accepts `{{ language }}` (default `en`)
- `scripts/generate_plant_content.py` — accepts `--language` flag, threads it into LLM prompts
- `tests/test_plant4_agent_responds_in_spanish.py` — smoke check: dispatch Plant 4 maintenance agent, assert reply contains Spanish-language tokens (e.g., `mantenimiento`, `programa`, or simply `language == "es"` detected via langid)

### Out of scope (deliberate)

- UI language toggle, RTL support, locale number formatting, English↔Spanish KB cross-references, translating Plant 7. The single demo beat is *"watch the same code answer in Spanish from Monterrey while the manager composes everything in English for leadership."*

### Cost estimate

- ~2 extra hours: profile field plumbing, generator prompt parameterization, validator language-awareness, one new test.
- Zero impact on existing Plant 7 tests (Plant 7 keeps `language: en` implicit / default).

## Sign-off request

Gate D may proceed only after explicit user approval. Specifically requesting:

1. **Confirm Blocking drift fixes** — six roles (not five), per-plant SQL tables (option a), explicit catalog counts in tests.
2. **Confirm Scope addendum (Option A)** — Spanish narrative, English schema, `language: es` profile field, one new test.
3. **Approve to start Task 2** — *"Map Plant 7 template responsibilities"* — once approved, the next deliverable is `docs/specs/gate-d-template-map.md`.

Reply with explicit approval (e.g. `Approved to start Gate D`) before any
template, script, or Plant 4 file is created.
