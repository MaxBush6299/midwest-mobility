"""Reference scenario from DEMO_BUILD_HANDOFF.md §5 (Task 27).

Gate B (Task 27) bounds: the brake-caliper task must now exercise both plant
agents and enterprise procurement/PLM/demand, and must backtrack at least
once when supply-chain reports NO_DIRECT_ALT.
"""

PROBLEM_STATEMENT = (
    "A tier-1 supplier flagged a 3-week delay on brake calipers (part BRK-CAL-XYZ). "
    "What's the impact on our plants, what mitigations are available, and what's the "
    "cost picture?"
)

EXPECTED_BOUNDS = {
    "min_distinct_agents": 5,
    "min_backtracks": 1,
    "must_include_agents": {
        "ent-supply-chain",
        "plant7-maintenance",
        "plant7-quality",
        "ent-procurement",
    },
    "must_observe_terms": {"NO_DIRECT_ALT", "BRK-CAL-XYZ"},
}
