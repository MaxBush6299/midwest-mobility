# Gate B status — 2026-06-16

**Working:** Full 10-agent pool is discoverable in `agents/catalog.json` (5 Plant 7 + 5 enterprise). All 5 enterprise nodes (supply-chain, procurement, engineering-plm, enterprise-quality, demand-program) have CSV data, narrative `kb/` docs, deterministically derived fixtures, and KB-source layouts ready for Foundry IQ seeding. Plant 7 has CAPA, CMMS, QMS, SCADA, MES, and LMS fixture-backed tool seams in addition to the Gate A trio. The Magentic manager (`StandardMagenticManager` over `MagenticBuilder`) is hardened with: a `ScenarioRun` capture for hops / backtracks / plan / progress ledger / synthesis (`run_and_capture`); a `NO_DIRECT_ALT_RULE` appended to its instructions so it backtracks off supply-chain dead-ends; `summarize_scenario_run()` surfacing partial state when `max_round_count` fires; and Gate B EXPECTED_BOUNDS for the brake-caliper scenario (5 distinct agents, ≥1 backtrack, NO_DIRECT_ALT + BRK-CAL-XYZ evidence). A second scenario (`loto_cluster`) composes a distinct flow across EHS, maintenance, training, and quality/enterprise exposure on the Plant 7 LOTO near-miss cluster (INC-062/063/064, CAPA-062/063/064). The enterprise factory (`emit_enterprise_agent_card` + `_enterprise_kb_tool`) emits prompt-agent cards from `enterprise/profile.yaml` so all 10 cards refresh from one source of truth, and `seed_foundry_iq.py --enterprise [--source]` uploads all 5 sources into a single `kb-enterprise` KB with `KnowledgeRetrievalMinimalReasoningEffort()`.

**Verification:**
- `pytest -v` — 65 passed, 4 skipped (live smokes + 1 conditional)
- `az bicep build --file infra\bicep\main.bicep` — PASS
- `python scripts\validate_naming.py enterprise\supply-chain\kb enterprise\procurement\kb enterprise\engineering-plm\kb enterprise\enterprise-quality\kb enterprise\demand-program\kb` — PASS (exit 0)
- `python scripts\derive_fixtures.py --node all` — 16 fixtures derived; `--plant plant7` — 6 fixtures; no diff after re-derive
- `MMC_LIVE=1 pytest tests\test_brake_caliper_smoke.py tests\test_loto_cluster_smoke.py -v -s` — deferred: requires `seed_foundry_iq.py --enterprise` against deployed Search + manual Foundry IQ KB connection wiring (per user direction, KB connection is created in portal after the KB exists and the 10 prompt agents are registered).

**Demo notes:**
- Brake-caliper trigger: `BRK-CAL-XYZ` / `SUP-001` / `NO_DIRECT_ALT`. The BOM row carries `Alt_Source_Status=NO_DIRECT_ALT` and `supplier.alternates()` returns a sentinel that the manager must observe and backtrack from supply-chain into procurement / PLM / demand.
- LOTO trigger: 3 L1 Press near-misses in 60 days with open CAPAs (INC-062 → CAPA-062, INC-063 → CAPA-063, INC-064 → CAPA-064). LOTO-L1 course attendance in `lms.csv` lets the training agent identify qualified-vs-scheduled employees.
- Foundry portal threads show KB citations and Magentic progress-ledger / replan events; `run_and_capture` exposes them programmatically for tests and any future UI overlay.

**Deferred to Gate C:** custom trace UI, hot-add visual choreography, governance overlay / Entra Agent ID blast-radius view, automated Foundry IQ KB-connection provisioning.
