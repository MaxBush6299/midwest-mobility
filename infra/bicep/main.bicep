targetScope = 'resourceGroup'

param location string = 'eastus'
param storageNamePrefix string = 'stmmcdemo'
param searchPlantName string
param searchPlant4Name string = 'srch-mmc-plant4'
param searchEnterpriseName string
param foundryAccountName string
param plantProjectName string = 'mmc-plant'
param plant4ProjectName string = 'mmc-plant4'
param enterpriseProjectName string = 'mmc-enterprise'
param plant7KbName string = 'kb-plant7'
param plant4KbName string = 'kb-plant4'
param enterpriseKbName string = 'kb-enterprise'

// Azure SQL (Pattern A — Foundry IQ indexed Azure SQL knowledge source).
param sqlServerName string = 'sql-mmc-demo'
param sqlDatabaseName string = 'mmcops'
param sqlAadAdminObjectId string
param sqlAadAdminLogin string
param sqlAadAdminPrincipalType string = 'User'

var storageName = '${storageNamePrefix}${uniqueString(resourceGroup().id)}'

module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: { location: location, storageName: storageName }
}

module searchPlant 'modules/ai-search.bicep' = {
  name: 'searchPlant'
  params: { location: location, searchName: searchPlantName }
}

module searchPlant4 'modules/ai-search.bicep' = {
  name: 'searchPlant4'
  params: { location: location, searchName: searchPlant4Name }
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
    projectNames: [plantProjectName, plant4ProjectName, enterpriseProjectName]
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

module plant4SearchConn 'modules/search-connection.bicep' = {
  name: 'plant4SearchConn'
  params: {
    foundryAccountName: foundryAccountName
    projectName: plant4ProjectName
    connectionName: searchPlant4Name
    searchName: searchPlant4Name
  }
  dependsOn: [foundry, searchPlant4]
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

module kbPlant4 'modules/foundry-iq-kb.bicep' = {
  name: 'kbPlant4'
  params: {
    location: location
    kbName: plant4KbName
    searchResourceId: searchPlant4.outputs.searchId
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

module sql 'modules/sql.bicep' = {
  name: 'sql'
  params: {
    location: location
    sqlServerName: sqlServerName
    sqlDatabaseName: sqlDatabaseName
    aadAdminObjectId: sqlAadAdminObjectId
    aadAdminLogin: sqlAadAdminLogin
    aadAdminPrincipalType: sqlAadAdminPrincipalType
  }
}

output foundryAccountEndpoint string = foundry.outputs.accountEndpoint
output foundryAccountName string = foundry.outputs.accountName
output foundryModelDeploymentName string = foundry.outputs.modelDeploymentName
output foundryProjectEndpoints array = foundry.outputs.projectEndpoints
output storageAccountName string = storage.outputs.storageAccountName
output searchPlantId string = searchPlant.outputs.searchId
output searchPlant4Id string = searchPlant4.outputs.searchId
output searchEnterpriseId string = searchEnt.outputs.searchId
output plantSearchConnectionName string = plantSearchConn.outputs.connectionName
output plant4SearchConnectionName string = plant4SearchConn.outputs.connectionName
output enterpriseSearchConnectionName string = enterpriseSearchConn.outputs.connectionName
output sqlServerFqdn string = sql.outputs.sqlServerFqdn
output sqlDatabaseName string = sql.outputs.sqlDatabaseName
