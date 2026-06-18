# Gate C — Status

**Status**: ✅ Complete
**Branch**: `gate-a-thin-slice` (Gate C landed on the same branch as A/B).
**Test count at close**: 104 passed · 4 skipped.

## What Gate C shipped

| Task                                  | Deliverable                                                                                          | Citation                                                            |
|---------------------------------------|------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| Trace UI markdown synthesis           | `marked@12` rendering + citation-glyph stripping in the synthesis pane only                          | `src/mmc_agents/trace_ui/static/index.html`                          |
| Manager prompt broadening             | Accepts "could not find", "not available in my KB", etc. as terminal — no more max-rounds replan loops | `src/mmc_agents/orchestrator/manager.py`, `tests/test_manager_hardening.py` |
| t06 — Governance metadata             | `governance/kb_metadata.json` (12 sources, 11 agents), `governance/infra_metadata.json` (Foundry account + 2 projects + 2 Search + SQL with full RBAC), Pydantic loaders | `src/mmc_agents/governance/metadata.py`, `tests/test_governance.py` |
| t07 — Blast-radius computation        | Pure-function `compute_blast_radius`, snapshot generator, snapshot-freshness test                    | `src/mmc_agents/governance/blast_radius.py`, `scripts/generate_blast_radius.py` |
| t08 — Blast-radius UI overlay         | Clickable agent rows, centered modal with color-coded edges + 🔒 revocation call-outs, Esc/backdrop close | `src/mmc_agents/trace_ui/static/index.html`, `src/mmc_agents/trace_ui/app.py` |
| t09 — Restricted EHS source + external-auditor | Confidential brief in `02_EHS_Internal_Restricted/`, new `external-auditor` role mapped to ONLY `ehs` source (per-agent readable-sources demo) | `plants/plant7/profile.yaml`, `governance/kb_metadata.json`, `tests/test_governance.py::test_external_auditor_blast_radius_omits_restricted_source` |
| t10 — Hot-add agent moment            | `POST /demo/hot-add` + `/reset`, shadow catalog allow-list, UI button + reset + dashed-amber styling, runbook | `src/mmc_agents/trace_ui/app.py`, `static/index.html`, `docs/demo/hot-add-runbook.md` |
| t11 — Identity Bicep                  | `infra/bicep/modules/agent-identities.bicep` + `parameters/agent-identities.bicepparam` (per-agent UAMI, stand-alone deployment, does not touch main.bicep) | `infra/bicep/modules/agent-identities.bicep` |
| t12 — Run-of-show + this status doc   | Full pre-flight + 7-act script + fallback plans                                                      | `docs/demo/run-of-show.md`                                          |

## Test posture

- **Snapshot freshness** test (`test_generated_blast_radius_json_matches_current_metadata`) ensures `governance/blast_radius.json` matches live `compute_all_blast_radii()` output — catches "I edited the YAML but forgot to re-run the generator."
- **Sensitivity boundary** test (`test_external_auditor_blast_radius_omits_restricted_source`) locks in the demo's whole point: the auditor sees `ehs` only, never `ehs_restricted` or `incident_data`.
- **Docs-only carve-out** test (`test_blast_radius_for_docs_only_agent_omits_sql_chain`) prevents the overlay from lying about SQL access for agents whose sources are all documents.
- **Hot-add** tests cover all three branches: already-persisted reject, outside-shadow-catalog reject, happy-path add → list → reset.

## Deferred / out of scope

- **Foundry IQ KB connection** is still a manual portal step (carried from Gate B). Documented in `docs/demo/run-of-show.md` pre-flight.
- **Per-agent UAMI → Foundry agent wiring** is not yet automated. The Bicep provisions the identities; assigning them to specific Foundry agents (and granting them the right Search/SQL roles) is a Gate D candidate.
- **Cleanup**: redundant Reader role assignments on the SQL server scope. Contributor is sufficient (see Gate C pivot notes in `plan.md`).

## What this enables for Gate D / live demo

- Operators can rehearse the full 25-min show from `docs/demo/run-of-show.md` end-to-end with no additional engineering.
- Governance team has a defensible answer to "how do I know what each agent can read?" — the overlay is computed from the same JSON the deployment uses, so drift is impossible without a failing test.
- Adding a new agent is: edit `plants/<plant>/profile.yaml` → edit `governance/kb_metadata.json` → `python scripts/generate_blast_radius.py` → CI proves no surprise blast radius.
