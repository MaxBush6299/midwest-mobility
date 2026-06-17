"""Narrow enterprise-only scenario: at-risk POs with SUP-001.

Grounded in po_spend.csv (Status in {'At Risk','Watch','Open'},
Supplier_ID='SUP-001' is Acme Brakes).
"""

PROBLEM_STATEMENT = (
    "Which of our open POs with supplier SUP-001 are currently flagged "
    "'At Risk' or 'Watch'? List PO_ID, Part_ID, Open_Qty, and "
    "Extended_Value, and cite po_spend.csv."
)

EXPECTED_BOUNDS = {
    "min_distinct_agents": 1,
    "min_backtracks": 0,
    "must_include_agents": {"ent-procurement"},
    "must_observe_terms": {"SUP-001"},
}
