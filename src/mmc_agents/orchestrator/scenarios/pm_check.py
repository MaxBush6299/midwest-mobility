"""Narrow plant-only scenario: 2-agent preventive-maintenance check.

Smallest possible exercise — single plant, two related agents — for fast
smoke tests of the trace UI streaming pipeline.
"""

PROBLEM_STATEMENT = (
    "Is the L1 Press due for preventive maintenance in the next 7 days, "
    "and if so, which shift can take it down without disrupting active runs?"
)

EXPECTED_BOUNDS = {
    "min_distinct_agents": 2,
    "min_backtracks": 0,
    "must_include_agents": {
        "plant7-maintenance",
        "plant7-shiftops",
    },
    "must_observe_terms": {"L1"},
}
