# Bicep deployment

Target: resource group `rg-magentictest` in `eastus`.

## Prereqs

- Azure CLI ≥ 2.60 with Bicep CLI installed (`az bicep version`)
- Resource group already created: `az group create -n rg-magentictest -l eastus`
- Logged in to the right subscription

## Deploy

```pwsh
az login
az account set --subscription <your-sub-id>
az deployment group create `
  --resource-group rg-magentictest `
  --template-file main.bicep `
  --parameters parameters/dev.bicepparam
```

Capture outputs (used to fill `.env`):

```pwsh
az deployment group show `
  --resource-group rg-magentictest `
  --name main `
  --query properties.outputs
```

## Tear down

```pwsh
az group delete --name rg-magentictest --yes --no-wait
```

## Notes

The `foundry-project.bicep` and `foundry-iq-kb.bicep` modules contain
`TODO(verify-on-Learn)` markers. The Foundry project resource type/apiVersion
and whether Foundry IQ KB is control-plane deployable should be verified
against Microsoft Learn and pinned before the first real deploy.
