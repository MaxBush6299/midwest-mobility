# Gate B pre-review — 2026-06-17

## Inputs reviewed

- `docs/specs/gate-a-status.md` (refreshed 2026-06-16, commit `544c1c5`)
- `docs/plans/2026-06-16-gate-a-thin-slice.md`
- `docs/plans/2026-06-16-gate-b-full-network.md` (re-aligned 2026-06-16, commit `3ccbe56`)
- `git log gate-a..HEAD` — 6 commits since the Gate A tag
- Current tree under `src/mmc_agents/`, `scripts/`, `enterprise/`, `plants/plant7/`

## Gate A actual state

### Working
- **Infra:** `rg-magentictest` with 2 Foundry projects (`mmc-plant`, `mmc-enterprise`) on the new Foundry Agent Service, 2 Azure AI Search instances, storage, project→Search Entra connections, MI RBAC.
- **Knowledge:** Foundry IQ KB `kb-plant7` seeded with 22 docs across 3 sources. `scripts/verify_kb_retrieval.py` confirms semantic retrieval (rerank 2.14–2.25).
- **Agents:** 5 Plant 7 portal-managed prompt agents (`plant7-ehs`, `plant7-maintenance`, `plant7-quality`, `plant7-shiftops`, `plant7-training`) on `gpt-5.4-mini` via `azure-ai-projects 2.2` `AIProjectClient.agents.create_version()` with `PromptAgentDefinition`. KB MCP tool baked into every version by `agent_factory.py` (commit `4410884`).
- **Orchestration:** `MagenticBuilder` + `StandardMagenticManager` coordinating the 5 FoundryAgent participants. Manager runs on its own `FOUNDRY_MANAGER_DEPLOYMENT=gpt-5.4` deployment to avoid TPM contention with agents on `gpt-5.4-mini`. Final synthesis arrives as `WorkflowEvent(type='output')` with `data=AgentResponse`.
- **Tracing:** `azure-monitor-opentelemetry` + Agent Framework instrumentation; spans grouped under `magentic.scenario.<plant_id>` parent span in `mmc-plant-appinsights-5430`.
- **Demo runner:** `scripts/run_scenario.py` brake-caliper scenario passes live, writes per-agent answers + manager synthesis to `scenario_out.txt`.
- **Supply Chain stub:** In-process `@tool` functions backed by deterministic CSV-derived fixtures + hand-authored A2A card.
- **Tests:** 10 unit + 2 live tests pass.

### Deferred to Gate B
- 4 remaining enterprise nodes (procurement, engineering/PLM, enterprise-quality, demand-program) as portal-managed agents on `mmc-enterprise`.
- Full enterprise content generation for all 5 enterprise nodes (only supply-chain seed exists).
- Safety/LOTO scenario + cross-link validators.
- Migrate supply-chain stub from in-process tools to portal-managed agent.

### Deferred to Gate D
- Plants 1–6 cloning from Plant 7 profile.

### Drift from Gate B plan (already addressed in commit `3ccbe56`)
- Plan now references the real Magentic API (`MagenticBuilder`/`StandardMagenticManager`), `WorkflowEvent(type='output')` synthesis path, KB MCP wiring through `azure-ai-projects 2.2`, and the dual-deployment guidance.
- **No further drift observed** between the refreshed plan and the actual Gate A code.

### Remaining `TODO(verify-on-Learn)` markers (Task 2 inputs)
- `infra/bicep/modules/foundry-iq-kb.bicep:6` — KB resource type vs. data-plane-only fallback.
- `infra/bicep/README.md:40` — narrative reference to the marker policy.
- `src/mmc_agents/tools/erp.py:7` — `from agent_framework import tool` import path.
- `src/mmc_agents/tools/supplier.py:5` — same `@tool` import.

(The previously-flagged marker in `kb_client.py` is gone — that file no longer exists; KB MCP wiring lives in `agent_factory.py` now.)

## Gate B plan adjustments

The Gate B plan was already refreshed yesterday (`3ccbe56`) to reflect the actual Gate A API surface. After re-reading both, the only minor follow-ups for Task 2 are:

1. **Marker list** in Task 2 should drop `kb_client.py` (file does not exist). The 4 markers above are the real targets.
2. **No other adjustments required.** The 33-task structure (content → TDD → agents → integration → smoke) still matches reality.

## Sign-off checkpoint

Gate B implementation pauses here. Please review and approve `docs/specs/gate-b-pre-review.md` before Task 2 (Learn-marker cleanup) starts.
