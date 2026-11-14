# Setup guide

These steps describe a manual setup so you can see exactly what happens at each stage. Portal labels and policy requirements can differ between organizations.

## 1. Plan environments and naming

- Use neutral names such as `<prefix>-dev-ws`, `<prefix>-test-ws` and `<prefix>-prod-ws`.
- Confirm the Azure region, Fabric capacity, subscription permissions, address space, subnets, DNS ownership and outbound connectivity.
- Create a virtual network with at least an agent subnet and a private endpoint subnet.

## 2. Set up the Fabric workspaces

- Assign each workspace to a Fabric F SKU capacity. Premium (P SKU) and trial capacities aren't supported for workspace-level private links.
- Ask a Fabric administrator to enable the tenant setting **Configure workspace-level inbound network rules**.
- Add the deployment service principal to each workspace with the minimum role it needs.

## 3. Deploy the self-hosted agent

- Create a VM in the agent subnet and apply your organization's baseline for patching, endpoint protection, logging and admin access.
- Don't expose management ports to the internet. Use Azure Bastion or another approved path.
- Allow outbound access to Azure DevOps, Microsoft Entra ID, package feeds, Key Vault and Fabric through your egress controls.
- Install Python 3.9 to 3.14 and make sure `python` is on the agent's PATH.
- Register the agent in a pool, add the pool to the project and authorize the pipeline to use it.

## 4. Configure identity and secrets

- Register a Microsoft Entra application and service principal, and grant it the required role on each workspace.
- Store the tenant ID, client ID and client secret in Azure Key Vault.
- Create one variable group per environment: `fabric-dev`, `fabric-test` and `fabric-prod`. A group linked to Key Vault can only hold Key Vault secrets, so either store the workspace ID and name in Key Vault too, or add a second variable group to each stage for them.

| Variable | Mapped to | Notes |
| --- | --- | --- |
| `fabricTenantId` | `FABRIC_TENANT_ID` | Microsoft Entra tenant ID |
| `fabricClientId` | `FABRIC_CLIENT_ID` | Application (client) ID of the service principal |
| `fabricClientSecret` | `FABRIC_CLIENT_SECRET` | Secret, read from Key Vault at runtime |
| `workspaceId` | `TARGET_WORKSPACE_ID` | ID of the target workspace |
| `workspaceName` | `TARGET_WORKSPACE_NAME` | Name of the target workspace |

## 5. Configure workspace-level private links

- The first time you use workspace-level private links in a subscription, re-register the `Microsoft.Fabric` resource provider.
- For each workspace, create a private link service (`Microsoft.Fabric/privateLinkServicesForFabric`) and a private endpoint by following the Microsoft Learn setup guide.
- Link the private DNS zones to the agent's virtual network.
- From the agent VM, confirm that each workspace FQDN resolves to a private IP address and that HTTPS works. The API FQDN has the form `https://{workspaceId}.z{xy}.w.api.fabric.microsoft.com`, where `{workspaceId}` is the workspace ID without dashes and `{xy}` is its first two characters.
- Keep public access enabled until a baseline deployment succeeds.

## 6. Prepare the repository

Commit your item definitions under `workspace/` with Fabric Git integration. See [workspace/README.md](../workspace/README.md) for the expected layout.

## 7. Review deploy.py

`deploy.py` reads its configuration from environment variables, sets the workspace-specific FQDN, then creates the `FabricWorkspace` client and publishes the items. Update `item_type_in_scope` to match the item types you deploy.

## 8. Create the pipeline

- Create the Azure DevOps environments `fabric-dev`, `fabric-test` and `fabric-prod`, and add approval checks to test and prod.
- Replace `<self-hosted-agent-pool>` in `azure-pipelines.yml` with your pool name, then create the pipeline from the file.
- The stages run in order: DEV, then TEST, then PROD.

## 9. Validate in phases

1. **Baseline:** With public access still allowed, run the DEV deployment and confirm that authentication, packaging and publishing succeed.
2. **Private endpoint:** From the agent VM, confirm that the DEV workspace FQDN resolves to a private IP address.
3. **Restrict inbound access:** Deny public inbound access on DEV, wait for the policy to apply, then make a read-only Fabric REST call through the workspace FQDN.
4. **Write test:** Create or update a supported test item, then read it back.
5. **Real deployment:** Run the pipeline and confirm that the item is updated in DEV.
6. **Negative test:** From a device outside the private network, confirm that public access is blocked.
7. **Promote:** Repeat the setup for TEST and PROD, using the pipeline and its approval checks.

## Troubleshooting

| Symptom | Likely cause | What to check |
| --- | --- | --- |
| Request denied by inbound communication policy | Requests are going to the public endpoint | Set the workspace FQDN before you create the `FabricWorkspace` client |
| Workspace not found | Configuration or permissions | The workspace name and ID mapping, and the service principal's role |
| Agent offline, or the pipeline can't find the pool | Agent pool setup | The pool is added to the project and authorized for the pipeline |
| Workspace FQDN resolves to a public IP, or not at all | DNS | Private DNS zone links, records, conditional forwarders and the resolver the agent uses |
| Authentication works but deployment fails | Item support or permissions | Item type support, workspace permissions, the fabric-cicd version and the private link support matrix |
| Agent VM has no outbound access | Egress design | An approved outbound path, such as NAT Gateway, Azure Firewall or a proxy, with the required destination rules |
