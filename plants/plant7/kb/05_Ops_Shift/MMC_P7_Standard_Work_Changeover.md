# MMC Plant 7 — Standard Work: Changeover Procedures
**Document ID:** MMC_P7_Standard_Work_Changeover  
**Document Owner:** Production Manager, Plant 7  
**Version:** v1.0  
**Effective Date:** 2026-01-26  
**Review Cycle:** Annual  
**Applies To:** All personnel performing changeovers on Lines 1, 2, and 3 at MMC Plant 7

---

## 1. Purpose

This document establishes standardized changeover procedures for production lines at MMC Plant 7. Standardized changeovers ensure safety, quality, and efficiency by defining the sequence of tasks, responsibilities, and verification steps required when transitioning between products or production configurations.

---

## 2. Scope

This procedure applies to:
- All planned changeovers on Lines 1, 2, and 3
- All personnel involved in changeover activities (Operators, Setup Technicians, Maintenance, Quality)
- All shifts (1st, 2nd, 3rd)

**Changeover Types Covered:**

| Changeover Type | Description | Typical Duration |
|-----------------|-------------|------------------|
| Product Changeover | Change from one part number to another | 15-60 min depending on line |
| Die Change (Line 1) | Replace stamping die for different part geometry | 45-90 min |
| Robot Program Change (Line 2) | Load different robot program and end-of-arm tooling | 30-60 min |
| Tooling Change (Line 2) | Replace fixtures, grippers, or torque tooling | 20-45 min |
| Pack Configuration Change (Line 3) | Change packaging materials, labels, pallet pattern | 15-30 min |
| Material Lot Change | Transition to new material lot (same part number) | 10-20 min |

---

## 3. Safety Requirements

### 3.1 General Safety

All changeover activities must comply with:
- **MMC_P7_LOTO_SOP** — Lockout/Tagout for all energy isolation
- **MMC_P7_Machine_Guarding_SOP** — Guard removal and reinstallation
- **MMC_P7_PPE_Matrix** — Required PPE for each work area

### 3.2 Changeover-Specific Hazards

| Line | Hazard | Control Measure |
|------|--------|-----------------|
| Line 1 | Suspended die (crane) | Die change LOTO; hard hat required; no personnel under suspended load |
| Line 1 | Stored hydraulic/pneumatic energy | Bleed pressure before die removal; verify zero energy |
| Line 1 | Sharp die edges | Cut-resistant gloves (ANSI A4); handle dies with lifting equipment only |
| Line 2 | Unexpected robot motion | Robot in teach mode or LOTO; safeguarded stop before cell entry |
| Line 2 | Pinch points (fixture change) | LOTO required; verify zero energy before fixture work |
| Line 2 | Electrical (servo tools) | LOTO electrical before tooling change |
| Line 3 | Conveyor motion | LOTO or controlled stop before adjustment |
| Line 3 | Stretch wrap machine | LOTO before any film path or turntable adjustment |
| All | Slip/trip hazards | Maintain housekeeping during changeover; clean up immediately |

### 3.3 LOTO Requirements by Changeover Type

| Changeover Activity | LOTO Required | Reference Procedure |
|---------------------|---------------|---------------------|
| Die change (Line 1) | Yes — Full press LOTO | LOTO-L1-001 |
| Coil change (Line 1) | Yes — Coil line LOTO | LOTO-L1-003 |
| Robot program change only | No — Teach mode acceptable | N/A |
| Robot tooling change | Yes — Robot cell LOTO | LOTO-L2-001 |
| Fixture change (Line 2) | Yes — Station LOTO | LOTO-L2-002 |
| Conveyor adjustment (Line 3) | Yes — Section LOTO | LOTO-L3-001 |
| Labeler changeover | Yes — Labeler LOTO | LOTO-L3-002 |
| Pack material change only | No — System stopped | N/A |

---

## 4. Roles and Responsibilities

| Role | Responsibilities |
|------|------------------|
| **Line Supervisor** | Authorize changeover start; verify resources available; ensure changeover completed on time; sign off on changeover verification |
| **Setup Technician** | Execute changeover per standard work; perform first-piece inspection; verify tooling and settings; document changeover completion |
| **Operator** | Assist with changeover tasks as assigned; verify material staging; perform quality checks on first production |
| **Maintenance Technician** | Perform LOTO for energy isolation; assist with die/tooling installation; troubleshoot issues; verify equipment function |
| **Quality Engineer** | Approve first-piece inspection; verify dimensional requirements; release production; document quality records |
| **Material Handler** | Stage incoming materials; remove outgoing materials; transport tooling/dies as needed |

---

## 5. Changeover Planning

### 5.1 Pre-Changeover Checklist

Complete this checklist before initiating any changeover:

| Item | Verification | Responsible |
|------|--------------|-------------|
| Production schedule confirms changeover timing | Schedule reviewed | Supervisor |
| Incoming tooling/dies available and inspected | Tooling staged at line | Setup Tech |
| Incoming materials available and verified | Material staged | Material Handler |
| Required personnel available | Team confirmed | Supervisor |
| LOTO equipment available | Locks and tags ready | Maintenance |
| Quality documentation ready (work instructions, spec sheets) | Documents at station | Quality |
| Previous production completed and cleared | Last piece verified | Operator |
| Packaging materials available (Line 3) | Materials staged | Material Handler |

### 5.2 Changeover Scheduling

| Priority | Changeover Type | Advance Notice Required |
|----------|-----------------|------------------------|
| Planned | Scheduled production change | 4 hours minimum |
| Expedited | Customer priority change | 2 hours minimum |
| Emergency | Critical quality or safety issue | Immediate (Supervisor approval) |

### 5.3 Tooling and Material Staging

**Staging Locations:**

| Line | Tooling Staging Area | Material Staging Area |
|------|---------------------|----------------------|
| Line 1 | Die storage racks (adjacent to presses) | Coil staging area |
| Line 2 | Fixture storage rack (end of line) | Component racks at each station |
| Line 3 | Packaging storage (behind pack-out stations) | Carton/pallet staging area |

**Staging Timing:**
- Tooling must be staged at line **minimum 30 minutes** before scheduled changeover
- Materials must be staged **minimum 15 minutes** before scheduled changeover
- Setup Technician verifies staging and reports any shortages to Supervisor

---

## 6. Line 1 Changeover Procedures — Stamping & Forming

### 6.1 Die Change Procedure

**Estimated Time:** 45-90 minutes  
**Personnel Required:** Setup Technician, Maintenance Technician (crane), Operator

**Pre-Die Change:**

| Step | Action | Time (min) | Responsibility |
|------|--------|------------|----------------|
| 1 | Verify new die staged and inspected | — | Setup Tech |
| 2 | Complete last piece of current production | — | Operator |
| 3 | Clear all parts from press area | 5 | Operator |
| 4 | Notify Supervisor changeover starting | — | Setup Tech |

**Die Removal:**

| Step | Action | Time (min) | Responsibility | Safety Note |
|------|--------|------------|----------------|-------------|
| 5 | Stop press; cycle to bottom dead center | 2 | Setup Tech | — |
| 6 | Apply LOTO per LOTO-L1-001 | 5 | Maintenance | All energy sources |
| 7 | Verify zero energy state | 2 | Maintenance | Test start button |
| 8 | Disconnect die sensors and air lines | 3 | Setup Tech | Cap air lines |
| 9 | Release die clamps | 3 | Setup Tech | Verify die secure before release |
| 10 | Attach crane rigging to die | 3 | Maintenance | Inspect rigging; hard hats on |
| 11 | Lift die clear of bolster | 2 | Maintenance | No personnel under load |
| 12 | Transport die to storage rack | 5 | Maintenance | Secure in storage position |
| 13 | Clean bolster surface | 5 | Setup Tech | Remove debris, oil, chips |

**Die Installation:**

| Step | Action | Time (min) | Responsibility | Safety Note |
|------|--------|------------|----------------|-------------|
| 14 | Transport new die to press | 5 | Maintenance | Verify correct die number |
| 15 | Lower die onto bolster; align to locating pins | 5 | Maintenance | No hands in pinch zone |
| 16 | Release rigging when die seated | 2 | Maintenance | Verify die stable |
| 17 | Engage die clamps | 3 | Setup Tech | Torque per specification |
| 18 | Connect die sensors and air lines | 5 | Setup Tech | Verify connections secure |
| 19 | Set shut height per die setup sheet | 5 | Setup Tech | Reference die parameter sheet |
| 20 | Remove LOTO per procedure | 3 | Maintenance | All locks removed |
| 21 | Perform dry cycle (no material) | 2 | Setup Tech | Verify stroke and clearance |
| 22 | Run first piece with material | 3 | Setup Tech | Proceed to quality verification |

**Quality Verification:**

| Step | Action | Time (min) | Responsibility |
|------|--------|------------|----------------|
| 23 | Perform first-piece dimensional inspection | 10 | Setup Tech + Quality |
| 24 | Compare to specification and control plan | 5 | Quality |
| 25 | If acceptable: sign off and release production | 2 | Quality |
| 26 | If not acceptable: adjust and re-run first piece | Varies | Setup Tech |
| 27 | Document changeover on changeover log | 3 | Setup Tech |

**Total Estimated Time:** 75-90 minutes

### 6.2 Coil Change Procedure

**Estimated Time:** 20-30 minutes  
**Personnel Required:** Setup Technician, Material Handler

| Step | Action | Time (min) | Responsibility | Safety Note |
|------|--------|------------|----------------|-------------|
| 1 | Complete current coil (run to end) or stop at safe point | — | Operator | — |
| 2 | Apply LOTO to coil line per LOTO-L1-003 | 5 | Setup Tech | Coil tension hazard |
| 3 | Release coil tension | 2 | Setup Tech | Verify tension released |
| 4 | Remove coil remnant from cradle | 5 | Material Handler | Forklift operation |
| 5 | Stage new coil on cradle | 5 | Material Handler | Verify coil ID matches schedule |
| 6 | Thread material through straightener and feeder | 5 | Setup Tech | Gloves required |
| 7 | Set feeder parameters per setup sheet | 3 | Setup Tech | — |
| 8 | Remove LOTO | 2 | Setup Tech | — |
| 9 | Run test feed (no press cycle) | 2 | Setup Tech | Verify feed length |
| 10 | Document coil change on production log | 2 | Operator | Record coil lot number |

**Total Estimated Time:** 25-30 minutes

### 6.3 Line 1 Changeover Documentation

| Document | Purpose | Completed By |
|----------|---------|--------------|
| Die Setup Sheet | Die-specific parameters (shut height, tonnage, feed length) | Reference during setup |
| First-Piece Inspection Report | Dimensional verification record | Setup Tech + Quality |
| Changeover Log | Time tracking, issues encountered | Setup Tech |
| Production Log | Coil lot, part count, quality notes | Operator |
| LOTO Permit (if required) | Energy control documentation | Maintenance |

---

## 7. Line 2 Changeover Procedures — Assembly & Robot Cells

### 7.1 Robot Program and Tooling Change

**Estimated Time:** 30-60 minutes  
**Personnel Required:** Setup Technician, Maintenance Technician (if LOTO required)

**Pre-Changeover:**

| Step | Action | Time (min) | Responsibility |
|------|--------|------------|----------------|
| 1 | Verify new program and tooling staged | — | Setup Tech |
| 2 | Complete last piece of current production | — | Operator |
| 3 | Clear all parts from robot cell | 5 | Operator |
| 4 | Notify Supervisor changeover starting | — | Setup Tech |

**Program Change (No Tooling Change):**

| Step | Action | Time (min) | Responsibility | Safety Note |
|------|--------|------------|----------------|-------------|
| 5 | Place robot in TEACH mode | 1 | Setup Tech | Reduced speed enabled |
| 6 | Enter robot cell through interlocked gate | 1 | Setup Tech | Gate interlock stops robot |
| 7 | Load new program from teach pendant or network | 5 | Setup Tech | Verify program version |
| 8 | Verify program parameters match setup sheet | 3 | Setup Tech | Check speeds, positions, I/O |
| 9 | Exit cell; close gate | 1 | Setup Tech | — |
| 10 | Set robot to AUTO mode | 1 | Setup Tech | — |
| 11 | Run dry cycle (no parts) | 3 | Setup Tech | Verify motion path |
| 12 | Run first piece with parts | 5 | Setup Tech | Proceed to quality verification |

**Tooling Change (Gripper, Fixture, End Effector):**

| Step | Action | Time (min) | Responsibility | Safety Note |
|------|--------|------------|----------------|-------------|
| 5 | Apply LOTO to robot cell per LOTO-L2-001 | 5 | Maintenance | All energy sources |
| 6 | Verify zero energy state | 2 | Maintenance | — |
| 7 | Enter cell; remove current tooling | 10 | Setup Tech | Use proper lifting techniques |
| 8 | Store removed tooling in designated location | 3 | Setup Tech | Protect tooling from damage |
| 9 | Install new tooling | 10 | Setup Tech | Torque fasteners per spec |
| 10 | Connect pneumatic, electrical, sensor lines | 5 | Setup Tech | Verify secure connections |
| 11 | Exit cell; remove LOTO | 5 | Maintenance | — |
| 12 | Load corresponding program (if not already loaded) | 5 | Setup Tech | Per Section 7.1 above |
| 13 | Place robot in TEACH mode; verify tooling function | 5 | Setup Tech | Test gripper/tool operation |
| 14 | Run dry cycle in AUTO mode | 3 | Setup Tech | — |
| 15 | Run first piece with parts | 5 | Setup Tech | — |

**Quality Verification:**

| Step | Action | Time (min) | Responsibility |
|------|--------|------------|----------------|
| 16 | Perform first-piece inspection per control plan | 10 | Setup Tech + Quality |
| 17 | Verify torque values (if applicable) | 5 | Quality |
| 18 | Perform visual inspection | 3 | Quality |
| 19 | If acceptable: sign off and release production | 2 | Quality |
| 20 | If not acceptable: troubleshoot and re-run | Varies | Setup Tech |
| 21 | Document changeover on changeover log | 3 | Setup Tech |

### 7.2 Fixture Change Procedure

**Estimated Time:** 20-45 minutes  
**Personnel Required:** Setup Technician, Maintenance Technician

| Step | Action | Time (min) | Responsibility | Safety Note |
|------|--------|------------|----------------|-------------|
| 1 | Complete current production; clear parts | 5 | Operator | — |
| 2 | Apply LOTO to station per LOTO-L2-002 | 5 | Maintenance | — |
| 3 | Disconnect fixture utilities (air, electric, sensors) | 3 | Setup Tech | Cap connections |
| 4 | Release fixture clamps | 2 | Setup Tech | — |
| 5 | Remove fixture using lifting equipment if >50 lbs | 5 | Setup Tech | — |
| 6 | Clean station surface | 3 | Setup Tech | — |
| 7 | Install new fixture; align to locating pins | 5 | Setup Tech | — |
| 8 | Engage fixture clamps | 2 | Setup Tech | Torque per spec |
| 9 | Connect utilities | 3 | Setup Tech | Verify connections |
| 10 | Remove LOTO | 3 | Maintenance | — |
| 11 | Test fixture function (clamps, sensors) | 3 | Setup Tech | — |
| 12 | Run first piece and verify | 5 | Setup Tech + Quality | — |

### 7.3 Line 2 Changeover Documentation

| Document | Purpose | Completed By |
|----------|---------|--------------|
| Robot Setup Sheet | Program name, tool number, parameters | Reference during setup |
| Fixture Setup Sheet | Fixture ID, clamp settings, sensor positions | Reference during setup |
| First-Piece Inspection Report | Dimensional and torque verification | Setup Tech + Quality |
| Changeover Log | Time tracking, issues encountered | Setup Tech |
| LOTO Permit | Energy control documentation | Maintenance |

---

## 8. Line 3 Changeover Procedures — Conveyor & Pack-Out

### 8.1 Pack Configuration Change

**Estimated Time:** 15-30 minutes  
**Personnel Required:** Setup Technician, Operator

**Pre-Changeover:**

| Step | Action | Time (min) | Responsibility |
|------|--------|------------|----------------|
| 1 | Verify new packaging materials staged | — | Material Handler |
| 2 | Complete current production run | — | Operator |
| 3 | Clear product from pack-out stations and conveyor | 5 | Operator |

**Pack-Out Station Change:**

| Step | Action | Time (min) | Responsibility |
|------|--------|------------|----------------|
| 4 | Stop conveyor system (SYSTEM STOP) | 1 | Operator |
| 5 | Remove remaining packaging materials from stations | 3 | Operator |
| 6 | Stage new cartons/trays at pack stations | 3 | Material Handler |
| 7 | Adjust carton guides/holders if needed | 5 | Setup Tech |
| 8 | Load new label format on labeler (if applicable) | See 8.2 | — |
| 9 | Update pallet pattern on palletizer HMI | 3 | Setup Tech |
| 10 | Restart conveyor system | 1 | Operator |
| 11 | Run first units through pack-out | 5 | Operator |
| 12 | Verify pack count, label placement, pallet pattern | 5 | Quality |
| 13 | Document changeover | 2 | Setup Tech |

### 8.2 Labeler Changeover

**Estimated Time:** 10-20 minutes  
**Personnel Required:** Setup Technician

| Step | Action | Time (min) | Responsibility | Safety Note |
|------|--------|------------|----------------|-------------|
| 1 | Stop conveyor section (SYSTEM STOP at CV3-009) | 1 | Setup Tech | — |
| 2 | Apply LOTO to labeler per LOTO-L3-002 | 3 | Setup Tech | — |
| 3 | Remove remaining labels from applicator | 2 | Setup Tech | — |
| 4 | Load new label roll | 3 | Setup Tech | Verify label matches product |
| 5 | Thread label web through print head and applicator | 3 | Setup Tech | — |
| 6 | Load new label format on labeler controller | 2 | Setup Tech | Select from library |
| 7 | Adjust label position sensors if needed | 2 | Setup Tech | — |
| 8 | Remove LOTO | 2 | Setup Tech | — |
| 9 | Print test label and verify content | 2 | Setup Tech | — |
| 10 | Run test product through labeler | 2 | Setup Tech | — |
| 11 | Verify label placement and scannability | 2 | Quality | Scan barcode to verify |
| 12 | Document changeover | 1 | Setup Tech | — |

### 8.3 Stretch Wrap Parameter Change

**Estimated Time:** 5-10 minutes  
**Personnel Required:** Operator

| Step | Action | Time (min) | Responsibility |
|------|--------|------------|----------------|
| 1 | Stop stretch wrap machine | 1 | Operator |
| 2 | Access wrap parameters on HMI | 1 | Operator |
| 3 | Select new wrap program or adjust parameters | 2 | Operator |
| 4 | Verify film tension and wrap count settings | 1 | Operator |
| 5 | Run test pallet through wrapper | 3 | Operator |
| 6 | Verify wrap quality (coverage, tension, stability) | 2 | Quality |
| 7 | Document setting change | 1 | Operator |

### 8.4 Palletizer Pattern Change

**Estimated Time:** 5-15 minutes  
**Personnel Required:** Setup Technician

| Step | Action | Time (min) | Responsibility |
|------|--------|------------|----------------|
| 1 | Complete current pallet | — | Operator |
| 2 | Remove completed pallet from palletizer | 2 | Operator |
| 3 | Access palletizer HMI | 1 | Setup Tech |
| 4 | Select new pallet pattern from library | 2 | Setup Tech |
| 5 | Verify pattern parameters (layer count, orientation) | 2 | Setup Tech |
| 6 | Load empty pallet | 2 | Operator |
| 7 | Run first layer and verify pattern | 3 | Setup Tech |
| 8 | Complete first pallet and verify stability | 5 | Quality |
| 9 | Document pattern change | 1 | Setup Tech |

### 8.5 Line 3 Changeover Documentation

| Document | Purpose | Completed By |
|----------|---------|--------------|
| Pack-Out Specification | Pack count, carton type, label requirements | Reference |
| Label Approval Sample | Approved label for verification | Quality |
| Pallet Pattern Diagram | Layer configuration and orientation | Reference |
| Changeover Log | Time tracking, issues encountered | Setup Tech |

---

## 9. Material Lot Change Procedure

### 9.1 General Lot Change (All Lines)

When changing to a new material lot of the same part number:

| Step | Action | Responsibility | Quality Impact |
|------|--------|----------------|----------------|
| 1 | Verify new lot documentation (C of C, inspection report) | Quality | Material traceability |
| 2 | Confirm new lot is approved for use | Quality | Prevent use of unapproved material |
| 3 | Complete current lot or segregate remainder | Operator | Prevent lot mixing |
| 4 | Clear production area of previous lot material | Operator | Prevent lot mixing |
| 5 | Stage new lot material at line | Material Handler | — |
| 6 | Update lot number in production tracking system | Operator | Traceability |
| 7 | Run first piece and perform inspection | Setup Tech + Quality | Verify material conformance |
| 8 | Document lot change on production log | Operator | Traceability record |

### 9.2 Lot Segregation Requirements

| Situation | Action |
|-----------|--------|
| Completing lot with small remainder | Run to completion; scrap or return remainder per procedure |
| Switching mid-run (production requirement) | Physically segregate remaining material; label clearly with lot number |
| Suspect material identified | Stop production; segregate material; notify Quality immediately |

---

## 10. First-Piece Inspection Requirements

### 10.1 Inspection Matrix by Line

| Line | Inspection Type | Performed By | Documented On |
|------|-----------------|--------------|---------------|
| Line 1 | Dimensional (per control plan) | Setup Tech, verified by Quality | First-Piece Report |
| Line 1 | Visual (surface defects, burrs) | Setup Tech | First-Piece Report |
| Line 2 | Dimensional (per control plan) | Setup Tech, verified by Quality | First-Piece Report |
| Line 2 | Torque verification (if applicable) | Quality | Torque Log |
| Line 2 | Functional test (fit, assembly) | Quality | First-Piece Report |
| Line 3 | Pack count verification | Operator | Pack-Out Log |
| Line 3 | Label content and placement | Quality | Label Verification Log |
| Line 3 | Pallet pattern verification | Quality | Pack-Out Log |

### 10.2 First-Piece Hold

Production shall not proceed beyond first piece until:
1. First-piece inspection is completed
2. All dimensions are within specification
3. Quality Engineer has signed approval
4. Any discrepancies are resolved and documented

**First-Piece Hold Time Limit:** Maximum 30 minutes for Quality response; escalate to Supervisor if exceeded.

### 10.3 First-Piece Failure

If first piece does not meet specification:

| Step | Action | Responsibility |
|------|--------|----------------|
| 1 | Segregate non-conforming piece | Setup Tech |
| 2 | Identify probable cause (setup, tooling, material) | Setup Tech + Quality |
| 3 | Adjust setup parameters as appropriate | Setup Tech |
| 4 | Run additional piece(s) for verification | Setup Tech |
| 5 | Repeat first-piece inspection | Quality |
| 6 | If repeated failures, escalate to Supervisor and Engineering | Supervisor |
| 7 | Document all attempts and corrective actions | Quality |

---

## 11. Changeover Time Tracking

### 11.1 Changeover Time Definitions

| Metric | Definition |
|--------|------------|
| **Changeover Start** | Last good piece of previous production completed |
| **Changeover End** | First good piece of new production approved by Quality |
| **Changeover Time** | Total elapsed time from start to end |
| **Internal Time** | Tasks performed while line is stopped |
| **External Time** | Tasks that can be performed while line is running |

### 11.2 Target Changeover Times

| Line | Changeover Type | Target Time | Maximum Allowed |
|------|-----------------|-------------|-----------------|
| Line 1 | Die change | 60 min | 90 min |
| Line 1 | Coil change | 20 min | 30 min |
| Line 2 | Program + tooling change | 45 min | 60 min |
| Line 2 | Program only | 20 min | 30 min |
| Line 2 | Fixture change | 30 min | 45 min |
| Line 3 | Pack configuration | 15 min | 30 min |
| Line 3 | Full changeover (label + pack + pallet) | 25 min | 40 min |

### 11.3 Changeover Time Tracking Log

| Field | Entry |
|-------|-------|
| Date | |
| Line | |
| Changeover Type | |
| From Part Number | |
| To Part Number | |
| Start Time | |
| End Time | |
| Total Time | |
| Target Time | |
| Variance | |
| Delays/Issues | |
| Performed By | |
| Verified By | |

---

## 12. SMED Principles (Single-Minute Exchange of Die)

### 12.1 External vs. Internal Tasks

To reduce changeover time, maximize external tasks (performed while line is running):

**External Tasks (Perform BEFORE stopping line):**
- Stage new tooling/dies at line
- Stage new materials and verify quantities
- Gather required tools and equipment
- Review setup documentation
- Pre-heat dies (if applicable)
- Prepare quality inspection equipment
- Print new labels in advance

**Internal Tasks (Require line stopped):**
- Remove current tooling/dies
- Install new tooling/dies
- Adjust machine parameters
- Perform first-piece inspection

### 12.2 Parallel Operations

Where safe and practical, perform tasks simultaneously:

| Primary Task | Parallel Task | Personnel |
|--------------|---------------|-----------|
| Die removal (Maintenance) | Clean new die (Setup Tech) | 2 |
| Program loading (Setup Tech) | Material staging (Material Handler) | 2 |
| Labeler changeover (Setup Tech) | Pack station material change (Operator) | 2 |

### 12.3 Standardization

| Standardization Area | Benefit |
|---------------------|---------|
| Standard die clamp locations | Reduce alignment time |
| Quick-change tooling connections | Reduce connect/disconnect time |
| Standard label roll sizes | Eliminate labeler adjustment |
| Color-coded fixtures | Reduce selection errors |
| Pre-set torque tool programs | Eliminate parameter entry |

---

## 13. Troubleshooting Changeover Issues

### 13.1 Common Issues and Remedies

| Issue | Possible Cause | Remedy |
|-------|----------------|--------|
| Tooling not available at start time | Late scheduling, storage issue | Verify staging 30 min before changeover |
| Wrong tooling staged | Mislabeling, pick error | Verify tooling ID before transport |
| Die won't seat properly | Debris on bolster, damaged locators | Clean bolster; inspect locating pins |
| Robot program error | Wrong version, parameter mismatch | Verify program version on setup sheet |
| First piece fails inspection | Setup error, tooling wear, material variation | Systematic troubleshooting per Section 10.3 |
| Changeover exceeds target time | Insufficient preparation, equipment issues | Review against external/internal task split |
| Missing LOTO equipment | Not returned from previous use | Verify LOTO kits before changeover |

### 13.2 Escalation Path

| Delay | Action | Escalate To |
|-------|--------|-------------|
| 15 min over target | Document cause; continue | Supervisor (notification) |
| 30 min over target | Request additional support | Supervisor (active involvement) |
| 60 min over target | Stop and assess; consider alternate plan | Production Manager |
| Equipment failure during changeover | Initiate maintenance work order | Maintenance Supervisor |

---

## 14. Quality Records and Traceability

### 14.1 Required Documentation

| Document | Retention | Location |
|----------|-----------|----------|
| First-Piece Inspection Report | 3 years | Quality Office |
| Changeover Log | 1 year | Production Office |
| LOTO Permits | 1 year | EHS Office |
| Setup Sheets (reference) | Life of product | Document Control |
| Material Lot Records | Per customer requirement (typically 15 years for safety-critical) | Quality Office |

### 14.2 Traceability Requirements

For safety-critical components, the following traceability must be maintained:

| Information | Recorded On | Verification |
|-------------|-------------|--------------|
| Part number | Production log, shipping documents | Matches work order |
| Lot/serial number | Label, production log | Unique identifier applied |
| Material lot | Production log | Links to material C of C |
| Die/tooling used | Changeover log | Links to tooling maintenance records |
| Operator ID | Production log | Training verification |
| Inspection results | First-piece report | Quality approval |
| Date/time of production | Production log | Shift traceability |

---

## 15. Training Requirements

### 15.1 Training Matrix

| Role | Initial Training | Annual Refresher | Certification |
|------|------------------|------------------|---------------|
| Operator | Line-specific changeover assistance | ✓ | — |
| Setup Technician | Full changeover procedure (line-specific) | ✓ | Changeover Certified |
| Maintenance Technician | LOTO, equipment-specific changeover | ✓ | LOTO Authorized |
| Quality Engineer | First-piece inspection, release authority | ✓ | — |
| Supervisor | Changeover oversight, time tracking | ✓ | — |

### 15.2 Qualification Requirements

Setup Technicians must demonstrate competency on:
- Minimum 3 supervised changeovers per changeover type
- First-piece inspection procedures
- LOTO application (if applicable)
- Troubleshooting common issues
- Documentation completion

---

## 16. Continuous Improvement

### 16.1 Changeover Time Reduction Initiatives

| Initiative | Method | Frequency |
|------------|--------|-----------|
| Video analysis | Record changeover; identify waste | As needed |
| Time studies | Detailed task timing | Quarterly |
| Kaizen events | Cross-functional improvement teams | Semi-annually |
| Suggestion program | Operator and technician ideas | Ongoing |

### 16.2 Performance Metrics

| Metric | Target | Review Frequency |
|--------|--------|------------------|
| Average changeover time vs. target | ≤100% of target | Weekly |
| Changeovers exceeding maximum | <5% of total | Monthly |
| First-piece acceptance rate | >95% | Weekly |
| Changeover-related downtime | <2% of production time | Monthly |

---

## 17. Related Documents

| Document ID | Title |
|-------------|-------|
| MMC_P7_LOTO_SOP | Lockout/Tagout Standard Operating Procedure |
| MMC_P7_Machine_Guarding_SOP | Machine Guarding Standard Operating Procedure |
| MMC_P7_PPE_Matrix | Personal Protective Equipment Matrix |
| MMC_P7_Quality_Policy | Quality Policy and Management System |
| MMC_P7_Shift_Handover_Guidelines | Shift Handover Guidelines |
| MMC_P7_PM_Program_Overview | Preventive Maintenance Program Overview |

---

## 18. Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-01-26 | Production Manager | Initial release |

---

## Appendix A: Changeover Checklist — Line 1 Die Change

**Date:** __________ **From P/N:** __________ **To P/N:** __________

| Phase | Task | ✓ | Time |
|-------|------|---|------|
| **Pre-Changeover** | New die staged at press | ☐ | |
| | Die inspected (no damage) | ☐ | |
| | Setup sheet available | ☐ | |
| | LOTO equipment ready | ☐ | |
| | Quality notified | ☐ | |
| **Current Production** | Last piece completed | ☐ | |
| | Parts cleared from area | ☐ | |
| **Die Removal** | LOTO applied | ☐ | |
| | Zero energy verified | ☐ | |
| | Die sensors/air disconnected | ☐ | |
| | Die clamps released | ☐ | |
| | Die removed via crane | ☐ | |
| | Die stored properly | ☐ | |
| | Bolster cleaned | ☐ | |
| **Die Installation** | New die transported | ☐ | |
| | Die lowered and aligned | ☐ | |
| | Die clamps engaged | ☐ | |
| | Sensors/air connected | ☐ | |
| | Shut height set | ☐ | |
| | LOTO removed | ☐ | |
| **Verification** | Dry cycle completed | ☐ | |
| | First piece run | ☐ | |
| | First-piece inspection passed | ☐ | |
| | Quality release obtained | ☐ | |
| | Changeover log completed | ☐ | |

**Start Time:** __________ **End Time:** __________ **Total Time:** __________

**Setup Tech:** _________________ **Supervisor:** _________________

---

## Appendix B: Changeover Checklist — Line 2 Robot Cell

**Date:** __________ **From P/N:** __________ **To P/N:** __________

| Phase | Task | ✓ | Time |
|-------|------|---|------|
| **Pre-Changeover** | New tooling staged | ☐ | |
| | Program verified available | ☐ | |
| | Setup sheet available | ☐ | |
| | Materials staged | ☐ | |
| **Current Production** | Last piece completed | ☐ | |
| | Parts cleared from cell | ☐ | |
| **Tooling Change** | LOTO applied (if required) | ☐ | |
| | Current tooling removed | ☐ | |
| | Tooling stored properly | ☐ | |
| | New tooling installed | ☐ | |
| | Connections made | ☐ | |
| | LOTO removed | ☐ | |
| **Program Change** | Program loaded | ☐ | |
| | Parameters verified | ☐ | |
| | Teach mode test | ☐ | |
| **Verification** | Dry cycle (AUTO) | ☐ | |
| | First piece run | ☐ | |
| | Dimensional inspection | ☐ | |
| | Torque verification (if applicable) | ☐ | |
| | Quality release obtained | ☐ | |

**Start Time:** __________ **End Time:** __________ **Total Time:** __________

**Setup Tech:** _________________ **Supervisor:** _________________

---

## Appendix C: Changeover Checklist — Line 3 Pack-Out

**Date:** __________ **From P/N:** __________ **To P/N:** __________

| Phase | Task | ✓ | Time |
|-------|------|---|------|
| **Pre-Changeover** | New packaging materials staged | ☐ | |
| | New labels available | ☐ | |
| | Pallet pattern identified | ☐ | |
| **Current Production** | Line cleared of product | ☐ | |
| | Last pallet completed | ☐ | |
| **Pack Station Change** | Conveyor stopped | ☐ | |
| | Old materials removed | ☐ | |
| | New cartons/trays staged | ☐ | |
| | Guides adjusted | ☐ | |
| **Labeler Change** | LOTO applied | ☐ | |
| | New labels loaded | ☐ | |
| | Format selected | ☐ | |
| | LOTO removed | ☐ | |
| | Test label printed | ☐ | |
| **Palletizer Change** | Pattern selected | ☐ | |
| | Parameters verified | ☐ | |
| **Verification** | First units packed | ☐ | |
| | Pack count verified | ☐ | |
| | Label verified (scan test) | ☐ | |
| | Pallet pattern verified | ☐ | |
| | Quality release obtained | ☐ | |

**Start Time:** __________ **End Time:** __________ **Total Time:** __________

**Setup Tech:** _________________ **Supervisor:** _________________

---

## Appendix D: First-Piece Inspection Report

**Line:** __________ **Part Number:** __________ **Date:** __________  
**Setup Technician:** _________________ **Quality Engineer:** _________________

**Setup Information:**
| Field | Value |
|-------|-------|
| Die/Tooling ID | |
| Program Version | |
| Material Lot Number | |
| Machine/Cell ID | |

**Dimensional Inspection:**
| Dimension | Specification | Tolerance | Measured Value | Pass/Fail |
|-----------|---------------|-----------|----------------|-----------|
| | | ± | | ☐ P ☐ F |
| | | ± | | ☐ P ☐ F |
| | | ± | | ☐ P ☐ F |
| | | ± | | ☐ P ☐ F |
| | | ± | | ☐ P ☐ F |

**Visual Inspection:**
| Attribute | Acceptable | Not Acceptable |
|-----------|:----------:|:--------------:|
| Surface finish | ☐ | ☐ |
| Burrs/sharp edges | ☐ | ☐ |
| Cosmetic defects | ☐ | ☐ |
| Correct part marking | ☐ | ☐ |

**Functional Test (if applicable):**
| Test | Result | Pass/Fail |
|------|--------|-----------|
| | | ☐ P ☐ F |
| | | ☐ P ☐ F |

**Disposition:**
☐ **APPROVED** — Production may proceed  
☐ **REJECTED** — Adjustments required (see notes)

**Notes:**
____________________________________________________________________________
____________________________________________________________________________

**Signatures:**
Setup Technician: _________________ Date/Time: _____________  
Quality Engineer: _________________ Date/Time: _____________

---

**End of Document**
