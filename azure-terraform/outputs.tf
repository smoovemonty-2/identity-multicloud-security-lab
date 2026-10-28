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
