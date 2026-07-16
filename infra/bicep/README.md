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

Foundry IQ KB is data-plane-only as of `azure-ai-projects` 2.2; the
`foundry-iq-kb.bicep` module emits names and bindings only, and
`scripts/seed_foundry_iq.py` creates the KB at deploy time. The portal-managed
IQ connection is then created by the operator and surfaced to agents via the
`PLANT_KB_CONNECTION_ID` + `PLANT_KB_MCP_URL` env vars consumed by
`agent_factory.py`. All Foundry agents are provisioned as portal-managed
prompt agents (`PromptAgentDefinition`), never via the classic
`azure-ai-agents` SDK (retired 2027-03-31).
