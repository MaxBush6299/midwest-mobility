# MMC Plant 7 — Jam Clearing Work Instruction
**Document ID:** MMC_P7_Jam_Clearing_WI  
**Document Owner:** Maintenance Supervisor, Plant 7  
**Version:** v1.0  
**Effective Date:** 2026-01-26  
**Review Cycle:** Annual  
**Applies To:** All personnel authorized to clear jams on production equipment at MMC Plant 7

---

## 1. Purpose

This work instruction establishes safe procedures for clearing jams on production equipment at MMC Plant 7. Jam clearing is a high-risk activity that can expose personnel to hazardous energy, pinch points, and unexpected machine motion. Following these procedures protects employees from serious injury.

---

## 2. Scope

This instruction applies to:
- All jam clearing activities on Lines 1, 2, and 3
- All jam clearing on auxiliary equipment (conveyors, feeders, transfer systems)
- All personnel authorized to clear jams (Operators, Setup Technicians, Maintenance Technicians)
- All shifts (1st, 2nd, 3rd)

**Equipment Covered:**

| Line | Equipment | Common Jam Types |
|------|-----------|------------------|
| Line 1 | Stamping presses | Misfed blanks, stuck parts in die, scrap buildup |
| Line 1 | Coil feed system | Coil edge curl, loop loss, material buckle |
| Line 1 | Scrap conveyor | Scrap accumulation, slug jam |
| Line 2 | Robot cells | Part misposition, gripper failure, nest obstruction |
| Line 2 | Servo torque stations | Fastener cross-thread, socket jam |
| Line 2 | Parts feeders | Bowl feeder jam, track blockage |
| Line 3 | Main conveyor | Product tip-over, accumulation backup |
| Line 3 | Stretch wrap machine | Film break, wrap tangle, turntable jam |
| Line 3 | Labeling system | Label jam, backing paper buildup |
| Line 3 | Palletizer | Misaligned load, gripper jam |

---

## 3. Hazard Identification

### 3.1 Primary Hazards During Jam Clearing

| Hazard | Source | Potential Injury |
|--------|--------|------------------|
| Unexpected startup | Machine activation during clearing | Amputation, crushing, death |
| Stored energy release | Springs, counterweights, pneumatics | Crushing, struck-by |
| Pinch points | Rollers, belts, gears, dies | Amputation, laceration, fracture |
| Sharp edges | Cut material, tooling, scrap | Laceration |
| Falling objects | Elevated parts, dies, product | Struck-by, crushing |
| Electrical shock | Energized components | Electrocution, burns |
| Caught-in | Rotating shafts, conveyors, feed mechanisms | Entanglement, amputation |
| Ergonomic strain | Awkward postures, forceful exertion | Musculoskeletal injury |

### 3.2 Hazard Severity by Line

| Line | Highest Risk Hazards | Severity |
|------|---------------------|----------|
| Line 1 — Stamping | Press activation, die closing, coil tension | Critical — Death/Amputation |
| Line 2 — Robot Cells | Robot motion, servo tool activation | High — Crushing/Struck-by |
| Line 3 — Conveyor | Conveyor startup, palletizer motion | Medium — Pinch/Caught-in |

---

## 4. Authorization Requirements

### 4.1 Authorization Matrix

| Task | Operator | Setup Tech | Maintenance Tech | Supervisor |
|------|:--------:|:----------:|:----------------:|:----------:|
| Clear jam with machine stopped (no guard removal) | ✓ | ✓ | ✓ | ✓ |
| Clear jam requiring guard removal (LOTO) | — | ✓ | ✓ | — |
| Clear jam in robot cell (safeguarded stop) | — | ✓ | ✓ | — |
| Clear jam in press die (LOTO required) | — | — | ✓ | — |
| Clear jam requiring troubleshooting | — | — | ✓ | — |

### 4.2 Training Requirements

Personnel must complete the following training before performing jam clearing:

| Training | Required For | Frequency |
|----------|--------------|-----------|
| Jam Clearing Awareness | All Operators | Initial + Annual |
| Jam Clearing — Authorized | Setup Techs, Maintenance | Initial + Annual |
| LOTO Authorized Person | Setup Techs, Maintenance | Initial + Annual |
| Equipment-Specific Jam Clearing | By equipment assignment | Initial + as needed |
| Robot Cell Entry | Robot cell personnel | Initial + Annual |

---

## 5. General Jam Clearing Procedure

### 5.1 Decision Tree — Is LOTO Required?

```
                    JAM DETECTED
                         │
                         ▼
        ┌─── Can jam be cleared from OUTSIDE ───┐
        │         the hazard zone?              │
        │                                       │
       YES                                      NO
        │                                       │
        ▼                                       ▼
  Machine STOPPED?                    LOTO REQUIRED
        │                            Go to Section 6
       YES
        │
        ▼
  ┌─── Is guard removal required? ───┐
  │                                  │
  NO                                YES
  │                                  │
  ▼                                  ▼
Clear jam per                   LOTO REQUIRED
Section 5.2                    Go to Section 6
```

### 5.2 Minor Jam Clearing (No Guard Removal, No LOTO)

**Conditions for Minor Jam Clearing:**
- Machine is fully stopped (not in pause or standby)
- Jam can be cleared without entering hazard zone
- No guard removal required
- No stored energy hazard present
- Jam visible and accessible from operator position

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Press E-STOP or stop machine using normal controls | Machine fully stopped; all motion ceased |
| 2 | Notify nearby personnel of jam condition | Verbal confirmation |
| 3 | Visually assess jam location and cause | Identify root cause if possible |
| 4 | Using appropriate tool (not hands), clear jammed material | Material removed; path clear |
| 5 | Inspect for damage to equipment or product | No visible damage; if damage found, notify Supervisor |
| 6 | Reset E-STOP (if used) | E-STOP released |
| 7 | Verify all personnel are clear | Visual confirmation |
| 8 | Restart equipment per normal procedure | Machine operating normally |
| 9 | Monitor first cycles for repeat jam | No recurrence |
| 10 | If jam recurs, escalate to Setup or Maintenance | Notify Supervisor |

**Tools for Minor Jam Clearing:**
- Brass rod or wooden dowel (no steel tools near dies)
- Plastic pry tool
- Vacuum wand (for small debris)
- Long-handled hook (for material retrieval)

---

## 6. Jam Clearing Requiring LOTO

### 6.1 When LOTO Is Required

LOTO is **always required** when:
- Guard removal is necessary to access the jam
- Entry into the hazard zone is required
- Body parts could be placed in pinch points, dies, or rotating equipment
- Stored energy could cause motion
- Troubleshooting is required beyond simple material removal

### 6.2 LOTO Jam Clearing Procedure

| Step | Action | Responsibility |
|------|--------|----------------|
| 1 | Stop equipment using normal controls | Operator/Technician |
| 2 | Notify Supervisor of jam requiring LOTO | Operator/Technician |
| 3 | Notify affected personnel in the area | Technician |
| 4 | Locate equipment-specific LOTO procedure | Technician |
| 5 | Identify all energy sources and isolation points | Technician |
| 6 | Isolate all energy sources per LOTO procedure | Authorized Employee |
| 7 | Apply personal lock and tag to each isolation point | Authorized Employee |
| 8 | Dissipate/restrain stored energy | Authorized Employee |
| 9 | Verify zero energy state (try to start) | Authorized Employee |
| 10 | Remove guards as needed to access jam | Authorized Employee |
| 11 | Clear jam using appropriate tools and methods | Authorized Employee |
| 12 | Inspect for equipment damage | Authorized Employee |
| 13 | Remove all tools and debris from equipment | Authorized Employee |
| 14 | Replace all guards and verify secure | Authorized Employee |
| 15 | Verify all personnel are clear | Authorized Employee |
| 16 | Remove personal lock and tag | Authorized Employee |
| 17 | Re-energize equipment | Authorized Employee |
| 18 | Test equipment operation | Authorized Employee |
| 19 | Return to production | Supervisor |

**Reference:** MMC_P7_LOTO_SOP for complete lockout procedure

---

## 7. Line-Specific Jam Clearing Procedures

### 7.1 Line 1 — Stamping & Forming

#### 7.1.1 Press Jam (Part Stuck in Die)

**Hazards:** Die closing, ram drop, hydraulic release, pinch points

**LOTO Required:** Yes — Always

| Step | Action | Notes |
|------|--------|-------|
| 1 | Press E-STOP immediately | Do not attempt to jog or cycle |
| 2 | Notify Supervisor and Maintenance | Log in downtime system |
| 3 | Apply LOTO per LOTO-L1-001 or LOTO-L1-002 | Lock out main disconnect, hydraulics, pneumatics |
| 4 | Block ram in UP position using die block | Never work under unsupported ram |
| 5 | Verify zero energy state | Attempt to cycle press at controls |
| 6 | Remove stuck part using brass tools only | Do not use steel tools in die |
| 7 | Inspect die for damage | Check cutting edges, forming surfaces |
| 8 | Inspect part for defects | Segregate suspect parts for Quality |
| 9 | Remove die block | Verify clear before removal |
| 10 | Remove LOTO and restore per procedure | Verify guards in place |
| 11 | Run first part and verify quality | Quality inspection required |

**Die Block Requirement:** Die blocks must be rated for the tonnage of the press. Die blocks are stored at each press and inspected monthly.

#### 7.1.2 Coil Feed Jam

**Hazards:** Coil tension release, pinch points, sharp edges

**LOTO Required:** Yes — If entering feed area or working near coil

| Step | Action | Notes |
|------|--------|-------|
| 1 | Stop coil line and press | Use line stop, not E-STOP if possible |
| 2 | Apply LOTO per LOTO-L1-003 | Lock out feed motor, press, loop control |
| 3 | Release coil tension using controlled release | Never cut tensioned material |
| 4 | Clear buckled or misaligned material | Use gloves; material edges are sharp |
| 5 | Re-thread material if necessary | Follow standard threading procedure |
| 6 | Restore loop control settings | Verify settings per job setup sheet |
| 7 | Remove LOTO and restart | Monitor first 5 cycles |

#### 7.1.3 Scrap Conveyor Jam

**Hazards:** Conveyor startup, pinch points, sharp scrap

**LOTO Required:** Yes — If reaching into conveyor trough

| Step | Action | Notes |
|------|--------|-------|
| 1 | Stop scrap conveyor | Use local stop or E-STOP |
| 2 | Apply LOTO per LOTO-L1-004 | Lock out conveyor motor |
| 3 | Clear scrap accumulation using rake tool | Wear cut-resistant gloves |
| 4 | Check for damaged belt or cleats | Report damage to Maintenance |
| 5 | Remove LOTO and restart | Monitor for repeat jam |

---

### 7.2 Line 2 — Assembly & Robot Cells

#### 7.2.1 Robot Cell Jam (Part Misposition)

**Hazards:** Robot motion, servo tool activation, pneumatic grippers

**Entry Method:** Safeguarded stop via teach pendant OR LOTO

| Method | When Used |
|--------|-----------|
| Safeguarded Stop (Teach Pendant) | Quick jam clear by trained robot operator; no maintenance required |
| Full LOTO | Maintenance required; working on robot hardware; extended duration |

**Safeguarded Stop Procedure:**

| Step | Action | Notes |
|------|--------|-------|
| 1 | Press cell E-STOP | All motion stops; robot holds position |
| 2 | Obtain teach pendant from lockbox | Key held by trained personnel only |
| 3 | Select TEACH mode on pendant | Robot enters safeguarded state |
| 4 | Enable light curtain bypass using key switch | Bypass active only with key |
| 5 | Enter cell through designated access point | Maintain awareness of robot position |
| 6 | Clear mispositioned part manually | Do not reach into gripper unless open |
| 7 | Exit cell and secure access point | Verify no personnel in cell |
| 8 | Return teach pendant to lockbox | Lock box |
| 9 | Reset light curtain bypass | Key switch to RUN |
| 10 | Reset cell and resume production | Monitor first 3 cycles |

**LOTO Procedure (Extended Work):**

| Step | Action | Notes |
|------|--------|-------|
| 1 | Press cell E-STOP | All motion stops |
| 2 | Apply LOTO per LOTO-L2-001/002/003 | Lock out robot controller, pneumatics, conveyors |
| 3 | Vent pneumatic lines | Bleed grippers and cylinders |
| 4 | Verify zero energy state | Enable teach pendant and verify no motion |
| 5 | Perform jam clearing or maintenance | |
| 6 | Exit cell and remove LOTO | |
| 7 | Perform home sequence and resume | |

#### 7.2.2 Servo Torque Station Jam

**Hazards:** Servo motor torque, fastener ejection, pinch points

**LOTO Required:** Yes — If reaching into tool area

| Step | Action | Notes |
|------|--------|-------|
| 1 | Stop station (E-STOP or cycle stop) | Tool stops mid-cycle |
| 2 | Apply LOTO per LOTO-L2-004 | Lock out servo controller, pneumatics |
| 3 | Manually back out cross-threaded fastener | Use appropriate bit or extractor |
| 4 | Clear socket jam using pick tool | Do not use fingers |
| 5 | Inspect socket and replace if damaged | |
| 6 | Remove LOTO and reset station | Run test cycle before production |

#### 7.2.3 Parts Feeder Jam (Bowl Feeder / Track)

**Hazards:** Vibration startup, pinch points, parts ejection

**LOTO Required:** Situational — Yes if hands enter bowl area

| Step | Action | Notes |
|------|--------|-------|
| 1 | Stop feeder using local controls | Bowl stops vibrating |
| 2 | If track jam only, clear with pick tool from outside | No LOTO needed |
| 3 | If bowl jam, apply LOTO to feeder | Lock out vibrator motor |
| 4 | Clear tangled or bridged parts | Wear safety glasses |
| 5 | Verify orientation tooling not damaged | |
| 6 | Remove LOTO and restart | Observe feed rate |

---

### 7.3 Line 3 — Conveyor & Pack-Out

#### 7.3.1 Main Conveyor Jam (Product Accumulation)

**Hazards:** Conveyor startup, pinch points at rollers, falling product

**LOTO Required:** Situational — Yes if reaching between rollers or under conveyor

| Step | Action | Notes |
|------|--------|-------|
| 1 | Press conveyor STOP (local or E-STOP) | Conveyor stops; product may continue to arrive |
| 2 | Notify upstream stations to stop feeding | Prevent additional accumulation |
| 3 | If product accessible from top, manually reposition | Wear gloves; no LOTO needed |
| 4 | If product under/between rollers, apply LOTO per LOTO-L3-001 | Lock out conveyor drives |
| 5 | Clear jammed product | Do not force; may indicate conveyor issue |
| 6 | Inspect product for damage | Segregate damaged product |
| 7 | Remove LOTO and restart | Notify upstream to resume |

#### 7.3.2 Stretch Wrap Machine Jam

**Hazards:** Turntable rotation, film carriage motion, entanglement

**LOTO Required:** Yes — For film carriage or turntable access

| Step | Action | Notes |
|------|--------|-------|
| 1 | Press E-STOP on stretch wrap machine | All motion stops |
| 2 | Apply LOTO per LOTO-L3-002 | Lock out turntable and carriage drives |
| 3 | Cut tangled film using safety cutter | Do not use box cutter or knife |
| 4 | Clear film from rollers and carriage | Watch for spring-loaded rollers |
| 5 | Rethread film per setup procedure | |
| 6 | Remove LOTO and restart | Run empty test cycle |

**Film Break Procedure (No LOTO if accessible):**

| Step | Action | Notes |
|------|--------|-------|
| 1 | Press STOP (not E-STOP if not needed) | Machine pauses |
| 2 | Rethread film to load | Film tail accessible without entering machine |
| 3 | Press START | Resume wrapping |

#### 7.3.3 Labeling System Jam

**Hazards:** Label carriage motion, pinch points, pneumatic applicator

**LOTO Required:** Situational — Yes if reaching into applicator area

| Step | Action | Notes |
|------|--------|-------|
| 1 | Press STOP on labeler | Applicator stops |
| 2 | If jam at peel edge, clear backing paper with pick | No LOTO needed if accessible |
| 3 | If jam at applicator, apply LOTO per LOTO-L3-003 | Lock out pneumatics and drive |
| 4 | Clear label jam and buildup | |
| 5 | Check label sensor alignment | Misalignment causes repeat jams |
| 6 | Remove LOTO and restart | Run test labels |

#### 7.3.4 Palletizer Jam

**Hazards:** Robot/gantry motion, gripper release, falling loads

**LOTO Required:** Yes — Always (heavy loads, complex motion)

| Step | Action | Notes |
|------|--------|-------|
| 1 | Press E-STOP on palletizer | All motion stops |
| 2 | Apply LOTO per LOTO-L3-004 | Lock out robot/gantry, gripper pneumatics |
| 3 | Assess load stability before entering | Use spotter if load unstable |
| 4 | Clear misaligned product or gripper obstruction | Do not stand under gripper |
| 5 | If product fell, clear using pallet jack or forklift | Coordinate with material handling |
| 6 | Verify gripper function before restart | |
| 7 | Remove LOTO and restart | Run test cycle |

---

## 8. Post-Jam Clearing Requirements

### 8.1 Quality Checks

| Condition | Action | Responsibility |
|-----------|--------|----------------|
| Product damaged during jam | Segregate and tag for Quality review | Operator |
| Product produced during abnormal condition | Hold for inspection | Operator + Quality |
| Die or tooling damage suspected | Notify Quality; hold production until verified | Maintenance + Quality |
| Repeat jam on same equipment | Notify Quality; review recent production | Supervisor + Quality |

### 8.2 Equipment Inspection

| Item | Inspection Point | Action if Defective |
|------|------------------|---------------------|
| Guards | Secure, undamaged, properly positioned | Do not restart; notify Maintenance |
| Sensors | Clean, aligned, responding | Notify Maintenance; may affect quality |
| Belts/rollers | No cuts, debris, damage | Notify Maintenance for repair |
| Tooling | No visible damage, wear, or deformation | Notify Maintenance and Quality |
| Pneumatic lines | No leaks, connected, pressurized | Notify Maintenance |

### 8.3 Documentation

| Event | Documentation Required | Where to Record |
|-------|----------------------|-----------------|
| All jams | Jam type, cause, resolution, duration | Production log / downtime system |
| Jams requiring LOTO | LOTO permit (if applicable) | LOTO log |
| Jams with product damage | Quantity affected, disposition | Quality hold log |
| Jams causing equipment damage | Work order for repair | Maintenance system |
| Repeat jams (same shift) | Escalation to Supervisor and Maintenance | Production log + verbal notification |

---

## 9. Escalation Procedure

### 9.1 When to Escalate

| Condition | Escalate To |
|-----------|-------------|
| Jam cannot be cleared safely | Supervisor → Maintenance |
| Jam cause unknown | Maintenance |
| Repeat jam (3+ times same shift) | Supervisor + Maintenance + Engineering |
| Equipment damage discovered | Supervisor + Maintenance |
| Product quality affected | Quality |
| Near-miss or injury during clearing | Supervisor + EHS immediately |

### 9.2 Escalation Contacts

| Role | Primary Contact Method | Backup |
|------|----------------------|--------|
| Line Supervisor | Radio / direct | Shift Supervisor |
| Maintenance Technician | Radio to Maintenance Crib | Maintenance Supervisor |
| Maintenance Supervisor | Radio / phone | Plant Manager (off-hours) |
| Quality Engineer | Radio / phone | Quality Supervisor |
| EHS Manager | Phone / radio | Plant Manager |

---

## 10. Prohibited Actions

The following actions are **strictly prohibited** during jam clearing:

| Prohibited Action | Reason |
|-------------------|--------|
| Reaching into a die, press, or pinch point without LOTO | Risk of amputation or death |
| Bypassing guards or interlocks without authorization | Creates uncontrolled hazard |
| Using hands to clear jams when tools are available | Laceration, pinch injuries |
| Working on energized equipment | Unexpected motion or shock |
| Clearing jams while equipment is in AUTO or PAUSE | May restart unexpectedly |
| Cutting tensioned coil or spring material without release | Violent energy release |
| Standing under suspended or elevated loads | Falling object hazard |
| Working alone on high-hazard jam clearing (Line 1 dies) | No rescue capability |
| Removing another employee's lock to clear a jam | Violation of LOTO procedure |
| Ignoring repeat jams without investigation | Underlying problem worsens |

---

## 11. Personal Protective Equipment

### 11.1 Minimum PPE for Jam Clearing

| PPE | Required For | Specification |
|-----|--------------|---------------|
| Safety glasses | All jam clearing | ANSI Z87.1+ |
| Cut-resistant gloves | Handling material, scrap, sheet metal | ANSI A4 minimum |
| Safety footwear | All jam clearing | Steel/composite toe, ASTM F2413 |
| Hearing protection | Line 1 area | NRR 25+ earplugs or muffs |
| Long sleeves (fitted) | Press and robot work | No loose clothing |

### 11.2 Additional PPE by Task

| Task | Additional PPE |
|------|----------------|
| Coil handling | Metatarsal guards |
| Sharp scrap removal | Forearm guards (optional) |
| Robot cell entry | No loose clothing, jewelry, lanyards |
| Chemical spill during jam | Per SDS (goggles, nitrile gloves) |

---

## 12. Roles and Responsibilities

| Role | Responsibilities |
|------|------------------|
| **Operator** | Identify jams; attempt minor jam clearing per training; escalate as needed; document jams in production log |
| **Setup Technician** | Clear jams requiring guard access; apply LOTO; assist with robot cell jams; notify Maintenance of equipment issues |
| **Maintenance Technician** | Clear complex jams; diagnose root cause; repair equipment damage; update LOTO procedures if needed |
| **Supervisor** | Coordinate jam response; authorize LOTO activities; ensure documentation; escalate repeat jams; review shift jam summary |
| **Quality Engineer** | Evaluate product impact; authorize release of held product; investigate quality-related jam causes |
| **EHS Manager** | Investigate jam-related injuries or near-misses; audit jam clearing compliance; update procedures as needed |

---

## 13. Training and Qualification

### 13.1 Qualification Requirements

| Level | Can Perform | Requirements |
|-------|-------------|--------------|
| Level 1 — Operator | Minor jam clearing (no guard removal) | Jam Clearing Awareness training; equipment-specific orientation |
| Level 2 — Setup/Authorized | Jam clearing with LOTO; robot cell entry | LOTO Authorized training; Jam Clearing Authorized training; equipment-specific qualification |
| Level 3 — Maintenance | All jam clearing; troubleshooting; repair | Level 2 + Maintenance qualification; equipment-specific LOTO procedures |

### 13.2 Competency Verification

- Operators demonstrate minor jam clearing during on-the-job training
- Setup and Maintenance personnel demonstrate LOTO jam clearing under supervision before working independently
- Annual competency verification during LOTO audit
- Retraining required after jam-related incident or observed non-compliance

---

## 14. Related Documents

| Document ID | Title |
|-------------|-------|
| MMC_P7_LOTO_SOP | Lockout/Tagout Standard Operating Procedure |
| MMC_P7_Machine_Guarding_SOP | Machine Guarding Standard Operating Procedure |
| MMC_P7_Safety_Program_Overview | Safety Program Overview |
| MMC_P7_PPE_Matrix | Personal Protective Equipment Matrix |
| LOTO-L1-001 | LOTO Procedure — 600-Ton Press #1 |
| LOTO-L1-002 | LOTO Procedure — 600-Ton Press #2 |
| LOTO-L1-003 | LOTO Procedure — Coil Feed Line |
| LOTO-L1-004 | LOTO Procedure — Scrap Conveyor |
| LOTO-L2-001 | LOTO Procedure — Robot Cell A |
| LOTO-L2-002 | LOTO Procedure — Robot Cell B |
| LOTO-L2-003 | LOTO Procedure — Robot Cell C |
| LOTO-L2-004 | LOTO Procedure — Servo Torque Station |
| LOTO-L3-001 | LOTO Procedure — Main Conveyor Line |
| LOTO-L3-002 | LOTO Procedure — Stretch Wrap Machine |
| LOTO-L3-003 | LOTO Procedure — Labeling System |
| LOTO-L3-004 | LOTO Procedure — Palletizer |

---

## 15. Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-01-26 | Maintenance Supervisor | Initial release |

---

## Appendix A: Jam Clearing Quick Reference

### When in Doubt, Lock It Out!

```
┌─────────────────────────────────────────────────────────────┐
│                    JAM CLEARING CHECKLIST                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  □ STOP the machine (E-STOP or normal stop)                 │
│                                                             │
│  □ ASSESS the jam:                                          │
│    • Can I clear it from OUTSIDE the hazard zone?           │
│    • Do I need to remove a guard?                           │
│    • Is there stored energy?                                │
│                                                             │
│  □ If YES to any above → LOTO REQUIRED                      │
│                                                             │
│  □ APPLY LOTO per equipment-specific procedure              │
│                                                             │
│  □ VERIFY zero energy (try to start)                        │
│                                                             │
│  □ CLEAR the jam using proper tools (not hands)             │
│                                                             │
│  □ INSPECT equipment and product                            │
│                                                             │
│  □ REPLACE guards                                           │
│                                                             │
│  □ REMOVE LOTO (your lock, your key)                        │
│                                                             │
│  □ RESTART and verify operation                             │
│                                                             │
│  □ DOCUMENT in production log                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Appendix B: Jam Clearing Tools by Area

| Area | Authorized Tools | Prohibited Tools |
|------|------------------|------------------|
| Line 1 — Press/Die | Brass rod, wooden dowel, plastic pry bar, brass hammer | Steel pry bar, steel hammer (damages die) |
| Line 1 — Coil | Material guides, brass roller, cut-resistant gloves | Bare hands, unguarded knife |
| Line 1 — Scrap | Scrap rake, magnetic pickup | Reaching into conveyor by hand |
| Line 2 — Robot | Plastic pry tool, pick tool, vacuum | Bare hands in gripper zone |
| Line 2 — Torque | Socket drivers, extraction bits | Pliers on fastener heads |
| Line 3 — Conveyor | Gloved hands, vacuum, pushers | Reaching between rollers |
| Line 3 — Stretch Wrap | Safety film cutter, gloves | Box cutter, knife |
| Line 3 — Labeler | Pick tool, tweezers, vacuum | Bare hands near applicator |

---

## Appendix C: Common Jam Causes and Prevention

| Jam Type | Common Causes | Prevention |
|----------|---------------|------------|
| Material misfeed | Coil edge defect, loop sensor fault, lubricant issue | Incoming inspection, sensor calibration, PM |
| Part stuck in die | Slug buildup, vacuum failure, stripper spring weak | Die PM, vacuum check, spring replacement |
| Robot part misposition | Fixture wear, part variation, gripper slip | Fixture PM, SPC on parts, gripper PM |
| Conveyor accumulation | Sensor failure, downstream stoppage, belt slip | Sensor PM, communication between stations |
| Film break | Material defect, tension too high, film expired | Material inspection, tension adjustment |
| Label jam | Humidity, adhesive issue, sensor misalignment | Climate control, material storage, sensor check |

---

**End of Document**
