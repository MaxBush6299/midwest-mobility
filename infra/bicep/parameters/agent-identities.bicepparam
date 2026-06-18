using '../modules/agent-identities.bicep'

// One UAMI per agent. Order matches agents/catalog.json (excluding the demo-only
// hot-add agent, which lives in-memory only). The external-auditor IS included
// because the sensitivity demo's whole point is that its UAMI is distinct from
// plant7-ehs's UAMI even though they share a KB.
param location = 'eastus'

param foundryProjectId = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mmc-demo/providers/Microsoft.CognitiveServices/accounts/mmc-foundry/projects/mmc-plant'

param agentNames = [
  'plant7-ehs'
  'plant7-external-auditor'
  'plant7-maintenance'
  'plant7-quality'
  'plant7-shiftops'
  'plant7-training'
  'ent-supply-chain'
  'ent-procurement'
  'ent-engineering-plm'
  'ent-quality'
  'ent-demand-program'
]

param namePrefix = 'mmc-agent-'
