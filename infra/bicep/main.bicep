targetScope = 'resourceGroup'

param location string = 'eastus'
param storageName string
param searchPlantName string
param searchEnterpriseName string
param foundryPlantProjectName string
param foundryEnterpriseProjectName string
param plant7KbName string = 'kb-plant7'
param enterpriseKbName string = 'kb-enterprise'

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

module foundryPlant 'modules/foundry-project.bicep' = {
  name: 'foundryPlant'
  params: { location: location, projectName: foundryPlantProjectName, tier: 'plant' }
}

module foundryEnt 'modules/foundry-project.bicep' = {
  name: 'foundryEnt'
  params: { location: location, projectName: foundryEnterpriseProjectName, tier: 'enterprise' }
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

output foundryPlantEndpoint string = foundryPlant.outputs.projectEndpoint
output foundryEnterpriseEndpoint string = foundryEnt.outputs.projectEndpoint
output storageAccountName string = storage.outputs.storageAccountName
