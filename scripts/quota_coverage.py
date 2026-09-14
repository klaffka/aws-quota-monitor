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


def main() -> int:
    parser = argparse.ArgumentParser(description='Offline Service-Quota-Coverage prüfen')
    parser.add_argument('input', help='Lokaler Service-Quotas-JSON-Export')
    parser.add_argument('--format', choices=('table', 'json'), default='table')
    args = parser.parse_args()
    rows = catalog_coverage(load_catalog(args.input))
    print(json.dumps(rows, indent=2, ensure_ascii=False) if args.format == 'json' else render_table(rows))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
