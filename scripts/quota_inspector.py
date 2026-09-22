#!/usr/bin/env python3
"""
CLI-Tool zum Auflisten aller Service-Quotas einer AWS-Region.

- Zeigt, ob eine Quota anpassbar ("erweiterbar") ist.
- Markiert, ob AWS bereits eine Usage-Metric dafür bereitstellt.
- Ausgabe als Tabelle oder JSON.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from collections.abc import Iterable, Sequence

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError


@dataclass
class QuotaRow:
    region: str
    service_code: str
    service_name: str
    quota_code: str
    quota_name: str
    adjustable: bool
    has_usage_metric: bool
    value: float | None
    unit: str | None
    usage_namespace: str | None
    usage_name: str | None
    usage_dimensions: dict[str, str] | None
    usage_statistic: str | None

    def as_dict(self) -> dict:
        return {
            "region": self.region,
            "serviceCode": self.service_code,
            "serviceName": self.service_name,
            "quotaCode": self.quota_code,
            "quotaName": self.quota_name,
            "adjustable": self.adjustable,
            "hasUsageMetric": self.has_usage_metric,
            "value": self.value,
            "unit": self.unit,
            "usageMetric": None
            if not self.has_usage_metric
            else {
                "namespace": self.usage_namespace,
                "name": self.usage_name,
                "dimensions": self.usage_dimensions,
                "statisticRecommendation": self.usage_statistic,
            },
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Listet alle Service-Quotas einer Region und markiert erweiterbare Quotas.",
    )
    parser.add_argument(
        "--region",
        default="eu-central-1",
        help="AWS-Region (Default: %(default)s)",
    )
    parser.add_argument(
        "--profile",
        default=None,
        help="Optionales AWS CLI/SDK Profil (z. B. --profile prod)",
    )
    parser.add_argument(
        "--service-code",
        action="append",
        dest="service_codes",
        help="Optional: auf bestimmte Service-Codes einschränken (mehrfach nutzbar)",
    )
    parser.add_argument(
        "--format",
        choices=("table", "json"),
        default="table",
        help="Ausgabeformat (Default: %(default)s)",
    )
    parser.add_argument(
        "--output-csv",
        dest="output_csv",
        help="Optionaler Dateipfad für einen CSV-Export (unabhängig vom Format).",
    )
    return parser.parse_args()


def format_bool(value: bool) -> str:
    return "ja" if value else "nein"


def format_dimensions(dimensions: dict[str, str] | None) -> str:
    if not dimensions:
        return ""
    return ", ".join(f"{key}={value}" for key, value in sorted(dimensions.items()))


def format_metric(row: QuotaRow) -> str:
    if not row.has_usage_metric:
        return "nein"
    metric = f"{row.usage_namespace or ''}:{row.usage_name or ''}".strip(":")
    dims = format_dimensions(row.usage_dimensions)
    if dims:
        metric = f"{metric} [{dims}]"
    return metric or "ja"


def render_table(rows: Sequence[QuotaRow]) -> str:
    headers = (
        "Service",
        "Quota",
        "Einheit",
        "Wert",
        "Erweiterbar",
        "Usage-Metric",
    )
    table: list[Sequence[str]] = [
        (
            row.service_name,
            row.quota_name,
            row.unit or "",
            "" if row.value is None else f"{row.value:g}",
            format_bool(row.adjustable),
            format_metric(row),
        )
        for row in rows
    ]
    widths = [
        max(len(headers[idx]), *(len(col[idx]) for col in table)) if table else len(headers[idx])
        for idx in range(len(headers))
    ]

    def fmt_row(values: Sequence[str]) -> str:
        return "  ".join(value.ljust(widths[idx]) for idx, value in enumerate(values))

    lines = [fmt_row(headers), fmt_row(tuple("-" * w for w in widths))]
    lines.extend(fmt_row(row) for row in table)
    return "\n".join(lines)


def iter_services(client, service_codes: Iterable[str] | None = None) -> Iterable[dict]:
    paginator = client.get_paginator("list_services")
    codes = {code.lower() for code in service_codes} if service_codes else None
    for page in paginator.paginate():
        for service in page.get("Services", []):
            if codes and service["ServiceCode"].lower() not in codes:
                continue
            yield service


def fetch_service_quotas(client, service_code: str) -> Iterable[dict]:
    paginator = client.get_paginator("list_service_quotas")
    for page in paginator.paginate(ServiceCode=service_code):
        yield from page.get("Quotas", [])


def collect_quotas(region: str, profile: str | None, service_codes: Iterable[str] | None) -> list[QuotaRow]:
    session_kwargs = {"region_name": region}
    if profile:
        session_kwargs["profile_name"] = profile
    session = boto3.Session(**session_kwargs)
    config = Config(retries={"max_attempts": 10, "mode": "adaptive"})
    client = session.client("service-quotas", config=config)

    rows: list[QuotaRow] = []
    for service in iter_services(client, service_codes):
        code = service["ServiceCode"]
        name = service["ServiceName"]
        try:
            for quota in fetch_service_quotas(client, code):
                usage_metric = quota.get("UsageMetric") or {}
                rows.append(
                    QuotaRow(
                        region=region,
                        service_code=code,
                        service_name=name,
                        quota_code=quota.get("QuotaCode", ""),
                        quota_name=quota.get("QuotaName", ""),
                        adjustable=bool(quota.get("Adjustable")),
                        has_usage_metric=bool(quota.get("UsageMetric")),
                        value=quota.get("Value"),
                        unit=quota.get("Unit"),
                        usage_namespace=usage_metric.get("MetricNamespace"),
                        usage_name=usage_metric.get("MetricName"),
                        usage_dimensions=usage_metric.get("MetricDimensions"),
                        usage_statistic=usage_metric.get("MetricStatisticRecommendation"),
                    )
                )
        except (ClientError, BotoCoreError) as exc:
            print(f"[WARN] Quotas für Service {code} konnten nicht geladen werden: {exc}", file=sys.stderr)
            continue
    return rows


def write_csv(path: str, rows: Sequence[QuotaRow]) -> None:
    fieldnames = (
        "region",
        "serviceCode",
        "serviceName",
        "quotaCode",
        "quotaName",
        "unit",
        "value",
        "adjustable",
        "hasUsageMetric",
        "metricNamespace",
        "metricName",
        "metricDimensions",
        "metricStatisticRecommendation",
    )
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "region": row.region,
                    "serviceCode": row.service_code,
                    "serviceName": row.service_name,
                    "quotaCode": row.quota_code,
                    "quotaName": row.quota_name,
                    "unit": row.unit or "",
                    "value": "" if row.value is None else f"{row.value:g}",
                    "adjustable": "true" if row.adjustable else "false",
                    "hasUsageMetric": "true" if row.has_usage_metric else "false",
                    "metricNamespace": row.usage_namespace or "",
                    "metricName": row.usage_name or "",
                    "metricDimensions": format_dimensions(row.usage_dimensions),
                    "metricStatisticRecommendation": row.usage_statistic or "",
                }
            )


def main() -> int:
    args = parse_args()
    try:
        rows = collect_quotas(args.region, args.profile, args.service_codes)
    except (ClientError, BotoCoreError) as exc:
        print(f"Fehler beim Abruf der Quotas: {exc}", file=sys.stderr)
        return 2

    rows.sort(key=lambda row: (row.service_name, row.quota_name))
    if not rows:
        print("Keine Quotas gefunden (prüfe Region/Service-Code/Konto-Berechtigungen).")
        return 0

    if args.format == "json":
        print(json.dumps([row.as_dict() for row in rows], indent=2, ensure_ascii=False))
    else:
        print(render_table(rows))
        print(f"\n{len(rows)} Quotas gefunden in Region {args.region}.")

    if args.output_csv:
        try:
            write_csv(args.output_csv, rows)
        except OSError as exc:
            print(f"[WARN] CSV-Datei konnte nicht geschrieben werden: {exc}", file=sys.stderr)
            return 3
        print(f"CSV exportiert nach {args.output_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
