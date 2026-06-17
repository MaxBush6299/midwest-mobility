"""Narrow plant-only scenario: PM follow-up work orders on Line 1.

Grounded in MMC_P7_PM_Schedule.csv (Location='Line 1',
Follow_Up_WO column, Findings column).

The quality agent owns the ``quality_ops`` KB source which contains
``08_Logs_Data/MMC_P7_PM_Schedule.csv`` — see plants/plant7/profile.yaml.
The maintenance agent has the PM procedures (PM_Program_Overview.md) but
NOT the actual schedule/log data.
"""

PROBLEM_STATEMENT = (
    "Which preventive-maintenance tasks on Line 1 generated follow-up "
    "work orders this quarter, what were the findings, and which "
    "asset is each tied to? Cite PM_Schedule entries."
)

EXPECTED_BOUNDS = {
    "min_distinct_agents": 1,
    "min_backtracks": 0,
    "must_include_agents": {"plant7-maintenance"},
    "must_observe_terms": {"Line 1"},
}
