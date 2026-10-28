# Session 5 — Python Multi-Cloud Security Automation

## Objective

Develop reusable Python security auditing capabilities that collect, validate, and consolidate AWS and Microsoft Azure security findings.

The implementation builds on previously validated IAM and RBAC configurations to demonstrate automated access reviews, exception detection, API integration, and security reporting.

## Technologies

- Python 3
- Boto3 and AWS STS
- Amazon S3
- Azure Identity SDK
- Azure Authorization Management SDK
- Azure Resource Management SDK
- JSON and CSV reporting
- AWS CLI and Azure Cloud Shell

## Architecture

The solution consists of three Python components:

### AWS Access Audit — aws_access_audit.py

Authenticates through the restricted `lab-s3-prefix-reader` IAM role and conducts real, read-only S3 listing requests.

Validates allowed access to the approved prefix and denied access to unauthorized prefixes.

### Azure RBAC Audit — azure_rbac_audit.py

Authenticates using Azure CLI credentials, retrieves the configured resource group and its direct role assignments, and compares the Entra security group's assignment with the expected Reader baseline.

### Consolidated Reporting — generate_report.py

Loads AWS and Azure JSON findings, validates required evidence and timestamps, normalizes records, and produces combined JSON and CSV reports.

## Validation Results

| Test | Expected outcome | Status |
|---|---|---|
| AWS Boto3 role authentication | Restricted IAM role verified | Passed |
| AWS approved prefix | Allowed | Passed |
| AWS unauthorized prefix | Denied | Passed |
| AWS full-bucket listing | Denied | Passed |
| AWS invalid-bucket test | Nonzero exit code | Passed |
| Azure SDK authentication and import | Successful | Passed |
| Azure Reader baseline | PASS, exit 0 | Passed |
| Azure Contributor baseline simulation | FAIL, exit 1 | Passed |
| Azure nonexistent resource group | Error, exit 2 | Passed |
| Consolidated security audit | Four passing findings | Passed |
| Consolidated JSON/CSV reporting | Four findings exported | Passed |
| Missing AWS evidence | Error, exit 2 | Passed |

## Consolidated Audit Outcome

- AWS: 3 passing authorization checks
- Azure: 1 passing RBAC configuration check
- Total: 4 passing findings
- Overall security audit status: PASS

These results represent the tested configuration at the time the reports were generated. They are not continuous security-monitoring results.

## Error Handling

The scripts distinguish between:

- Successful validation of expected permissions
- Security baseline deviations
- Authentication, API, configuration, or evidence failures

The consolidated reporting tool uses:

- Exit 0: All findings passed
- Exit 1: One or more security deviations
- Exit 2: Incomplete or invalid evidence

## Troubleshooting

### AWS credentials

Used an AWS CLI role profile configured with environment-based source credentials to assume the restricted IAM role through STS.

### Azure Python SDK imports

Updated the ResourceManagementClient import to the path required by the installed Azure SDK version.

### Azure Python virtual environment

Resolved a missing-module error by executing the audit with the verified Cloud Shell Python virtual environment.

### Cross-environment report transfer

Transferred the Azure source script and successful RBAC report from Cloud Shell to the local development environment.

Corrected file-path handling and successfully consolidated the AWS and Azure results.

## Security Practices

- Read-only cloud API calls
- Temporary AWS role credentials
- Resource-scoped access policies
- Explicit authentication validation
- Fail-safe behavior on unexpected errors
- Timestamped JSON and CSV reporting
- Private storage of raw cloud findings
- No credentials or sensitive tenant configuration committed to GitHub
- Version-pinned direct SDK dependencies

## Limitations and Future Improvements

The solution validates specific configured AWS S3 listing permissions and one direct Azure RBAC group assignment.

It does not provide comprehensive organization-wide IAM discovery, effective-permissions analysis across all services, continuous monitoring, or automatic remediation.

Potential improvements include automated scheduled execution, unit tests, structured logging, cloud-native alert integrations, CI/CD validation, and broader access-control coverage.

## Outcome

Successfully implemented and validated Python-based AWS and Azure security audits, combined their findings into a normalized reporting workflow, and demonstrated reliable exception detection, failure handling, and multi-cloud API integration.
