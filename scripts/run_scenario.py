"""Run the brake-caliper scenario and print every agent message + the final answer."""
import asyncio, os, sys
from dotenv import load_dotenv; load_dotenv()
from azure.identity import AzureCliCredential
from agent_framework.orchestrations import (
    MagenticBuilder,
    MagenticOrchestratorEvent,
    MagenticOrchestratorEventType,
)
from mmc_agents.agent_factory import build_foundry_agents
from mmc_agents.observability import setup_tracing
from mmc_agents.orchestrator.manager import _build_manager
from mmc_agents.orchestrator.scenarios.brake_caliper import PROBLEM_STATEMENT


def safe_print(s):
    try:
        sys.stdout.buffer.write((s + "\n").encode("utf-8"))
        sys.stdout.flush()
    except Exception:
        print(s.encode("ascii", "replace").decode("ascii"))


async def main():
    setup_tracing()
    cred = AzureCliCredential()
    endpoint = os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"]
    participants = build_foundry_agents("plant7", endpoint, cred)
    wf = MagenticBuilder(participants=participants, manager=_build_manager()).build()

    workflow_output_chunks: list[str] = []
    last_plant_msg: str | None = None

    def _extract_text(obj):
        # AgentResponse has .messages[-1].text; AgentResponseUpdate has .contents (list of str/Content)
        msgs = getattr(obj, "messages", None)
        if msgs:
            last = msgs[-1]
            t = getattr(last, "text", None)
            if t:
                return t
            cs = getattr(last, "contents", None)
            if cs:
                return "".join(str(c) for c in cs)
        cs = getattr(obj, "contents", None)
        if cs:
            return "".join(getattr(c, "text", str(c)) for c in cs)
        if isinstance(obj, str):
            return obj
        return None

    async for ev in wf.run(PROBLEM_STATEMENT, stream=True):
        executor_id = getattr(ev, "executor_id", None)
        data = getattr(ev, "data", None)
        evtype = str(getattr(ev, "type", ""))
        clsname = type(ev).__name__

        # WorkflowEvent type='output' is the terminal/final yield from the workflow
        if evtype == "output":
            text = _extract_text(data)
            if text:
                workflow_output_chunks.append(text)

        # Agent responses (executor_completed on plant7-* executors)
        if evtype == "executor_completed" and executor_id and executor_id.startswith("plant7-"):
            for r in (data if isinstance(data, list) else [data]):
                ar = getattr(r, "agent_response", None)
                text = getattr(ar, "text", None) if ar else None
                if text:
                    last_plant_msg = text
                    safe_print(f"\n=== [{executor_id}] ===\n{text[:2000]}\n")

        # Magentic orchestrator plan/replan events — for visibility only
        if isinstance(data, MagenticOrchestratorEvent):
            content = getattr(data, "content", None)
            text = getattr(content, "text", None) if content else None
            if data.event_type == MagenticOrchestratorEventType.PLAN_CREATED and text:
                safe_print(f"\n--- [PLAN] ---\n{text[:1500]}\n")

    safe_print("\n" + "=" * 70)
    safe_print("FINAL SYNTHESIS (manager's synthesized answer):")
    safe_print("=" * 70)
    if workflow_output_chunks:
        # In streaming mode the manager yields one chunk per update; concatenate them.
        safe_print("".join(workflow_output_chunks))
    else:
        safe_print("(no WorkflowOutputEvent captured — falling back to last plant7-* agent message)\n")
        safe_print(last_plant_msg or "(no plant7 messages either)")


asyncio.run(main())
