"""Safety/LOTO cluster scenario (Gate B Task 29).

Mirrors the brake-caliper scenario shape so live smokes and unit tests can
treat scenarios uniformly. Trigger: three LOTO-related near-misses on Plant 7
L1 in the last 60 days (INC-062, INC-063, INC-064 with open CAPA-062/063/064).
"""

PROBLEM_STATEMENT = (
    "We've had 3 LOTO-related near-misses on Plant 7 L1 in the last 60 days. "
    "What's the pattern, who is qualified to address it, what corrective "
    "actions are open, and is there any enterprise quality or customer "
    "exposure?"
)

EXPECTED_BOUNDS = {
    "min_distinct_agents": 4,
    "min_backtracks": 0,
    "must_include_agents": {
        "plant7-ehs",
        "plant7-maintenance",
        "plant7-training",
    },
    "optional_agents": {"plant7-quality", "ent-quality"},
    "must_observe_terms": {"LOTO", "L1", "CAPA"},
}
