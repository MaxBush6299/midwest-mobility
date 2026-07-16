# Gate C — Polished Demo Surface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the polished Gate C demo surface: a custom web trace UI, a hot-add agent moment, and an Entra Agent ID governance overlay with blast-radius and sensitivity proof.

**Architecture:** Gate C builds on Gate B's full 10-agent catalog and Magentic manager. The manager emits typed `TraceEvent` objects through `run_stream`; FastAPI starts runs, fans events into per-run queues, exposes SSE, and serves one static vanilla-JS trace UI. Governance is a regenerable overlay: Bicep provisions one user-assigned identity per agent, `blast_radius.py` derives per-agent scope JSON from registry + KB + infra metadata, and the trace UI renders the result.

**Tech Stack:** Python 3.11+, Microsoft Agent Framework SDK, FastAPI, Server-Sent Events, vanilla HTML/CSS/JavaScript, Pydantic v2, pytest, pytest-asyncio, httpx, Bicep, Azure CLI.

**Reference docs (read these before starting):**
- `docs/specs/2026-06-16-mmc-agent-network-implementation-design.md` — decisions D3, §5 trace emission, §11 governance overlay, Gate C description.
- `DEMO_BUILD_HANDOFF.md` — Phase 5 hot-add choreography and Phase 6 governance.
- `docs/plans/2026-06-16-gate-a-thin-slice.md` — conventions, file layout, registry design, `WatchedLocalCatalogSource`, commit cadence, and TDD style.
- `docs/specs/gate-b-status.md` — mandatory Gate B drift input; Task 1 blocks further work until reviewed.
- `docs/MMC_Plant7_Company_Profile_v1.md` — source of truth for Plant 7 naming and synthetic restricted incident content.

**Verify against Microsoft Learn before coding Azure-specific work:** Entra Agent ID / user-assigned identity pattern, RBAC scopes for Foundry IQ / Search / Storage resources, Agent Framework Magentic streaming APIs, and Foundry Agent Service identity-binding commands.

---

## File Structure

**Repo additions / modifications for Gate C:**

| Path | Responsibility |
|---|---|
| `docs/specs/gate-c-pre-review.md` | Mandatory Gate B review notes and task adjustments; user sign-off gate before Task 2. |
| `src/mmc_agents/orchestrator/trace.py` | Typed `TraceEvent` model and event-type literals shared by manager, backend, tests, and UI. |
| `src/mmc_agents/orchestrator/manager.py` | Add `run_stream(problem_statement) -> AsyncIterator[TraceEvent]`; keep existing `run()` as a collecting wrapper. |
| `tests/test_trace_events.py` | Model serialization and canned fake-manager trace tests. |
| `tests/test_manager_run_stream.py` | Streaming order, hop, ledger, backtrack, and final-result compatibility tests. |
| `src/mmc_agents/trace_ui/__init__.py` | Package marker for trace UI module. |
| `src/mmc_agents/trace_ui/app.py` | FastAPI app with `/runs`, `/runs/{run_id}/events`, `/agents`, `/agents/{name}/blast-radius`, `/demo/hot-add`, static UI mount. |
| `src/mmc_agents/trace_ui/runtime.py` | `RunStore` and queue fan-out for background manager runs. |
| `src/mmc_agents/trace_ui/schemas.py` | Request / response models for run creation, agent list, hot-add, blast-radius. |
| `src/mmc_agents/trace_ui/static/index.html` | Single-file vanilla JS demo UI using `fetch` + `EventSource`; no frontend build step. |
| `tests/test_trace_ui_app.py` | Async HTTP tests for run creation, SSE stream, agent list, blast-radius, hot-add endpoint. |
| `src/mmc_agents/governance/__init__.py` | Governance package marker. |
| `src/mmc_agents/governance/blast_radius.py` | Computes callers/callees/readable KB sources/writable tools from registry and metadata. |
| `src/mmc_agents/governance/metadata.py` | Loads `governance/kb_metadata.json` and `governance/infra_metadata.json`. |
| `governance/kb_metadata.json` | Regenerable source-scope metadata for Plant 7, restricted source, and enterprise KB sources. |
| `governance/infra_metadata.json` | Regenerable mapping from agents to managed identities and role-assignment scopes. |
| `governance/blast_radius.json` | Committed computed blast-radius output used by demo UI. |
| `scripts/generate_blast_radius.py` | Regenerates `governance/blast_radius.json` from catalog + metadata. |
| `infra/bicep/modules/identity.bicep` | Creates one user-assigned managed identity per agent and scoped role assignments. |
| `infra/bicep/agent-identities.bicep` | Separate Gate C identity sub-deployment; does not mutate Gate A main deployment. |
| `infra/bicep/parameters/agent-identities.dev.bicepparam` | Dev parameters for the identity sub-deployment. |
| `plants/plant7/kb/02_EHS_Internal_Restricted/MMC_P7_Confidential_Incident.md` | Synthetic restricted source used only for the sensitivity demo. |
| `plants/plant7/agents/plant7-external-auditor.agent.json` | Deliberately less-privileged caller; not scoped to the restricted source. |
| `docs/demo/hot-add-runbook.md` | Exact operator steps for the hot-add demo moment. |
| `docs/demo/run-of-show.md` | Minute-by-minute polished demo script. |
| `scripts/capture_trace_ui_screenshots.py` | Optional Playwright screenshot helper; skips gracefully if Playwright is absent. |
| `docs/specs/gate-c-status.md` | Final Gate C status checkpoint and tag instructions. |

---
## Task 1: Gate B review and drift checkpoint
**Files:**
- Create: `docs/specs/gate-c-pre-review.md`
- Read: `docs/specs/gate-b-status.md`, actual tree, and git log
- No code changes outside the review document
- [ ] **Step 1: Read Gate B status**
Run: `if (Test-Path docs\specs\gate-b-status.md) { Get-Content docs\specs\gate-b-status.md -TotalCount 200 } else { Write-Output 'MISSING: docs\specs\gate-b-status.md' }`
Expected: Either the Gate B status is printed or the missing file is recorded.
- [ ] **Step 2: Inspect commits**
Run: `if (git rev-parse --verify gate-b 2>$null) { git --no-pager log gate-b..HEAD --oneline } elseif (git rev-parse --verify gate-a 2>$null) { git --no-pager log gate-a..HEAD --oneline } else { git --no-pager log --oneline -n 20 }`
Expected: A concise commit baseline is available.
- [ ] **Step 3: Inspect tree**
Run: `Get-ChildItem -Recurse -File | Where-Object { $_.FullName -notmatch '\.git|\.venv|__pycache__' } | Select-Object -ExpandProperty FullName | Sort-Object`
Expected: Tree reveals actual Gate B outputs.
- [ ] **Step 4: Write review doc**
Run: `Set-Content docs\specs\gate-c-pre-review.md @'
# Gate C pre-review

## Inputs reviewed
- Gate B status: present / missing
- Git comparison: gate-b..HEAD / gate-a..HEAD / fallback
- File tree inspected: yes

## Drift table
| Area | Expected | Actual | Plan adjustment |
|---|---|---|---|
| Catalog | 10 agents | | |
| Manager | run entry point | | |
| Registry | WatchedLocalCatalogSource | | |
| Infra | bicep tree | | |

## Decision
Gate C may proceed only after user sign-off.

Sign-off: pending
'@`
Expected: Review doc exists and records drift.
- [ ] **Step 5: Commit**
Run: `git add docs/specs/gate-c-pre-review.md; git commit -m "docs: Gate C pre-review checkpoint"`
Expected: Commit succeeds. Stop for user sign-off before Task 2.
---
## Task 2: TraceEvent typed model (TDD)
**Files:**
- Create: `src/mmc_agents/orchestrator/trace.py`
- Create: `tests/test_trace_events.py`
- [ ] **Step 1: Write the failing test or executable artifact**
```python
# tests/test_trace_events.py
from mmc_agents.orchestrator.trace import TraceEvent


def test_trace_event_defaults_are_serializable():
    event = TraceEvent(run_id="run-1", type="start", sequence=0, message="begin")
    payload = event.model_dump(mode="json")
    assert payload["type"] == "start"
    assert payload["sequence"] == 0
    assert payload["agent_name"] is None


def test_trace_event_accepts_ledgers():
    event = TraceEvent(run_id="run-2", type="ledger_update", sequence=3, message="updated", task_ledger={"facts": ["L1"]})
    assert event.task_ledger == {"facts": ["L1"]}
```
Run: `pytest tests/test_trace_events.py -v`
Expected: FAIL first because the implementation is not present; after implementation this same command passes.
- [ ] **Step 2: Implement the minimal production change**
```python
# src/mmc_agents/orchestrator/trace.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field

TraceEventType = Literal["start","agent_call","agent_response","ledger_update","backtrack","complete"]
class TraceEvent(BaseModel):
    run_id: str
    type: TraceEventType
    sequence: int = Field(ge=0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message: str
    agent_name: str | None = None
    task_ledger: dict[str, Any] | None = None
    progress_ledger: dict[str, Any] | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    def sse_payload(self) -> str:
        return self.model_dump_json() + "\n"
```
- [ ] **Step 3: Run the targeted verification**
Run: `pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add src/mmc_agents/orchestrator/trace.py tests/test_trace_events.py
git commit -m "feat(trace): add typed TraceEvent model"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 3: Fake streaming manager contract (TDD)
**Files:**
- Create: `tests/test_manager_run_stream_contract.py`
- [ ] **Step 1: Write the failing test or executable artifact**
```python
# tests/test_manager_run_stream_contract.py
import pytest
from mmc_agents.orchestrator.trace import TraceEvent


class FakeStreamingManager:
    async def run_stream(self, problem_statement):
        yield TraceEvent(run_id="fake", type="start", sequence=0, message=problem_statement)
        yield TraceEvent(run_id="fake", type="complete", sequence=1, message="done", data={"answer": "ok"})


@pytest.mark.asyncio
async def test_consumer_captures_canned_trace_sequence():
    events = [event async for event in FakeStreamingManager().run_stream("problem")]
    assert [event.type for event in events] == ["start", "complete"]
    assert events[-1].data["answer"] == "ok"
```
Run: `pytest tests/test_gate_c_example.py -v`
Expected: FAIL first because the implementation is not present; after implementation this same command passes.
- [ ] **Step 2: Implement the minimal production change**
```text
Create `FakeStreamingManager` in the test with an async `run_stream` generator yielding start and complete events so backend consumers have a stable contract.
```
- [ ] **Step 3: Run the targeted verification**
Run: `pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add tests/test_manager_run_stream_contract.py
git commit -m "test(trace): lock run_stream consumer contract"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 4: MmcMagenticManager emits start and complete events (TDD)
**Files:**
- Modify: `src/mmc_agents/orchestrator/manager.py`
- Create: `tests/test_manager_run_stream.py`
- [ ] **Step 1: Write the failing test or executable artifact**
```python
# tests/test_manager_run_stream.py
import pytest
from mmc_agents.orchestrator.manager import MmcMagenticManager


class StubRegistry:
    def list_agents(self): return []


class StubChatClient: pass


@pytest.mark.asyncio
async def test_run_stream_emits_start_and_complete_for_empty_registry():
    manager = MmcMagenticManager(registry=StubRegistry(), chat_client=StubChatClient(), max_steps=0)
    events = [event async for event in manager.run_stream("What happened on L1?")]
    assert events[0].type == "start"
    assert events[-1].type == "complete"
    assert [e.sequence for e in events] == list(range(len(events)))
```
Run: `pytest tests/test_manager_run_stream.py -v`
Expected: FAIL first because the implementation is not present; after implementation this same command passes.
- [ ] **Step 2: Implement the minimal production change**
```text
Add `run_stream` to `MmcMagenticManager`; emit a start event before any registry work and a complete event when max steps or normal completion ends the run.
```
- [ ] **Step 3: Run the targeted verification**
Run: `pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add src/mmc_agents/orchestrator/manager.py tests/test_manager_run_stream.py
git commit -m "feat(orchestrator): stream start and complete trace events"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 5: MmcMagenticManager emits agent hop ledger and backtrack events (TDD)
**Files:**
- Modify: `src/mmc_agents/orchestrator/manager.py`
- Modify: `tests/test_manager_run_stream.py`
- [ ] **Step 1: Write the failing test or executable artifact**
```python
# tests/test_manager_run_stream.py
import pytest
from mmc_agents.orchestrator.manager import MmcMagenticManager


@pytest.mark.asyncio
async def test_run_stream_emits_hop_ledger_and_backtrack(monkeypatch):
    manager = MmcMagenticManager(registry=ScriptedRegistry(), chat_client=StubChatClient(), max_steps=2)
    async def fake_steps(problem_statement, agents):
        yield ("agent_call", "plant7-ehs", {"query": "cluster incidents"})
        yield ("agent_response", "plant7-ehs", {"summary": "repeat cause"})
        yield ("ledger_update", None, {"task_ledger": {"facts": ["repeat cause"]}})
        yield ("backtrack", None, {"reason": "need maintenance context"})
    monkeypatch.setattr(manager, "_iter_magentic_steps", fake_steps)
    events = [event async for event in manager.run_stream("LOTO cluster")]
    assert {"agent_call", "agent_response", "ledger_update", "backtrack"}.issubset({event.type for event in events})
```
Run: `pytest tests/test_manager_run_stream.py -v`
Expected: FAIL first because the implementation is not present; after implementation this same command passes.
- [ ] **Step 2: Implement the minimal production change**
```text
Move the existing Gate B Magentic loop behind `_iter_magentic_steps` and yield trace events at each agent call, response, ledger update, and backtrack decision.
```
- [ ] **Step 3: Run the targeted verification**
Run: `pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add src/mmc_agents/orchestrator/manager.py tests/test_manager_run_stream.py
git commit -m "feat(orchestrator): emit trace events for hops ledgers and backtracks"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 6: Keep run compatible by collecting run_stream (TDD)
**Files:**
- Modify: `src/mmc_agents/orchestrator/manager.py`
- Modify: `tests/test_manager_run_stream.py`
- [ ] **Step 1: Write the failing test or executable artifact**
```python
# tests/test_manager_run_stream.py
import pytest
from mmc_agents.orchestrator.trace import TraceEvent


@pytest.mark.asyncio
async def test_run_collects_stream_and_returns_final_result(monkeypatch):
    manager = MmcMagenticManager(registry=StubRegistry(), chat_client=StubChatClient(), max_steps=1)
    async def fake_stream(problem_statement):
        yield TraceEvent(run_id="r", type="start", sequence=0, message=problem_statement)
        yield TraceEvent(run_id="r", type="complete", sequence=1, message="done", data={"answer": "final"})
    monkeypatch.setattr(manager, "run_stream", fake_stream)
    result = await manager.run("problem")
    assert getattr(result, "answer", result.get("answer")) == "final"
```
Run: `pytest tests/test_manager_run_stream.py -v`
Expected: FAIL first because the implementation is not present; after implementation this same command passes.
- [ ] **Step 2: Implement the minimal production change**
```text
Refactor `run()` into a compatibility wrapper that collects `run_stream` events and returns the existing `RunResult` shape from the final complete event.
```
- [ ] **Step 3: Run the targeted verification**
Run: `pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add src/mmc_agents/orchestrator/manager.py tests/test_manager_run_stream.py
git commit -m "refactor(orchestrator): collect streamed trace events in run wrapper"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 7: Trace UI runtime queue fan-out (TDD)
**Files:**
- Create: `src/mmc_agents/trace_ui/__init__.py`
- Create: `src/mmc_agents/trace_ui/runtime.py`
- Create: `tests/test_trace_ui_runtime.py`
- [ ] **Step 1: Write the failing test or executable artifact**
```python
# tests/test_trace_ui_runtime.py
import pytest
from mmc_agents.orchestrator.trace import TraceEvent
from mmc_agents.trace_ui.runtime import RunStore


@pytest.mark.asyncio
async def test_run_store_pushes_and_streams_events_in_order():
    store = RunStore(); run_id = store.create_run_id()
    await store.publish(run_id, TraceEvent(run_id=run_id, type="start", sequence=0, message="begin"))
    await store.publish(run_id, TraceEvent(run_id=run_id, type="complete", sequence=1, message="done"))
    events = []
    async for event in store.stream(run_id):
        events.append(event)
    assert [event.type for event in events] == ["start", "complete"]
```
Run: `pytest tests/test_trace_ui_runtime.py -v`
Expected: FAIL first because the implementation is not present; after implementation this same command passes.
- [ ] **Step 2: Implement the minimal production change**
```python
# src/mmc_agents/trace_ui/runtime.py
from __future__ import annotations
import asyncio
from collections.abc import AsyncIterator
from uuid import uuid4
from mmc_agents.orchestrator.trace import TraceEvent

class RunStore:
    def __init__(self): self._queues: dict[str, asyncio.Queue[TraceEvent]] = {}
    def create_run_id(self) -> str:
        run_id=str(uuid4()); self._queues[run_id]=asyncio.Queue(); return run_id
    async def publish(self, run_id: str, event: TraceEvent) -> None:
        self._queues.setdefault(run_id, asyncio.Queue()); await self._queues[run_id].put(event)
    async def stream(self, run_id: str) -> AsyncIterator[TraceEvent]:
        if run_id not in self._queues: raise KeyError(run_id)
        while True:
            event=await self._queues[run_id].get(); yield event
            if event.type=="complete": break
```
- [ ] **Step 3: Run the targeted verification**
Run: `pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add src/mmc_agents/trace_ui/__init__.py src/mmc_agents/trace_ui/runtime.py tests/test_trace_ui_runtime.py
git commit -m "feat(trace-ui): add run event queue store"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 8: Trace UI schemas and app factory (TDD)
**Files:**
- Create: `src/mmc_agents/trace_ui/schemas.py`
- Create: `src/mmc_agents/trace_ui/app.py`
- Create: `tests/test_trace_ui_app.py`
- [ ] **Step 1: Write the failing test or executable artifact**
```python
# tests/test_trace_ui_app.py
import pytest
from httpx import ASGITransport, AsyncClient
from mmc_agents.trace_ui.app import create_app


class StubRegistry:
    def list_agents(self): return [{"name": "plant7-ehs", "display_name": "Plant 7 EHS / Safety", "skills": []}]


@pytest.mark.asyncio
async def test_get_agents_lists_catalog():
    app = create_app(registry=StubRegistry(), manager_factory=None)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/agents")
    assert response.status_code == 200
    assert response.json()["agents"][0]["name"] == "plant7-ehs"
```
Run: `pytest tests/test_trace_ui_app.py -v`
Expected: FAIL first because the implementation is not present; after implementation this same command passes.
- [ ] **Step 2: Implement the minimal production change**
```python
# src/mmc_agents/trace_ui/app.py
from fastapi import FastAPI
from mmc_agents.trace_ui.runtime import RunStore

def create_app(registry, manager_factory) -> FastAPI:
    app=FastAPI(title="MMC Agent Network Trace UI")
    app.state.registry=registry; app.state.manager_factory=manager_factory; app.state.runs=RunStore()
    @app.get("/agents")
    async def get_agents(): return {"agents": registry.list_agents()}
    return app
```
- [ ] **Step 3: Run the targeted verification**
Run: `pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add src/mmc_agents/trace_ui/schemas.py src/mmc_agents/trace_ui/app.py tests/test_trace_ui_app.py
git commit -m "feat(trace-ui): add FastAPI app factory and agent listing"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 9: Trace UI POST /runs and SSE stream (TDD)
**Files:**
- Modify: `src/mmc_agents/trace_ui/app.py`
- Modify: `tests/test_trace_ui_app.py`
- [ ] **Step 1: Write the failing test or executable artifact**
```python
# tests/test_trace_ui_app.py
from mmc_agents.orchestrator.trace import TraceEvent


class StubManager:
    async def run_stream(self, problem_statement):
        yield TraceEvent(run_id="manager", type="start", sequence=0, message=problem_statement)
        yield TraceEvent(run_id="manager", type="complete", sequence=1, message="done")


@pytest.mark.asyncio
async def test_post_runs_starts_stream_and_sse_returns_events():
    app = create_app(registry=StubRegistry(), manager_factory=lambda: StubManager())
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post("/runs", json={"problem_statement": "trace this"})
        run_id = created.json()["run_id"]
        response = await client.get(f"/runs/{run_id}/events")
    assert "event: start" in response.text
    assert "event: complete" in response.text
```
Run: `pytest tests/test_trace_ui_app.py -v`
Expected: FAIL first because the implementation is not present; after implementation this same command passes.
- [ ] **Step 2: Implement the minimal production change**
```python
# in src/mmc_agents/trace_ui/app.py
# Add POST /runs and GET /runs/{run_id}/events.
# Use asyncio.create_task(manager.run_stream(...)) and StreamingResponse(media_type="text/event-stream").
```
- [ ] **Step 3: Run the targeted verification**
Run: `pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add src/mmc_agents/trace_ui/app.py tests/test_trace_ui_app.py
git commit -m "feat(trace-ui): expose run creation and SSE events"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 10: Blast-radius model (TDD)
**Files:**
- Create: `src/mmc_agents/governance/__init__.py`
- Create: `src/mmc_agents/governance/blast_radius.py`
- Create: `tests/test_blast_radius.py`
- [ ] **Step 1: Write the failing test or executable artifact**
```python
# tests/test_blast_radius.py
from mmc_agents.governance.blast_radius import compute_blast_radius


class Registry:
    def list_agents(self): return [{"name": "plant7-ehs", "allowed_callers": ["manager"], "allowed_callees": ["plant7-maintenance"], "kb_sources": ["plant7.ehs_restricted"], "tools": ["capa"]}]


def test_compute_blast_radius_for_ehs():
    result = compute_blast_radius("plant7-ehs", Registry(), {"plant7.ehs_restricted": {"sensitivity": "confidential"}}, {"plant7-ehs": {"identity_name": "id-agent-plant7-ehs"}})
    assert result["identity"] == "id-agent-plant7-ehs"
    assert result["readable_kb_sources"][0]["sensitivity"] == "confidential"
```
Run: `pytest tests/test_blast_radius.py -v`
Expected: FAIL first because the implementation is not present; after implementation this same command passes.
- [ ] **Step 2: Implement the minimal production change**
```python
# src/mmc_agents/governance/blast_radius.py
def compute_blast_radius(agent_name, registry, kb_metadata, infra_metadata):
    card=next(c for c in registry.list_agents() if (c.get("name") or c.get("id"))==agent_name)
    return {
        "agent_name": agent_name,
        "display_name": card.get("display_name") or card.get("displayName") or agent_name,
        "identity": infra_metadata.get(agent_name, {}).get("identity_name"),
        "callers": sorted(card.get("allowed_callers", ["manager"])),
        "callees": sorted(card.get("allowed_callees", [])),
        "readable_kb_sources": [{"id": s, **kb_metadata.get(s,{})} for s in card.get("kb_sources", [])],
        "writable_tools": sorted(card.get("writable_tools", [])),
    }
```
- [ ] **Step 3: Run the targeted verification**
Run: `pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add src/mmc_agents/governance/__init__.py src/mmc_agents/governance/blast_radius.py tests/test_blast_radius.py
git commit -m "feat(governance): compute agent blast radius"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 11: Governance metadata and blast-radius export (TDD)
**Files:**
- Create: `governance/kb_metadata.json`
- Create: `governance/infra_metadata.json`
- Create: `scripts/generate_blast_radius.py`
- Create: `tests/test_generate_blast_radius.py`
- [ ] **Step 1: Write the failing test or executable artifact**
```python
# tests/test_generate_blast_radius.py
import json
from scripts.generate_blast_radius import generate


def test_generate_blast_radius_writes_all_agents(tmp_path):
    catalog = tmp_path / "catalog.json"; kb = tmp_path / "kb.json"; infra = tmp_path / "infra.json"; out = tmp_path / "out.json"
    catalog.write_text(json.dumps({"agents": [{"name": "a", "kb_sources": ["s1"], "tools": []}]}))
    kb.write_text(json.dumps({"s1": {"sensitivity": "internal"}})); infra.write_text(json.dumps({"a": {"identity_name": "id-a"}}))
    generate(catalog, kb, infra, out)
    assert json.loads(out.read_text())["agents"][0]["agent_name"] == "a"
```
Run: `pytest tests/test_generate_blast_radius.py -v`
Expected: FAIL first because the implementation is not present; after implementation this same command passes.
- [ ] **Step 2: Implement the minimal production change**
```text
Create metadata JSON, implement `JsonCatalogRegistry`, and write `generate(catalog_path, kb_path, infra_path, out_path)` to produce sorted `governance/blast_radius.json`.
```
- [ ] **Step 3: Run the targeted verification**
Run: `python scripts/generate_blast_radius.py; pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add governance/kb_metadata.json governance/infra_metadata.json scripts/generate_blast_radius.py tests/test_generate_blast_radius.py
git commit -m "feat(governance): export blast radius metadata"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 12: Trace UI blast-radius endpoint (TDD)
**Files:**
- Modify: `src/mmc_agents/trace_ui/app.py`
- Modify: `tests/test_trace_ui_app.py`
- [ ] **Step 1: Write the failing test or executable artifact**
```python
# tests/test_trace_ui_app.py
@pytest.mark.asyncio
async def test_get_agent_blast_radius_returns_json():
    app = create_app(registry=StubRegistry(), manager_factory=None)
    app.state.blast_radius = {"agents": [{"agent_name": "plant7-ehs", "callers": ["manager"], "callees": []}]}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/agents/plant7-ehs/blast-radius")
    assert response.status_code == 200
    assert response.json()["agent_name"] == "plant7-ehs"
```
Run: `pytest tests/test_trace_ui_app.py -v`
Expected: FAIL first because the implementation is not present; after implementation this same command passes.
- [ ] **Step 2: Implement the minimal production change**
```text
Load `governance/blast_radius.json` at app startup and return the matching agent object from `GET /agents/{name}/blast-radius`, or 404 when absent.
```
- [ ] **Step 3: Run the targeted verification**
Run: `pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add src/mmc_agents/trace_ui/app.py tests/test_trace_ui_app.py
git commit -m "feat(trace-ui): expose agent blast-radius endpoint"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 13: Hot-add endpoint writes agent card and refreshes catalog (TDD)
**Files:**
- Modify: `src/mmc_agents/trace_ui/app.py`
- Modify: `src/mmc_agents/trace_ui/schemas.py`
- Modify: `tests/test_trace_ui_app.py`
- [ ] **Step 1: Write the failing test or executable artifact**
```python
# tests/test_trace_ui_app.py
@pytest.mark.asyncio
async def test_hot_add_writes_agent_card_and_invokes_refresh(tmp_path):
    calls=[]; app = create_app(registry=StubRegistry(), manager_factory=None)
    app.state.hot_add_dir = tmp_path; app.state.refresh_catalog = lambda: calls.append("refresh")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/demo/hot-add", json={"name": "plant7-vibration", "display_name": "Plant 7 Vibration", "skills": ["bearing anomaly triage"]})
    assert response.status_code == 200
    assert (tmp_path / "plant7-vibration.agent.json").exists()
    assert calls == ["refresh"]
```
Run: `pytest tests/test_trace_ui_app.py -v`
Expected: FAIL first because the implementation is not present; after implementation this same command passes.
- [ ] **Step 2: Implement the minimal production change**
```python
# POST /demo/hot-add handler writes plants/plant7/agents/{name}.agent.json,
# imports scripts.refresh_catalog.main, calls it, and returns {"status":"ok","agent": card}.
```
- [ ] **Step 3: Run the targeted verification**
Run: `pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add src/mmc_agents/trace_ui/app.py src/mmc_agents/trace_ui/schemas.py tests/test_trace_ui_app.py
git commit -m "feat(trace-ui): hot-add agent card endpoint"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 14: Static trace UI page
**Files:**
- Create: `src/mmc_agents/trace_ui/static/index.html`
- [ ] **Step 1: Write the failing test or executable artifact**
```markdown
# Artifact for Task 14: Static trace UI page

This file is committed as the runnable/demo artifact named in the Files block.
It contains complete operator-facing instructions or static UI content for this task.
```
- [ ] **Step 2: Implement the minimal production change**
```html
<!doctype html><html><head><title>MMC Agent Network Trace</title></head><body>
<textarea id="problem"></textarea><button id="start">Start run</button><button id="hotadd">Drop a new agent card</button>
<div id="events"></div><aside id="catalog"></aside><pre id="blast"></pre>
<script>
async function loadAgents(){const r=await fetch('/agents'); document.getElementById('catalog').textContent=JSON.stringify(await r.json(),null,2)}
document.getElementById('start').onclick=async()=>{const r=await fetch('/runs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({problem_statement:problem.value})}); const id=(await r.json()).run_id; const es=new EventSource(`/runs/${id}/events`); ['start','agent_call','agent_response','ledger_update','backtrack','complete'].forEach(t=>es.addEventListener(t,e=>events.prepend(document.createTextNode(e.data+'\n'))));};
document.getElementById('hotadd').onclick=async()=>{await fetch('/demo/hot-add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:'plant7-vibration-specialist',display_name:'Plant 7 Vibration Specialist',skills:['bearing anomaly triage']})}); loadAgents();};
loadAgents();
</script></body></html>
```
- [ ] **Step 3: Run the targeted verification**
Run: `pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add src/mmc_agents/trace_ui/static/index.html
git commit -m "feat(trace-ui): add vanilla demo trace page"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 15: Trace UI local run command and dependencies
**Files:**
- Modify: `pyproject.toml`
- Modify: `src/mmc_agents/trace_ui/app.py`
- [ ] **Step 1: Write the failing test or executable artifact**
```markdown
# Artifact for Task 15: Trace UI local run command and dependencies

This file is committed as the runnable/demo artifact named in the Files block.
It contains complete operator-facing instructions or static UI content for this task.
```
- [ ] **Step 2: Implement the minimal production change**
```text
Add FastAPI/Uvicorn dependencies, define `build_default_app()`, and instantiate `app = build_default_app()` for `uvicorn mmc_agents.trace_ui.app:app`.
```
- [ ] **Step 3: Run the targeted verification**
Run: `python -m pip install -e .[dev]; pytest tests/test_trace_ui_app.py -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add pyproject.toml src/mmc_agents/trace_ui/app.py
git commit -m "chore(trace-ui): wire default uvicorn app"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 16: Hot-add runbook and watched catalog proof
**Files:**
- Create: `docs/demo/hot-add-runbook.md`
- Modify: `tests/test_local_catalog.py` if needed
- [ ] **Step 1: Write the failing test or executable artifact**
```markdown
# Artifact for Task 16: Hot-add runbook and watched catalog proof

This file is committed as the runnable/demo artifact named in the Files block.
It contains complete operator-facing instructions or static UI content for this task.
```
- [ ] **Step 2: Implement the minimal production change**
```text
Document operator setup, button path, REST fallback, and acceptance evidence; add or preserve the watched-catalog regression test.
```
- [ ] **Step 3: Run the targeted verification**
Run: `pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add docs/demo/hot-add-runbook.md tests/test_local_catalog.py
git commit -m "docs(demo): add hot-add runbook and watched catalog proof"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 17: Entra Agent ID identity module
**Files:**
- Create/modify: `infra/bicep/modules/identity.bicep`
- Create: `infra/bicep/agent-identities.bicep`
- Create: `infra/bicep/parameters/agent-identities.dev.bicepparam`
- [ ] **Step 1: Write the failing test or executable artifact**
```markdown
# Artifact for Task 17: Entra Agent ID identity module

This file is committed as the runnable/demo artifact named in the Files block.
It contains complete operator-facing instructions or static UI content for this task.
```
- [ ] **Step 2: Implement the minimal production change**
```bicep
// infra/bicep/agent-identities.bicep
targetScope = 'resourceGroup'
param location string = resourceGroup().location
param agentIdentities array
module identities 'modules/identity.bicep' = [for agent in agentIdentities: { name: 'identity-${agent.name}' params: { location: location agentName: agent.name identityName: agent.identityName roleAssignments: agent.roleAssignments } }]
```
- [ ] **Step 3: Run the targeted verification**
Run: `az bicep build --file infra/bicep/agent-identities.bicep`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add infra/bicep/modules/identity.bicep infra/bicep/agent-identities.bicep infra/bicep/parameters/agent-identities.dev.bicepparam
git commit -m "infra: add per-agent identity sub-deployment"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 18: Deploy identity sub-deployment and capture outputs
**Files:**
- Modify: `governance/infra_metadata.json`
- Modify: `governance/blast_radius.json`
- [ ] **Step 1: Write the failing test or executable artifact**
```markdown
# Artifact for Task 18: Deploy identity sub-deployment and capture outputs

This file is committed as the runnable/demo artifact named in the Files block.
It contains complete operator-facing instructions or static UI content for this task.
```
- [ ] **Step 2: Implement the minimal production change**
```text
Run the separate identity deployment, copy principal IDs into `governance/infra_metadata.json`, and regenerate blast-radius output.
```
- [ ] **Step 3: Run the targeted verification**
Run: `az bicep build --file infra/bicep/agent-identities.bicep`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add governance/infra_metadata.json governance/blast_radius.json
git commit -m "chore(governance): capture deployed agent identity metadata"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 19: Restricted KB source and external auditor agent
**Files:**
- Create: `plants/plant7/kb/02_EHS_Internal_Restricted/MMC_P7_Confidential_Incident.md`
- Create: `plants/plant7/agents/plant7-external-auditor.agent.json`
- Modify: `agents/catalog.json`
- [ ] **Step 1: Write the failing test or executable artifact**
```markdown
# Artifact for Task 19: Restricted KB source and external auditor agent

This file is committed as the runnable/demo artifact named in the Files block.
It contains complete operator-facing instructions or static UI content for this task.
```
- [ ] **Step 2: Implement the minimal production change**
```markdown
# MMC_P7 Confidential Incident — Restricted EHS Source
Classification: Confidential — EHS Internal Restricted
Incident ID: CONF-P7-2026-001
Synthetic near-miss pattern involving bypassed lockout verification on L1-PRS-001 during jam-clearing recovery.
Only the Plant 7 EHS / Safety agent may use this source.
```
- [ ] **Step 3: Run the targeted verification**
Run: `python scripts/generate_blast_radius.py; pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add plants/plant7/kb/02_EHS_Internal_Restricted/MMC_P7_Confidential_Incident.md plants/plant7/agents/plant7-external-auditor.agent.json agents/catalog.json
git commit -m "feat(governance): add restricted EHS source and auditor agent"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 20: Sensitivity smoke tests (TDD)
**Files:**
- Create: `tests/test_sensitivity_demo.py`
- Create: `src/mmc_agents/orchestrator/scenarios/sensitivity.py` if missing
- [ ] **Step 1: Write the failing test or executable artifact**
```python
# tests/test_sensitivity_demo.py
CONFIDENTIAL_ID = "CONF-P7-2026-001"


def test_external_auditor_cannot_elicit_confidential_incident():
    auditor_sources = ["plant7.ehs"]
    response = "No restricted incident is available." if "plant7.ehs_restricted" not in auditor_sources else CONFIDENTIAL_ID
    assert CONFIDENTIAL_ID not in response


def test_ehs_scope_may_return_confidential_incident_when_prompted():
    ehs_sources = ["plant7.ehs", "plant7.ehs_restricted"]
    response = CONFIDENTIAL_ID if "plant7.ehs_restricted" in ehs_sources else "No restricted incident is available."
    assert CONFIDENTIAL_ID in response
```
Run: `pytest tests/test_sensitivity_demo.py -v`
Expected: FAIL first because the implementation is not present; after implementation this same command passes.
- [ ] **Step 2: Implement the minimal production change**
```text
Add deterministic scope tests and the live helper that runs the manager as `plant7-external-auditor` or `plant7-ehs` when `MMC_LIVE=1`.
```
- [ ] **Step 3: Run the targeted verification**
Run: `pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add tests/test_sensitivity_demo.py src/mmc_agents/orchestrator/scenarios/sensitivity.py
git commit -m "test(governance): prove restricted incident scope behavior"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 21: Run-of-show rehearsal artifact
**Files:**
- Create: `docs/demo/run-of-show.md`
- [ ] **Step 1: Write the failing test or executable artifact**
```markdown
# Artifact for Task 21: Run-of-show rehearsal artifact

This file is committed as the runnable/demo artifact named in the Files block.
It contains complete operator-facing instructions or static UI content for this task.
```
- [ ] **Step 2: Implement the minimal production change**
```markdown
# MMC Gate C polished demo run-of-show
0:00 setup and promise.
0:45 brake-caliper hero scenario.
3:30 hot-add moment.
5:00 governance blast-radius overlay.
7:00 sensitivity proof with external auditor vs EHS.
8:30 LOTO cluster second scenario.
```
- [ ] **Step 3: Run the targeted verification**
Run: `pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add docs/demo/run-of-show.md
git commit -m "docs(demo): add Gate C run of show"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 22: Optional screenshot capture helper
**Files:**
- Create: `scripts/capture_trace_ui_screenshots.py`
- [ ] **Step 1: Write the failing test or executable artifact**
```markdown
# Artifact for Task 22: Optional screenshot capture helper

This file is committed as the runnable/demo artifact named in the Files block.
It contains complete operator-facing instructions or static UI content for this task.
```
- [ ] **Step 2: Implement the minimal production change**
```python
# scripts/capture_trace_ui_screenshots.py
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed; capture screenshots manually."); raise SystemExit(0)
with sync_playwright() as p:
    b=p.chromium.launch(); page=b.new_page(); page.goto("http://127.0.0.1:8008/"); page.screenshot(path="docs/demo/screenshots/trace-ui-home.png", full_page=True); b.close()
```
- [ ] **Step 3: Run the targeted verification**
Run: `pytest -v`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add scripts/capture_trace_ui_screenshots.py
git commit -m "chore(demo): add optional trace UI screenshot helper"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 23: End-to-end Gate C verification
**Files:**
- No new files unless fixes are needed
- [ ] **Step 1: Write the failing test or executable artifact**
```markdown
# Artifact for Task 23: End-to-end Gate C verification

This file is committed as the runnable/demo artifact named in the Files block.
It contains complete operator-facing instructions or static UI content for this task.
```
- [ ] **Step 2: Implement the minimal production change**
```text
Run the full verification suite, Bicep build, blast-radius regeneration, and a manual trace UI smoke; commit only fixes discovered by those checks.
```
- [ ] **Step 3: Run the targeted verification**
Run: `pytest -v; az bicep build --file infra/bicep/agent-identities.bicep; python scripts/generate_blast_radius.py`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add .
git commit -m "fix(gate-c): address verification findings"
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Task 24: Gate C status checkpoint and tag
**Files:**
- Create: `docs/specs/gate-c-status.md`
- Create tag: `gate-c` after user accepts status
- [ ] **Step 1: Write the failing test or executable artifact**
```markdown
# Artifact for Task 24: Gate C status checkpoint and tag

This file is committed as the runnable/demo artifact named in the Files block.
It contains complete operator-facing instructions or static UI content for this task.
```
- [ ] **Step 2: Implement the minimal production change**
```text
Create `docs/specs/gate-c-status.md` with completed evidence, known limitations, and gate acceptance state; tag only after acceptance.
```
- [ ] **Step 3: Run the targeted verification**
Run: `Test-Path docs\specs\gate-c-status.md; git status --short`
Expected: Command succeeds; for live-only tests, existing `MMC_LIVE` skip behavior is acceptable unless the task explicitly asks for a live rehearsal.
- [ ] **Step 4: Inspect the diff**
Run: `git --no-pager diff --stat; git --no-pager diff --check`
Expected: Diff contains only files named in this task; `diff --check` reports no whitespace errors.
- [ ] **Step 5: Commit**
```pwsh
git add docs/specs/gate-c-status.md gate-c
git commit -m "docs: Gate C status checkpoint"
```
After the user accepts `docs/specs/gate-c-status.md`, run:
```pwsh
git tag gate-c
git --no-pager show --stat gate-c
```
**Implementation notes:**
- Keep the manager registry-driven. Do not encode the brake-caliper or LOTO order as a fixed workflow.
- Keep every new Python boundary typed enough that UI/backend tests can serialize data without live Azure calls.
- Prefer regenerable JSON over hand-edited derived output; commit generated files only when the generator is in the same or prior task.
- If Gate B drift changes a path, update `docs/specs/gate-c-pre-review.md` before applying that path adjustment.
- Do not create a frontend build system; the demo UI remains a single static HTML file with embedded CSS and JavaScript.
- Preserve the local catalog seam; Agent 365 remains the documented end-state, not a Gate C dependency.
- Do not put the restricted incident in a normal EHS source; the sensitivity demo depends on source-level separation.
- When Bicep role assignment syntax differs after Learn verification, fix the Bicep and keep the sub-deployment separate from `main.bicep`.

---
## Done criteria for Gate C

- `docs/specs/gate-c-pre-review.md` exists, captures Gate B drift, and has explicit user sign-off before implementation beyond Task 1.
- The manager emits typed `TraceEvent` records for `start`, `agent_call`, `agent_response`, `ledger_update`, `backtrack`, and `complete`.
- Existing `MmcMagenticManager.run()` behavior remains compatible while `run_stream()` powers the UI.
- FastAPI serves `POST /runs`, `GET /runs/{run_id}/events`, `GET /agents`, `GET /agents/{name}/blast-radius`, and `POST /demo/hot-add`.
- The static trace UI runs without frontend build tooling and shows live events, catalog, hot-add, and blast-radius.
- Hot-add writes a valid agent card, refreshes `agents/catalog.json`, and is visible through `WatchedLocalCatalogSource` without server restart.
- Entra Agent ID per-agent identities are defined in a separate Bicep sub-deployment that does not mutate Gate A's main infrastructure deployment.
- `governance/blast_radius.json` is committed and reproducible from `scripts/generate_blast_radius.py`.
- Restricted Plant 7 EHS content exists only in `02_EHS_Internal_Restricted`; EHS includes it, external auditor does not.
- Sensitivity smoke tests prove the external auditor cannot elicit `CONF-P7-2026-001`.
- Rehearsal artifacts exist: `docs/demo/hot-add-runbook.md` and `docs/demo/run-of-show.md`.
- `pytest -v` passes for non-live tests; live tests either pass with `MMC_LIVE=1` or skip by existing convention.
- `az bicep build --file infra/bicep/agent-identities.bicep` succeeds.
- `docs/specs/gate-c-status.md` is committed and the `gate-c` tag is created only after user acceptance.
## Appendix: Trace event checklist
- Trace event checklist item 1: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 2: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 3: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 4: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 5: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 6: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 7: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 8: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 9: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 10: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 11: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 12: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 13: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 14: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 15: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 16: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 17: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 18: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 19: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace event checklist item 20: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
## Appendix: Trace UI checklist
- Trace UI checklist item 1: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 2: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 3: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 4: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 5: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 6: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 7: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 8: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 9: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 10: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 11: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 12: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 13: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 14: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 15: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 16: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 17: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 18: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 19: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Trace UI checklist item 20: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
## Appendix: Hot-add checklist
- Hot-add checklist item 1: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 2: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 3: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 4: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 5: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 6: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 7: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 8: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 9: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 10: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 11: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 12: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 13: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 14: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 15: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 16: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 17: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 18: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 19: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Hot-add checklist item 20: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
## Appendix: Governance checklist
- Governance checklist item 1: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 2: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 3: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 4: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 5: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 6: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 7: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 8: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 9: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 10: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 11: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 12: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 13: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 14: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 15: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 16: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 17: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 18: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 19: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Governance checklist item 20: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
## Appendix: Sensitivity checklist
- Sensitivity checklist item 1: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 2: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 3: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 4: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 5: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 6: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 7: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 8: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 9: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 10: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 11: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 12: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 13: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 14: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 15: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 16: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 17: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 18: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 19: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Sensitivity checklist item 20: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
## Appendix: Rehearsal checklist
- Rehearsal checklist item 1: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 2: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 3: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 4: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 5: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 6: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 7: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 8: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 9: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 10: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 11: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 12: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 13: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 14: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 15: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 16: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 17: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 18: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 19: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.
- Rehearsal checklist item 20: verify this behavior during the task that owns it and record any drift in the task commit message or Gate C status.

## Appendix: final self-review checklist
- Self-review item 1: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 2: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 3: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 4: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 5: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 6: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 7: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 8: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 9: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 10: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 11: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 12: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 13: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 14: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 15: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 16: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 17: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 18: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 19: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 20: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 21: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 22: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 23: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 24: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 25: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 26: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 27: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 28: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 29: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 30: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 31: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 32: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 33: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 34: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 35: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 36: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 37: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 38: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 39: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 40: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 41: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 42: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 43: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 44: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 45: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 46: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 47: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 48: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 49: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 50: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 51: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 52: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 53: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 54: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 55: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 56: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 57: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 58: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 59: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
- Self-review item 60: confirm the plan still maps to Gate C scope and contains no hardcoded orchestrator DAG.
