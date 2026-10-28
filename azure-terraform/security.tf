# Application subnet network security group
resource "azurerm_network_security_group" "app" {
  name                = "nsg-idlab-app"
  location            = azurerm_resource_group.secure_platform.location
  resource_group_name = azurerm_resource_group.secure_platform.name

  security_rule {
    name                       = "DenyDataToApp"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "10.40.2.0/24"
    destination_address_prefix = "10.40.1.0/24"
  }

  security_rule {
    name                       = "DenyInternetInbound"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "Internet"
    destination_address_prefix = "*"
  }

  tags = local.common_tags
}

# Data subnet network security group
resource "azurerm_network_security_group" "data" {
  name                = "nsg-idlab-data"
  location            = azurerm_resource_group.secure_platform.location
  resource_group_name = azurerm_resource_group.secure_platform.name

  security_rule {
    name                       = "DenyAppToData"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "10.40.1.0/24"
    destination_address_prefix = "10.40.2.0/24"
  }

  security_rule {
    name                       = "DenyInternetInbound"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "Internet"
    destination_address_prefix = "*"
  }

  tags = local.common_tags
}

# Apply the NSGs to their respective subnets
resource "azurerm_subnet_network_security_group_association" "app" {
  subnet_id                 = azurerm_subnet.app.id
  network_security_group_id = azurerm_network_security_group.app.id
}

resource "azurerm_subnet_network_security_group_association" "data" {
  subnet_id                 = azurerm_subnet.data.id
  network_security_group_id = azurerm_network_security_group.data.id
}
