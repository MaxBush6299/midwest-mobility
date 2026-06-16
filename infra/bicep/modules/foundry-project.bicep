param location string
param projectName string
param tier string

// TODO(verify-on-Learn): confirm resource type + apiVersion for Foundry project.
// Likely candidates as of 2026: Microsoft.MachineLearningServices/workspaces (kind=Project),
// or the newer Microsoft.AIFoundry namespace. Pin the correct one before deploying.
resource project 'Microsoft.MachineLearningServices/workspaces@2024-10-01' = {
  name: projectName
  location: location
  kind: 'Project'
  identity: { type: 'SystemAssigned' }
  properties: {
    friendlyName: 'MMC ${tier} Foundry Project'
  }
}

output projectId string = project.id
output projectName string = project.name
output projectEndpoint string = project.properties.discoveryUrl
