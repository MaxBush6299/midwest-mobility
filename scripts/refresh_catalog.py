"""Aggregate plant and enterprise agent cards into agents/catalog.json.

Plant cards live at plants/<plant>/cards/*.json (legacy schema written by
scripts/generate_cards.py). Enterprise cards live at enterprise/<node>/agent.json
in the AgentCard schema. This script normalises both into AgentCard shape.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Title-case display names for the 5 Gate-A plant agents.
_PLANT_DISPLAY = {
    "plant7-ehs": "Plant 7 EHS / Safety",
    "plant7-maintenance": "Plant 7 Maintenance & Reliability",
    "plant7-quality": "Plant 7 Quality",
    "plant7-shiftops": "Plant 7 Shift Operations",
    "plant7-training": "Plant 7 Training",
}


def _normalise_plant(card: dict) -> dict:
    name = card["name"]
    return {
        "name": name,
        "display_name": card.get("display_name") or _PLANT_DISPLAY.get(name, name),
        "description": card.get("description", name),
        "endpoint": card["endpoint"],
        "skills": card.get("skills", []),
        "tier": "plant",
        "metadata": card.get("metadata", {}),
    }


def main() -> None:
    cards: list[dict] = []
    for p in sorted(ROOT.glob("plants/*/cards/*.json")):
        cards.append(_normalise_plant(json.loads(p.read_text(encoding="utf-8"))))
    for p in sorted(ROOT.glob("enterprise/*/agent.json")):
        cards.append(json.loads(p.read_text(encoding="utf-8")))
    out = ROOT / "agents" / "catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"agents": cards}, indent=2), encoding="utf-8")
    print(f"Wrote {out} with {len(cards)} agents.")


if __name__ == "__main__":
    main()
