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
// SQL AAD admin = the deploying user/group. Fill these in for your tenant, e.g.:
//   az ad signed-in-user show --query '{id:id, upn:userPrincipalName}'
param sqlAadAdminObjectId = '<your-sql-admin-object-id>'
param sqlAadAdminLogin = '<your-sql-admin-upn>'
param sqlAadAdminPrincipalType = 'User'
