// agent-identities.bicep — provisions one User-Assigned Managed Identity (UAMI)
// per agent so each Foundry agent gets its own Entra principal. This is what
// makes the blast-radius overlay believable: "revoke this UAMI -> only this
// agent loses access", and it's a prerequisite for handing agents distinct
// privileges (e.g. plant7-ehs reading ehs_restricted while plant7-external-
// auditor cannot).
//
// Intentionally a sub-deployment — it does NOT mutate main.bicep. Deploy
// stand-alone, then wire the resulting identity principalIds into agent
// role assignments / Foundry connections out-of-band.
//
// Usage (per project):
//   az deployment group create \
//     --resource-group <rg> \
//     --template-file infra/bicep/modules/agent-identities.bicep \
//     --parameters infra/bicep/parameters/agent-identities.bicepparam \
//     --parameters foundryProjectId='/subscriptions/.../projects/mmc-plant'
//
// Re-running is idempotent — UAMI is a CRUD-shaped resource so existing
// identities are preserved.

@description('Azure region for the UAMIs. Should match the Foundry project region.')
param location string

@description('Names of the agents that need their own UAMI (typically the catalog name, e.g. plant7-ehs).')
param agentNames array

@description('Foundry project resource ID this batch of identities is scoped to. Used only as a tag for traceability.')
param foundryProjectId string

@description('Optional prefix prepended to each UAMI name to disambiguate environments.')
param namePrefix string = 'mmc-agent-'

resource agentUamis 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = [for name in agentNames: {
  name: '${namePrefix}${name}'
  location: location
  tags: {
    'mmc:agent': name
    'mmc:foundryProjectId': foundryProjectId
    'mmc:purpose': 'per-agent-identity'
  }
}]

output agentIdentities array = [for (name, i) in agentNames: {
  agentName: name
  uamiName: agentUamis[i].name
  uamiResourceId: agentUamis[i].id
  uamiPrincipalId: agentUamis[i].properties.principalId
  uamiClientId: agentUamis[i].properties.clientId
}]
