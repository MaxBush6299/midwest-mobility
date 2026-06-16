targetScope = 'resourceGroup'

param location string = 'eastus'
param storageNamePrefix string = 'stmmcdemo'
param searchPlantName string
param searchEnterpriseName string
param foundryAccountName string
param plantProjectName string = 'mmc-plant'
param enterpriseProjectName string = 'mmc-enterprise'
param plant7KbName string = 'kb-plant7'
param enterpriseKbName string = 'kb-enterprise'

var storageName = '${storageNamePrefix}${uniqueString(resourceGroup().id)}'

module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: { location: location, storageName: storageName }
}

module searchPlant 'modules/ai-search.bicep' = {
  name: 'searchPlant'
  params: { location: location, searchName: searchPlantName }
}

module searchEnt 'modules/ai-search.bicep' = {
  name: 'searchEnt'
  params: { location: location, searchName: searchEnterpriseName }
}

module foundry 'modules/foundry-project.bicep' = {
  name: 'foundry'
  params: {
    location: location
    accountName: foundryAccountName
    projectNames: [plantProjectName, enterpriseProjectName]
  }
}

module plantSearchConn 'modules/search-connection.bicep' = {
  name: 'plantSearchConn'
  params: {
    foundryAccountName: foundryAccountName
    projectName: plantProjectName
    connectionName: searchPlantName
    searchName: searchPlantName
  }
  dependsOn: [foundry, searchPlant]
}

module enterpriseSearchConn 'modules/search-connection.bicep' = {
  name: 'enterpriseSearchConn'
  params: {
    foundryAccountName: foundryAccountName
    projectName: enterpriseProjectName
    connectionName: searchEnterpriseName
    searchName: searchEnterpriseName
  }
  dependsOn: [foundry, searchEnt]
}

module kbPlant7 'modules/foundry-iq-kb.bicep' = {
  name: 'kbPlant7'
  params: {
    location: location
    kbName: plant7KbName
    searchResourceId: searchPlant.outputs.searchId
    sourceNames: ['ehs', 'maintenance', 'quality_ops']
  }
}

module kbEnterprise 'modules/foundry-iq-kb.bicep' = {
  name: 'kbEnterprise'
  params: {
    location: location
    kbName: enterpriseKbName
    searchResourceId: searchEnt.outputs.searchId
    sourceNames: ['supply_chain', 'procurement', 'engineering_plm', 'enterprise_quality', 'demand_program']
  }
}

output foundryAccountEndpoint string = foundry.outputs.accountEndpoint
output foundryAccountName string = foundry.outputs.accountName
output foundryModelDeploymentName string = foundry.outputs.modelDeploymentName
output foundryProjectEndpoints array = foundry.outputs.projectEndpoints
output storageAccountName string = storage.outputs.storageAccountName
output searchPlantId string = searchPlant.outputs.searchId
output searchEnterpriseId string = searchEnt.outputs.searchId
output plantSearchConnectionName string = plantSearchConn.outputs.connectionName
output enterpriseSearchConnectionName string = enterpriseSearchConn.outputs.connectionName
