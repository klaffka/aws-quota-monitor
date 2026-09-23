#!/usr/bin/env python3
"""Read-only formatter for collector ``COVERAGE#`` and ``RUN#`` snapshots.

The collector stores snapshots in DynamoDB.  This utility deliberately accepts
an exported JSON response instead of creating an AWS client, so it is safe to
use in local review and CI.  The input can be a list of items, a DynamoDB
``scan`` response (``{"Items": [...]}``), or JSON-lines.

``--view errors`` groups the latest run's failures, and ``--view persistent``
lists the quotas that failed in *every* recorded run.  A check that is broken
rather than merely unlucky looks exactly like the latter: it errors on every
run, forever, and nothing else in the system says so.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections.abc import Iterable

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from modules.qmcore.coverage import reason_group


def load_items(path: str) -> list[dict]:
    text = Path(path).read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    if isinstance(value, dict):
        value = value.get("Items", [value])
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError("Input muss eine JSON-Liste, ein scan-Objekt oder JSON-Lines enthalten")
    return value


def latest_snapshots(items: Iterable[dict], prefix: str = "COVERAGE#") -> list[dict]:
    latest: dict[str, dict] = {}
    for item in items:
        pk = str(item.get("PK", ""))
        if not pk.startswith(prefix):
            continue
        current = latest.get(pk)
        if current is None or str(item.get("SK", "")) > str(current.get("SK", "")):
            latest[pk] = item
    return [latest[key] for key in sorted(latest)]


def _number(value: object) -> str:
    if value is None:
        return "-"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _percent(value: object, total: object) -> str:
    """Format a count as a catalog percentage without inventing 0% data."""
    try:
        denominator = float(total)
        numerator = float(value)
    except (TypeError, ValueError):
        return "-"
    if denominator <= 0:
        return "-"
    return f"{numerator / denominator * 100:.1f}%"


def coverage_percentages(item: dict) -> dict[str, str]:
    """Return display-only percentages for one raw coverage snapshot."""
    total = item.get("totalCatalog")
    return {
        "measured": _percent(item.get("measured"), total),
        "ok": _percent(item.get("ok"), total),
    }


def render_table(items: Iterable[dict]) -> str:
    rows = []
    for item in items:
        rows.append((
            str(item.get("PK", "")).removeprefix("COVERAGE#"),
            str(item.get("SK", "")).removeprefix("TS#"),
            _number(item.get("totalCatalog")),
            _number(item.get("measured")),
            coverage_percentages(item)["measured"],
            _number(item.get("ok")),
            coverage_percentages(item)["ok"],
            _number(item.get("unsupported")),
            _number(item.get("noData")),
            _number(item.get("errors")),
            _number(item.get("byMeasurementType", {}).get("RESOURCE_COUNT")),
            _number(item.get("byMeasurementType", {}).get("USAGE_METRIC")),
        ))
    headers = ("Account/Region", "Timestamp", "Catalog", "Measured", "Measured%", "OK", "OK%", "Unsupported", "No data", "Errors", "Resource", "Metric")
    all_rows = [headers, *rows]
    widths = [max(len(row[index]) for row in all_rows) for index in range(len(headers))]
    return "\n".join("  ".join(value.ljust(widths[index]) for index, value in enumerate(row))
                     for row in all_rows)


def run_items(items: Iterable[dict]) -> list[dict]:
    """Return every RUN# record, oldest first within each account and Region."""
    runs = [item for item in items if str(item.get("PK", "")).startswith("RUN#")]
    return sorted(runs, key=lambda item: (str(item.get("PK")), str(item.get("SK"))))


def split_error(text: str) -> tuple[str, str]:
    """Split a recorded ``<service>/<quotaCode>: <reason>`` entry."""
    key, _, reason = str(text).partition(": ")
    return key, reason.strip()


def render_errors(items: Iterable[dict]) -> str:
    """Group the newest run's failures per account and Region by reason."""
    from collections import Counter

    lines = []
    for run in latest_snapshots(items, "RUN#"):
        scope = str(run.get("PK", "")).removeprefix("RUN#")
        errors = list(run.get("errors") or ())
        lines.append(f"## {scope} at {str(run.get('SK', '')).removeprefix('TS#')}"
                     f" — {len(errors)} errors")
        grouped: dict[str, list[str]] = {}
        for entry in errors:
            key, reason = split_error(entry)
            grouped.setdefault(reason_group(reason), []).append(f"{key}: {reason}")
        for group, entries in sorted(grouped.items(), key=lambda pair: (-len(pair[1]), pair[0])):
            lines.append(f"\n### {group} ({len(entries)})")
            lines.extend(f"- {entry}" for entry in sorted(entries))
        services = Counter(split_error(entry)[0].split("/")[0] for entry in errors)
        if services:
            lines.append("\n### by service")
            lines.extend(f"- {service}: {count}"
                         for service, count in services.most_common())
    return "\n".join(lines) if lines else "No RUN# records in the input"


def persistent_errors(items: Iterable[dict]) -> dict[str, list[tuple[str, int, str]]]:
    """Return the quotas that failed in every recorded run, per account/Region.

    A structural defect -- a wrong parameter, a missing operation -- fails every
    single run. A throttle or a transient permission problem does not.
    """
    runs: dict[str, list[dict]] = {}
    for run in run_items(items):
        runs.setdefault(str(run.get("PK", "")).removeprefix("RUN#"), []).append(run)
    result = {}
    for scope, records in runs.items():
        always = None
        reasons: dict[str, str] = {}
        for record in records:
            keys = set()
            for entry in record.get("errors") or ():
                key, reason = split_error(entry)
                keys.add(key)
                reasons[key] = reason
            always = keys if always is None else always & keys
        result[scope] = sorted((key, len(records), reasons[key]) for key in (always or ()))
    return result


def render_persistent(items: Iterable[dict]) -> str:
    lines = []
    for scope, failures in sorted(persistent_errors(items).items()):
        lines.append(f"## {scope} — {len(failures)} quotas failing in every run")
        lines.extend(f"- {key} (all {runs} runs): {reason}" for key, runs, reason in failures)
    return "\n".join(lines) if lines else "No RUN# records in the input"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Liest lokale COVERAGE#-Snapshots aus JSON")
    parser.add_argument("input", help="JSON-/JSONL-Datei mit DynamoDB-Items")
    parser.add_argument("--format", choices=("table", "json"), default="table")
    parser.add_argument("--view", choices=("coverage", "errors", "persistent"),
                        default="coverage")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    items = load_items(args.input)
    if args.view == "errors":
        print(json.dumps(latest_snapshots(items, "RUN#"), indent=2, default=str)
              if args.format == "json" else render_errors(items))
        return 0
    if args.view == "persistent":
        print(json.dumps(persistent_errors(items), indent=2, default=str)
              if args.format == "json" else render_persistent(items))
        return 0
    snapshots = latest_snapshots(items)
    if args.format == "json":
        print(json.dumps(snapshots, indent=2, ensure_ascii=False, default=str))
    else:
        print(render_table(snapshots))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
