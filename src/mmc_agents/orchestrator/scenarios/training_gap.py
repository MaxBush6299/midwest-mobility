"""Narrow plant-only scenario: LOTO refresher expiration check.

Grounded in MMC_P7_Training_Log.csv (Course_Category=Safety,
Training_Course='LOTO Authorized Person', Expiration_Date column).

The training agent owns the ``quality_ops`` KB source which contains
``08_Logs_Data/MMC_P7_Training_Log.csv`` — see plants/plant7/profile.yaml.
"""

PROBLEM_STATEMENT = (
    "List all Plant 7 employees whose 'LOTO Authorized Person' training "
    "expires before 2026-12-31. Cite the Training_Log entries."
)

EXPECTED_BOUNDS = {
    "min_distinct_agents": 1,
    "min_backtracks": 0,
    "must_include_agents": {"plant7-ehs"},
    "must_observe_terms": {"LOTO"},
}
