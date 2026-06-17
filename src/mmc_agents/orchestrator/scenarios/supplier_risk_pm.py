"""Cross-KB mid-size scenario: at-risk PO ↔ Plant 7 PM impact ↔ supplier backup.

Stitches three SQL-backed knowledge sources across both KBs:
- ent-procurement: po_spend (PO-00001 At Risk, BRK-CAL-XYZ, SUP-001)
- plant7-maintenance: pm_schedule (Line 1 PMs touching brake calipers)
- ent-supply-chain: supplier_master (alternate supplier rows for the part)
"""

PROBLEM_STATEMENT = (
    "Our open PO PO-00001 for BRK-CAL-XYZ from SUP-001 is flagged At Risk. "
    "Which Plant 7 Line 1 PM tasks involve this part, and does the supplier "
    "master show any backup suppliers we could pivot to? Cite po_spend, "
    "pm_schedule, and supplier_master."
)

EXPECTED_BOUNDS = {
    "min_distinct_agents": 3,
    "min_backtracks": 0,
    "must_include_agents": {
        "ent-procurement",
        "plant7-maintenance",
        "ent-supply-chain",
    },
    "must_observe_terms": {"PO-00001", "BRK-CAL-XYZ", "SUP-001"},
}
