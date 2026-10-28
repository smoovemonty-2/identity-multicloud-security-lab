#!/usr/bin/env python3
"""Read-only AWS S3 authorization audit."""

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError


PROFILE = "session4-s3-reader"
EXPECTED_ROLE = "lab-s3-prefix-reader"
REGION = "us-east-1"


def utc_timestamp():
    return datetime.now(timezone.utc).isoformat()


def get_aws_session():
    """Authenticate through the configured assumed-role profile."""
    session = boto3.Session(
        profile_name=PROFILE,
        region_name=REGION
    )

    identity = session.client("sts").get_caller_identity()
    arn = identity["Arn"]

    expected_fragment = (
        f":assumed-role/{EXPECTED_ROLE}/"
    )

    if expected_fragment not in arn:
        raise RuntimeError(
            "Unexpected AWS identity. "
            "Expected the restricted lab role."
        )

    print("[PASS] Restricted IAM role verified")
    return session


def test_s3_access(s3, bucket, test_name, prefix, expected):
    """Execute a read-only list request and classify the result."""

    kwargs = {
        "Bucket": bucket,
        "MaxKeys": 1
    }

    if prefix is not None:
        kwargs["Prefix"] = prefix

    try:
        s3.list_objects_v2(**kwargs)

        observed = "Allowed"
        error_code = ""

    except ClientError as exc:
        error_code = exc.response.get(
            "Error", {}
        ).get("Code", "Unknown")

        if error_code in ("AccessDenied", "403"):
            observed = "Denied"
        else:
            observed = "Error"

    except (BotoCoreError, Exception) as exc:
        # Authentication, networking and other failures are
        # not evidence of a permission denial.
        observed = "Error"
        error_code = type(exc).__name__

    status = (
        "PASS" if observed == expected else "FAIL"
    )

    return {
        "timestamp_utc": utc_timestamp(),
        "cloud": "AWS",
        "test_name": test_name,
        "action": "s3:ListBucket",
        "requested_prefix": (
            prefix if prefix is not None else "<none>"
        ),
        "expected": expected,
        "observed": observed,
        "status": status,
        "error_code": error_code
    }


def save_reports(results, output_dir):
    """Write timestamped private JSON and CSV reports."""

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
        mode=0o700
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")

    json_path = output_dir / f"aws-audit-{timestamp}.json"
    csv_path = output_dir / f"aws-audit-{timestamp}.csv"

    with json_path.open("x", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    fields = [
        "timestamp_utc",
        "cloud",
        "test_name",
        "action",
        "requested_prefix",
        "expected",
        "observed",
        "status",
        "error_code"
    ]

    with csv_path.open("x", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )
        writer.writeheader()
        writer.writerows(results)

    json_path.chmod(0o600)
    csv_path.chmod(0o600)

    return json_path, csv_path


def main():
    parser = argparse.ArgumentParser(
        description="Audit restricted AWS S3 access."
    )

    parser.add_argument(
        "--bucket",
        required=True,
        help="Existing S3 lab bucket name"
    )

    parser.add_argument(
        "--output-dir",
        default=str(
            Path.home() / "session5-security-reports"
        )
    )

    args = parser.parse_args()

    try:
        session = get_aws_session()
        s3 = session.client("s3")

        tests = [
            (
                "Approved prefix",
                "session4-iam/",
                "Allowed"
            ),
            (
                "Unauthorized prefix",
                "unapproved/",
                "Denied"
            ),
            (
                "Entire bucket",
                None,
                "Denied"
            )
        ]

        results = []

        for name, prefix, expected in tests:
            result = test_s3_access(
                s3,
                args.bucket,
                name,
                prefix,
                expected
            )

            results.append(result)

            print(
                f"[{result['status']}] {name}: "
                f"expected={expected}, "
                f"observed={result['observed']}"
            )

        json_path, csv_path = save_reports(
            results,
            Path(args.output_dir).expanduser()
        )

        passed = sum(
            result["status"] == "PASS"
            for result in results
        )

        print()
        print(f"Tests passed: {passed}/{len(results)}")
        print(f"JSON report: {json_path}")
        print(f"CSV report: {csv_path}")

        if passed != len(results):
            print("Audit failed: unexpected authorization behavior.")
            return 1

        print("AWS authorization audit completed successfully.")
        return 0

    except Exception as exc:
        print(
            f"Audit execution failed: {type(exc).__name__}",
            file=sys.stderr
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
