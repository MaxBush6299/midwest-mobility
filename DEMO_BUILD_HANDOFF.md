# MMC Reusable Agent Network — Coding-Agent Build Handoff

**Status:** Design complete, ready to build. **Owner handoff:** architecture + phase plan below are self-contained; you should not need the originating conversation.
**Last updated:** 2026-06-16

---

## 1. What we are building (one paragraph)

A **network of reusable Foundry agents** for a fictitious automotive Tier-1/2 supplier (**MMC — Midwest Mobility Components**). Each agent is published with an **A2A agent card** and grounded by **Foundry IQ** (Azure AI Search agentic retrieval). A **Magentic orchestration manager** (Microsoft Agent Framework SDK) takes a natural-language **problem statement**, **discovers** candidate agents from a registry, and **composes a multi-agent flow at runtime** — no hardcoded workflow/DAG. The demo proves: *AI can design the agentic flow from a problem statement + the agent registry, rather than requiring a deterministic, pre-wired orchestration.*

**The headline talking point:** AI plans the path at **two layers** — Magentic plans across **agents**; Foundry IQ agentic retrieval plans across **knowledge sources**.

**Why it matters (customer question being answered):** *"With hundreds of agents in a registry — home-built and third-party — must the multi-agent orchestration be deterministic, or can the AI help design the agentic flow given a problem statement + the registry?"* This demo answers: **yes, the AI composes it** (Magentic), and that is the recommended pattern for dynamic, registry-driven orchestration.

---

## 2. Tech stack (use these, current as of June 2026)

| Layer | Technology | Notes |
|---|---|---|
| Orchestration | **Microsoft Agent Framework SDK** — Magentic orchestration | Magentic manager is flagged **experimental** in the SDK; pin the version. Reasoning layer is **model-agnostic** (any `IChatClient` / chat model) — do NOT hardcode to a specific vendor. |
| Agent runtime | **Foundry Agent Service** agents | Each agent = one A2A card. |
| Discovery / registry | **Microsoft Agent 365** registry (Graph API, preview) + **Entra Agent ID** (identity/access scope) + **Azure API Center** (A2A card + skills surface) | A2A discovery via well-known URI `/.well-known/agent-card.json`, catalog, or direct config. |
| Inter-agent protocol | **A2A protocol** | Home-built + third-party agents hydrate as `AIAgent`. |
| Knowledge / grounding | **Foundry IQ** knowledge base (built on **Azure AI Search** agentic retrieval) | A KB is the top-level resource; it orchestrates retrieval across **knowledge sources**. Exposes an **MCP endpoint**; connect to Foundry Agent Service via the first-party "Connect a Foundry IQ knowledge base to Foundry Agent Service" path. LLM query planning is optional but recommended (`retrieval reasoning effort`: minimal / low / medium). Use `output_mode = extractive` for verbatim grounding. |

> Before implementing any Microsoft/Azure specifics, **verify against Microsoft Learn** (Foundry IQ, Agent Framework Magentic, A2A, Agent 365, Entra Agent ID). Some features are GA, some preview — check the API version you target.

---

## 3. The dataset (already exists in this repo)

This repo (`mmc_demo`) already contains the **Plant 7** plant-floor operations dataset, which is **live/grounded today** via an existing **Foundry IQ knowledge base: 1 KB with 3 knowledge sources** (one per subfolder area).

- **Company:** MMC, Tier-1/2 automotive supplier (EV OEMs, heavy equipment, fleets).
- **Plant 7:** Illinois, ~280 employees, 3-shift 24/5. Lines: **L1** Stamping/Forming, **L2** Assembly/Robot Cells, **L3** Conveyor/Pack-Out.
- **Source of truth:** `docs/MMC_Plant7_Company_Profile_v1.md` — **read this before generating ANY new MMC content** to stay consistent with naming, sites, and standards.
- **Naming conventions:** `MMC_P7`, lines `L1/L2/L3`, equipment `[Type]-[Line]-[Number]` (e.g., `L1-PRS-001`), LOTO `LOTO-L1-001`, hazards `HAZ_001`–`HAZ_099`.
- **Standards referenced:** OSHA 29 CFR 1910, ISO 45001, ISO 9001, ANSI/RIA R15.06, NFPA 70E.

### Existing knowledge sources / data
- `kb/Internal/` — EHS SOPs (LOTO, Machine Guarding, PPE Matrix, Safety Program), Maintenance (PM Program, Jam-Clearing WI, Conveyor manual), Quality (NCR/CAPA, Quality Policy), Ops/Shift (Handover, Standard Work Changeover).
- `kb/Internal/08_Logs_Data/` — three CSV logs (schemas below).
- `kb/oem-manuals/` — Fanuc, HAAS PDFs.
- `kb/regulatory-reference/OSHA/` — six OSHA 1910 PDFs.

### CSV schemas (exact columns — do not invent new columns without updating the profile)
- **`MMC_P7_Incident_Log.csv`** (60 rows, Sep 2025–Jan 2026): `Incident_ID, Date, Time, Shift, Location, Area, Incident_Type, Severity, Description, Immediate_Cause, Root_Cause, Injury_Type, Body_Part, Treatment, Days_Away, Days_Restricted, Reported_By, Investigated_By, CAPA_ID, CAPA_Status, Closed_Date`
- **`MMC_P7_PM_Schedule.csv`** (80 rows): `PM_ID, Asset_ID, Equipment_Name, Location, PM_Type, Frequency, Scheduled_Date, Completed_Date, Status, Technician, Duration_Hours, LOTO_Required, Findings, Follow_Up_WO, Notes`
- **`MMC_P7_Training_Log.csv`** (60 rows): `Training_ID, Employee_ID, Employee_Name, Department, Area, Training_Course, Training_Type, Course_Category, Scheduled_Date, Completed_Date, Status, Trainer, Score_Percent, Pass_Fail, Expiration_Date, Notes`

### Foundry IQ KB → source mapping (Plant 7, existing)
| KB source | Backs which agent(s) | Content |
|---|---|---|
| **EHS / Safety source** | EHS / Safety agent | Incident_Log, LOTO SOPs, OSHA 1910 PDFs, PPE/Guarding SOPs |
| **Maintenance source** | Maintenance & Reliability agent | PM_Schedule, Jam-Clearing WI, OEM manuals (Fanuc/HAAS) |
| **Quality & Ops source** | Quality (Plant), Shift Ops, Training agents | NCR/CAPA, Quality Policy, Shift Handover, Standard Work, Training_Log |

> **Binding pattern (decided):** Each agent binds to its **scoped KB source(s)** rather than raw files — cleaner blast-radius/governance and crisper A2A skill boundaries. Agents call the KB via its **MCP endpoint** as a single tool.

---

## 4. The agent network (the build target)

**10 agents, 2 tiers, 1 manager.** Each agent: publishes an A2A card at `/.well-known/agent-card.json`, advertises **skills**, calls **tools** (KB via MCP + named APIs).

### Tier 1 — Plant Ops node (Plant 7 — grounded in REAL data today)
| Agent | A2A Skills (advertised) | Tools |
|---|---|---|
| **EHS / Safety** | Hazard & LOTO requirement lookup; Incident clustering & repeat-cause; OSHA/ISO 45001 compliance check | Foundry IQ KB (EHS source); CAPA tracker API |
| **Maintenance & Reliability** | PM status & overdue WOs; Asset history & jam-clear procedure; Spare-part lookup & OEE/downtime | Foundry IQ KB (Maint source); CMMS API; IoT/SCADA telemetry |
| **Quality (Plant)** | NCR/CAPA status & 8D containment; Defect → safety-issue linkage; First-piece/changeover inspection | Foundry IQ KB (Quality&Ops source); QMS/SPC API; Traceability DB |
| **Shift Ops** | Shift-handover summary & open items; Changeover/SMED step guidance; Line-stop decision support | Foundry IQ KB (Quality&Ops source); MES schedule API |
| **Training / Competency** | Cert status & expiration lookup; "Who is qualified for this task?"; Training-gap vs. incident link | Foundry IQ KB (Quality&Ops source); LMS API; Skills matrix |

### Tier 2 — Enterprise nodes (NEW data to generate in this repo)
| Agent | A2A Skills | Tools (data to build) |
|---|---|---|
| **Supply Chain** | Supplier health & disruption impact; BOM explode & where-used; Alt-source & inbound-logistics ETA | Supplier master; BOM/where-used; ERP inventory; TMS/freight |
| **Procurement & Cost** | Should-cost & PO-impact analysis; Contract terms & expedite cost; Spend & supplier-tier rollup | Contracts DB; PO/spend; Should-cost model |
| **Engineering / PLM** | ECO/ECN status & impact; Part-revision & effectivity lookup; Cross-plant where-installed | PLM/Teamcenter; CAD part master; ECO workflow |
| **Enterprise Quality** | Warranty-claim clustering; Cross-plant defect trends; Recall-threshold & safety call | Warranty DB; Field-failure feed; Recall ruleset |
| **Demand / Program** | OEM order signal & build-mix; Launch-program readiness; Demand → plant allocation | Order/CRM feed; Program plan; Allocation model |

> Both tiers register into **one catalog**; the Magentic manager treats all 10 as a single discoverable pool. Plant nodes are cloneable per facility (Plant 4, Plant 5…). Enterprise nodes are built once and reused by every plant.

---

## 5. Reference scenario (acceptance test for orchestration)

**Problem statement:** *"A tier-1 supplier flagged a 3-week delay on brake calipers. What's the impact and what are our options?"*

**Expected Magentic-composed flow (NOT hardcoded — the manager must derive this):**
`Supply Chain (ent)` → `Plant 7 Maintenance (local)` → `Plant 7 Quality (local)` → `Procurement & Cost (ent)` → ↺ **backtrack** → `Supply Chain · alt-source (ent)`

**What it proves:** the same Plant 7 agents built for a safety question now serve a supply-chain question; the flow spans enterprise + local tiers; the manager selected this mix from the problem statement; a different question composes a different set with **zero re-coding**.

---

## 6. Phase plan (build order)

> Critical path **0 → 1 → 2 → 3 → 4 → 5**; Phase 6 (governance) runs in parallel from Phase 3.
> **Thin slice** to a live wow (P0 + P1 + one stub enterprise agent + P4 happy-path) ≈ **3–4 days**. **Full polished build** ≈ **8–13 days**.

### Phase 0 — Foundations & environment  *(½–1 day)*
- Provision Foundry project + Azure AI Search (Foundry IQ backbone).
- Install/verify **Microsoft Agent Framework SDK** builds a "hello agent". Pin the (experimental) Magentic package version.
- Enable Entra Agent ID tenant scoping; confirm Agent 365 registry access (preview).
- Scaffold repo: add top-level `enterprise/` (datasets) and `agents/` (one A2A card JSON per agent, 10 total).
- **Exit:** SDK builds hello-agent; `enterprise/` + `agents/` trees exist.

### Phase 1 — Plant 7 node (grounded, live today)  *(1–2 days)*
- Confirm the existing Foundry IQ KB (1 KB / 3 sources) and source→agent mapping in §3.
- Stand up the **5 plant agents**: each publishes its A2A card, binds to scoped KB source(s) via MCP, advertises skills.
- Register all 5 into the catalog.
- **Exit:** 5 Plant 7 agents answer grounded questions; cards discoverable at `/.well-known/agent-card.json`; registered.

### Phase 2 — Enterprise data buildout  *(1–2 days)*
- Generate fictitious datasets **consistent with `docs/MMC_Plant7_Company_Profile_v1.md`** and the naming conventions: supplier master, BOM/where-used, warranty claims, contracts/PO, PLM/ECO log, demand/program plan.
- Land them in `mmc_demo/enterprise/<node>/`. Create a Foundry IQ KB per enterprise node.
- **Cross-link to Plant 7** so the brake-caliper scenario resolves end-to-end (e.g., a supplier in the supplier master maps to a part in the BOM that is consumed on a Plant 7 line and appears in Plant 7 quality/maintenance data).
- **Exit:** 6 enterprise datasets committed; enterprise KBs created.

### Phase 3 — Enterprise agents  *(1–2 days)*
- Stand up the **5 enterprise agents** (Supply Chain, Procurement & Cost, Engineering/PLM, Enterprise Quality, Demand/Program) — same A2A-card + scoped-KB pattern. Register.
- **Exit:** full **10-agent pool** discoverable as one catalog; manager can enumerate it.

### Phase 4 — Magentic orchestration  *(2–3 days)*
- Wire the Magentic manager to the registry: problem statement in → discover candidates → build task ledger (facts + plan) + progress ledger (on-track? who next? looping?) → select/sequence → evaluate → **backtrack** until solved.
- Keep the reasoning model **configurable/model-agnostic** (any chat model). Do not couple to a vendor.
- Validate the **brake-caliper** composition (§5) end-to-end.
- **Exit:** manager composes the flow with **no hardcoded DAG**; backtrack works.

### Phase 5 — Demo choreography & wow moments  *(1–2 days)*
- Script 3–4 scenarios (safety, supply disruption, recall/warranty, launch readiness).
- **Hot-add moment:** drop a new agent card mid-demo → manager discovers and uses it with zero redeploy.
- Trace/visualization so the audience sees the manager's plan + ledgers + agent hops.
- **Exit:** rehearsed run-of-show; reuse + backtrack + hot-add all land.

### Phase 6 — Governance & security overlay  *(1 day, parallel from P3)*
- Entra Agent ID per-agent access scope; **blast-radius** view ("what can this agent touch / talk to").
- Sensitivity handling; posture story.
- **Exit:** per-agent scope + blast-radius demoable.

---

## 7. Proposed repo layout (target after Phase 0–3)

```
mmc_demo/
├── docs/
│   └── MMC_Plant7_Company_Profile_v1.md      # source of truth (exists)
├── kb/                                        # Plant 7 node data (exists)
│   ├── Internal/ ... 08_Logs_Data/*.csv
│   ├── oem-manuals/
│   └── regulatory-reference/OSHA/
├── enterprise/                                # NEW (Phase 2)
│   ├── supply-chain/        (supplier master, BOM/where-used, ERP inv, TMS)
│   ├── procurement/         (contracts, PO/spend, should-cost)
│   ├── engineering-plm/     (PLM part master, ECO log)
│   ├── enterprise-quality/  (warranty claims, field-failure, recall ruleset)
│   └── demand-program/      (order/CRM feed, program plan, allocation)
├── agents/                                    # NEW (Phase 0/1/3) — A2A card JSON per agent
│   ├── plant7-ehs.agent.json
│   ├── plant7-maintenance.agent.json
│   ├── plant7-quality.agent.json
│   ├── plant7-shiftops.agent.json
│   ├── plant7-training.agent.json
│   ├── ent-supply-chain.agent.json
│   ├── ent-procurement.agent.json
│   ├── ent-engineering-plm.agent.json
│   ├── ent-quality.agent.json
│   └── ent-demand-program.agent.json
├── orchestrator/                              # NEW (Phase 4) — Magentic manager app
└── DEMO_BUILD_HANDOFF.md                      # this file
```

---

## 8. Open decisions (confirm with stakeholder before/at Phase 4)
1. **Scope of first showing:** thin slice vs. full 10-agent build?
2. **Manager reasoning model:** pick a default, or keep it configurable/open in the demo?
3. **Live-trace UI:** custom web surface vs. Foundry portal threads?

## 9. Guardrails / conventions
- Stay consistent with `docs/MMC_Plant7_Company_Profile_v1.md` for every new artifact (sites, line names, ID formats, standards).
- Don't add columns to the existing CSVs without updating the profile.
- Verify all Microsoft/Azure API specifics against **Microsoft Learn** before coding (GA vs. preview, API versions).
- Keep the Magentic reasoning layer model-agnostic.
- All data is fictitious; keep it internally cross-consistent so scenarios resolve end-to-end.

## 10. Companion artifact
A rendered reference architecture + roadmap visual exists at:
`…/Microsoft Scout/CoS/artifacts/mmc-agent-network.html` (+ `.png`).
It shows the control plane, both node tiers with per-agent skills/tools, the Foundry IQ knowledge layer, the brake-caliper composition, and the 6-phase roadmap. Use it as the visual companion to this spec.
