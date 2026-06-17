# src/mmc_agents/tools/supplier.py
from __future__ import annotations
from pathlib import Path
from mmc_agents.tools.fixtures_loader import load_fixture, _read
from agent_framework import tool

_FIX_SUP = Path(__file__).resolve().parents[3] / "enterprise" / "supply-chain" / "fixtures" / "supplier_master.json"
_FIX_BOM = Path(__file__).resolve().parents[3] / "enterprise" / "supply-chain" / "fixtures" / "bom_where_used.json"

@tool(description="Look up a supplier by ID; returns master record incl. disruption flag.")
def lookup(supplier_id: str) -> dict:
    hit = load_fixture(_FIX_SUP, supplier_id)
    if hit is None:
        return {"status": "not_found", "supplier_id": supplier_id}
    return hit

@tool(description="Find alternate suppliers for a given part. Returns list (possibly empty); a single-element list with status='NO_DIRECT_ALT' signals a supplier dead-end requiring manager backtrack.")
def alternates(part_id: str) -> list[dict]:
    bom = load_fixture(_FIX_BOM, part_id)
    if bom is None:
        return []
    incumbent = bom["Supplier_ID"]
    plant = bom["Plant_ID"]
    line = bom["Line_ID"]
    if bom.get("Alt_Source_Status") == "NO_DIRECT_ALT":
        return [{
            "status": "NO_DIRECT_ALT",
            "part_id": part_id,
            "incumbent_supplier_id": incumbent,
            "plant_id": plant,
            "line_id": line,
            "note": (
                "No qualified alternate supplier exists for this part on this "
                "line; manager should backtrack to procurement, PLM, or demand "
                "for a different mitigation dimension."
            ),
        }]
    all_bom = _read(str(_FIX_BOM))
    all_sup = _read(str(_FIX_SUP))
    other_sup_ids = {r["Supplier_ID"] for r in all_bom.values()
                     if r["Plant_ID"] == plant and r["Line_ID"] == line and r["Supplier_ID"] != incumbent}
    return [all_sup[sid] for sid in other_sup_ids if sid in all_sup]
