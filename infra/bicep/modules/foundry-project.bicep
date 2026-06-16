param location string
param accountName string
param projectNames array
param modelDeploymentName string = 'gpt-4o-mini'
param modelName string = 'gpt-4o-mini'
param modelVersion string = '2024-07-18'
param modelSkuCapacity int = 10

resource account 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' = {
  name: accountName
  location: location
  sku: { name: 'S0' }
  kind: 'AIServices'
  identity: { type: 'SystemAssigned' }
  properties: {
    allowProjectManagement: true
    customSubDomainName: accountName
    networkAcls: {
      defaultAction: 'Allow'
      virtualNetworkRules: []
      ipRules: []
    }
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: false
  }
}

resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' = {
  parent: account
  name: modelDeploymentName
  sku: {
    name: 'GlobalStandard'
    capacity: modelSkuCapacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
  }
}

@batchSize(1)
resource projects 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' = [for projectName in projectNames: {
  parent: account
  name: projectName
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    description: 'MMC Reusable Agent Network — ${projectName}'
    displayName: projectName
  }
  dependsOn: [
    modelDeployment
  ]
}]

output accountId string = account.id
output accountName string = account.name
output accountEndpoint string = account.properties.endpoint
output modelDeploymentName string = modelDeployment.name
output projectNames array = [for (p, i) in projectNames: projects[i].name]
output projectEndpoints array = [for (p, i) in projectNames: '${account.properties.endpoint}api/projects/${projects[i].name}']

