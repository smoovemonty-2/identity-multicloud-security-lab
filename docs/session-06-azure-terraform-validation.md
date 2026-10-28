# Session 6 — Secure Azure Infrastructure with Terraform

## Objective

Deploy an Azure network security foundation using Terraform, with protected remote state, Microsoft Entra authentication, network segmentation, and validated infrastructure configuration.

## Technologies

- Terraform and HashiCorp AzureRM Provider
- Azure Cloud Shell and Azure CLI
- Azure Storage
- Microsoft Entra ID and Azure RBAC
- Azure Virtual Networks and Subnets
- Azure Network Security Groups
- Azure Policy

## Implementation

### 1. Secure Terraform Remote State

Created a dedicated Azure Storage account and private Blob container to store Terraform state separately from managed application infrastructure.

Implemented the following protections:

- Shared Key authentication disabled
- Microsoft Entra ID authentication
- Container-scoped Storage Blob Data Contributor
- HTTPS required and TLS 1.2 minimum
- Anonymous blob access disabled
- Blob versioning enabled
- Blob and container soft-delete retention enabled
- Azure Blob remote state storage

Verified that the backend initialized successfully and that the Terraform state blob was created after deployment.

### 2. Terraform-Managed Network

Provisioned eight Azure resources:

| Resource | Quantity |
|---|---:|
| Resource group | 1 |
| Virtual network | 1 |
| Subnets | 2 |
| Network security groups | 2 |
| NSG/subnet associations | 2 |
| **Total** | **8** |

The network uses the address space `10.40.0.0/16`, with application and data subnets assigned `10.40.1.0/24` and `10.40.2.0/24`, respectively.

### 3. Network Security Controls

Implemented custom inbound deny rules to restrict Internet ingress and communication between the application and data subnets.

Verified four custom deny rules and confirmed that both subnets were associated with their intended NSGs.

No VMs, public IP addresses, or public application endpoints were deployed.

### 4. Azure Policy Compliance

Encountered an Azure Policy deployment denial requiring `Environment=Production`.

Inspected the policy evaluation details and corrected the resource tagging in accordance with the subscription's enforced value.

The resources remain development-lab infrastructure despite the policy-required Production tag classification.

## Validation Results

| Test | Outcome | Status |
|---|---|---|
| Terraform initialization | Successful | Passed |
| Terraform configuration validation | Valid | Passed |
| Remote backend authentication | Microsoft Entra authentication verified | Passed |
| Storage security controls | Configured settings verified | Passed |
| Storage recovery protections | Versioning and soft delete verified | Passed |
| Infrastructure deployment | Eight resources created | Passed |
| Subnet and NSG associations | Both verified | Passed |
| Custom NSG rules | Four deny rules verified | Passed |
| Remote Terraform state | State blob verified | Passed |
| Final Terraform plan | No changes | Passed |

## Security Considerations

- Terraform state stored in a dedicated Azure Storage backend
- No storage account keys embedded in source code
- Data-plane RBAC limited to the state container
- State recovery enabled through versioning and soft delete
- Network segmentation through dedicated subnets and NSGs
- Centralized Terraform resource tagging
- Deployment and configuration validation

## Limitations

NSG configuration and associations were validated through Azure APIs and Terraform state, not through actual packet-flow testing.

The storage backend permits public network endpoint access for Cloud Shell connectivity, but requires authenticated Blob access. Production environments should evaluate more restrictive network access, private endpoints, additional monitoring, and stronger recovery protections.

The Terraform infrastructure is a security engineering lab, not a production workload deployment.

## Outcome

Successfully deployed and validated a secure Azure Terraform foundation demonstrating Infrastructure as Code, Microsoft Entra authentication, Azure RBAC, Azure Policy troubleshooting, state protection, network segmentation, and infrastructure validation.

The resulting foundation will be extended in Session 7 with secure Azure Storage, Key Vault, managed identities, and scoped role assignments.
