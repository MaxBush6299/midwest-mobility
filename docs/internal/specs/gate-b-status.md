# Gate B status — 2026-06-17 (live-verified)

**Working:** Full 10-agent pool is discoverable in `agents/catalog.json` (5 Plant 7 + 5 enterprise) **and live on Foundry** (`mmc-plant` + `mmc-enterprise` projects, all as portal-managed prompt agents with KB MCP tools baked in). All 5 enterprise nodes (supply-chain, procurement, engineering-plm, enterprise-quality, demand-program) have CSV data, narrative `kb/` docs, deterministically derived fixtures, and KB-source layouts, plus the live `kb-enterprise` Foundry IQ knowledge base on `srch-mmc-enterprise` (5 knowledge sources, 31 docs). Plant 7 has CAPA, CMMS, QMS, SCADA, MES, and LMS fixture-backed tool seams in addition to the Gate A trio. The Magentic manager (`StandardMagenticManager` over `MagenticBuilder`) is hardened with: a `ScenarioRun` capture for hops / backtracks / plan / progress ledger / synthesis (`run_and_capture`); a `NO_DIRECT_ALT_RULE` appended to its instructions as a safety net; `summarize_scenario_run()` surfacing partial state when `max_round_count` fires; and Gate B EXPECTED_BOUNDS for the brake-caliper scenario (5 distinct agents, NO_DIRECT_ALT-aware planning, BRK-CAL-XYZ evidence). A second scenario (`loto_cluster`) composes a distinct flow across EHS, maintenance, training, and quality/enterprise exposure on the Plant 7 LOTO near-miss cluster (INC-062/063/064, CAPA-062/063/064). The enterprise factory (`emit_enterprise_agent_card`, `upsert_enterprise_agents`, `build_enterprise_agents`, `_enterprise_kb_tool`) emits prompt-agent cards from `enterprise/profile.yaml`, provisions all 5 prompt agents on the enterprise project (with KB MCP attached when env vars are set), and exposes a participant builder so the orchestrator and live tests combine plant + enterprise pools. `seed_foundry_iq.py --enterprise [--source]` uploads all 5 sources into a single `kb-enterprise` KB with `KnowledgeRetrievalMinimalReasoningEffort()`. Both Search services (`srch-mmc-plant`, `srch-mmc-enterprise`) have SystemAssigned managed identities with `Cognitive Services User` + `Foundry User` on `mmcfdy` so KB→model reasoning calls authenticate per current Microsoft Learn guidance.

**Verification:**
- `pytest -v` — 65 passed, 4 skipped
- `az bicep build --file infra\bicep\main.bicep` — PASS
- `python scripts\validate_naming.py enterprise\supply-chain\kb enterprise\procurement\kb enterprise\engineering-plm\kb enterprise\enterprise-quality\kb enterprise\demand-program\kb` — PASS (exit 0)
- `python scripts\derive_fixtures.py --node all` — 16 fixtures derived; `--plant plant7` — 6 fixtures; no diff after re-derive
- `python scripts\upsert_enterprise.py` — provisions 5 enterprise prompt agents on `mmc-enterprise` (idempotent; new version per run; KB MCP tool attached when `ENTERPRISE_KB_CONNECTION_ID` / `ENTERPRISE_KB_MCP_URL` set)
- `python scripts\seed_foundry_iq.py --enterprise` — creates `kb-enterprise` with 5 sources (31 docs)
- `MMC_LIVE=1 pytest tests\test_brake_caliper_smoke.py -v -s` — **PASS** (2:09; 40 hops across all 10 agents; KB-grounded synthesis citing BRK-CAL-XYZ, SUP-001, EV-BRK-26, $8,880 expedite cost)
- `MMC_LIVE=1 pytest tests\test_loto_cluster_smoke.py -v -s` — **PASS** (2:59; 40 hops across all 10 agents; LOTO/L1/CAPA evidence in synthesis)

**Demo notes:**
- Brake-caliper trigger: `BRK-CAL-XYZ` / `SUP-001` / `NO_DIRECT_ALT`. The BOM row carries `Alt_Source_Status=NO_DIRECT_ALT` and `supplier.alternates()` returns a sentinel. With the full 10-agent pool the manager plans correctly upfront — it puts ent-supply-chain in the initial plan, observes NO_DIRECT_ALT on the first turn, and fans out to procurement / PLM / demand without needing a formal `REPLANNED` event. The `NO_DIRECT_ALT_RULE` in the manager instructions remains as a safety net for mid-flow dead-ends.
- LOTO trigger: 3 L1 Press near-misses in 60 days with open CAPAs (INC-062 → CAPA-062, INC-063 → CAPA-063, INC-064 → CAPA-064). LOTO-L1 course attendance in `lms.csv` lets the training agent identify qualified-vs-scheduled employees.
- Foundry portal threads show KB citations and Magentic progress-ledger / replan events; `run_and_capture` exposes them programmatically for tests and any future UI overlay.

**RBAC requirements (live-verified 2026-06-17):**
- `srch-mmc-plant` SystemAssigned MI → `Cognitive Services User` + `Foundry User` on `mmcfdy` (required for KB→LLM reasoning call per Learn: agentic-retrieval-how-to-create-knowledge-base)
- `srch-mmc-enterprise` SystemAssigned MI → same two roles on `mmcfdy`
- `mmcfdy` SystemAssigned MI → `Cognitive Services OpenAI User` on `mmcfdy` (self, for Foundry IQ KB connection's `ProjectManagedIdentity` auth)

**Known follow-up (not blocking Gate B):**
- `gpt-5.4` (manager deployment) hit a 429 in the first live run before the 10-agent pool was wired. After wiring the full pool the manager plans more efficiently (40 hops vs 45 + reset loop) and the issue did not recur. A quota bump in eastus is still recommended before Gate C demos.

**Deferred to Gate C:** custom trace UI, hot-add visual choreography, governance overlay / Entra Agent ID blast-radius view, automated Foundry IQ KB-connection provisioning (today's wiring is manual portal step).
