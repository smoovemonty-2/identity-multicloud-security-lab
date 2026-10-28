variable "location" {
  description = "Azure region for the lab."
  type        = string
  default     = "eastus"
}

variable "resource_group_name" {
  description = "Dedicated secure platform resource group."
  type        = string
  default     = "rg-identity-multicloud-dev"
}
