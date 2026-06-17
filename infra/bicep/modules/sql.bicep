// Azure SQL Database (Serverless) for MMC demo ops-data tables.
//
// Used as a Foundry IQ "indexed Azure SQL knowledge source" so that
// row-level tabular data (training logs, PM schedules, PO spend, etc.)
// can be reliably retrieved by the plant/enterprise agents.
//
// Auth model: Entra-only (no SQL auth). Deployer is set as Entra admin
// at the server level; the Search service managed identity is granted
// db_datareader inside the database (out-of-band, after deploy).
//
// Serverless tier auto-pauses after 1 hour idle, so demo cost ≈ $0
// when not in active use.

param location string
param sqlServerName string
param sqlDatabaseName string = 'mmcops'

@description('Object ID of the Entra principal (user or group) that will be SQL admin.')
param aadAdminObjectId string

@description('Display name / UPN of the Entra principal that will be SQL admin.')
param aadAdminLogin string

@description('Principal type for the Entra admin (User, Group, or Application).')
@allowed(['User', 'Group', 'Application'])
param aadAdminPrincipalType string = 'User'

resource sqlServer 'Microsoft.Sql/servers@2023-08-01-preview' = {
  name: sqlServerName
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    administrators: {
      administratorType: 'ActiveDirectory'
      principalType: aadAdminPrincipalType
      login: aadAdminLogin
      sid: aadAdminObjectId
      tenantId: subscription().tenantId
      azureADOnlyAuthentication: true
    }
  }
}

// Allow Azure services (so AI Search + our local az-CLI session can connect).
resource allowAzureServices 'Microsoft.Sql/servers/firewallRules@2023-08-01-preview' = {
  parent: sqlServer
  name: 'AllowAllAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// Open client IPs for demo seeding from local machines. Tighten before any
// real production-style use.
resource allowAllClientIps 'Microsoft.Sql/servers/firewallRules@2023-08-01-preview' = {
  parent: sqlServer
  name: 'AllowAllClientIPsDemo'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '255.255.255.255'
  }
}

resource sqlDb 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  parent: sqlServer
  name: sqlDatabaseName
  location: location
  sku: {
    name: 'GP_S_Gen5_2'
    tier: 'GeneralPurpose'
    family: 'Gen5'
    capacity: 2
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    autoPauseDelay: 60
    minCapacity: json('0.5')
    maxSizeBytes: 34359738368 // 32 GB
    zoneRedundant: false
    readScale: 'Disabled'
    requestedBackupStorageRedundancy: 'Local'
  }
}

output sqlServerName string = sqlServer.name
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName
output sqlDatabaseName string = sqlDb.name
output sqlServerPrincipalId string = sqlServer.identity.principalId
