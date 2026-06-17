"""Narrow enterprise-only scenario: 2-agent PO/inbound status check.

Exercises the enterprise tier in isolation (procurement + supply-chain) so
plant agents stay quiet — useful for verifying the trace UI's tier
grouping and per-project labels.
"""

PROBLEM_STATEMENT = (
    "What's the current status of our open POs with SUP-001 (Acme Brakes), "
    "and which inbound shipments are tracking late this week?"
)

EXPECTED_BOUNDS = {
    "min_distinct_agents": 2,
    "min_backtracks": 0,
    "must_include_agents": {
        "ent-procurement",
        "ent-supply-chain",
    },
    "must_observe_terms": {"SUP-001"},
}
