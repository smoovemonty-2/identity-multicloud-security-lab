# Session 7 — Azure Data Protection, Key Vault & Workload Identity

## Objective

Extend an existing Terraform-managed Azure security environment with secure data storage, secrets-management infrastructure, a user-assigned managed identity, and resource-scoped Azure RBAC.

The project demonstrates Infrastructure as Code, cloud identity security, data protection, configuration validation, and troubleshooting.

## Technologies

- Terraform with HashiCorp AzureRM Provider 4.x
- Microsoft Azure Storage
- Azure Key Vault
- Microsoft Entra ID
- User-assigned managed identities
- Azure RBAC
- Azure Policy
- Azure CLI and Cloud Shell

## Architecture

The new security components integrate with the existing Azure resource group and protected remote Terraform state.

### Secure Application-Data Storage

Provisioned an Azure Storage account with:

- HTTPS required
- Minimum TLS version 1.2
- Shared Key authentication disabled
- Anonymous blob access disabled
- Microsoft Entra authentication preference enabled
- Encryption at rest
- Blob versioning
- Seven-day blob and container soft-delete retention
- Cross-tenant replication disabled

### Azure Key Vault

Provisioned a Key Vault with:

- Microsoft Entra RBAC authorization
- Soft delete enabled
- Seven-day retention
- Purge protection enabled
- Unnecessary deployment integrations disabled

### User-Assigned Managed Identity

Created a dedicated user-assigned managed identity.

Configured resource-scoped permissions:

| Resource | Role | Access |
|---|---|---|
| Application-data Storage account | Storage Blob Data Reader | Read Blob data |
| Azure Key Vault | Key Vault Secrets User | Read secret values |

The identity was not granted permissions to the separate Terraform state storage account.

## Security Validation Results

| Validation | Result |
|---|---|
| Secure Storage deployment | Passed |
| Storage authentication and transport settings | Passed |
| Blob versioning and soft delete | Passed |
| Key Vault deployment | Passed |
| Key Vault RBAC authorization | Passed |
| Key Vault soft delete and purge protection | Passed |
| Managed identity provisioning | Passed |
| Storage Blob Data Reader assignment | Passed |
| Key Vault Secrets User assignment | Passed |
| Resource-level RBAC scope verification | Passed |
| Final Terraform reconciliation | Passed — no changes |

The complete Phase 2 environment contains 13 Terraform-managed resources, excluding data sources.

## Troubleshooting and Remediation

### Azure Policy Tagging

The Azure subscription required `Environment=Production`.

Terraform resources were configured to comply with the enforced subscription policy. The resources serve a security training lab; the Production tag reflects a subscription policy requirement rather than real production workload classification.

### Cloud Shell Authentication

Encountered a Cloud Shell token-audience limitation during Azure Storage provisioning.

Resolved the authentication issue through interactive Azure CLI sign-in and verified the required Storage OAuth audience.

### Terraform Resource Taint

Following the interrupted Storage provisioning operation, Terraform marked the Storage account as tainted and proposed replacement.

Verified the existing resource configuration, removed the tainted designation, and confirmed successful state reconciliation without destroying or recreating the account.

### Ephemeral Cloud Shell Recovery

Recovered Terraform source from GitHub and reconnected to the existing Azure Blob remote backend, preserving previously deployed resources.

## Security Design and Limitations

The project uses identity-based authentication and resource-scoped authorization without embedding workload credentials in Terraform source code.

The Storage RBAC assignment is scoped to the application-data storage account, not an individual container. The Key Vault Secrets User assignment is scoped to the vault, not an individual secret.

Public network access remains enabled for the Storage account and Key Vault to support Cloud Shell-based lab administration. The Key Vault firewall uses an allow-default configuration; these resources are not private-endpoint isolated.

The managed identity and its permissions were verified at the configuration level. Effective workload access was not tested because no runtime resource was attached to the identity and no test secrets were created.

## Future Enhancements

- Narrow Storage permissions to a specific container
- Evaluate secret-level RBAC scoping
- Introduce private endpoints and private DNS
- Deploy an Azure workload with the managed identity attached
- Test authenticated Blob and Key Vault data-plane access
- Introduce CI/CD checks and Terraform security scanning
- Add monitoring, alerting, and automated compliance validation

## Outcome

Successfully extended a Terraform-managed Azure environment with secure data services, Key Vault, managed identity, and scoped RBAC while preserving existing infrastructure and protected remote state.

The project demonstrates practical Azure cloud security engineering across identity, data protection, governance, infrastructure automation, and operational troubleshooting.
