#!/usr/bin/env python3
"""Compare a Service Quotas export with resource checks and compatible metrics.

This utility is intentionally offline: it reads JSON and imports the local check
registry, but never creates an AWS client.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

# Allow ``python scripts/quota_coverage.py ...`` from a repository checkout
# without requiring an editable package installation.
if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from modules.qmcore.registry import custom_keys
from modules.qmcore.catalog import account_catalog
from modules.qmcore.metrics import compatible


SERVICE_ALIASES = {'awscloudmap': 'servicediscovery'}


def load_catalog(path: str) -> list[dict]:
    value = json.loads(Path(path).read_text(encoding='utf-8'))
    if isinstance(value, dict):
        value = value.get('Quotas', value.get('Items', [value]))
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError('Katalog muss eine JSON-Liste oder ein Quotas/Items-Objekt enthalten')
    return value


def service_code(value: object) -> str:
    raw = str(value or '')
    return SERVICE_ALIASES.get(raw.lower(), raw.lower())


def normalize_quota(quota: dict) -> dict:
    """Accept both AWS API records and the older camel-case export format."""
    result = dict(quota)
    for key in ('ServiceCode', 'QuotaCode', 'QuotaName', 'UsageMetric', 'Unit',
                'GlobalQuota', 'QuotaAppliedAtLevel', 'Period', 'Value', 'ErrorReason'):
        legacy = key[0].lower() + key[1:]
        if key not in result and legacy in result:
            result[key] = result[legacy]
    if not result.get('ServiceCode') or not result.get('QuotaCode'):
        raise ValueError('Katalogeintrag ohne ServiceCode/QuotaCode')
    result['ServiceCode'] = service_code(result['ServiceCode'])
    return result


def catalog_coverage(quotas: list[dict], implemented: set[tuple[str, str]] | None = None) -> list[dict]:
    implemented = implemented if implemented is not None else custom_keys()
    implemented = {(service_code(service), code) for service, code in implemented}
    unique = {(q['ServiceCode'], q['QuotaCode']): q
              for q in account_catalog([normalize_quota(q) for q in quotas])}
    services = defaultdict(lambda: {'total': 0, 'implemented': 0, 'compatibleMetric': 0,
                                    'covered': 0, 'uncovered': 0, 'uncoveredCodes': []})
    for (service, code), quota in sorted(unique.items()):
        row = services[service]
        row['total'] += 1
        custom = (service, code) in implemented
        metric = compatible(quota)
        row['implemented'] += int(custom)
        row['compatibleMetric'] += int(metric)
        if custom or metric:
            row['covered'] += 1
        else:
            row['uncovered'] += 1
            row['uncoveredCodes'].append(code)
    result = []
    for service, row in sorted(services.items()):
        total = row['total']
        result.append({**row, 'serviceCode': service,
                       'coveredPct': round(row['covered'] / total * 100, 1) if total else None,
                       'implementedPct': round(row['implemented'] / total * 100, 1) if total else None})
    return result


def render_table(rows: list[dict]) -> str:
    headers = ('Service', 'Total', 'Custom', 'Metric', 'Covered', 'Coverage', 'Uncovered')
    values = [(r['serviceCode'], str(r['total']), str(r['implemented']), str(r['compatibleMetric']),
               str(r['covered']), '-' if r['coveredPct'] is None else f"{r['coveredPct']:.1f}%",
               str(r['uncovered'])) for r in rows]
    total = sum(r['total'] for r in rows)
    covered = sum(r['covered'] for r in rows)
    values.append(('TOTAL', str(total), str(sum(r['implemented'] for r in rows)),
                   str(sum(r['compatibleMetric'] for r in rows)), str(covered),
                   f'{covered / total * 100:.1f}%' if total else '-', str(total - covered)))
    all_rows = [headers, *values]
    widths = [max(len(row[i]) for row in all_rows) for i in range(len(headers))]
    return '\n'.join('  '.join(value.ljust(widths[i]) for i, value in enumerate(row))
                     for row in all_rows)


MEASURES = ('total', 'implemented', 'compatibleMetric', 'covered', 'uncovered')


def merge_catalogs(paths: list[str]) -> list[dict]:
    """Union several exports; later files win per service/quota code.

    A single export is never the whole truth: ``list_service_quotas`` returns a
    different set with and without ``QuotaAppliedAtLevel``, so quotas that exist
    in the account can be missing from any one snapshot.
    """
    merged: dict[tuple[str, str], dict] = {}
    for path in paths:
        for quota in load_catalog(path):
            item = normalize_quota(quota)
            merged[(item['ServiceCode'], item['QuotaCode'])] = item
    return list(merged.values())


CATALOG_FIELDS = ('ServiceCode', 'QuotaCode', 'QuotaName', 'UsageMetric', 'Unit',
                  'GlobalQuota', 'QuotaAppliedAtLevel', 'Period')


def write_catalog(quotas: list[dict], path: str) -> int:
    """Store the merged catalog with just the fields coverage depends on.

    The exports under ``data/`` are untracked, so CI and contributors need a
    committed copy to reproduce the same numbers.
    """
    rows = sorted(({field: quota[field] for field in CATALOG_FIELDS
                    if quota.get(field) is not None} for quota in quotas),
                  key=lambda row: (row['ServiceCode'], row['QuotaCode']))
    Path(path).write_text(json.dumps(rows, separators=(',', ':'), sort_keys=True),
                          encoding='utf-8')
    return len(rows)


def totals(rows: list[dict]) -> dict:
    return {measure: sum(row[measure] for row in rows) for measure in MEASURES}


def compare_baseline(rows: list[dict], path: str) -> list[str]:
    """Return one message per measure that regressed against the baseline."""
    baseline = json.loads(Path(path).read_text(encoding='utf-8'))
    current = totals(rows)
    failures = []
    for measure in ('implemented', 'compatibleMetric', 'covered'):
        expected = baseline.get(measure)
        if expected is not None and current[measure] < expected:
            failures.append(f'{measure} fell from {expected} to {current[measure]}')
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description='Offline Service-Quota-Coverage prüfen')
    parser.add_argument('input', nargs='+', help='Lokale Service-Quotas-JSON-Exporte')
    parser.add_argument('--format', choices=('table', 'json'), default='table')
    parser.add_argument('--baseline', help='Baseline-JSON; Exit 1 bei Rückschritt')
    parser.add_argument('--update-baseline', metavar='PATH',
                        help='Aktuelle Summen als Baseline schreiben')
    parser.add_argument('--write-catalog', metavar='PATH',
                        help='Zusammengeführten Katalog als Fixture schreiben')
    args = parser.parse_args()
    merged = merge_catalogs(args.input)
    if args.write_catalog:
        print(f'{write_catalog(merged, args.write_catalog)} Quotas -> {args.write_catalog}')
    rows = catalog_coverage(merged)
    print(json.dumps(rows, indent=2, ensure_ascii=False) if args.format == 'json' else render_table(rows))
    if args.update_baseline:
        Path(args.update_baseline).write_text(
            json.dumps(totals(rows), indent=2) + '\n', encoding='utf-8')
    if args.baseline:
        failures = compare_baseline(rows, args.baseline)
        for failure in failures:
            print(f'Coverage-Rückschritt: {failure}', file=sys.stderr)
        return 1 if failures else 0
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
