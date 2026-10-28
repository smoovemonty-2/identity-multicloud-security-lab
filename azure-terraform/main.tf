locals {
  common_tags = {
    Project     = "identity-multicloud-security-lab"
    Environment = "Production"
    Purpose     = "security-lab"
    ManagedBy   = "Terraform"
    Phase       = "2"
  }
}

resource "azurerm_resource_group" "secure_platform" {
  name     = var.resource_group_name
  location = var.location

  tags = local.common_tags
}
