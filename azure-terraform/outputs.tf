output "resource_group_name" {
  description = "Terraform-managed lab resource group."
  value       = azurerm_resource_group.secure_platform.name
}

output "virtual_network_name" {
  description = "Name of the Azure lab VNet."
  value       = azurerm_virtual_network.lab.name
}

output "virtual_network_address_space" {
  description = "Address space of the lab VNet."
  value       = azurerm_virtual_network.lab.address_space
}

output "app_subnet_id" {
  description = "Application subnet resource ID."
  value       = azurerm_subnet.app.id
}

output "data_subnet_id" {
  description = "Data subnet resource ID."
  value       = azurerm_subnet.data.id
}

output "app_nsg_name" {
  description = "Application subnet NSG."
  value       = azurerm_network_security_group.app.name
}

output "data_nsg_name" {
  description = "Data subnet NSG."
  value       = azurerm_network_security_group.data.name
}

output "data_storage_account_name" {
  description = "Secure application-data Storage account name."
  value       = azurerm_storage_account.data.name
}

output "data_storage_account_id" {
  description = "Secure application-data Storage account resource ID."
  value       = azurerm_storage_account.data.id
}

output "key_vault_name" {
  description = "Name of the secure Azure Key Vault."
  value       = azurerm_key_vault.secure.name
}

output "key_vault_id" {
  description = "Resource ID for scoped RBAC assignments."
  value       = azurerm_key_vault.secure.id
}

output "key_vault_uri" {
  description = "Key Vault endpoint."
  value       = azurerm_key_vault.secure.vault_uri
}

output "workload_identity_id" {
  description = "Azure resource ID of the workload managed identity."
  value       = azurerm_user_assigned_identity.workload.id
}

output "workload_identity_client_id" {
  description = "Client ID used to select the managed identity."
  value       = azurerm_user_assigned_identity.workload.client_id
}

output "workload_identity_principal_id" {
  description = "Entra service principal object ID used for RBAC."
  value       = azurerm_user_assigned_identity.workload.principal_id
}
