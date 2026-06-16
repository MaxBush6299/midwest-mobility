# Gate A — Thin Slice Results

Durable tracking for the `gate-a-thin-slice` branch. Each task records what
was built, what was verified, and any deviations from the plan.

Branch: `gate-a-thin-slice`
Resource group: `rg-magentictest` (eastus)
Subscription: `<subscription-id>` (`<admin-upn>`)

---

## Tasks 1–9 — Bootstrap + Bicep deploy ✅

Commits `3dd0f01` … `738d98f`. Live Azure resources:

| Resource | Name | Notes |
|---|---|---|
| Foundry account | `mmcfdy` | `Microsoft.CognitiveServices/accounts` kind=AIServices |
| Project (plant) | `mmc-plant` | endpoint captured to `.env` |
| Project (enterprise) | `mmc-enterprise` | endpoint captured to `.env` |
| Model deployment | `gpt-4o-mini` | GlobalStandard, capacity 10 |
| Search (plant) | `srch-mmc-plant` | standard tier, semantic search on |
| Search (enterprise) | `srch-mmc-enterprise` | standard tier, semantic search on |
| Storage | `stmmcdemopzspe6qo5hmwy` | bootstrap |

Roles granted to admin OID `<admin-object-id>`:
`Search Service Contributor`, `Search Index Data Contributor` (both Search services).

---

## Task 10 — Foundry IQ KB seeder ✅

Commit: `4a70056` — `scripts/seed_foundry_iq.py`

**What it does:** For each KB source in `plants/plant7/profile.yaml`:
1. Creates an Azure AI Search index with a default `SemanticConfiguration`.
2. Walks `paths`, parses text/markdown/csv/json/yaml, batch-uploads as docs.
3. Creates a `SearchIndexKnowledgeSource` pointing at the index.
4. After all sources are registered, creates the `KnowledgeBase` `kb-plant7`
   aggregating them.

**Result (live against `srch-mmc-plant`):**

| Knowledge source | Index | Docs |
|---|---|---|
| ehs | `ks-plant7-ehs` | 10 |
| maintenance | `ks-plant7-maintenance` | 5 |
| quality_ops | `ks-plant7-quality-ops` | 7 |

→ Knowledge base `kb-plant7` is ready (3 sources, 22 docs).

**SDK gotchas worth recording for the D16 addendum:**
- `KnowledgeBase` cannot reference a Search index directly; it needs a
  `SearchIndexKnowledgeSource` registered on the service first.
- That knowledge source requires the target index to define at least one
  `SemanticConfiguration` (else: *"Target Index … does not have semantic
  configurations set"*).

---

## Task 11 — Verify Plant 7 KB grounds a sample question ✅

Replaced the plan's manual portal step with a programmatic check
(`scripts/verify_kb_retrieval.py`) so the verification is reproducible.

Three semantic queries (`query_type="semantic"`, `semantic_configuration_name="default"`),
top 3 hits each. All three returned grounded hits from the expected KB folder:

| Query | Index | Top hit |
|---|---|---|
| "What LOTO procedure applies to L1-PRS-001?" | `ks-plant7-ehs` | `plants/plant7/kb/02_EHS_Internal/MMC_P7_LOTO_SOP.md` (rerank 2.163) |
| "What is the PM schedule for the brake caliper line?" | `ks-plant7-maintenance` | `plants/plant7/kb/03_Maintenance/MMC_P7_PM_Program_Overview.md` (rerank 2.145) |
| "What are common quality defects on Line 1?" | `ks-plant7-quality-ops` | `plants/plant7/kb/04_Quality/MMC_P7_Quality_Policy.md` (rerank 2.249) |

All three queries cited files under `plants/plant7/kb/` as required by the plan's
acceptance criterion.
