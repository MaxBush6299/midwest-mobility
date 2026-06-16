# SDK Addendum — Verified Microsoft Learn Facts (2026-06-16)

Captured during Gate A Task 9–10 implementation. Resolves every `TODO(verify-on-Learn)` marker in the original spec and Gate A plan with real package names, import paths, and API shapes.

This addendum is **authoritative** — where it conflicts with the original spec or any plan, this document wins.

---

## D16 — Foundry IQ ≡ Azure AI Search Knowledge Base

**Source:** https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-create-knowledge-base

Foundry IQ is not a standalone resource. A "Foundry IQ knowledge base" is an Azure AI Search knowledge base created against a Search service via the `azure-search-documents` preview Python SDK. Our existing `srch-mmc-plant` and `srch-mmc-enterprise` Search services from `infra/bicep/` are the hosting resources for the two KBs (one per Search instance).

**Package:**
```
pip install --pre azure-search-documents
pip install azure-identity
```

**Authoring pattern (per Search service):**
```python
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    KnowledgeBase, KnowledgeSourceReference,
    SearchIndex, SimpleField, SearchableField, SearchFieldDataType,
)

cred = DefaultAzureCredential()
idx = SearchIndexClient(endpoint=search_endpoint, credential=cred)

# 1. Per source: create a Search index holding the source's documents
idx.create_or_update_index(SearchIndex(
    name="ks-ehs-index",
    fields=[
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="source_path", type=SearchFieldDataType.String, filterable=True),
    ],
))

# 2. Per source: create a knowledge source wrapping the index
# (use the AzureAISearch knowledge-source variant — see SDK models)
# 3. Create the KB referencing all knowledge sources
idx.create_or_update_knowledge_base(KnowledgeBase(
    name="kb-plant7",
    description="MMC Plant 7 grounding for EHS / maintenance / quality_ops agents",
    knowledge_sources=[
        KnowledgeSourceReference(name="ks-ehs"),
        KnowledgeSourceReference(name="ks-maintenance"),
        KnowledgeSourceReference(name="ks-quality-ops"),
    ],
))
```

**Document upload:** push documents directly via `SearchClient(index_name).upload_documents(...)` after parsing source files into `{id, content, source_path}` records. The plan's "upload files in place" via a high-level KB client does not exist — we do extraction + push ourselves.

**RBAC required:**
- User running seed: `Search Service Contributor` on `srch-mmc-plant` and `srch-mmc-enterprise`
- Search service managed identity: `Cognitive Services User` on `mmcfdy` Foundry account (only if KB uses an LLM for answer synthesis — for thin slice, skip; use `output_mode=null` / minimal extractive)

**Region:** Agentic retrieval is available in `eastus` ✓.

---

## D17 — Microsoft Agent Framework Python SDK

**Source:** https://learn.microsoft.com/agent-framework/overview, https://github.com/microsoft/agent-framework/blob/main/python/samples/03-workflows/orchestrations/magentic.py

**Packages:**
```
pip install --pre agent-framework        # meta package (installs core + all providers)
# OR pick subset:
pip install --pre agent-framework-core agent-framework-foundry
```

**Imports** (all from `agent_framework`, regardless of which subpackage installed):
```python
from agent_framework import Agent, AgentResponseUpdate, Message, WorkflowEvent
from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import (
    MagenticBuilder, MagenticProgressLedger, GroupChatRequestSentEvent,
)
from azure.identity import AzureCliCredential
```

**Chat client (per agent, against our Foundry projects):**
```python
client = FoundryChatClient(
    project_endpoint=os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"],
    model=os.environ["FOUNDRY_MODEL_DEPLOYMENT"],  # 'gpt-4o-mini'
    credential=AzureCliCredential(),
)
```

**Agent construction:**
```python
agent = Agent(
    name="Plant7-EHS",
    description="...",
    instructions="...",
    client=client,
    tools=[...],  # @tool-decorated callables OR client.get_code_interpreter_tool() etc.
)
```

**Magentic orchestration (replaces our `MmcMagenticManager` design):**
```python
workflow = MagenticBuilder(
    participants=[agent1, agent2, ...],
    intermediate_output_from=[agent1, agent2, ...],
    manager_agent=manager_agent,        # a regular Agent acting as orchestrator
    max_round_count=10,
    max_stall_count=3,
    max_reset_count=2,
).build()

async for event in workflow.run(task, stream=True):
    # event.type ∈ {'intermediate', 'output', 'magentic_orchestrator', ...}
    ...
```

**Class-name impact on our plans:** The plan referred to `MmcMagenticManager` as our own class. The real Framework uses `StandardMagenticManager` internally but the user-facing API is `MagenticBuilder`. Our `manager.py` becomes a thin wrapper that:
1. Loads all agents from the catalog (`LocalCatalogSource`)
2. Constructs a `manager_agent` from instructions in YAML
3. Builds the workflow via `MagenticBuilder`
4. Runs it and emits our typed events
We keep the `MmcMagenticManager` class name (it owns config, lifecycle, and our trace event emission).

---

## D18 — Foundry Agent Service Provider Choice

Agent Framework's `FoundryChatClient` talks to a Foundry project endpoint (`https://<account>.cognitiveservices.azure.com/api/projects/<project>`). It can use a model deployed on the Foundry account directly — no separate Azure OpenAI resource needed, which matches our current deploy (gpt-4o-mini deployed on `mmcfdy`).

For agents that need tools beyond what the Agent Service hosts, we attach `@tool`-decorated Python callables to the `Agent(tools=[...])` parameter. These run **client-side** (in our Python process), not server-side in the Agent Service. This is fine for thin slice; later we can promote tools to MCP servers.

---

## D19 — Authentication

All Azure SDK calls use `DefaultAzureCredential` (production) or `AzureCliCredential` (dev). `az login` with the admin account (`<admin-upn>`) is the dev path.

Roles already required for thin slice (must be granted):
- `Cognitive Services User` on `mmcfdy` (calling agents)
- `Search Service Contributor` on both Search services (creating KBs)
- `Storage Blob Data Contributor` on the storage account (uploading source docs)

---

## Capability Hosts deferred

The Foundry sample wires `capabilityHosts` of kind `Agents` on both the account and each project. We **skipped** these in our Bicep deploy because:
1. The sample wires them to a BYO Azure OpenAI connection we don't have
2. Without BYO, agents created via `FoundryChatClient` may still work for direct chat completion, but server-hosted Agent Service features (assistants, threads, file search) require capability hosts

If Task 22 (`agent_factory.py`) hits an error like "agents capability not enabled on project", we add a follow-up Bicep update creating capability hosts that point at the account's own AIServices model deployment. Leaving as a known potential blocker.
