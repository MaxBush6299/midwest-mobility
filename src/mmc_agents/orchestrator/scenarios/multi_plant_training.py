"""Multi-plant training scenario — cross-plant LOTO refresher rollup.

Engineered to require BOTH plant training agents (plant7-training and
plant4-training) plus enterprise quality to roll up an enterprise-wide
refresher load. Grounded in:

  - plants/plant7/kb/08_Logs_Data/MMC_P7_Training_Log.csv
  - plants/plant4/kb/08_Logs_Data/MMC_P4_Training_Log.csv

Both logs share schema (Training_Course, Expiration_Date, ...) so the
manager can dispatch the same query to each plant's training agent in
parallel and have enterprise quality consolidate.
"""

PROBLEM_STATEMENT = (
    "Across both Plant 7 (Hayward) and Plant 4 (Monterrey), identify every "
    "employee whose 'LOTO Authorized Person' training expires before "
    "2026-12-31. Each plant's training agent must cite the specific "
    "Training_Log entries from its own plant, and enterprise quality should "
    "summarize the combined refresher load and any cross-plant scheduling "
    "risks."
)

EXPECTED_BOUNDS = {
    "min_distinct_agents": 3,
    "min_backtracks": 0,
    "must_include_agents": {
        "plant7-training",
        "plant4-training",
        "ent-quality",
    },
    "must_observe_terms": {"LOTO"},
    "must_mention_plants": {"Plant 7", "Plant 4"},
}
