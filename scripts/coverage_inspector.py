#!/usr/bin/env python3
"""Read-only formatter for collector ``COVERAGE#`` snapshots.

The collector stores snapshots in DynamoDB.  This utility deliberately accepts
an exported JSON response instead of creating an AWS client, so it is safe to
use in local review and CI.  The input can be a list of items, a DynamoDB
``scan`` response (``{"Items": [...]}``), or JSON-lines.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


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


def latest_snapshots(items: Iterable[dict]) -> list[dict]:
    latest: dict[str, dict] = {}
    for item in items:
        pk = str(item.get("PK", ""))
        if not pk.startswith("COVERAGE#"):
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Liest lokale COVERAGE#-Snapshots aus JSON")
    parser.add_argument("input", help="JSON-/JSONL-Datei mit DynamoDB-Items")
    parser.add_argument("--format", choices=("table", "json"), default="table")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    snapshots = latest_snapshots(load_items(args.input))
    if args.format == "json":
        print(json.dumps(snapshots, indent=2, ensure_ascii=False, default=str))
    else:
        print(render_table(snapshots))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
