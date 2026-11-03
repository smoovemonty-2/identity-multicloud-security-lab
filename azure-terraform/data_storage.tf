resource "azurerm_storage_account" "data" {
  name = "stidlabs${substr(
    md5(azurerm_resource_group.secure_platform.id),
    0,
    12
  )}"

  resource_group_name = azurerm_resource_group.secure_platform.name
  location            = azurerm_resource_group.secure_platform.location

  account_kind             = "StorageV2"
  account_tier             = "Standard"
  account_replication_type = "LRS"

  # Secure transport and authentication
  https_traffic_only_enabled       = true
  min_tls_version                  = "TLS1_2"
  shared_access_key_enabled        = false
  default_to_oauth_authentication  = true
  allow_nested_items_to_be_public  = false
  cross_tenant_replication_enabled = false

  # Public endpoint retained for lab accessibility
  public_network_access_enabled = true

  # Data recovery protections
  blob_properties {
    versioning_enabled = true

    delete_retention_policy {
      days = 7
    }

    container_delete_retention_policy {
      days = 7
    }
  }

  tags = local.common_tags
}
