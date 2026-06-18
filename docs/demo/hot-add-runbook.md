# Hot-add agent runbook (Gate C · t10)

> **Demo moment**: "Watch — we'll pull a brand new agent onto the stage *during* the run. No redeploy. The trace UI sees it immediately."

This runbook walks through the live hot-add demo backed by `POST /demo/hot-add`.

## What it proves

1. The trace-UI registry is **hot-pluggable** — the FastAPI app picks up new agents on the next `/agents` poll without a restart.
2. The catalog is the **single source of truth**: anything the registry serves is dispatchable.
3. The governance overlay degrades gracefully — a hot-added agent that lacks `governance/kb_metadata.json` entries renders an `available: false` blast-radius card, signaling "this hasn't been baked into the policy graph yet."

## What's pre-staged

`src/mmc_agents/trace_ui/app.py` ships an in-memory shadow catalog (`_HOT_ADD_CATALOG`) containing exactly one agent today:

| Catalog name              | Display name                            | Tier  |
|---------------------------|-----------------------------------------|-------|
| `plant7-supplier-quality` | Plant 7 Supplier Quality (hot-added)    | plant |

Hot-add is intentionally an allow-list — arbitrary names are rejected so the demo can't be hijacked into materializing fake executors in the trace.

## Live demo flow (≈ 60 seconds)

1. **Set the stage.** Trace UI open, left rail showing 11 agents (6 plant + 5 enterprise).
2. **Narrate the gap.** "Supplier quality is missing from our roster — we'd want it for incoming-material investigations."
3. **Click `+ Hot-add supplier-quality`** in the bottom-left of the agents pane.
4. **Toast confirms** the add (`✨ Hot-added Plant 7 Supplier Quality...`).
5. **Left rail re-renders** with the new agent shown with a dashed-amber border — the visual cue that it's not in the persisted catalog.
6. **Click the new agent row** to open its blast-radius modal. Expect `available: false` with the message "agent has no governance metadata yet." Narrate: "The agent is dispatchable, but governance hasn't sealed it into the blast-radius policy graph. That's the seam between operator agility and policy lock-in."
7. **(Optional)** Re-run a scenario to demonstrate the manager *can* dispatch to it once it's in `/agents`.
8. **Click `Reset`** to undo. Toast confirms `Cleared 1 hot-added agent.`

## API surface

```http
POST /demo/hot-add
Content-Type: application/json
{ "name": "plant7-supplier-quality", "tier": "plant" }
```

Response shape (`HotAddResponse`):

```json
{
  "accepted": true,
  "agent": { "name": "plant7-supplier-quality", "tier": "plant", "...": "..." },
  "detail": "agent 'plant7-supplier-quality' added to the in-memory catalog. ...",
  "active_count": 1
}
```

Reset:

```http
POST /demo/hot-add/reset
```

Returns `{"cleared": <int>}`.

## Failure modes (and how to recover)

| Symptom                                            | Cause                                                                                 | Fix                                                                              |
|----------------------------------------------------|----------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| Toast says `already in the persisted catalog`      | You hot-added something that's already in `agents/catalog.json`                        | Pick a different name, or remove it from the catalog                             |
| Toast says `not in the demo hot-add catalog`       | Body's `name` is not in `_HOT_ADD_CATALOG`                                             | Edit `src/mmc_agents/trace_ui/app.py` to pre-bake the agent                      |
| Hot-added agent never appears                      | `/agents` cached client-side                                                           | Hard-refresh or click `+ Hot-add` again — the UI calls `loadAgents()` after add  |
| Manager doesn't dispatch to hot-added agent        | Manager prompt doesn't yet reference its role                                          | Expected — the demo's about the *registration* moment, not orchestrator routing  |

## What does NOT happen during hot-add

- **No Foundry resource is created.** The Foundry agent already exists (or doesn't) — hot-add only flips visibility in the in-memory registry.
- **No governance JSON is mutated.** That's why the blast-radius modal says "no metadata."
- **No persistence.** Restart the trace UI and the hot-add is gone. This is deliberate — the demo is supposed to be reversible.

## Extending

To add a new hot-add candidate, edit `_HOT_ADD_CATALOG` in `src/mmc_agents/trace_ui/app.py`:

```python
_HOT_ADD_CATALOG["plant7-energy-monitoring"] = AgentInfo(
    name="plant7-energy-monitoring",
    display_name="Plant 7 Energy Monitoring (hot-added)",
    tier="plant",
    description="...mention hot-add so the dashed-amber border styling fires...",
    foundry_project="mmc-plant",
)
```

Then update the button label in `static/index.html` (`+ Hot-add supplier-quality`) and the `HOT_ADD_NAME` constant in the script tag at the bottom.
