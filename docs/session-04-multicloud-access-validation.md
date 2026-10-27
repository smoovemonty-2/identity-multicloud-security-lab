# Session 4 — AWS IAM and Azure RBAC Security Engineering

## Objective

Implement and validate least-privilege authorization across AWS and Microsoft Azure, including trusted identity access, resource-scoped permissions, and positive and negative authorization testing.

## Technologies

- AWS IAM and AWS STS
- Amazon S3
- AWS CLI
- Microsoft Entra ID
- Azure RBAC
- Azure CLI and Azure Cloud Shell

## AWS Implementation

### IAM role and trust relationship

Created the `lab-s3-prefix-reader` IAM role with a trust policy scoped to an authorized IAM user.

Configured AWS CLI role assumption using temporary STS credentials and an environment-based credential source.

Successfully verified the assumed-role identity.

### Permission boundary

Configured a custom IAM policy permitting:

- `s3:ListBucket` for the approved `session4-iam/` prefix.
- `s3:GetObject` for objects under that prefix.

No S3 write or delete permissions were added to the role's custom policy.

### AWS Validation

| Test | Expected | Result |
|---|---|---|
| STS AssumeRole | Successful assumption | Passed |
| List approved S3 prefix | Allowed | Passed |
| List unauthorized prefix | Denied | Passed |
| List bucket without prefix | Denied | Passed |

Actual S3 object reads, writes, and KMS decryption were not included in the confirmed live validation.

## Azure Implementation

### Scoped RBAC assignment

Created a dedicated lab resource group and assigned the built-in Reader role to the Microsoft Entra security group `SG-LAB-App-Users`.

The assignment was scoped to the lab resource group instead of the entire Azure subscription.

### Azure Validation

| Test | Expected | Result |
|---|---|---|
| Reader assignment verification | Correct principal, role, and scope | Passed |
| Alex: View resource group | Allowed | Passed |
| Taylor: Access resource group | Denied | Passed |
| Alex: CLI resource-group read | Allowed | Passed |
| Alex: ARM deployment validation | Denied | Passed |

## Cross-Cloud Comparison

AWS IAM authorization uses trust relationships, permission policies, and resource-level conditions to establish access boundaries.

Azure RBAC uses security principals, role definitions, and resource scopes to grant permissions. Group-based assignments connect Microsoft Entra identity governance to Azure infrastructure access.

Both platforms support least-privilege engineering, but their authorization mechanisms and evaluation models differ.

## Troubleshooting

### AWS CLI credential source

The AWS CLI was originally authenticating using environment variables rather than a configured default profile.

Updated the assumed-role profile to use `credential_source = Environment`, removed the conflicting `source_profile` setting, and verified successful STS role assumption.

### Azure CLI installation

Local Azure CLI installation encountered a Python compilation failure on macOS Ventura.

Used Azure Cloud Shell as an alternative environment and successfully completed the Azure RBAC engineering and authorization tests.

## Security Design Decisions

- Used a specific trusted IAM principal.
- Restricted S3 authorization to a designated bucket prefix.
- Tested access using an assumed role, not the original IAM user's privileges.
- Scoped Azure Reader access to a dedicated resource group.
- Validated access using separate authorized and unauthorized identities.
- Performed non-destructive authorization tests.
- Preserved the existing S3 SSE-KMS configuration.
- Excluded credentials, tokens, and private account identifiers from public documentation.

## Scope and Limitations

The AWS tests demonstrated STS role assumption and S3 prefix-listing authorization. They did not establish successful object retrieval, object writes being denied through a live request, or KMS decryption access.

The Azure tests demonstrated control-plane authorization for a resource group and a deployment-validation request. They did not test every action supported by Azure RBAC.

Additional identities, inherited permissions, resource policies, service control policies, and other organizational security controls may influence effective authorization in production.

## Outcome

Successfully engineered and validated least-privilege authorization across AWS and Azure using live access tests.

Demonstrated IAM trust-policy configuration, STS role assumption, resource-scoped permissions, Entra group-based RBAC, positive and negative security testing, and multi-cloud troubleshooting.
