# Python Multi-Cloud Security Audit

Read-only Python automation for validating AWS S3 authorization and Azure RBAC assignments against approved access baselines.

## Components

| File | Purpose |
|---|---|
| `aws_access_audit.py` | Tests allowed and denied AWS S3 listing operations |
| `azure_rbac_audit.py` | Validates a direct Azure RBAC group assignment |
| `generate_report.py` | Consolidates AWS and Azure JSON findings |
| `requirements-aws.txt` | Tested AWS Python dependency versions |
| `requirements-azure.txt` | Tested Azure Python dependency versions |

## AWS Execution

Requires a configured AWS CLI role profile named `session4-s3-reader`, whose target role is `lab-s3-prefix-reader`.

Install the AWS dependencies:

```bash
python -m pip install -r requirements-aws.txt
```

Run the audit:

```bash
python aws_access_audit.py --bucket YOUR-LAB-BUCKET
```

## Azure Execution

Requires Azure CLI authentication to the intended tenant and subscription and the necessary permissions to inspect resource groups and role assignments.

Install the Azure dependencies:

```bash
python -m pip install -r requirements-azure.txt
```

Run from the authenticated Azure environment:

```bash
python azure_rbac_audit.py \
  --subscription YOUR-SUBSCRIPTION-ID \
  --resource-group YOUR-LAB-RG \
  --principal-id YOUR-ENTRA-GROUP-ID \
  --expected-role Reader
```

## Consolidated Reporting

Supply the JSON reports produced by the AWS and Azure audit scripts:

```bash
python generate_report.py \
  --aws /path/to/aws-audit.json \
  --azure /path/to/azure-audit.json
```

The consolidator creates timestamped JSON and CSV reports.

## Exit Codes

- `0`: All expected checks passed
- `1`: Security baseline deviation detected
- `2`: Execution failure or incomplete/invalid evidence

## Security and Privacy

Keep raw audit reports outside the public repository. Do not commit credentials, access tokens, tenant identifiers, private configurations, or unredacted cloud evidence.

The scripts do not modify AWS or Azure resources.

## Scope

This project demonstrates automated S3 authorization testing, Azure RBAC configuration auditing, and consolidated security reporting. It is a portfolio lab rather than a complete production security-monitoring system.

See `../docs/session-05-python-multicloud-validation.md` for implementation details, validation evidence, and limitations.
