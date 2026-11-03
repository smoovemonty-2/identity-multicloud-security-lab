# Secure Azure Terraform Infrastructure

Terraform-based Azure security engineering lab covering infrastructure provisioning, data protection, secrets management, managed identities, and least-privilege RBAC.

## Architecture

**Networking**
- Dedicated resource group and virtual network
- Separate application and data subnets
- Network security groups with explicit inbound deny rules

**Data Protection**
- Secure Azure Storage account
- Blob versioning and soft delete
- Disabled Shared Key authentication and anonymous Blob access

**Identity and Secrets**
- Azure Key Vault with RBAC authorization and purge protection
- User-assigned managed identity
- Storage Blob Data Reader and Key Vault Secrets User role assignments

**Infrastructure Management**
- Azure Blob remote Terraform state
- Microsoft Entra authentication
- Container-scoped backend data permissions
- Azure Policy-compliant resource tags

## Prerequisites

- Terraform compatible with the repository's version constraints
- Azure CLI authenticated to the authorized subscription
- Required Azure resource provider registrations
- Appropriate infrastructure deployment and RBAC administration permissions
- Access to the existing AzureRM remote backend

## Reconnecting to the Existing Environment

Restore the source files from GitHub and authenticate to Azure:

```bash
az login --use-device-code
az account set --subscription YOUR_SUBSCRIPTION
```

Configure the Azure subscription and tenant environment variables:

```bash
export ARM_SUBSCRIPTION_ID="$(az account show --query id -o tsv)"
export ARM_TENANT_ID="$(az account show --query tenantId -o tsv)"
```

Create a private backend configuration using the **existing** storage resource group, storage account, `tfstate` container, and state key.

Then initialize:

```bash
terraform init \
  -reconfigure \
  -backend-config=/path/to/backend.private.hcl
```

Never create an empty replacement state file to reconnect to existing infrastructure.

## Validation

```bash
terraform fmt -check -recursive
terraform validate
terraform plan -detailed-exitcode
```

Exit code `0` from the final plan indicates no changes are proposed. Exit code `2` indicates proposed changes, and exit code `1` indicates an error.

## Security Notes

Do not commit credentials, private backend configuration, Terraform state, saved plans, or actual secret values.

The subscription requires `Environment=Production`, although these resources are used for a lab.

Storage and Key Vault have public endpoints enabled for lab administration and are not fully network-isolated.

Managed identity access has been validated through role assignments and scopes, not through application-level data-plane testing.

## Documentation

- `../docs/session-06-azure-terraform-validation.md`
- `../docs/session-07-azure-data-identity-validation.md`

## Future Work

Add private endpoints, automated security tests, CI/CD workflows, workload identity validation, and continuous monitoring.
