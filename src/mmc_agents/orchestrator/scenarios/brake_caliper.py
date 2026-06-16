"""Reference scenario from DEMO_BUILD_HANDOFF.md §5 (Task 27)."""

PROBLEM_STATEMENT = (
    "A tier-1 supplier flagged a 3-week delay on brake calipers (part BRK-CAL-XYZ). "
    "What's the impact on our plants, what mitigations are available, and what's the "
    "cost picture?"
)

EXPECTED_BOUNDS = {
    "min_distinct_agents": 3,
    "min_backtracks": 0,  # Gate A thin slice — single plant + stub supply chain
    "must_include_agents": {"plant7-maintenance", "plant7-quality"},
}
