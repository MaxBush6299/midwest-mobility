param location string
param kbName string
param searchResourceId string
param sourceNames array

// Foundry IQ KB is data-plane-only as of azure-ai-projects 2.2 (verified in Gate A).
// This module intentionally emits names + bindings only; `scripts/seed_foundry_iq.py`
// creates the KB at deploy-time using KnowledgeRetrievalMinimalReasoningEffort().
// The portal-managed IQ connection is created by the operator after the KB exists,
// and `agent_factory.py` then bakes the MCP tool into every agent version via
// PLANT_KB_CONNECTION_ID + PLANT_KB_MCP_URL env vars.

output kbName string = kbName
output sourceNames array = sourceNames
output location string = location
output searchResourceId string = searchResourceId
