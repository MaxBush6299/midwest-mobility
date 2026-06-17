# Gate C pre-review

Mandatory pre-flight before any Gate C implementation work, per the multi-gate
review convention. Compares Gate B's actual delivered surface against what the
Gate C plan (`docs/plans/2026-06-16-gate-c-polish.md`) assumes, and records the
plan adjustments needed.

## Inputs reviewed

- **Gate B status doc:** `docs/specs/gate-b-status.md` — live-verified
  (2026-06-17), commit `2289226`.
- **Git baseline:** 34 task commits from Gate A through `2289226`; current
  branch `gate-a-thin-slice` (Gate B work landed on the same branch — see
  Decision below).
- **Tree inspection:** `src/`, `infra/`, `agents/` enumerated; matches Gate A/B
  expectations with no orphan files.
- **Code spot checks:**
  - `src/mmc_agents/registry/local_catalog.py` — `LocalCatalogSource` +
    `WatchedLocalCatalogSource` present.
  - `src/mmc_agents/orchestrator/manager.py` — `ScenarioRun` dataclass +
    `run_and_capture` exist; track `hops`, `backtracks`, `last_progress_ledger`,
    and final synthesis.

## Drift table

| Area | Gate C plan expected | Gate B actual | Plan adjustment |
|---|---|---|---|
| Catalog | 10 agents (5 plant + 5 enterprise) | `agents/catalog.json` includes the full 10 | None |
| Manager | `run()` / `run_and_capture()` as the entry point | `run_and_capture` returns `ScenarioRun(hops, backtracks, plan_text, last_progress_ledger, synthesis)` | Gate C `run_stream()` must emit events whose aggregate matches the existing `ScenarioRun` fields so `run_and_capture` can be re-implemented as a thin collector over `run_stream` without breaking existing tests |
| Per-agent reply text | Trace UI shows per-agent prompts and replies | `ScenarioRun` captures hops + final synthesis only — per-turn message bodies are not retained today | `TraceEvent.agent_response` events MUST carry the per-turn message text from the Magentic stream; this is the gap the demo UI is meant to close |
| Registry | `WatchedLocalCatalogSource` for hot-add | Present and used by tests | None |
| Foundry projects | Single Foundry project assumption in early plan text | **Two** projects live: `mmc-plant` and `mmc-enterprise`, each with its own KB connection (`kb-kb-plant7-c63vl`, `kb-kb-enterprise-i4uol`) | `governance/infra_metadata.json` must namespace identities and KB-connection IDs by project; `blast_radius.py` must surface project boundary in the overlay; identity Bicep must take a project parameter (or deploy twice) |
| KB scope | One plant KB | Two KBs: `kb-plant7` (5 sources) on `srch-mmc-plant`, `kb-enterprise` (5 sources / 31 docs) on `srch-mmc-enterprise` | `governance/kb_metadata.json` must list both KBs and all 10 sources; per-agent readable-source mapping needs the enterprise tier added |
| Search RBAC chain | Not modeled | Both Search MIs (`srch-mmc-plant`, `srch-mmc-enterprise`) hold `Cognitive Services User` + `Foundry User` on `mmcfdy` — required for KB→LLM reasoning | Blast-radius overlay should include the Search MI → Foundry leg so the demo can show "revoke this role and the KB stops answering." Add a `kb_reasoning` edge type. |
| KB connection provisioning | Bicep / script automated | Manual portal step (Gate B explicitly defers) | Keep automated KB-connection provisioning out of Gate C scope (matches Gate B status §Deferred). Document the manual step in `docs/demo/run-of-show.md`. |
| Scenarios | `brake_caliper` Gate B scenario | `brake_caliper` + `loto_cluster` both live and passing | UI scenario picker must list both; default to brake-caliper for the run-of-show. |
| Manager deployment | `FOUNDRY_MODEL_DEPLOYMENT` (shared) | Split: `FOUNDRY_MANAGER_DEPLOYMENT=gpt-5.4` + `FOUNDRY_MODEL_DEPLOYMENT=gpt-5.4-mini`; 429 risk noted on manager | `docs/demo/run-of-show.md` must include the "request quota bump on `gpt-5.4` in eastus before any live demo" pre-flight item. |
| Infra | `infra/bicep/agent-identities.bicep` sub-deployment | Not yet created (Gate C work) | Add; must NOT mutate Gate A `main.bicep`. Identity Bicep should accept a `foundryProjectId` param and be deployed once per project. |
| Restricted source / auditor agent | Created in Gate C for sensitivity demo | Not yet present | Confirmed in scope; create as part of Task 16/17 (per plan). |
| Branch hygiene | Gate-b branch, then merge | Gate B work landed on `gate-a-thin-slice`; no `gate-b` tag/branch | Tag `gate-b` at `2289226` so the Gate C plan's `git log gate-b..HEAD` step works. (Done as part of this checkpoint — see Decision.) |

## Decision

Gate C may proceed only after user sign-off.

**Recommended adjustments to lock in before Task 2:**

1. Tag the current `HEAD` as `gate-b` so the plan's diff anchors resolve.
2. When implementing `TraceEvent` (Task 2), include `agent_response.content`
   as a first-class field — that is the single biggest visible improvement
   over what `ScenarioRun` exposes today.
3. When implementing `run_stream` (Task 3), refactor `run_and_capture` to be
   a thin `async for event in run_stream(...)` consumer so we have one source
   of truth and existing tests keep passing.
4. Governance metadata schema (Tasks 13–15) must be project-aware: each agent
   carries `foundry_project` (`mmc-plant` | `mmc-enterprise`), each KB carries
   its parent Search service, and each role assignment carries its scope.
5. Run-of-show (Task 22) must include the `gpt-5.4` quota pre-flight and the
   manual Foundry IQ KB-connection portal note.

No tasks in the existing plan need to be **removed**. The above are
augmentations only.

Sign-off: **pending — awaiting user**.
