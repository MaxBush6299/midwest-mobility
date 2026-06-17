"""Tests for Plant 7 fixture-backed tools (Gate B Tasks 17-19)."""
from mmc_agents.tools.capa import capa_status, capa_by_incident
from mmc_agents.tools.cmms import pm_status, asset_history
from mmc_agents.tools.qms import ncr_status, quality_signals_for_part
from mmc_agents.tools.scada import telemetry_snapshot
from mmc_agents.tools.mes import line_schedule
from mmc_agents.tools.lms import qualified_employees, training_status


# Task 17 — CAPA
def test_capa_status_known_loto_capa():
    assert capa_status("CAPA-061")["CAPA_ID"] == "CAPA-061"


def test_capa_by_incident_known_incident():
    assert capa_by_incident("INC-061")["CAPA_ID"] == "CAPA-061"


# Task 18 — CMMS / QMS
def test_pm_status_for_l1_press():
    assert any(r["LOTO_Required"] == "Y" for r in pm_status("L1-PRS-001"))


def test_asset_history_unknown_returns_empty():
    assert asset_history("NO-ASSET") == []


def test_quality_signals_for_brake_caliper():
    assert any(r["Line_ID"] == "L1" for r in quality_signals_for_part("BRK-CAL-XYZ"))


def test_ncr_status_known_record():
    assert ncr_status("NCR-BRK-001")["Part_ID"] == "BRK-CAL-XYZ"


# Task 19 — SCADA / MES / LMS
def test_scada_snapshot_for_l1_press():
    assert telemetry_snapshot("L1-PRS-001")["Asset_ID"] == "L1-PRS-001"


def test_mes_line_schedule_l1():
    assert all(r["Line_ID"] == "L1" for r in line_schedule("L1"))


def test_lms_qualified_for_loto_l1():
    assert qualified_employees("LOTO-L1")


def test_training_status_known_employee():
    assert training_status("EMP-001")["Employee_ID"] == "EMP-001"
