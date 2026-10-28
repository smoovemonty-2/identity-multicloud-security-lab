
#!/usr/bin/env python3
"""Read-only Azure RBAC assignment audit."""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from azure.identity import AzureCliCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.resource.resources import ResourceManagementClient


ROLE_IDS = {
    "Reader": "acdd72a7-3385-48ef-bd42-f606fba81ae7",
    "Contributor": "b24988ac-6180-42a0-ab88-20f7382dd24c",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def validate_guid(value):
    return str(UUID(value))


def audit_assignment(
    subscription_id,
    resource_group,
    principal_id,
    expected_role,
):
    """Audit direct RBAC assignments for one principal at one scope."""

    credential = AzureCliCredential()

    resource_client = ResourceManagementClient(
        credential,
        subscription_id,
    )

    authorization_client = AuthorizationManagementClient(
        credential,
        subscription_id,
    )

    # Verify that the resource group actually exists.
    rg = resource_client.resource_groups.get(resource_group)

    scope = (
        f"/subscriptions/{subscription_id}"
        f"/resourceGroups/{rg.name}"
    )

    # Retrieve assignments applying to the requested scope.
    assignments = list(
        authorization_client.role_assignments.list_for_scope(
            scope,
            filter="atScope()",
        )
    )

    # Restrict the analysis to assignments made directly
    # at this resource group scope to the target principal.
    matching = [
        item
        for item in assignments
        if item.principal_id
        and item.principal_id.lower() == principal_id.lower()
        and item.scope
        and item.scope.lower() == scope.lower()
    ]

    actual_role_ids = [
        item.role_definition_id.rsplit("/", 1)[-1].lower()
        for item in matching
    ]

    expected_role_id = ROLE_IDS[expected_role]

    # Require exactly one expected role and no extra
    # direct assignments to this principal at this scope.
    passed = (
        len(actual_role_ids) == 1
        and actual_role_ids[0] == expected_role_id
    )

    role_names = {
        value: name
        for name, value in ROLE_IDS.items()
    }

    observed = [
        role_names.get(role_id, role_id)
        for role_id in actual_role_ids
    ]

    return {
        "timestamp_utc": utc_now(),
        "cloud": "Azure",
        "test_name": "Scoped RBAC assignment",
        "action": "Microsoft.Authorization/roleAssignments/read",
        "scope": scope,
        "principal_id": principal_id,
        "expected": expected_role,
        "observed": ", ".join(observed) if observed else "None",
        "status": "PASS" if passed else "FAIL",
        "error_code": "",
    }


def save_reports(results, output_dir):
    """Write private JSON and CSV audit reports."""

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
        mode=0o700,
    )

    stamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    json_path = output_dir / f"azure-audit-{stamp}.json"
    csv_path = output_dir / f"azure-audit-{stamp}.csv"

    with json_path.open("x", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    with csv_path.open(
        "x",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0]),
        )
        writer.writeheader()
        writer.writerows(results)

    return json_path, csv_path


def main():
    parser = argparse.ArgumentParser(
        description="Audit Azure RBAC assignments."
    )

    parser.add_argument("--subscription", required=True)
    parser.add_argument("--resource-group", required=True)
    parser.add_argument("--principal-id", required=True)

    parser.add_argument(
        "--expected-role",
        choices=list(ROLE_IDS),
        default="Reader",
    )

    parser.add_argument(
        "--output-dir",
        default=str(
            Path.home() / "session5-security-reports"
        ),
    )

    args = parser.parse_args()

    # Ensure newly generated reports are private.
    os.umask(0o077)

    try:
        subscription_id = validate_guid(args.subscription)
        principal_id = validate_guid(args.principal_id)

        finding = audit_assignment(
            subscription_id,
            args.resource_group,
            principal_id,
            args.expected_role,
        )

        json_path, csv_path = save_reports(
            [finding],
            Path(args.output_dir).expanduser(),
        )

        print(f"Status: {finding['status']}")
        print(f"Expected role: {finding['expected']}")
        print(f"Observed role(s): {finding['observed']}")
        print(f"JSON report: {json_path}")
        print(f"CSV report: {csv_path}")

        if finding["status"] != "PASS":
            print("Azure RBAC baseline deviation detected.")
            return 1

        print("Azure RBAC audit completed successfully.")
        return 0

    except Exception as exc:
        print(
            f"Azure audit failed: {type(exc).__name__}",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
