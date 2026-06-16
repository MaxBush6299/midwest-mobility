# MMC Plant 7 — Quality Policy and Management System
**Document ID:** MMC_P7_Quality_Policy  
**Document Owner:** Quality Manager, Plant 7  
**Version:** v1.0  
**Effective Date:** 2026-01-26  
**Review Cycle:** Annual  
**Applies To:** All employees, processes, and products at MMC Plant 7

---

## 1. Quality Policy Statement

**Midwest Mobility Components is committed to delivering defect-free products that meet or exceed customer requirements while ensuring the safety and reliability demanded by the mobility industry.**

We achieve this through:
- Understanding and meeting customer requirements
- Maintaining an effective Quality Management System aligned to ISO 9001 principles
- Continuous improvement of our processes, products, and people
- Employee engagement at all levels in quality ownership
- Prevention of defects through robust process controls
- Traceability of safety-critical components throughout the supply chain

This policy is communicated to all employees and reviewed annually for continued suitability.

**Signed:** Plant Manager, MMC Plant 7  
**Date:** 2026-01-26

---

## 2. Purpose

This document establishes the Quality Management System (QMS) framework for MMC Plant 7. It defines the policies, procedures, and responsibilities for ensuring consistent product quality, regulatory compliance, and customer satisfaction.

---

## 3. Scope

This policy applies to:
- All products manufactured at Plant 7
- All production processes on Lines 1, 2, and 3
- All support processes (Receiving, Shipping, Maintenance, Calibration)
- All employees involved in quality-affecting activities
- All suppliers of materials and components

**Products Manufactured:**
- Mechanical assemblies for propulsion systems
- Electrified subcomponents for EV applications
- Safety-critical parts for braking and structural systems
- Battery component assemblies (EV programs)

**Customer Base:**
- Electric vehicle (EV) OEMs
- Heavy equipment manufacturers
- Commercial fleet and mobility providers

---

## 4. Quality Management System Framework

### 4.1 QMS Principles

MMC Plant 7's QMS is aligned to **ISO 9001:2015** principles:

| Principle | Application at Plant 7 |
|-----------|----------------------|
| Customer Focus | Customer requirements flow to production; feedback drives improvement |
| Leadership | Plant Manager accountable for quality; resources provided |
| Engagement of People | Training, empowerment, and recognition programs |
| Process Approach | Defined processes with inputs, outputs, controls, and measures |
| Improvement | CAPA, 8D, and continuous improvement activities |
| Evidence-Based Decision Making | Data-driven decisions; metrics and analysis |
| Relationship Management | Supplier development; customer partnership |

### 4.2 QMS Processes

| Process Category | Processes |
|------------------|-----------|
| **Management** | Management Review, Quality Planning, Resource Management |
| **Core** | Order Entry, Production Planning, Manufacturing, Inspection, Shipping |
| **Support** | Purchasing, Calibration, Maintenance, Training, Document Control |
| **Measurement** | Internal Audit, Customer Feedback, Data Analysis, Corrective Action |

### 4.3 Process Interaction

```
Customer Requirements → Order Entry → Production Planning
                                            ↓
Purchasing ← Material Requirements ← Manufacturing (L1, L2, L3)
    ↓                                       ↓
Receiving → Incoming Inspection      In-Process Inspection
                                            ↓
                                    Final Inspection
                                            ↓
                               Packaging → Shipping → Customer
                                            ↓
                               Customer Feedback → Improvement
```

---

## 5. Quality Objectives

### 5.1 Annual Quality Objectives

| Objective | Metric | Target | Frequency |
|-----------|--------|--------|-----------|
| Customer Satisfaction | Customer scorecards / complaints | <5 complaints/year | Monthly review |
| Defect Rate | Internal PPM (defects per million) | <500 PPM | Monthly |
| Customer Returns | External PPM | <100 PPM | Monthly |
| On-Time Delivery | % of orders shipped on time | ≥98% | Weekly |
| First Pass Yield | % passing first inspection | ≥97% | Weekly |
| Scrap Rate | % of production scrapped | <2% | Monthly |
| NCR Closure | % of NCRs closed within 30 days | ≥90% | Monthly |
| CAPA Effectiveness | % of CAPAs verified effective | ≥95% | Quarterly |
| Audit Findings | Major findings per internal audit | 0 major | Per audit |
| Supplier Quality | Supplier PPM | <200 PPM | Quarterly |

### 5.2 Objectives by Production Line

| Line | Key Quality Focus | Primary Metric | Target |
|------|------------------|----------------|--------|
| Line 1 — Stamping | Dimensional accuracy, surface finish | CPK on critical dimensions | ≥1.33 |
| Line 2 — Assembly | Torque accuracy, assembly completeness | Torque verification pass rate | ≥99.5% |
| Line 3 — Pack-Out | Labeling accuracy, packaging integrity | Label/pack error rate | <0.1% |

---

## 6. Process Controls by Production Line

### 6.1 Line 1 — Stamping & Forming

| Control Point | Method | Frequency | Responsibility |
|---------------|--------|-----------|----------------|
| First Article Inspection | Dimensional measurement, visual | First part after setup/changeover | Setup Technician + Quality |
| In-Process Inspection | Attribute and dimensional checks | Per control plan (hourly minimum) | Operator |
| SPC Monitoring | Control charts on critical dimensions | Continuous | Operator + Quality |
| Die Verification | Die condition check, hit counter | Per die change | Setup Technician |
| Material Verification | Coil identification, MTR review | Each coil | Receiving / Operator |
| Last Article Inspection | Dimensional and visual | Last part before changeover | Operator + Quality |

**Critical-to-Quality (CTQ) Characteristics — Line 1:**
- Hole positions and diameters
- Bend angles and radii
- Blank dimensions
- Surface finish (no scratches, burrs, oil stains)
- Material thickness

### 6.2 Line 2 — Assembly & Robot Cells

| Control Point | Method | Frequency | Responsibility |
|---------------|--------|-----------|----------------|
| Component Verification | Barcode/visual scan of incoming parts | Each assembly | Operator / System |
| Torque Verification | Servo tool feedback / torque audit | 100% (servo) / sample (audit) | System / Quality |
| Vision Inspection | Automated camera inspection | 100% of assemblies | Vision System |
| Assembly Completeness | Poka-yoke / sensor verification | 100% | System |
| First Article Inspection | Full dimensional and functional | First assembly after setup | Quality |
| Functional Test | Performance verification per spec | Per control plan | Test Technician |

**Critical-to-Quality (CTQ) Characteristics — Line 2:**
- Fastener torque values
- Component presence and orientation
- Electrical connections (where applicable)
- Assembly dimensions and fits
- Weld quality (if applicable)

### 6.3 Line 3 — Conveyor & Pack-Out

| Control Point | Method | Frequency | Responsibility |
|---------------|--------|-----------|----------------|
| Product Identification | Label scan / verification | 100% | System / Operator |
| Label Accuracy | Visual / scan verification | 100% | Operator / System |
| Packaging Completeness | Count verification, weight check | Per container | Operator |
| Packaging Integrity | Visual inspection | 100% | Operator |
| Shipping Documentation | Documentation review | Each shipment | Shipping / Quality |
| Final Audit | Random sampling per AQL | Per lot | Quality |

**Critical-to-Quality (CTQ) Characteristics — Line 3:**
- Correct product in correct package
- Accurate labeling (part number, lot, quantity)
- Shipping documentation accuracy
- Package protection (no damage)

---

## 7. Inspection and Testing

### 7.1 Inspection Types

| Inspection Type | When Performed | Sample Size | Responsibility |
|-----------------|----------------|-------------|----------------|
| Receiving Inspection | Incoming materials | Per sampling plan (AQL) | Receiving Inspector |
| First Article Inspection (FAI) | After setup, changeover, or process change | 100% of first articles | Quality + Setup |
| In-Process Inspection | During production | Per control plan | Operator |
| Final Inspection | Before release to stock/ship | Per sampling plan (AQL) | Quality Inspector |
| Outgoing Audit | Before shipment | Random per lot | Quality |
| Layout Inspection | Periodic full dimensional | Per PPAP schedule or customer request | Quality Lab |

### 7.2 Sampling Plans

| Product Risk Level | Incoming | In-Process | Final | Standard |
|--------------------|----------|------------|-------|----------|
| Safety-Critical | AQL 0.65 Level II | 100% or per control plan | AQL 0.65 Level II | ANSI/ASQ Z1.4 |
| Standard | AQL 1.0 Level II | Per control plan | AQL 1.0 Level II | ANSI/ASQ Z1.4 |
| Low Risk | AQL 2.5 Level I | Per control plan | AQL 2.5 Level I | ANSI/ASQ Z1.4 |

### 7.3 Inspection Documentation

| Document | Content | Retention |
|----------|---------|-----------|
| Receiving Inspection Report | Material ID, quantity, inspection results, disposition | 5 years |
| First Article Inspection Report | All dimensions, visual, functional results | Life of part + 3 years |
| In-Process Inspection Record | Inspection data per control plan | 3 years |
| Final Inspection Report | Inspection results, lot disposition | 5 years |
| Certificate of Conformance (CoC) | Certification of product conformance | 5 years |

---

## 8. Nonconformance Management

### 8.1 Nonconforming Material Definition

Material is nonconforming when it:
- Does not meet drawing or specification requirements
- Does not meet customer requirements
- Is damaged or contaminated
- Is suspect due to process deviation
- Has expired shelf life or traceability issues

### 8.2 Nonconformance Identification and Segregation

| Step | Action | Responsibility |
|------|--------|----------------|
| 1 | Identify nonconforming material | Discoverer (any employee) |
| 2 | Stop production if ongoing nonconformance | Operator / Supervisor |
| 3 | Tag material with red "HOLD" tag | Discoverer |
| 4 | Physically segregate to Quality Hold Area | Operator / Material Handler |
| 5 | Notify Quality and Supervisor | Discoverer |
| 6 | Initiate Nonconformance Report (NCR) | Quality |
| 7 | Log in NCR tracking system | Quality |

### 8.3 Nonconformance Report (NCR) Process

| Step | Action | Responsibility | Timeframe |
|------|--------|----------------|-----------|
| 1 | NCR initiated with description, quantity, location | Quality | Same day as discovery |
| 2 | Containment action implemented | Quality + Production | Within 24 hours |
| 3 | Root cause investigation initiated | Quality Engineer | Within 48 hours |
| 4 | Disposition determined (Use As-Is, Rework, Scrap, Return) | Quality / Engineering | Within 5 days |
| 5 | Disposition approved (customer approval if required) | Quality Manager / Customer | Per agreement |
| 6 | Disposition executed | Production / Material Handler | Per disposition |
| 7 | NCR closed with verification | Quality | Within 30 days |
| 8 | CAPA initiated if systemic issue | Quality Engineer | If required |

### 8.4 Disposition Options

| Disposition | Definition | Authorization Required |
|-------------|------------|----------------------|
| **Use As-Is** | Accept without repair; meets functional requirements | Quality Manager; Customer (if out of spec) |
| **Rework** | Bring to conformance through additional operations | Quality Engineer |
| **Repair** | Bring to usable condition (may not meet all specs) | Quality Manager; Customer (if applicable) |
| **Scrap** | Dispose of material; not usable | Quality / Production |
| **Return to Supplier** | Return to supplier for credit/replacement | Purchasing / Quality |
| **Sort** | 100% inspection to segregate conforming from nonconforming | Quality |

### 8.5 Customer Notification

Customer notification is required when:
- Nonconforming product may have been shipped
- Deviation from customer specifications is requested
- Safety or regulatory implications exist
- Customer contract requires notification

| Step | Action | Responsibility |
|------|--------|----------------|
| 1 | Assess if customer notification required | Quality Manager |
| 2 | Prepare notification with facts and containment | Quality Manager |
| 3 | Contact customer quality representative | Quality Manager / Account Manager |
| 4 | Document communication | Quality |
| 5 | Implement customer-directed actions | Quality + Production |
| 6 | Provide closure report to customer | Quality Manager |

---

## 9. Corrective and Preventive Action (CAPA)

### 9.1 CAPA Triggers

CAPA is initiated for:
- Customer complaints
- Repeat NCRs (same issue 3+ occurrences)
- Internal audit findings (major)
- External audit findings
- Significant process deviations
- High-risk nonconformances
- Management direction

### 9.2 CAPA Process (8D Methodology)

| Discipline | Action | Responsibility | Timeframe |
|------------|--------|----------------|-----------|
| D1 — Team | Form cross-functional team | Quality Engineer | Day 1 |
| D2 — Problem Description | Define problem with data (5W2H) | Team | Day 1-2 |
| D3 — Containment | Implement interim containment actions | Team | Day 1-3 |
| D4 — Root Cause | Identify root cause(s) using 5 Whys, fishbone | Team | Day 3-10 |
| D5 — Corrective Actions | Define permanent corrective actions | Team | Day 10-15 |
| D6 — Implementation | Implement and validate corrective actions | Team | Day 15-30 |
| D7 — Prevention | Prevent recurrence; update procedures, training | Team | Day 30-45 |
| D8 — Closure | Verify effectiveness; recognize team | Quality Manager | Day 45-60 |

### 9.3 Root Cause Analysis Tools

| Tool | When Used |
|------|-----------|
| 5 Whys | Simple cause chains; initial investigation |
| Fishbone (Ishikawa) | Multiple potential causes; brainstorming |
| Fault Tree Analysis | Complex systems; safety-critical |
| Pareto Analysis | Prioritizing multiple causes |
| Is/Is Not Analysis | Defining problem boundaries |

### 9.4 CAPA Effectiveness Verification

| Step | Action | Responsibility |
|------|--------|----------------|
| 1 | Define verification criteria at time of CAPA | Quality Engineer |
| 2 | Allow sufficient time for actions to take effect | Quality Engineer |
| 3 | Collect data to verify effectiveness | Quality Engineer |
| 4 | Compare results to criteria | Quality Engineer |
| 5 | If effective, close CAPA | Quality Manager |
| 6 | If not effective, reopen and revise actions | Quality Engineer |

---

## 10. Traceability

### 10.1 Traceability Requirements

MMC Plant 7 manufactures safety-critical components requiring full traceability:

| Traceability Level | Requirement | Products |
|--------------------|-------------|----------|
| **Lot Traceability** | Trace to incoming material lot | All products |
| **Serial Traceability** | Individual unit tracking | Safety-critical assemblies |
| **Process Traceability** | Link to process parameters | Safety-critical parts |

### 10.2 Traceability Elements

| Element | How Captured | Retention |
|---------|--------------|-----------|
| Incoming Material Lot | Receiver log, material tag | 10 years |
| Production Lot | Lot traveler, system record | 10 years |
| Serial Number | Barcode/label, system record | Life of product + 10 years |
| Operator | Badge scan, signature | 10 years |
| Machine/Station | System log, traveler | 10 years |
| Date/Time | System timestamp | 10 years |
| Inspection Results | Inspection record | 10 years |
| Torque Data | Servo tool log | 10 years |
| Test Results | Test record | 10 years |

### 10.3 Traceability by Line

| Line | Traceability Method |
|------|---------------------|
| Line 1 | Lot number linked to coil lot; traveler with date/shift/operator |
| Line 2 | Serial number barcode; torque data linked to serial; vision inspection logged |
| Line 3 | Lot/serial label; pack list linked to contents; ship record |

### 10.4 Recall/Containment Capability

In the event of a recall or containment, the following must be achievable:
- Identify all affected lots/serials within 4 hours
- Identify all shipped locations within 8 hours
- Initiate containment notification within 24 hours
- Complete physical containment within 48 hours

---

## 11. Supplier Quality

### 11.1 Supplier Approval

| Step | Action | Responsibility |
|------|--------|----------------|
| 1 | Identify potential supplier | Purchasing / Engineering |
| 2 | Supplier self-assessment questionnaire | Supplier / Quality |
| 3 | Supplier audit (if required) | Quality / Purchasing |
| 4 | Sample approval (PPAP or equivalent) | Quality / Engineering |
| 5 | Supplier added to Approved Supplier List (ASL) | Quality Manager |
| 6 | Purchase orders issued | Purchasing |

### 11.2 Supplier Classification

| Classification | Criteria | Incoming Inspection |
|----------------|----------|---------------------|
| **Certified** | Excellent quality history; certified QMS | Reduced / Skip lot |
| **Approved** | Acceptable quality; approved per ASL | Standard sampling |
| **Conditional** | New supplier or quality issues | Increased sampling |
| **Probationary** | Serious quality issues | 100% inspection |
| **Disqualified** | Removed from ASL | No purchase |

### 11.3 Supplier Performance Monitoring

| Metric | Frequency | Target | Action if Below Target |
|--------|-----------|--------|----------------------|
| Quality (PPM) | Quarterly | <200 PPM | Supplier Corrective Action Request (SCAR) |
| Delivery | Monthly | ≥95% on-time | Performance review |
| Responsiveness | Per issue | SCAR response within 10 days | Escalation |

### 11.4 Supplier Corrective Action Request (SCAR)

| Step | Action | Responsibility | Timeframe |
|------|--------|----------------|-----------|
| 1 | Issue SCAR to supplier | Quality | Within 48 hours of issue |
| 2 | Supplier acknowledges receipt | Supplier | Within 24 hours |
| 3 | Supplier provides containment | Supplier | Within 48 hours |
| 4 | Supplier provides root cause and corrective action | Supplier | Within 10 business days |
| 5 | Quality reviews response | Quality | Within 5 days |
| 6 | Accept or reject response | Quality | Within 5 days |
| 7 | Monitor effectiveness | Quality | 90 days |
| 8 | Close SCAR | Quality | Upon verification |

---

## 12. Customer Requirements

### 12.1 Customer-Specific Requirements

Customer requirements are documented and communicated through:
- Customer quality manuals and specifications
- Purchase order requirements
- Customer-specific work instructions
- PPAP (Production Part Approval Process) requirements
- Customer audit findings

### 12.2 Contract Review

| Step | Action | Responsibility |
|------|--------|----------------|
| 1 | Review customer requirements before order acceptance | Sales / Quality |
| 2 | Identify capability to meet requirements | Engineering / Quality |
| 3 | Document any exceptions or clarifications | Quality |
| 4 | Communicate requirements to production | Quality / Planning |
| 5 | Maintain record of review | Quality |

### 12.3 Customer Feedback

| Feedback Type | Response Time | Responsibility |
|---------------|---------------|----------------|
| Complaint | Initial response within 24 hours | Quality Manager |
| Return (RMA) | Disposition within 5 days | Quality |
| Audit Finding | Response per customer timeline | Quality Manager |
| Scorecard | Review within 5 days of receipt | Quality Manager |

---

## 13. Calibration

### 13.1 Calibration Program

All measuring and test equipment used to verify product conformance is calibrated:

| Requirement | Standard |
|-------------|----------|
| Calibration Interval | Per manufacturer recommendation or historical data |
| Traceability | NIST traceable standards |
| Calibration Records | Retained for life of equipment + 3 years |
| Out-of-Tolerance | Impact assessment on product measured since last calibration |

### 13.2 Calibration Process

| Step | Action | Responsibility |
|------|--------|----------------|
| 1 | Equipment identified with unique ID | Quality / Calibration Lab |
| 2 | Equipment entered in calibration database | Calibration Lab |
| 3 | Calibration schedule generated | Calibration Lab |
| 4 | Equipment calibrated per procedure | Calibration Technician |
| 5 | Calibration sticker applied with due date | Calibration Technician |
| 6 | If out of tolerance: flag, assess impact, notify Quality | Calibration Technician |
| 7 | Records maintained | Calibration Lab |

### 13.3 Equipment Categories

| Category | Examples | Calibration Interval |
|----------|----------|---------------------|
| Dimensional | Micrometers, calipers, height gauges | 6-12 months |
| Torque | Torque wrenches, servo tool verification | 3-6 months |
| Electrical | Multimeters, insulation testers | 12 months |
| Force/Pressure | Load cells, pressure gauges | 12 months |
| Go/No-Go | Pin gauges, thread gauges | 12 months |

---

## 14. Document Control

### 14.1 Document Types

| Document Type | Examples | Approval Authority |
|---------------|----------|-------------------|
| Policy | Quality Policy, EHS Policy | Plant Manager |
| Procedure | Inspection procedures, CAPA procedure | Department Manager |
| Work Instruction | Operator work instructions, inspection instructions | Supervisor / Engineer |
| Form | NCR form, inspection checklist | Document Control |
| Record | Completed forms, inspection data | Originating function |
| External | Customer specs, standards | Document Control |

### 14.2 Document Control Process

| Step | Action | Responsibility |
|------|--------|----------------|
| 1 | Draft document | Author |
| 2 | Review for accuracy and completeness | Reviewers (cross-functional) |
| 3 | Approve document | Approval authority |
| 4 | Assign document number and revision | Document Control |
| 5 | Distribute to users | Document Control |
| 6 | Train affected personnel | Supervisor / Training |
| 7 | Remove obsolete versions | Document Control |
| 8 | Maintain master file | Document Control |

### 14.3 Document Revision

| Revision Type | Process |
|---------------|---------|
| Minor (editorial) | Document Control approval; no retraining required |
| Major (technical) | Full review and approval; retraining required |

---

## 15. Training

### 15.1 Quality-Related Training

| Training Topic | Audience | Frequency |
|----------------|----------|-----------|
| Quality Policy Awareness | All employees | Initial + Annual |
| Work Instructions | Operators by work area | Initial + changes |
| Inspection Methods | Inspectors, Operators | Initial + as needed |
| NCR/CAPA Process | Quality, Supervisors | Initial + Annual |
| SPC/Control Charts | Operators (applicable areas) | Initial |
| Calibration | Calibration Technicians | Initial |
| Customer Requirements | Applicable personnel | Per customer / changes |
| Internal Audit | Auditors | Initial + 3-year refresh |

### 15.2 Training Records

| Record | Content | Retention |
|--------|---------|-----------|
| Training Log | Training completed, date, trainer | Duration of employment + 3 years |
| Competency Verification | Evidence of competency (test, observation) | Duration of employment + 3 years |

---

## 16. Internal Audit

### 16.1 Audit Program

| Element | Requirement |
|---------|-------------|
| Frequency | All QMS elements audited at least annually |
| Schedule | Developed annually by Quality Manager |
| Auditor Qualification | Trained; independent of area audited |
| Audit Criteria | ISO 9001 clauses; procedures; customer requirements |

### 16.2 Audit Process

| Step | Action | Responsibility |
|------|--------|----------------|
| 1 | Develop annual audit schedule | Quality Manager |
| 2 | Assign auditors; ensure independence | Quality Manager |
| 3 | Prepare audit checklist | Auditor |
| 4 | Notify auditee of audit | Auditor |
| 5 | Conduct audit (document review, interviews, observation) | Auditor |
| 6 | Document findings (major, minor, observation) | Auditor |
| 7 | Conduct closing meeting | Auditor |
| 8 | Issue audit report | Auditor |
| 9 | Auditee develops corrective action plan | Auditee |
| 10 | Verify corrective action implementation | Auditor |
| 11 | Close audit | Quality Manager |

### 16.3 Finding Classification

| Classification | Definition | Response Time |
|----------------|------------|---------------|
| Major | Absence of or significant failure in QMS element | 30 days |
| Minor | Isolated lapse in procedure compliance | 60 days |
| Observation | Opportunity for improvement | Next audit |

---

## 17. Management Review

### 17.1 Management Review Inputs

| Input | Source |
|-------|--------|
| Audit results (internal and external) | Audit reports |
| Customer feedback and complaints | Customer data |
| Process performance and product conformity | Quality metrics |
| Status of corrective and preventive actions | CAPA log |
| Follow-up from previous reviews | Previous review minutes |
| Changes affecting QMS | Planning / Management |
| Recommendations for improvement | All functions |
| Supplier performance | Supplier data |

### 17.2 Management Review Outputs

| Output | Action |
|--------|--------|
| Improvement opportunities | Assign responsibility and resources |
| Changes to QMS | Initiate document changes |
| Resource needs | Budget/staffing decisions |
| Quality objectives | Set/revise objectives |

### 17.3 Review Schedule

| Review | Frequency | Attendees |
|--------|-----------|-----------|
| Quality Management Review | Quarterly | Plant Manager, Quality Manager, Production, Engineering, EHS |
| Annual QMS Review | Annual | Same + Corporate Quality (if applicable) |

---

## 18. Roles and Responsibilities

| Role | Quality Responsibilities |
|------|-------------------------|
| **Plant Manager** | Overall accountability for quality; approve policy; allocate resources; participate in management review |
| **Quality Manager** | Manage QMS; oversee inspections; manage NCR/CAPA; customer quality interface; report metrics; lead audits |
| **Quality Engineer** | Lead root cause investigations; develop control plans; analyze data; manage PPAP; support CAPA |
| **Quality Inspector** | Perform inspections; document results; identify nonconformances; verify rework |
| **Line Supervisor** | Ensure operators follow work instructions; stop production for quality issues; support NCR/CAPA |
| **Operator** | Follow work instructions; perform in-process inspections; identify and segregate nonconformances |
| **Maintenance Supervisor** | Ensure equipment capable of meeting quality requirements; support calibration program |
| **Maintenance Technician** | Maintain equipment; report equipment issues affecting quality |
| **EHS Manager** | Interface on safety-related quality issues; support product safety requirements |
| **Receiving/Shipping** | Verify incoming materials; maintain shipping accuracy; handle customer returns |
| **Purchasing** | Manage supplier quality; issue SCARs; maintain ASL |

---

## 19. Quality and Safety Interface

Quality and EHS work together on:

| Interface Area | Collaboration |
|----------------|---------------|
| Product Safety | Safety-critical characteristics; failure mode analysis |
| Process Safety | Process controls that affect both quality and safety |
| Incident Investigation | Root cause analysis for quality and safety events |
| Customer Requirements | Safety and quality requirements from customers |
| Nonconformance | NCRs that may have safety implications |
| Supplier Quality | Supplier safety certifications and compliance |

**Escalation:** Any nonconformance with potential safety implications must be immediately escalated to both Quality Manager and EHS Manager.

---

## 20. Continuous Improvement

### 20.1 Improvement Sources

| Source | Process |
|--------|---------|
| CAPA | Systematic issues addressed through 8D |
| Audit Findings | Corrective actions from internal/external audits |
| Customer Feedback | Improvements driven by customer input |
| Employee Suggestions | Kaizen / suggestion program |
| Metrics Review | Data-driven improvement initiatives |
| Benchmarking | Industry best practices |

### 20.2 Improvement Process

| Step | Action | Responsibility |
|------|--------|----------------|
| 1 | Identify improvement opportunity | Any employee |
| 2 | Evaluate feasibility and impact | Engineering / Quality |
| 3 | Prioritize and approve | Management |
| 4 | Plan and implement | Assigned team |
| 5 | Verify results | Quality |
| 6 | Standardize if successful | Document Control |
| 7 | Share lessons learned | Quality / Training |

---

## 21. Related Documents

| Document ID | Title |
|-------------|-------|
| MMC_P7_NCR_Procedure | Nonconformance Report Procedure |
| MMC_P7_CAPA_Procedure | Corrective and Preventive Action Procedure |
| MMC_P7_Incoming_Inspection_WI | Incoming Inspection Work Instruction |
| MMC_P7_Final_Inspection_WI | Final Inspection Work Instruction |
| MMC_P7_Calibration_Procedure | Calibration Procedure |
| MMC_P7_Internal_Audit_Procedure | Internal Audit Procedure |
| MMC_P7_Document_Control_Procedure | Document Control Procedure |
| MMC_P7_Supplier_Quality_Manual | Supplier Quality Requirements |
| MMC_P7_Control_Plans | Control Plans by Product Family |
| MMC_P7_Safety_Program_Overview | Safety Program Overview |

---

## 22. Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-01-26 | Quality Manager | Initial release |

---

## Appendix A: Quality Hold Area Locations

| Area | Location | Signage |
|------|----------|---------|
| Line 1 Hold | East end of Line 1, caged area | Red "QUALITY HOLD" sign |
| Line 2 Hold | Near inspection station, marked floor area | Red "QUALITY HOLD" sign |
| Line 3 Hold | Adjacent to pack-out, caged area | Red "QUALITY HOLD" sign |
| Receiving Hold | Receiving dock, designated rack | Red "QUALITY HOLD" sign |
| Shipping Hold | Shipping staging, marked floor area | Red "QUALITY HOLD" sign |

---

## Appendix B: NCR Quick Reference

**When to Initiate NCR:**
- Material does not meet specification
- Customer complaint received
- Inspection failure (receiving, in-process, final)
- Process deviation discovered
- Damaged or contaminated material

**Immediate Actions:**
1. STOP if problem is ongoing
2. TAG material with red hold tag
3. SEGREGATE to Quality Hold Area
4. NOTIFY Quality and Supervisor
5. DOCUMENT quantity and location

**Do NOT:**
- Ship suspect material
- Mix nonconforming with conforming material
- Dispose without authorization
- Ignore and continue production

---

## Appendix C: Key Quality Contacts

| Role | Contact Method |
|------|----------------|
| Quality Manager | Radio / Phone extension |
| Quality Engineer (L1) | Radio / Phone extension |
| Quality Engineer (L2) | Radio / Phone extension |
| Quality Inspector (on shift) | Radio |
| Receiving Inspector | Radio / Phone extension |
| Calibration Lab | Phone extension |

**After Hours:** Contact Shift Supervisor; escalate to Quality Manager via phone tree.

---

**End of Document**
