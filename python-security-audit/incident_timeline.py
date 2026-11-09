#!/usr/bin/env python3
"""Session 8: local, read-only timeline from AWS CloudTrail and Azure Activity Log JSON.

Raw source evidence is never modified. Derived outputs contain sensitive metadata:
keep the output directory private and out of version control.
"""

import argparse
import csv
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

FIELDS = [
    "time_utc", "cloud", "operation", "actor", "source_ip", "resource",
    "outcome", "event_id", "correlation_id", "read_only", "review_reason",
]

AWS_ACCESS_CHANGES = {
    "createrole", "deleterole", "attachrolepolicy", "detachrolepolicy",
    "putrolepolicy", "deleterolepolicy", "updateassumerolepolicy",
    "createpolicy", "createpolicyversion", "setdefaultpolicyversion",
    "putuserpolicy", "attachuserpolicy", "createaccesskey",
    "putbucketpolicy", "deletebucketpolicy", "putbucketacl",
    "putkeypolicy", "creategrant", "revokegrant", "stoplogging",
    "deletetrail", "updateeventdatastore", "puttrail", "updatetrail",
}


def timestamp_utc(raw):
    if not isinstance(raw, str) or not raw:
        raise ValueError(f"Missing/invalid timestamp: {raw!r}")
    dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"Timestamp has no timezone: {raw!r}")
    return dt.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def field_value(value):
    if isinstance(value, dict):
        return str(value.get("value") or value.get("localizedValue") or "")
    if value is None:
        return ""
    return str(value)


def load_json_evidence(path, label):
    """Parse evidence without exposing event bodies in error messages."""
    if path.stat().st_size == 0:
        raise ValueError(f"{label} evidence file is empty: {path.name}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{label} evidence file is not valid JSON: {path.name}, "
            f"line {exc.lineno}, column {exc.colno} ({exc.msg})"
        ) from exc


def load_aws(path):
    data = load_json_evidence(path, "AWS")
    if not isinstance(data, dict) or not isinstance(data.get("Events"), list):
        raise ValueError("AWS file must be CloudTrail lookup-events JSON with an Events array")
    results = []
    for index, e in enumerate(data["Events"], start=1):
        if not isinstance(e, dict):
            raise ValueError("AWS Events array contains a non-object")
        detail = e.get("CloudTrailEvent") or {}
        if isinstance(detail, str):
            try:
                detail = json.loads(detail)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"AWS CloudTrailEvent embedded JSON is invalid in record "
                    f"#{index}, line {exc.lineno}, column {exc.colno} "
                    f"({exc.msg})"
                ) from exc
        if not isinstance(detail, dict):
            raise ValueError("AWS CloudTrailEvent detail must be an object")
        identity = detail.get("userIdentity") or {}
        if not isinstance(identity, dict):
            identity = {}
        operation = str(e.get("EventName") or detail.get("eventName") or "")
        if not operation:
            raise ValueError("AWS event missing operation")
        resources = e.get("Resources") or []
        resource_names = [str(r.get("ResourceName")) for r in resources if isinstance(r, dict) and r.get("ResourceName")]
        error = detail.get("errorCode")
        reason = ""
        if operation.lower() in AWS_ACCESS_CHANGES:
            reason = "Access or security-control change; verify authorization"
        elif error:
            reason = "API error; review surrounding activity"
        readonly = detail.get("readOnly", e.get("ReadOnly", ""))
        results.append({
            "time_utc": timestamp_utc(e.get("EventTime") or detail.get("eventTime")),
            "cloud": "AWS",
            "operation": operation,
            "actor": str(identity.get("arn") or identity.get("principalId") or e.get("Username") or ""),
            "source_ip": str(detail.get("sourceIPAddress") or ""),
            "resource": "; ".join(resource_names[:5]),
            "outcome": f"API error: {error}" if error else "No errorCode recorded",
            "event_id": str(e.get("EventId") or detail.get("eventID") or ""),
            "correlation_id": str(detail.get("requestID") or ""),
            "read_only": str(readonly).lower() if readonly != "" else "",
            "review_reason": reason,
        })
    return results


def load_azure(path):
    data = load_json_evidence(path, "Azure")
    if not isinstance(data, list):
        raise ValueError("Azure file must be Activity Log CLI JSON array")
    results = []
    for e in data:
        if not isinstance(e, dict):
            raise ValueError("Azure array contains a non-object")
        operation = field_value(e.get("operationName"))
        if not operation:
            raise ValueError("Azure event missing operationName")
        action = operation.lower()
        status = field_value(e.get("status")) or "Unknown"
        http = e.get("httpRequest") or {}
        if not isinstance(http, dict):
            http = {}
        reason = ""
        if any(action.endswith(s) for s in (
            "roleassignments/write", "roleassignments/delete",
            "roledefinitions/write", "roledefinitions/delete",
        )):
            reason = "RBAC change; verify principal, role and approval"
        elif any(action.endswith(s) for s in (
            "vaults/write", "storageaccounts/write", "networksecuritygroups/write",
        )):
            reason = "Security-relevant resource change; compare with approved deployment"
        elif status.lower() in {"failed", "failure"}:
            reason = "Failed operation; determine cause and relevance"
        results.append({
            "time_utc": timestamp_utc(e.get("eventTimestamp")),
            "cloud": "Azure",
            "operation": operation,
            "actor": str(e.get("caller") or ""),
            "source_ip": str(http.get("clientIpAddress") or ""),
            "resource": str(e.get("resourceId") or ""),
            "outcome": status,
            "event_id": str(e.get("eventDataId") or ""),
            "correlation_id": str(e.get("correlationId") or ""),
            "read_only": "",
            "review_reason": reason,
        })
    return results


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def safe_csv_text(s):
    s = str(s)
    # Prevent formula execution if a derived CSV is opened in a spreadsheet.
    if s.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + s
    return s


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aws", required=True, type=Path, help="Original AWS lookup-events JSON")
    parser.add_argument("--azure", required=True, type=Path, help="Original Azure Activity Log JSON")
    parser.add_argument("--output-dir", required=True, type=Path, help="Private local output directory")
    args = parser.parse_args()
    os.umask(0o077)

    aws_path = args.aws.expanduser().resolve(strict=True)
    azure_path = args.azure.expanduser().resolve(strict=True)
    if aws_path == azure_path:
        raise ValueError("AWS and Azure files must be different")
    aws = load_aws(aws_path)
    azure = load_azure(azure_path)
    if not aws or not azure:
        raise ValueError("Both inputs must contain at least one event")

    timeline = sorted(aws + azure, key=lambda r: (r["time_utc"], r["cloud"], r["event_id"]))
    rbac = [r for r in azure if "RBAC change;" in r["review_reason"]]
    grouped = defaultdict(list)
    for r in rbac:
        grouped[r["correlation_id"] or r["event_id"] or f"unidentified-{len(grouped)}"].append(r)
    rbac_groups = [
        {"correlation_key": k, "record_count": len(items),
         "operations": sorted({x["operation"] for x in items}),
         "statuses": sorted({x["outcome"] for x in items}),
         "first_seen_utc": min(x["time_utc"] for x in items)}
        for k, items in grouped.items()
    ]
    rbac_groups.sort(key=lambda x: x["first_seen_utc"])

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    output_dir.chmod(0o700)
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope_note": "Bounded samples; not a complete account/subscription history or proof of compromise",
        "sources": {
            "AWS": {"file": aws_path.name, "sha256": sha256(aws_path), "records": len(aws)},
            "Azure": {"file": azure_path.name, "sha256": sha256(azure_path), "records": len(azure)},
        },
        "summary": {
            "total_records": len(timeline),
            "aws_records": len(aws),
            "azure_records": len(azure),
            "flagged_for_review": sum(bool(r["review_reason"]) for r in timeline),
            "azure_rbac_records": len(rbac),
            "azure_rbac_correlation_groups": len(rbac_groups),
            "first_event_utc": timeline[0]["time_utc"],
            "last_event_utc": timeline[-1]["time_utc"],
        },
        "azure_rbac_groups": rbac_groups,
        "cautions": [
            "Review flags indicate investigative interest, not malicious intent.",
            "Azure Started and Succeeded records may describe one logical operation.",
            "CloudTrail Event History omits data events and is regional.",
            "AWS results capped at 50 and Azure at 100 in initial evidence collection.",
        ],
    }

    timeline_json = output_dir / "session8-timeline.json"
    timeline_csv = output_dir / "session8-timeline.csv"
    summary_json = output_dir / "session8-triage-summary.json"
    timeline_json.write_text(json.dumps(timeline, indent=2) + "\n", encoding="utf-8")
    summary_json.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    with timeline_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows({k: safe_csv_text(row[k]) for k in FIELDS} for row in timeline)
    for p in (timeline_json, timeline_csv, summary_json):
        p.chmod(0o600)

    print("Normalized event records:", len(timeline))
    print("AWS / Azure:", len(aws), "/", len(azure))
    print("Review candidates:", manifest["summary"]["flagged_for_review"])
    print("Azure RBAC records:", len(rbac))
    print("Azure RBAC correlation groups:", len(rbac_groups))
    print("Private outputs:", timeline_json, timeline_csv, summary_json, sep="\n  ")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Timeline generation failed: {exc}", file=sys.stderr)
        sys.exit(2)
