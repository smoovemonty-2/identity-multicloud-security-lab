resource "azurerm_user_assigned_identity" "workload" {
  name = "id-idlab-workload"

  resource_group_name = azurerm_resource_group.secure_platform.name
  location            = azurerm_resource_group.secure_platform.location

  tags = local.common_tags
}
