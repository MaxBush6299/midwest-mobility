"""Aggregate all *.agent.json files under plants/ and enterprise/ into agents/catalog.json."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main() -> None:
    cards = []
    for p in sorted(ROOT.glob("plants/*/agents/*.agent.json")):
        cards.append(json.loads(p.read_text(encoding="utf-8")))
    for p in sorted(ROOT.glob("enterprise/*/agent.json")):
        cards.append(json.loads(p.read_text(encoding="utf-8")))
    out = ROOT / "agents" / "catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"agents": cards}, indent=2), encoding="utf-8")
    print(f"Wrote {out} with {len(cards)} agents.")

if __name__ == "__main__":
    main()
