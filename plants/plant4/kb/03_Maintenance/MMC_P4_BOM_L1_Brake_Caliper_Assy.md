# MMC Plant 4 — BOM: Line 1 Brake Caliper Assembly

**Document owner:** Plant 4 Maintenance & Engineering
**Asset family:** L1-PRS- (Stamping/Forming presses)
**Finished good families served:** BRK-FG-7, BRK-FG-7E

## Bill of Materials (top level)

| Component | Part Number | Qty per FG | Source | Notes |
|---|---|---|---|---|
| Front caliper casting (primary) | **BRK-CAL-XYZ** | 1 | Acme Brakes (Tier 1) | Primary casting for FG-7 family |
| Front caliper casting (alternate) | BRK-CAL-XYZ-ALT | 1 | Bravo Castings (Tier 2, qualified) | 9-day lead time; QA flow-down required on each lot |
| Piston seal kit | BRK-SEAL-12 | 2 | Generic | High availability |
| Mounting hardware kit | BRK-HW-44 | 1 | Generic | High availability |

## BRK-CAL-XYZ usage notes

BRK-CAL-XYZ is **only consumed on Line 1 (L1)** — it does not appear in L2 or L3 work orders. PM tasks affected by a BRK-CAL-XYZ outage include the L1-PRS-03 die-change SMED procedure (no caliper-casting-specific PM, but the die is set up for the XYZ casting geometry; ALT geometry requires die-shim kit DK-XYZ-ALT-01).

## Substitution rules

- BRK-CAL-XYZ ↔ BRK-CAL-XYZ-ALT requires QA disposition (NCR not required if substitution is from the qualified-source list) and a 30-minute die-shim changeover on L1-PRS-03.
- No BRK-FG-7 finished good may ship without one of the two qualified castings installed.

## Cross-references

- Build schedule: `MMC_P4_L1_Build_Schedule.md`
- QA spec: `MMC_P4_Brake_Caliper_QA_Spec.md`
