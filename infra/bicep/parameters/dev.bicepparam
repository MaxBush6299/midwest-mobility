using '../main.bicep'

param location = 'eastus'
param storageName = 'stmmcdemo${uniqueString(resourceGroup().id)}'
param searchPlantName = 'srch-mmc-plant'
param searchEnterpriseName = 'srch-mmc-enterprise'
param foundryPlantProjectName = 'mmc-foundry-plant'
param foundryEnterpriseProjectName = 'mmc-foundry-enterprise'
