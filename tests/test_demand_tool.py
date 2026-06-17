"""Tests for src/mmc_agents/tools/demand.py (Gate B Task 15)."""
from mmc_agents.tools.demand import order_signal, program_status, allocation


def test_order_signal_for_brake_caliper():
    assert any(r["Priority"] == "High" for r in order_signal("BRK-CAL-XYZ"))


def test_program_status_at_risk():
    assert any(r["Status"] == "At Risk" for r in program_status("EV-BRK-26"))


def test_allocation_constrained_on_plant7_l1():
    rows = allocation("BRK-CAL-XYZ", "plant7")
    assert rows and all(r["Line_ID"] == "L1" for r in rows)


def test_allocation_unknown_part_returns_empty():
    assert allocation("NOPE", "plant7") == []
