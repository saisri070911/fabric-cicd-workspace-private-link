import os

from azure.identity import ClientSecretCredential
from fabric_cicd import FabricWorkspace, configure_fabric_fqdn, publish_all_items

# Read configuration at runtime. Never hard-code secrets.
tenant_id = os.environ["FABRIC_TENANT_ID"]
client_id = os.environ["FABRIC_CLIENT_ID"]
client_secret = os.environ["FABRIC_CLIENT_SECRET"]
workspace_id = os.environ["TARGET_WORKSPACE_ID"]
workspace_name = os.environ["TARGET_WORKSPACE_NAME"]
repository_directory = os.environ.get("REPOSITORY_DIRECTORY", "workspace")

credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret,
)

# Key step: target the workspace-specific Fabric FQDN first.
configure_fabric_fqdn(workspace_id)

target = FabricWorkspace(
    workspace_name=workspace_name,
    environment=os.environ.get("DEPLOYMENT_ENVIRONMENT", "DEV"),
    repository_directory=repository_directory,
    item_type_in_scope=["Notebook", "Lakehouse"],
    token_credential=credential,
)

publish_all_items(target)
