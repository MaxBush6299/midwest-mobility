"""Narrow plant-only scenario: 2-agent training/safety check.

Useful for fast iteration on the trace UI — exercises the full event
pipeline (start → agent_call → agent_response → ledger_update → complete)
without the 30-hop cost of the full brake-caliper task.
"""

PROBLEM_STATEMENT = (
    "Which Plant 7 L1 operators are due for a LOTO refresher this quarter, "
    "and are any of them currently on the shift roster?"
)

EXPECTED_BOUNDS = {
    "min_distinct_agents": 2,
    "min_backtracks": 0,
    "must_include_agents": {
        "plant7-training",
        "plant7-ehs",
    },
    "must_observe_terms": {"LOTO"},
}
