
#!/usr/bin/env python3
"""Consolidate validated AWS and Azure security audit reports."""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from uuid import UUID


AWS_BASELINE = {
    "Approved prefix": ("Allowed", "session4-iam/"),
    "Unauthorized prefix": ("Denied", "unapproved/"),
    "Entire bucket": ("Denied", "<none>"),
}

CSV_FIELDS = [
    "timestamp_utc",
    "cloud",
    "test_name",
    "action",
    "requested_prefix",
    "scope",
    "principal_id",
    "expected",
    "observed",
    "status",
    "error_code",
]


def load_report(path):
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list) or not data:
        raise ValueError(f"Invalid or empty report: {path.name}")

    if not all(isinstance(row, dict) for row in data):
        raise ValueError(f"Invalid report records: {path.name}")

    return data


def check_timestamp(row, max_age_hours):
    raw = row.get("timestamp_utc")

    if not isinstance(raw, str):
        raise ValueError("Missing audit timestamp.")

    stamp = datetime.fromisoformat(
        raw.replace("Z", "+00:00")
    )

    if stamp.tzinfo is None:
        raise ValueError("Audit timestamp lacks timezone.")

    now = datetime.now(timezone.utc)
    age = now - stamp.astimezone(timezone.utc)

    if age > timedelta(hours=max_age_hours):
        raise ValueError("Audit evidence is stale.")

    if age < timedelta(minutes=-5):
        raise ValueError("Audit timestamp is in the future.")


def normalize(row):
    return {
        field: row.get(field, "")
        for field in CSV_FIELDS
    }


def check_consistency(row):
    if row.get("observed") not in ("Allowed", "Denied", "Error", "Reader", "None"):
        # Azure can also report additional role names or IDs.
        if row.get("cloud") != "Azure":
            raise ValueError("Invalid observed AWS result.")

    expected_status = (
        "PASS"
        if row["expected"] == row["observed"]
        else "FAIL"
    )

    if row.get("status") != expected_status:
        raise ValueError(
            "Report status conflicts with observed result."
        )


def validate_aws(rows, max_age_hours):
    if len(rows) != len(AWS_BASELINE):
        raise ValueError("AWS report has missing or extra tests.")

    found = {}

    for row in rows:
        check_timestamp(row, max_age_hours)

        if row.get("cloud") != "AWS":
            raise ValueError("Unexpected cloud in AWS report.")

        name = row.get("test_name")

        if name not in AWS_BASELINE or name in found:
            raise ValueError("Unexpected or duplicate AWS test.")

        expected, prefix = AWS_BASELINE[name]

        if (
            row.get("expected") != expected
            or row.get("requested_prefix") != prefix
            or row.get("action") != "s3:ListBucket"
        ):
            raise ValueError("AWS test baseline mismatch.")

        if row.get("observed") not in ("Allowed", "Denied", "Error"):
            raise ValueError("Invalid AWS authorization outcome.")

        check_consistency(row)
        found[name] = normalize(row)

    return [found[name] for name in AWS_BASELINE]


def validate_azure(rows, max_age_hours):
    if len(rows) != 1:
        raise ValueError("Expected one Azure RBAC finding.")

    row = rows[0]
    check_timestamp(row, max_age_hours)

    if (
        row.get("cloud") != "Azure"
        or row.get("test_name") != "Scoped RBAC assignment"
        or row.get("expected") != "Reader"
        or row.get("action") != "Microsoft.Authorization/roleAssignments/read"
    ):
        raise ValueError("Azure test baseline mismatch.")

    scope = row.get("scope", "")
    principal_id = row.get("principal_id", "")

    if not isinstance(scope, str) or not (
        scope.lower().startswith("/subscriptions/")
        and "/resourcegroups/" in scope.lower()
    ):
        raise ValueError("Invalid Azure resource-group scope.")

    UUID(str(principal_id))
    check_consistency(row)

    return [normalize(row)]


def save_reports(payload, output_dir):
    output_dir.mkdir(
        parents=True, exist_ok=True, mode=0o700
    )

    stamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    json_path = output_dir / f"multicloud-audit-{stamp}.json"
    csv_path = output_dir / f"multicloud-audit-{stamp}.csv"

    with json_path.open("x", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)

    with csv_path.open(
        "x", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=CSV_FIELDS
        )
        writer.writeheader()
        writer.writerows(payload["findings"])

    json_path.chmod(0o600)
    csv_path.chmod(0o600)

    return json_path, csv_path


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate AWS and Azure audit evidence."
    )

    parser.add_argument("--aws", type=Path, required=True)
    parser.add_argument("--azure", type=Path, required=True)

    parser.add_argument(
        "--max-age-hours", type=int, default=168
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.home() / "session5-security-reports",
    )

    args = parser.parse_args()
    os.umask(0o077)

    try:
        if args.max_age_hours <= 0:
            raise ValueError("Maximum age must be positive.")

        aws_rows = validate_aws(
            load_report(args.aws), args.max_age_hours
        )

        azure_rows = validate_azure(
            load_report(args.azure), args.max_age_hours
        )

        findings = aws_rows + azure_rows
        passed = sum(
            row["status"] == "PASS" for row in findings
        )
        failed = len(findings) - passed

        overall = "PASS" if failed == 0 else "FAIL"

        payload = {
            "generated_at_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "summary": {
                "clouds": ["AWS", "Azure"],
                "total_tests": len(findings),
                "passed": passed,
                "failed": failed,
                "overall_status": overall,
            },
            "source_reports": [
                args.aws.name,
                args.azure.name,
            ],
            "findings": findings,
        }

        json_path, csv_path = save_reports(
            payload, args.output_dir.expanduser()
        )

        print(f"Overall status: {overall}")
        print(f"Passed: {passed}/{len(findings)}")
        print(f"Failed: {failed}")
        print(f"JSON: {json_path}")
        print(f"CSV: {csv_path}")

        return 0 if failed == 0 else 1

    except Exception as exc:
        print(
            f"Consolidation incomplete: "
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
