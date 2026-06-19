"""Reference scenario from DEMO_BUILD_HANDOFF.md §5 (Task 27).

Gate B (Task 27) bounds: the brake-caliper task must exercise both plant
agents and enterprise procurement/PLM/demand to compose a real cross-tier
answer to the BRK-CAL-XYZ delay.

Note on backtracks: when the manager is given the full 10-agent pool
(plant7 + 5 enterprise), it plans correctly upfront — it puts
ent-supply-chain in the initial plan, observes NO_DIRECT_ALT on the first
turn, and fans out to procurement/PLM/demand without needing a formal
``REPLANNED`` event. Backtracks are therefore *expected to be 0* in the
normal case; the ``NO_DIRECT_ALT_RULE`` in the manager's instructions
remains as a safety net if a plant agent surfaces a dead-end mid-flow.
"""

PROBLEM_STATEMENT = (
    "A tier-1 supplier flagged a 3-week delay on brake calipers (part BRK-CAL-XYZ). "
    "What's the impact on our plants, what mitigations are available, and what's the "
    "cost picture?"
)

EXPECTED_BOUNDS = {
    "min_distinct_agents": 6,
    "min_backtracks": 0,
    "must_include_agents": {
        "ent-supply-chain",
        "plant7-maintenance",
        "plant7-quality",
        "ent-procurement",
    },
    # Gate D: require at least one Plant 4 plant-local hop. Allow role-naming
    # drift across Gate B/C (shiftops vs production) — any of the alternatives
    # in each set is sufficient.
    "must_include_any": [
        {"plant4-shiftops", "plant4-production", "plant4-maintenance"},
    ],
    "must_observe_terms": {"BRK-CAL-XYZ"},
    "must_mention_plants": {"Plant 7", "Plant 4"},
}
