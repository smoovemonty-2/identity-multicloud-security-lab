resource "azurerm_virtual_network" "lab" {
  name                = "vnet-idlab-dev"
  location            = azurerm_resource_group.secure_platform.location
  resource_group_name = azurerm_resource_group.secure_platform.name

  address_space = ["10.40.0.0/16"]

  tags = local.common_tags
}

resource "azurerm_subnet" "app" {
  name                 = "snet-app"
  resource_group_name  = azurerm_resource_group.secure_platform.name
  virtual_network_name = azurerm_virtual_network.lab.name

  address_prefixes = ["10.40.1.0/24"]
}

resource "azurerm_subnet" "data" {
  name                 = "snet-data"
  resource_group_name  = azurerm_resource_group.secure_platform.name
  virtual_network_name = azurerm_virtual_network.lab.name

  address_prefixes = ["10.40.2.0/24"]
}
