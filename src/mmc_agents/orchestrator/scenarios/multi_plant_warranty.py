"""Multi-plant warranty spike — explicit cross-plant scenario (Gate D Task 23).

Engineered to require both Plant 7 and Plant 4 plant-local response plus
enterprise quality and supply-chain coordination. Unlike brake_caliper (which
allocates BRK-CAL-XYZ to MMC_P7 only and so legitimately concludes Plant 4 is
unaffected), this scenario's problem statement explicitly names both plants
and asks each to respond, so the manager must dispatch and the final answer
must mention both plant names.
"""

PROBLEM_STATEMENT = (
    "BRK-CAL-XYZ warranty claims are spiking. Which MMC plants are affected, "
    "what qualified maintenance and production response should each plant take, "
    "and what enterprise quality or supply-chain actions are needed?"
)

EXPECTED_BOUNDS = {
    "min_distinct_agents": 6,
    "min_backtracks": 0,
    "must_include_agents": {
        "ent-quality",
        "ent-supply-chain",
        "plant7-quality",
        "plant4-quality",
    },
    # Allow Gate B/C role-naming drift across plants. At least one of each
    # alternative set must appear in hops.
    "must_include_any": [
        {"plant7-maintenance", "plant7-shiftops", "plant7-production"},
        {"plant4-maintenance", "plant4-shiftops", "plant4-production"},
    ],
    "must_observe_terms": {"BRK-CAL-XYZ", "Acme Brakes"},
    "must_mention_plants": {"Plant 7", "Plant 4"},
}
