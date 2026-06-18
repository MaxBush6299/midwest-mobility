# MMC Plant 4 — Line 3 Conveyor System Manual Excerpt
**Document ID:** MMC_P4_Conveyor_Line3_Manual_Excerpt  
**Document Owner:** Maintenance Supervisor, Plant 4  
**Version:** v1.0  
**Effective Date:** 2026-01-26  
**Review Cycle:** Annual  
**Applies To:** Maintenance Technicians, Operators, and Supervisors working on Line 3 conveyor systems

---

## 1. Overview

This manual excerpt provides operational, maintenance, and troubleshooting information for the Line 3 Conveyor System at MMC Plant 4. Line 3 is the Conveyor & Pack-Out line, consisting of powered roller conveyors, transfer conveyors, accumulation zones, and integration points with the stretch wrap machine, labeling system, and palletizer.

**Line 3 Function:** Transport finished assemblies from Line 2 exit through pack-out stations to stretch wrap, labeling, and palletizing for shipment.

---

## 2. System Specifications

### 2.1 Conveyor Sections

| Section ID | Description | Type | Length (ft) | Width (in) | Speed (FPM) | Drive Motor |
|------------|-------------|------|-------------|------------|-------------|-------------|
| CV3-001 | Main Conveyor Section 1 | Powered Roller | 48 | 24 | 0-65 | 1.5 HP, 480V, 3-phase |
| CV3-002 | Main Conveyor Section 2 | Powered Roller | 36 | 24 | 0-65 | 1.5 HP, 480V, 3-phase |
| CV3-003 | Transfer Conveyor | Belt | 12 | 24 | 0-50 | 1.0 HP, 480V, 3-phase |
| CV3-004 | Accumulation Zone 1 | Zero-Pressure Accumulation | 24 | 24 | 0-65 | 2.0 HP, 480V, 3-phase |
| CV3-005 | Accumulation Zone 2 | Zero-Pressure Accumulation | 24 | 24 | 0-65 | 2.0 HP, 480V, 3-phase |
| CV3-006 | Pack-Out Station Conveyor | Powered Roller | 18 | 30 | 0-40 | 1.0 HP, 480V, 3-phase |
| CV3-007 | Stretch Wrap Infeed | Powered Roller | 8 | 30 | 0-40 | 0.75 HP, 480V, 3-phase |
| CV3-008 | Stretch Wrap Outfeed | Powered Roller | 8 | 30 | 0-40 | 0.75 HP, 480V, 3-phase |
| CV3-009 | Labeler Conveyor | Belt | 6 | 24 | 0-50 | 0.5 HP, 480V, 3-phase |
| CV3-010 | Palletizer Infeed | Chain | 12 | 48 | 0-30 | 2.0 HP, 480V, 3-phase |

### 2.2 System Parameters

| Parameter | Specification |
|-----------|---------------|
| Total System Length | Approximately 196 feet |
| Maximum Product Weight | 75 lbs per unit |
| Maximum Product Dimensions | 24" L × 18" W × 18" H |
| Roller Diameter | 1.9" (standard sections); 2.5" (heavy-duty sections) |
| Roller Spacing | 3" centers (standard); 6" centers (accumulation) |
| Belt Material | PVC, FDA-approved (belt sections) |
| Chain Type | ANSI #60 roller chain (palletizer infeed) |
| Control System | Allen-Bradley CompactLogix L33ER PLC |
| HMI | Allen-Bradley PanelView Plus 7 (10") |
| Network | EtherNet/IP |

### 2.3 Electrical System

| Component | Specification |
|-----------|---------------|
| Main Disconnect | 200A, 480V, 3-phase, fused |
| Control Power | 120V, 1-phase (from control transformer) |
| Motor Starters | Variable Frequency Drives (VFDs) — Allen-Bradley PowerFlex 525 |
| Safety System | Allen-Bradley GuardLogix 5370 (integrated safety PLC) |
| E-Stop Circuit | Category 3, Performance Level d |
| Photoelectric Sensors | Banner Q45 series |
| Proximity Sensors | Allen-Bradley 872C series |

---

## 3. Safety Systems

### 3.1 Emergency Stop Locations

| E-Stop ID | Location | Type | Zone Affected |
|-----------|----------|------|---------------|
| ES3-001 | CV3-001 Head (Line 2 exit) | Push-button, red mushroom | Full system stop |
| ES3-002 | CV3-001 Tail | Pull-cord | CV3-001 only |
| ES3-003 | CV3-002 Tail | Pull-cord | CV3-002 and downstream |
| ES3-004 | Pack-Out Station 1 | Push-button, red mushroom | CV3-004, CV3-006 |
| ES3-005 | Pack-Out Station 2 | Push-button, red mushroom | CV3-005, CV3-006 |
| ES3-006 | Stretch Wrap Machine | Push-button, red mushroom | CV3-007, CV3-008, SW-001 |
| ES3-007 | Labeler Station | Push-button, red mushroom | CV3-009, LB-001 |
| ES3-008 | Palletizer Infeed | Push-button, red mushroom | CV3-010, PZ-001 |
| ES3-009 | Main Control Panel | Push-button, red mushroom | Full system stop |
| ES3-010 | CV3-003 Transfer | Pull-cord | CV3-003 only |

**Pull-Cord Specifications:**
- Maximum spacing between supports: 10 feet
- Actuation force: 20-30 lbs
- Cord must be red or orange colored
- Reset requires manual intervention at control panel

### 3.2 Guarding

| Guard Location | Guard Type | Interlock | Reference |
|----------------|------------|-----------|-----------|
| CV3-001 Drive Pulley | Fixed guard, steel mesh | None | MMC_P4_Machine_Guarding_SOP |
| CV3-001 Tail Pulley | Fixed guard, steel mesh | None | MMC_P4_Machine_Guarding_SOP |
| CV3-002 Drive/Tail | Fixed guard, steel mesh | None | MMC_P4_Machine_Guarding_SOP |
| CV3-003 Access Panel | Hinged cover | Category 2 interlock | MMC_P4_Machine_Guarding_SOP |
| CV3-010 Chain Drive | Fixed enclosure | None | MMC_P4_Machine_Guarding_SOP |
| All Conveyor Length | Pull-cord E-stop | Category 3 safety | Section 3.1 |

### 3.3 Lockout/Tagout Points

| LOTO Point ID | Location | Energy Type | Isolation Device | Reference |
|---------------|----------|-------------|------------------|-----------|
| LOTO-CV3-001 | MCC-3, Breaker 12 | Electrical (480V) | Circuit breaker with lockout hasp | MMC_P4_LOTO_SOP |
| LOTO-CV3-002 | MCC-3, Breaker 14 | Electrical (480V) | Circuit breaker with lockout hasp | MMC_P4_LOTO_SOP |
| LOTO-CV3-003 | MCC-3, Breaker 16 | Electrical (480V) | Circuit breaker with lockout hasp | MMC_P4_LOTO_SOP |
| LOTO-CV3-004 | MCC-3, Breaker 18 | Electrical (480V) | Circuit breaker with lockout hasp | MMC_P4_LOTO_SOP |
| LOTO-CV3-005 | MCC-3, Breaker 20 | Electrical (480V) | Circuit breaker with lockout hasp | MMC_P4_LOTO_SOP |
| LOTO-CV3-006 | MCC-3, Breaker 22 | Electrical (480V) | Circuit breaker with lockout hasp | MMC_P4_LOTO_SOP |
| LOTO-CV3-007 | Local disconnect at stretch wrap | Electrical (480V) | Disconnect switch with lockout | MMC_P4_LOTO_SOP |
| LOTO-CV3-008 | Local disconnect at stretch wrap | Electrical (480V) | Disconnect switch with lockout | MMC_P4_LOTO_SOP |
| LOTO-CV3-009 | MCC-3, Breaker 26 | Electrical (480V) | Circuit breaker with lockout hasp | MMC_P4_LOTO_SOP |
| LOTO-CV3-010 | MCC-3, Breaker 28 | Electrical (480V) | Circuit breaker with lockout hasp | MMC_P4_LOTO_SOP |
| LOTO-CV3-AIR | Pneumatic manifold (CV3-004/005) | Pneumatic (90 PSI) | Ball valve with lockout | MMC_P4_LOTO_SOP |

**Note:** Accumulation zones CV3-004 and CV3-005 use pneumatic cylinders for zone control. Both electrical and pneumatic isolation required for maintenance.

---

## 4. Operating Procedures

### 4.1 System Startup

**Pre-Startup Checklist:**

| Step | Check | Verified By |
|------|-------|-------------|
| 1 | All E-stops reset (not latched) | Operator |
| 2 | All guards in place and secure | Operator |
| 3 | No personnel in conveyor areas | Operator |
| 4 | No product or debris obstructing conveyor | Operator |
| 5 | Compressed air supply on (90 PSI minimum) | Operator |
| 6 | Downstream equipment ready (stretch wrap, labeler, palletizer) | Operator |
| 7 | HMI displays no active faults | Operator |

**Startup Sequence:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Turn main disconnect to ON (MCC-3) | Power available to system |
| 2 | Press CONTROL POWER ON at main panel | HMI powers up; system initializes |
| 3 | Verify HMI shows "SYSTEM READY" | No active faults displayed |
| 4 | Clear any displayed faults | All faults acknowledged |
| 5 | Select operating mode: AUTO or MANUAL | Mode indicator illuminated |
| 6 | Press SYSTEM START (green illuminated button) | Conveyors start in sequence (CV3-010 first, then upstream) |
| 7 | Verify all sections running | Green RUN indicators on HMI |
| 8 | Verify accumulation zones functioning | Photoelectric sensors detecting product |
| 9 | Run test product through system | Product transfers correctly through all zones |

**Startup Sequence Timing:**
- CV3-010 starts first (palletizer infeed)
- CV3-009 starts after 2-second delay
- CV3-007/008 start after 2-second delay
- Remaining sections start in upstream sequence with 1-second delays

### 4.2 Normal Operation

**Operating Modes:**

| Mode | Description | Use Case |
|------|-------------|----------|
| AUTO | Fully automatic operation; sensors control product flow | Normal production |
| MANUAL | Individual section control via HMI | Troubleshooting, maintenance prep |
| JOG | Momentary motion while JOG button held | Positioning, jam clearing |
| E-STOP | All motion stopped; requires reset | Emergency condition |

**Speed Adjustment:**
- Speed adjustable via HMI: 0-100% of maximum
- Default production speed: 75% (approximately 49 FPM)
- Speed changes take effect immediately on running sections

**Accumulation Zone Operation:**
- Zones CV3-004 and CV3-005 provide zero-pressure accumulation
- Photoelectric sensors detect product presence in each zone
- When downstream zone is full, upstream zone stops until space available
- Minimum gap between products: 6 inches

### 4.3 Normal Shutdown

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Allow all product to clear system | HMI shows all zones empty |
| 2 | Press SYSTEM STOP (red button) | Conveyors stop in sequence |
| 3 | Verify all sections stopped | Red STOP indicators on HMI |
| 4 | If extended shutdown: Turn main disconnect to OFF | Power removed from system |
| 5 | If overnight shutdown: Shut off compressed air to manifold | Pneumatic energy removed |

### 4.4 Emergency Shutdown

| Condition | Action |
|-----------|--------|
| Immediate hazard to personnel | Press nearest E-STOP immediately |
| Product jam causing equipment damage | Press nearest E-STOP immediately |
| Fire or smoke observed | Press E-STOP; activate fire alarm; evacuate |
| Unusual noise or vibration | Press SYSTEM STOP; investigate before restart |
| Electrical fault (sparking, burning smell) | Press E-STOP; notify Maintenance immediately |

**E-Stop Reset Procedure:**

| Step | Action | Responsibility |
|------|--------|----------------|
| 1 | Identify and correct cause of E-stop activation | Operator/Maintenance |
| 2 | Verify all personnel clear of conveyor | Operator |
| 3 | Reset E-stop device (twist or pull to release) | Operator |
| 4 | At main control panel, press FAULT RESET | Operator |
| 5 | Verify HMI shows "SYSTEM READY" | Operator |
| 6 | Follow normal startup procedure | Operator |

---

## 5. Preventive Maintenance

### 5.1 Maintenance Schedule

| Task | Frequency | Performed By | Estimated Time | LOTO Required |
|------|-----------|--------------|----------------|---------------|
| Visual inspection (guards, rollers, belts) | Daily (pre-shift) | Operator | 10 min | No |
| Clean photoeyes and sensors | Weekly | Operator | 15 min | No (system stopped) |
| Check belt tension and tracking | Weekly | Maintenance | 30 min | Yes |
| Lubricate bearings (grease fittings) | Monthly | Maintenance | 45 min | Yes |
| Inspect chain tension (CV3-010) | Monthly | Maintenance | 20 min | Yes |
| Check roller condition and rotation | Monthly | Maintenance | 30 min | Yes |
| Inspect E-stop function | Monthly | Maintenance | 20 min | No (testing) |
| VFD parameter check and cleaning | Quarterly | Maintenance | 60 min | Yes |
| Full conveyor alignment check | Quarterly | Maintenance | 90 min | Yes |
| Motor current draw measurement | Quarterly | Maintenance | 30 min | No |
| Safety system verification (interlocks, E-stops) | Quarterly | Maintenance + EHS | 60 min | Partial |
| Replace worn rollers | As needed | Maintenance | 15 min per roller | Yes |
| Replace belts | Annually or as needed | Maintenance | 4 hours | Yes |
| Replace chain and sprockets (CV3-010) | Annually or as needed | Maintenance | 3 hours | Yes |

### 5.2 Lubrication Requirements

| Component | Lubricant | Quantity | Points | Frequency |
|-----------|-----------|----------|--------|-----------|
| Roller bearings | NLGI #2 EP grease | 2-3 pumps per fitting | 2 per roller end | Monthly |
| Drive shaft bearings | NLGI #2 EP grease | 3-4 pumps per fitting | 2 per drive | Monthly |
| Gearbox | ISO VG 220 gear oil | Check level; add as needed | 1 per gearbox | Monthly check; annual change |
| Chain (CV3-010) | Chain lubricant spray | Light coating | Full chain length | Weekly |
| Take-up bearings | NLGI #2 EP grease | 2-3 pumps per fitting | 2 per take-up | Monthly |

**Lubrication Procedure:**
1. Lock out conveyor section per MMC_P4_LOTO_SOP
2. Clean grease fitting with lint-free cloth
3. Attach grease gun to fitting
4. Apply specified number of pumps
5. Wipe excess grease from fitting and surrounding area
6. Document lubrication on PM work order

### 5.3 Belt Tension and Tracking

**Belt Tension Check (CV3-003, CV3-009):**

| Step | Action | Specification |
|------|--------|---------------|
| 1 | Lock out conveyor section | Per MMC_P4_LOTO_SOP |
| 2 | Press belt at midpoint between pulleys | — |
| 3 | Measure deflection | 1-2% of span length |
| 4 | If over-tensioned: Loosen take-up bolts, allow belt to relax | — |
| 5 | If under-tensioned: Tighten take-up bolts evenly | — |
| 6 | Re-check tension | Within specification |

**Belt Tracking Adjustment:**

| Condition | Adjustment |
|-----------|------------|
| Belt running to left side | Tighten left take-up; loosen right take-up |
| Belt running to right side | Tighten right take-up; loosen left take-up |
| Belt oscillating side-to-side | Check for material buildup on pulleys; check splice condition |
| Belt cupping or curling | Check for edge damage; belt may require replacement |

**Specification:** Belt should track within 0.25" of centerline.

### 5.4 Roller Replacement Procedure

| Step | Action | Tools Required |
|------|--------|----------------|
| 1 | Lock out conveyor section per MMC_P4_LOTO_SOP | LOTO kit |
| 2 | Remove product from affected area | — |
| 3 | Identify failed roller and record location | Marker |
| 4 | Compress spring-loaded axle and remove roller from frame | — |
| 5 | Inspect frame slots for debris or damage | Flashlight |
| 6 | Insert new roller; ensure axle seats in frame slots | — |
| 7 | Verify roller rotates freely | Rotate by hand |
| 8 | Remove LOTO; test conveyor operation | — |
| 9 | Document replacement on work order | — |

**Roller Replacement Criteria:**
- Roller does not rotate freely
- Visible flat spots or damage to roller surface
- Excessive bearing noise
- Roller wobble (bent axle)
- Missing or damaged O-rings (on O-ring driven rollers)

---

## 6. Troubleshooting

### 6.1 Common Faults and Remedies

| Fault Code | Description | Possible Causes | Remedy |
|------------|-------------|-----------------|--------|
| F001 | E-Stop Active | E-stop pressed or pull-cord activated | Locate activated E-stop; clear hazard; reset E-stop; press FAULT RESET |
| F002 | Motor Overload | Jam, seized bearing, overloaded belt | Clear jam; check for seized rollers; reduce load; check motor current |
| F003 | VFD Fault | Overvoltage, undervoltage, overcurrent | Check power supply; check wiring; reset VFD; if recurring, contact Maintenance |
| F004 | Safety Circuit Open | Guard interlock open, safety device triggered | Check CV3-003 access panel interlock; check all guard positions |
| F005 | Photoeye Blocked | Sensor obstructed or failed | Clean sensor lens; remove obstruction; check sensor alignment |
| F006 | Accumulation Zone Timeout | Product not clearing zone within timeout | Check downstream equipment; check for jam; verify sensor function |
| F007 | Communication Fault | Network error between PLC and devices | Check Ethernet cables; cycle power to affected device; contact Maintenance |
| F008 | Low Air Pressure | Pneumatic supply below 80 PSI | Check main air supply; check for leaks; verify regulator setting |
| F009 | Motor Thermal Overload | Motor overheating | Allow cool-down; check for jam; verify ventilation; check current draw |
| F010 | Conveyor Misalignment | Belt or chain tracking error | Check belt tracking; check chain alignment; adjust as needed |

### 6.2 Troubleshooting Decision Tree — Conveyor Won't Start

```
CONVEYOR WON'T START
        │
        ▼
Is main disconnect ON?
        │
   NO ──┴── YES
    │         │
    ▼         ▼
Turn ON     Is HMI powered on?
            │
       NO ──┴── YES
        │         │
        ▼         ▼
Check control   Is there an active fault?
transformer     │
           YES ─┴── NO
            │         │
            ▼         ▼
Clear fault    Is an E-stop active?
per 6.1        │
          YES ─┴── NO
           │         │
           ▼         ▼
Reset E-stop   Is SYSTEM READY displayed?
               │
          NO ──┴── YES
           │         │
           ▼         ▼
Check safety   Press SYSTEM START
circuit        │
               ▼
            System should start.
            If not, contact Maintenance.
```

### 6.3 Troubleshooting Decision Tree — Product Jam

```
PRODUCT JAM DETECTED
        │
        ▼
Can jam be cleared from outside hazard zone?
        │
   YES ─┴── NO
    │         │
    ▼         ▼
Press E-STOP   LOTO REQUIRED
or SYSTEM      Per MMC_P4_LOTO_SOP
STOP           and MMC_P4_Jam_Clearing_WI
    │
    ▼
Use tool (not hands) to clear jam
    │
    ▼
Inspect for product damage
    │
    ▼
Segregate damaged product for Quality review
    │
    ▼
Inspect for conveyor damage
    │
    ▼
If damage found, notify Maintenance
    │
    ▼
Reset system and restart
    │
    ▼
If jam recurs, escalate to Maintenance
```

### 6.4 Jam Clearing — Specific Locations

| Location | Common Jam Type | Clearing Procedure | LOTO Required |
|----------|-----------------|-------------------|---------------|
| CV3-001/002 Roller Section | Product tip-over, accumulation backup | Press E-STOP; remove product by hand; reset | No (if from outside) |
| CV3-003 Transfer | Product misalignment at transition | Press E-STOP; reposition or remove product; reset | No (if from outside) |
| CV3-004/005 Accumulation | Zone sensor blocked; pneumatic cylinder jam | Press E-STOP; check sensors; if cylinder issue, LOTO and clear | Yes (for cylinder) |
| CV3-006 Pack-Out | Overfilled carton; product obstruction | Press E-STOP; remove obstruction; reset | No |
| CV3-007/008 Stretch Wrap | Product misalignment entering/exiting wrapper | Press E-STOP; reposition product; reset | No |
| CV3-009 Labeler | Label jam; product misorientation | Press E-STOP; clear label jam; reposition product | No |
| CV3-010 Chain Conveyor | Product misalignment; chain jump | LOTO required; check chain tension; realign product | Yes |

**Reference:** MMC_P4_Jam_Clearing_WI for detailed jam clearing procedures and authorization matrix.

---

## 7. Component Details

### 7.1 Drive Motors

| Motor ID | Section | HP | Voltage | FLA | RPM | Frame | Manufacturer |
|----------|---------|-----|---------|-----|-----|-------|--------------|
| MTR-CV3-001 | CV3-001 | 1.5 | 480V 3PH | 2.2 | 1750 | 145TC | Baldor |
| MTR-CV3-002 | CV3-002 | 1.5 | 480V 3PH | 2.2 | 1750 | 145TC | Baldor |
| MTR-CV3-003 | CV3-003 | 1.0 | 480V 3PH | 1.5 | 1750 | 143TC | Baldor |
| MTR-CV3-004 | CV3-004 | 2.0 | 480V 3PH | 2.8 | 1750 | 145TC | Baldor |
| MTR-CV3-005 | CV3-005 | 2.0 | 480V 3PH | 2.8 | 1750 | 145TC | Baldor |
| MTR-CV3-006 | CV3-006 | 1.0 | 480V 3PH | 1.5 | 1750 | 143TC | Baldor |
| MTR-CV3-007 | CV3-007 | 0.75 | 480V 3PH | 1.2 | 1750 | 56C | Baldor |
| MTR-CV3-008 | CV3-008 | 0.75 | 480V 3PH | 1.2 | 1750 | 56C | Baldor |
| MTR-CV3-009 | CV3-009 | 0.5 | 480V 3PH | 0.9 | 1750 | 56C | Baldor |
| MTR-CV3-010 | CV3-010 | 2.0 | 480V 3PH | 2.8 | 1750 | 145TC | Baldor |

### 7.2 Variable Frequency Drives

| VFD ID | Motor Controlled | Model | HP Rating | Parameters File |
|--------|------------------|-------|-----------|-----------------|
| VFD-CV3-001 | MTR-CV3-001 | PowerFlex 525 | 2 HP | VFD_CV3_001_params.txt |
| VFD-CV3-002 | MTR-CV3-002 | PowerFlex 525 | 2 HP | VFD_CV3_002_params.txt |
| VFD-CV3-003 | MTR-CV3-003 | PowerFlex 525 | 1.5 HP | VFD_CV3_003_params.txt |
| VFD-CV3-004 | MTR-CV3-004 | PowerFlex 525 | 3 HP | VFD_CV3_004_params.txt |
| VFD-CV3-005 | MTR-CV3-005 | PowerFlex 525 | 3 HP | VFD_CV3_005_params.txt |
| VFD-CV3-006 | MTR-CV3-006 | PowerFlex 525 | 1.5 HP | VFD_CV3_006_params.txt |
| VFD-CV3-007 | MTR-CV3-007 | PowerFlex 525 | 1 HP | VFD_CV3_007_params.txt |
| VFD-CV3-008 | MTR-CV3-008 | PowerFlex 525 | 1 HP | VFD_CV3_008_params.txt |
| VFD-CV3-009 | MTR-CV3-009 | PowerFlex 525 | 0.75 HP | VFD_CV3_009_params.txt |
| VFD-CV3-010 | MTR-CV3-010 | PowerFlex 525 | 3 HP | VFD_CV3_010_params.txt |

**VFD Fault Reset Procedure:**
1. Press STOP on VFD keypad
2. Identify fault code on display
3. Correct fault condition (see Section 6.1)
4. Press STOP + ENTER simultaneously to clear fault
5. If fault clears, restart via HMI
6. If fault persists, contact Maintenance

### 7.3 Sensors

| Sensor ID | Location | Type | Function | Normally Open/Closed |
|-----------|----------|------|----------|---------------------|
| PE-CV3-001 | CV3-001 entry | Photoelectric (retro-reflective) | Product present at infeed | NO (dark = no product) |
| PE-CV3-002 | CV3-002 exit | Photoelectric (retro-reflective) | Product present at transfer | NO |
| PE-CV3-004A | CV3-004 Zone 1 | Photoelectric (diffuse) | Zone 1 occupied | NO |
| PE-CV3-004B | CV3-004 Zone 2 | Photoelectric (diffuse) | Zone 2 occupied | NO |
| PE-CV3-004C | CV3-004 Zone 3 | Photoelectric (diffuse) | Zone 3 occupied | NO |
| PE-CV3-005A | CV3-005 Zone 1 | Photoelectric (diffuse) | Zone 1 occupied | NO |
| PE-CV3-005B | CV3-005 Zone 2 | Photoelectric (diffuse) | Zone 2 occupied | NO |
| PE-CV3-005C | CV3-005 Zone 3 | Photoelectric (diffuse) | Zone 3 occupied | NO |
| PE-CV3-006 | Pack-Out Station | Photoelectric (retro-reflective) | Product at pack station | NO |
| PE-CV3-007 | Stretch wrap infeed | Photoelectric (retro-reflective) | Product at wrapper entry | NO |
| PE-CV3-010 | Palletizer infeed | Photoelectric (retro-reflective) | Product at palletizer entry | NO |
| PRX-CV3-010 | CV3-010 chain | Inductive proximity | Chain position/speed | NO |

**Sensor Cleaning Procedure:**
1. Stop conveyor section (E-STOP not required; SYSTEM STOP acceptable)
2. Use clean, dry, lint-free cloth
3. Wipe sensor lens and reflector (if retro-reflective type)
4. Do not use solvents or abrasives
5. Verify sensor LED indicates proper function
6. Document on weekly PM checklist

---

## 8. Spare Parts

### 8.1 Recommended Spare Parts Inventory

| Part Number | Description | Quantity On-Hand | Reorder Point | Location |
|-------------|-------------|------------------|---------------|----------|
| ROL-1924-BRG | Roller, 1.9" × 24", bearing ends | 24 | 12 | Maint. Crib, Bin L3-01 |
| ROL-2530-BRG | Roller, 2.5" × 30", bearing ends | 12 | 6 | Maint. Crib, Bin L3-02 |
| BLT-PVC-24 | Belt, PVC, 24" wide (per foot) | 50 ft | 25 ft | Maint. Crib, Shelf L3-03 |
| CHN-60-10 | Chain, ANSI #60, 10-foot length | 4 | 2 | Maint. Crib, Bin L3-04 |
| SPR-60-24 | Sprocket, #60 chain, 24-tooth | 4 | 2 | Maint. Crib, Bin L3-05 |
| BRG-UC205 | Bearing, pillow block, UC205 | 12 | 6 | Maint. Crib, Bin L3-06 |
| BRG-UC207 | Bearing, pillow block, UC207 | 8 | 4 | Maint. Crib, Bin L3-07 |
| PE-Q45VR2 | Photoeye, Banner Q45, retro-reflective | 4 | 2 | Maint. Crib, Bin L3-08 |
| PE-Q45D | Photoeye, Banner Q45, diffuse | 6 | 3 | Maint. Crib, Bin L3-09 |
| MTR-145TC-1.5 | Motor, 1.5 HP, 145TC frame | 1 | 1 | Maint. Crib, Shelf L3-10 |
| MTR-145TC-2.0 | Motor, 2.0 HP, 145TC frame | 1 | 1 | Maint. Crib, Shelf L3-11 |
| VFD-PF525-2HP | VFD, PowerFlex 525, 2 HP | 1 | 1 | Maint. Crib, Cabinet E-01 |
| ES-CORD-25 | E-stop pull-cord, 25 ft with hardware | 2 | 1 | Maint. Crib, Bin L3-12 |
| GRB-CV3 | Gearbox, CV3 standard | 1 | 0 | Order as needed |

### 8.2 Critical Spares

The following components should always be in stock to minimize downtime:

| Component | Typical Failure Mode | Lead Time if Not In Stock |
|-----------|---------------------|---------------------------|
| Rollers (both sizes) | Bearing failure, surface damage | 3-5 days |
| Motors (1.5 HP, 2.0 HP) | Bearing failure, winding failure | 1-2 weeks |
| VFDs | Power surge damage, component failure | 1-2 weeks |
| Photoelectric sensors | Lens damage, internal failure | 2-3 days |
| Bearings (pillow block) | Wear, contamination | 1-2 days |
| Belt (PVC) | Wear, tracking damage, splice failure | 1 week |
| Chain (#60) | Stretch, link failure | 3-5 days |

---

## 9. Control System

### 9.1 PLC Information

| Parameter | Specification |
|-----------|---------------|
| PLC Model | Allen-Bradley CompactLogix 5370 L33ER |
| Safety Controller | Allen-Bradley GuardLogix 5370 (integrated) |
| I/O Modules | 1769-IQ16, 1769-OW16, 1769-IF8, 1769-OF4 |
| Program File | CV3_Main_v3.2.ACD |
| Last Program Revision | 2025-08-15 |
| Program Backup Location | \\mmc-P4-server\Engineering\PLC_Backups\Line3\ |

### 9.2 HMI Screens

| Screen | Description | Access Level |
|--------|-------------|--------------|
| Main | System overview, section status, faults | Operator |
| Section Detail | Individual conveyor control, speed, status | Operator |
| Alarms | Active and historical alarm display | Operator |
| Diagnostics | Sensor status, I/O status, communication | Maintenance |
| VFD Status | Drive parameters, faults, current draw | Maintenance |
| Configuration | Speed settings, timing, zone parameters | Supervisor (password) |
| Maintenance | PM reminders, runtime counters | Maintenance |

### 9.3 Network Information

| Device | IP Address | Description |
|--------|------------|-------------|
| PLC | 192.168.1.30 | CompactLogix L33ER |
| HMI | 192.168.1.31 | PanelView Plus 7 |
| VFD-CV3-001 | 192.168.1.41 | PowerFlex 525 |
| VFD-CV3-002 | 192.168.1.42 | PowerFlex 525 |
| VFD-CV3-003 | 192.168.1.43 | PowerFlex 525 |
| VFD-CV3-004 | 192.168.1.44 | PowerFlex 525 |
| VFD-CV3-005 | 192.168.1.45 | PowerFlex 525 |
| VFD-CV3-006 | 192.168.1.46 | PowerFlex 525 |
| VFD-CV3-007 | 192.168.1.47 | PowerFlex 525 |
| VFD-CV3-008 | 192.168.1.48 | PowerFlex 525 |
| VFD-CV3-009 | 192.168.1.49 | PowerFlex 525 |
| VFD-CV3-010 | 192.168.1.50 | PowerFlex 525 |

---

## 10. Integration Points

### 10.1 Upstream Equipment (Line 2)

| Interface | Description | Signal Type |
|-----------|-------------|-------------|
| L2_READY | Line 2 robot cell ready to discharge | Discrete input (24VDC) |
| L3_READY | Line 3 ready to receive product | Discrete output (24VDC) |
| L2_PRODUCT_OUT | Product transferred from Line 2 | Discrete input (24VDC) |

**Handshake Sequence:**
1. Line 2 sets L2_READY when product at discharge
2. Line 3 sets L3_READY when CV3-001 clear and running
3. Line 2 transfers product and sets L2_PRODUCT_OUT
4. Line 3 detects product at PE-CV3-001 and clears L3_READY

### 10.2 Downstream Equipment

| Equipment | Interface Signals | Description |
|-----------|-------------------|-------------|
| Stretch Wrap (SW-001) | SW_READY, SW_COMPLETE | Wrapper ready; cycle complete |
| Labeler (LB-001) | LB_READY, LB_PRINT_CMD, LB_COMPLETE | Labeler ready; print command; print complete |
| Palletizer (PZ-001) | PZ_READY, PZ_LAYER_COMPLETE | Palletizer ready; layer complete |

### 10.3 Quality System Interface

| Signal | Description | Use |
|--------|-------------|-----|
| QC_HOLD | Quality hold signal | Stops CV3-006 to allow inspection |
| QC_REJECT | Quality reject signal | Diverts product to reject station (if equipped) |
| SERIAL_NO | Product serial number (string) | Sent to labeler for print |

---

## 11. Roles and Responsibilities

| Role | Responsibilities |
|------|------------------|
| **Line Supervisor** | Oversee Line 3 operations; authorize jam clearing; conduct weekly inspections; report deficiencies to Maintenance; verify operator training |
| **Operator** | Perform pre-shift inspections; operate conveyor system; clear minor jams (non-LOTO); report deficiencies; maintain housekeeping |
| **Maintenance Technician** | Perform PM tasks; troubleshoot faults; clear jams requiring LOTO; replace components; document repairs; maintain spare parts |
| **Maintenance Supervisor** | Schedule PM activities; approve LOTO for extended work; coordinate with production; manage spare parts inventory |
| **Quality Engineer** | Verify product integrity after jam clearing; coordinate QC hold/release; report quality issues related to conveyor handling |
| **EHS Manager** | Audit safety systems; review LOTO compliance; investigate incidents; maintain safety documentation |

---

## 12. Related Documents

| Document ID | Title |
|-------------|-------|
| MMC_P4_LOTO_SOP | Lockout/Tagout Standard Operating Procedure |
| MMC_P4_Machine_Guarding_SOP | Machine Guarding Standard Operating Procedure |
| MMC_P4_Jam_Clearing_WI | Jam Clearing Work Instruction |
| MMC_P4_PM_Program_Overview | Preventive Maintenance Program Overview |
| MMC_P4_Safety_Program_Overview | Safety Program Overview |
| MMC_P4_PPE_Matrix | Personal Protective Equipment Matrix |
| MMC_P4_Shift_Handover_Guidelines | Shift Handover Guidelines |

---

## 13. Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-01-26 | Maintenance Supervisor | Initial release |

---

## Appendix A: System Layout Diagram

```
                                    LINE 3 CONVEYOR SYSTEM — PLAN VIEW
                                    
    FROM LINE 2
         │
         ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │ CV3-001 Main Conveyor Section 1 (48 ft)                                 │
    │ ES3-001 ●────────────────────────────● ES3-002 (pull-cord)              │
    └─────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │ CV3-002 Main Conveyor Section 2 (36 ft)                         │
    │ ──────────────────────────────────● ES3-003 (pull-cord)         │
    └─────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
                              ┌──────────────────┐
                              │ CV3-003 Transfer │
                              │ ES3-010 ●        │
                              └──────────────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
    ┌───────────────────────────────┐         ┌───────────────────────────────┐
    │ CV3-004 Accumulation Zone 1   │         │ CV3-005 Accumulation Zone 2   │
    │ Pack-Out Station 1            │         │ Pack-Out Station 2            │
    │ ES3-004 ●                     │         │ ES3-005 ●                     │
    └───────────────────────────────┘         └───────────────────────────────┘
                    │                                         │
                    └────────────────────┬────────────────────┘
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │ CV3-006 Pack-Out Station Conveyor       │
                    └─────────────────────────────────────────┘
                                         │
                                         ▼
    ┌──────────────┐    ┌──────────────────────────┐    ┌──────────────┐
    │ CV3-007      │    │ SW-001 Stretch Wrap      │    │ CV3-008      │
    │ Infeed       │───▶│ ES3-006 ●                │───▶│ Outfeed      │
    └──────────────┘    └──────────────────────────┘    └──────────────┘
                                                               │
                                                               ▼
                              ┌──────────────────────────────────────────┐
                              │ CV3-009 Labeler Conveyor                 │
                              │ LB-001                 ES3-007 ●         │
                              └──────────────────────────────────────────┘
                                                               │
                                                               ▼
                              ┌──────────────────────────────────────────┐
                              │ CV3-010 Palletizer Infeed (Chain)        │
                              │ ES3-008 ●                                │
                              └──────────────────────────────────────────┘
                                                               │
                                                               ▼
                              ┌──────────────────────────────────────────┐
                              │ PZ-001 Palletizer                        │
                              └──────────────────────────────────────────┘
                                                               │
                                                               ▼
                                                      TO SHIPPING
                                                      
    ● = E-Stop Location                    Main Control Panel: ES3-009
```

---

## Appendix B: Electrical Panel Layout — MCC-3

```
    ┌─────────────────────────────────────────────────────────────────┐
    │                         MCC-3                                    │
    │                   LINE 3 CONVEYOR SYSTEM                         │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                  │
    │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │
    │  │ BKR 10 │ │ BKR 12 │ │ BKR 14 │ │ BKR 16 │ │ BKR 18 │        │
    │  │ MAIN   │ │CV3-001 │ │CV3-002 │ │CV3-003 │ │CV3-004 │        │
    │  │ 200A   │ │ 15A    │ │ 15A    │ │ 10A    │ │ 20A    │        │
    │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘        │
    │                                                                  │
    │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │
    │  │ BKR 20 │ │ BKR 22 │ │ BKR 24 │ │ BKR 26 │ │ BKR 28 │        │
    │  │CV3-005 │ │CV3-006 │ │ CTRL   │ │CV3-009 │ │CV3-010 │        │
    │  │ 20A    │ │ 10A    │ │ PWR 5A │ │ 5A     │ │ 20A    │        │
    │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘        │
    │                                                                  │
    │  Note: CV3-007 and CV3-008 fed from SW-001 local disconnect     │
    │                                                                  │
    └─────────────────────────────────────────────────────────────────┘
```

---

## Appendix C: Maintenance Log Sheet

**Line 3 Conveyor System — Maintenance Log**

| Date | Time | Technician | Section | Work Performed | Parts Used | Duration | WO# |
|------|------|------------|---------|----------------|------------|----------|-----|
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |

**Supervisor Review:** _________________ **Date:** _________________

---

**End of Document**
