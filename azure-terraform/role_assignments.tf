# Read-only access to application-data Blob Storage
resource "azurerm_role_assignment" "workload_blob_reader" {
  scope                = azurerm_storage_account.data.id
  role_definition_name = "Storage Blob Data Reader"

  principal_id   = azurerm_user_assigned_identity.workload.principal_id
  principal_type = "ServicePrincipal"

  # Avoid Entra replication timing issues for new identities
  skip_service_principal_aad_check = true
}

# Permission to read secrets from this specific Key Vault
resource "azurerm_role_assignment" "workload_secrets_user" {
  scope                = azurerm_key_vault.secure.id
  role_definition_name = "Key Vault Secrets User"

  principal_id   = azurerm_user_assigned_identity.workload.principal_id
  principal_type = "ServicePrincipal"

  skip_service_principal_aad_check = true
}
