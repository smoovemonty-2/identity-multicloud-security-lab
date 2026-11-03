data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "secure" {
  name = "kv-idlab-${substr(
    md5(azurerm_resource_group.secure_platform.id),
    0,
    12
  )}"

  location            = azurerm_resource_group.secure_platform.location
  resource_group_name = azurerm_resource_group.secure_platform.name
  tenant_id           = data.azurerm_client_config.current.tenant_id

  sku_name = "standard"

  # Microsoft Entra RBAC instead of legacy access policies
  enable_rbac_authorization = true

  # Deletion and recovery protections
  soft_delete_retention_days = 7
  purge_protection_enabled   = true

  # Disable unnecessary deployment integrations
  enabled_for_deployment          = false
  enabled_for_disk_encryption     = false
  enabled_for_template_deployment = false

  # Maintain reachability from Cloud Shell during the lab
  public_network_access_enabled = true

  network_acls {
    bypass         = "None"
    default_action = "Allow"
  }

  tags = local.common_tags
}
