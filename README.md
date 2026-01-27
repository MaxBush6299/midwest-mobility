# MMC Plant 7 Demo Dataset

A comprehensive, realistic knowledge base for **Midwest Mobility Components (MMC) Plant 7** — a fictional Tier 1/Tier 2 automotive manufacturing facility. This dataset is designed for demonstrations, training, and development of AI-powered manufacturing operations tools.

---

## Overview

**Midwest Mobility Components (MMC)** is a mid-sized manufacturer supplying subassemblies and critical components to the mobility industry, including electric vehicle (EV) OEMs, heavy equipment manufacturers, and commercial fleet providers.

**Plant 7 Profile:**
- **Location:** Illinois, USA
- **Employees:** ~280
- **Operating Model:** 3-shift, 24/5 with weekend maintenance
- **Plant Type:** High-mix / medium-volume manufacturing

---

## Production Lines

| Line | Description | Key Equipment | Primary Hazards |
|------|-------------|---------------|-----------------|
| **Line 1** | Stamping & Forming | High-tonnage presses, coil-fed material handling | Pinch points, ejected material, noise, oil mist |
| **Line 2** | Assembly & Robot Cells | Industrial robots, servo torque tools, vision systems | Unexpected motion, bypassed guarding, PPE noncompliance |
| **Line 3** | Conveyor & Pack-Out | Powered conveyors, stretch wrap, palletizer | Jams, pinch points, housekeeping, ergonomic strain |

**Shared Areas:** Receiving/Shipping, Maintenance Crib, Chemical Storage Cage, Battery Handling Station, Tool Calibration Room

---

## Repository Structure

```
mmc_demo/
├── README.md
├── docs/
│   └── MMC_Plant7_Company_Profile_v1.md      # Source of truth for all documents
│
└── kb/
    ├── Internal/
    │   ├── 02_EHS_Internal/                   # Safety & Environmental Health
    │   │   ├── MMC_P7_Safety_Program_Overview.md
    │   │   ├── MMC_P7_LOTO_SOP.md
    │   │   ├── MMC_P7_Machine_Guarding_SOP.md
    │   │   └── MMC_P7_PPE_Matrix.md
    │   │
    │   ├── 03_Maintenance/                    # Maintenance & Equipment
    │   │   ├── MMC_P7_PM_Program_Overview.md
    │   │   ├── MMC_P7_Jam_Clearing_WI.md
    │   │   └── MMC_P7_Conveyor_Line3_Manual_Excerpt.md
    │   │
    │   ├── 04_Quality/                        # Quality Management
    │   │   ├── MMC_P7_Quality_Policy.md
    │   │   └── MMC_P7_NCR_CAPA_Process.md
    │   │
    │   ├── 05_Ops_Shift/                      # Operations & Shift Management
    │   │   ├── MMC_P7_Shift_Handover_Guidelines.md
    │   │   └── MMC_P7_Standard_Work_Changeover.md
    │   │
    │   └── 08_Logs_Data/                      # Operational Data (CSV)
    │       ├── MMC_P7_Incident_Log.csv
    │       ├── MMC_P7_PM_Schedule.csv
    │       └── MMC_P7_Training_Log.csv
    │
    ├── oem-manuals/                           # Equipment Reference (PDFs)
    │   ├── Fanuc Robot LR Mate 200iD Operators Manual.pdf
    │   └── HAAS-cnc-mill-manual.pdf
    │
    └── regulatory-reference/                  # Regulatory Standards (PDFs)
        └── OSHA/
            ├── OSHA_eCFR_1910_147_Lockout_Tagout.pdf
            ├── OSHA_eCFR_1910_178_Powered_Industrial_Trucks.pdf
            ├── OSHA_eCFR_1910_1200_Hazard_Communication.pdf
            ├── OSHA_eCFR_1910_Subpart_D_Walking_Working_Surfaces.pdf
            ├── OSHA_eCFR_1910_Subpart_I_PPE.pdf
            └── OSHA_eCFR_1910_Subpart_O_Machine_Guarding.pdf
```

---

## Document Summaries

### Company Profile
| Document | Description |
|----------|-------------|
| `MMC_Plant7_Company_Profile_v1.md` | Master reference defining plant context, production lines, safety/quality frameworks, personas, and naming conventions |

### EHS / Safety (02_EHS_Internal)
| Document | Description |
|----------|-------------|
| `MMC_P7_Safety_Program_Overview.md` | Comprehensive EHS management system aligned to ISO 45001; covers LOTO, guarding, PPE, HazCom, forklift safety, hearing conservation, fall protection |
| `MMC_P7_LOTO_SOP.md` | Lockout/Tagout standard operating procedure with energy source identification, step-by-step procedures, group lockout, and equipment-specific procedure index |
| `MMC_P7_Machine_Guarding_SOP.md` | Machine guarding requirements by line, guard removal/reinstallation procedures, interlock bypass authorization, inspection schedules |
| `MMC_P7_PPE_Matrix.md` | Area-specific and task-specific PPE requirements, selection criteria, inspection procedures, enforcement |

### Maintenance (03_Maintenance)
| Document | Description |
|----------|-------------|
| `MMC_P7_PM_Program_Overview.md` | Preventive maintenance program with equipment classification, PM schedules by line, lubrication program, spare parts management, KPIs |
| `MMC_P7_Jam_Clearing_WI.md` | Work instruction for clearing jams on all lines; decision tree for LOTO requirement, line-specific procedures, authorization matrix |
| `MMC_P7_Conveyor_Line3_Manual_Excerpt.md` | Technical manual for Line 3 conveyor system; specifications, safety systems, operating procedures, troubleshooting, spare parts |

### Quality (04_Quality)
| Document | Description |
|----------|-------------|
| `MMC_P7_Quality_Policy.md` | Quality Management System aligned to ISO 9001; quality objectives, process controls by line, inspection procedures, traceability |
| `MMC_P7_NCR_CAPA_Process.md` | Nonconformance reporting and corrective action process using 8D methodology |

### Operations (05_Ops_Shift)
| Document | Description |
|----------|-------------|
| `MMC_P7_Shift_Handover_Guidelines.md` | Role-specific shift handover procedures for Supervisors, Operators, Maintenance, Quality; LOTO transfer, abnormal situations |
| `MMC_P7_Standard_Work_Changeover.md` | Standardized changeover procedures for Lines 1-3; die changes, robot tooling, pack configuration; SMED principles, first-piece inspection |

### Operational Data (08_Logs_Data)
| File | Records | Date Range | Description |
|------|---------|------------|-------------|
| `MMC_P7_Incident_Log.csv` | 60 rows | Sept 2025 – Jan 2026 | Safety incidents with severity, root cause, CAPA tracking |
| `MMC_P7_PM_Schedule.csv` | 80 rows | Sept 2025 – Feb 2026 | Preventive maintenance records with findings and follow-up |
| `MMC_P7_Training_Log.csv` | 60 rows | Sept 2025 – Jan 2026 | Employee training completions by course and certification |

---

## Data Patterns

The operational data includes realistic, internally consistent patterns:

| Area | Pattern |
|------|---------|
| **Line 1** | Energy control issues, LOTO compliance focus, hearing conservation |
| **Line 2** | Guarding and interlock issues, robot cell safety, ESD protection |
| **Line 3** | Housekeeping deficiencies, conveyor jams, ergonomic concerns |
| **Receiving/Shipping** | Forklift incidents, pedestrian safety |

---

## Regulatory Framework

All documents reference applicable standards:
- **OSHA 29 CFR 1910** — General Industry Standards
- **ISO 45001** — Occupational Health & Safety Management
- **ISO 9001** — Quality Management Systems
- **ANSI/RIA R15.06** — Robot Safety
- **NFPA 70E** — Electrical Safety

---

## Personas

The knowledge base supports queries from:

| Role | Typical Questions |
|------|-------------------|
| **EHS Manager** | "Are we compliant with LOTO?" / "Where are repeat hazards?" |
| **Maintenance Technician** | "How do I clear this jam safely?" / "What do I lock out?" |
| **Line Supervisor** | "What PPE is required here?" / "Do I stop the line?" |
| **Quality Engineer** | "Is this defect safety-related?" / "What containment is needed?" |
| **Plant Manager** | "What are our top risks?" / "What actions are overdue?" |

---

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Plant | `MMC_P7` | — |
| Lines | `L1`, `L2`, `L3` | — |
| Documents | `MMC_P7_[Category]_[Name].md` | `MMC_P7_LOTO_SOP.md` |
| Equipment | `[Type]-[Line]-[Number]` | `P1-001`, `RC2-003`, `CV3-007` |
| LOTO Procedures | `LOTO-[Line]-[Number]` | `LOTO-L1-001` |
| Dates | `YYYY-MM-DD` | `2026-01-27` |
| Versions | `v1.0`, `v1.1` | — |

---

## Usage Notes

- All documents are written as realistic internal manufacturing documents
- Cross-references between documents are consistent
- Equipment IDs, employee names, and incident patterns are internally coherent
- CSV data aligns with procedures and timelines described in markdown documents

---

## License

This is a fictional dataset created for demonstration purposes. Any resemblance to actual companies, facilities, or individuals is coincidental.

---

**Last Updated:** 2026-01-27
