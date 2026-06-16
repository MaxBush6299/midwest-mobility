param foundryAccountName string
param projectName string
param connectionName string
param searchName string

resource search 'Microsoft.Search/searchServices@2024-03-01-preview' existing = {
  name: searchName
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' existing = {
  name: '${foundryAccountName}/${projectName}'
}

resource conn 'Microsoft.CognitiveServices/accounts/projects/connections@2025-04-01-preview' = {
  parent: project
  name: connectionName
  properties: {
    category: 'CognitiveSearch'
    target: 'https://${searchName}.search.windows.net/'
    authType: 'AAD'
    isSharedToAll: true
    metadata: {
      ApiType: 'Azure'
      ResourceId: search.id
      Location: search.location
    }
  }
}

output connectionId string = conn.id
output connectionName string = conn.name
