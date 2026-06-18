using '../main.bicep'

param location = 'eastus'
param searchPlantName = 'srch-mmc-plant'
param searchPlant4Name = 'srch-mmc-plant4'
param searchEnterpriseName = 'srch-mmc-enterprise'
param foundryAccountName = 'mmcfdy'
param plantProjectName = 'mmc-plant'
param plant4ProjectName = 'mmc-plant4'
param enterpriseProjectName = 'mmc-enterprise'

// Azure SQL (Pattern A). Admin = current deployer. Note: SQL lives in centralus
// (eastus + eastus2 not accepting new SQL servers as of provisioning); other
// resources remain in eastus.
param sqlServerName = 'sql-mmc-demo-91327'
param sqlDatabaseName = 'mmcops'
param sqlAadAdminObjectId = '<admin-object-id>'
param sqlAadAdminLogin = '<admin-upn>'
param sqlAadAdminPrincipalType = 'User'
