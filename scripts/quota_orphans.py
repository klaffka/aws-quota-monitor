#!/usr/bin/env python3
"""Report implemented quota codes that a Service Quotas export does not contain.

Checks whose quota code is absent from the catalog measure nothing: the
collector never reports them. This utility separates the two possible causes so
they can be treated differently:

``UNKNOWN_QUOTA``
    The service is in the exports but the quota code is not. A mistyped or
    retired code is the likely cause, so the check needs verification.
``UNKNOWN_SERVICE``
    The service is absent from the exports altogether.

Neither reason proves a defect on its own. ``list_service_quotas`` returns a
different set with and without ``QuotaAppliedAtLevel``, so a single export can
omit quotas the account really has. Pass every available export to keep false
positives out of the report.

Like ``quota_coverage.py`` this is intentionally offline: it reads JSON and
imports the local check registry, but never creates an AWS client.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

if __package__ in {None, ''}:
    root = Path(__file__).resolve().parents[1]
    sys.path[:0] = [str(root), str(root / 'src')]

from modules.qmcore.registry import custom_keys
from scripts.quota_coverage import merge_catalogs, normalize_quota, service_code

UNKNOWN_QUOTA = 'UNKNOWN_QUOTA'
UNKNOWN_SERVICE = 'UNKNOWN_SERVICE'


def catalog_pairs(quotas: list[dict]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    for quota in quotas:
        item = normalize_quota(quota)
        result[item['ServiceCode']].add(item['QuotaCode'])
    return result


def orphans(quotas: list[dict], implemented: set[tuple[str, str]] | None = None) -> list[dict]:
    implemented = implemented if implemented is not None else custom_keys()
    catalog = catalog_pairs(quotas)
    rows = []
    for service, code in sorted({(service_code(s), c) for s, c in implemented}):
        known = catalog.get(service)
        if known is None:
            rows.append({'serviceCode': service, 'quotaCode': code, 'reason': UNKNOWN_SERVICE})
        elif code not in known:
            rows.append({'serviceCode': service, 'quotaCode': code, 'reason': UNKNOWN_QUOTA})
    return rows


def render_table(rows: list[dict]) -> str:
    services: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        services[row['reason']][row['serviceCode']].append(row['quotaCode'])
    lines = []
    for reason in (UNKNOWN_QUOTA, UNKNOWN_SERVICE):
        found = services.get(reason, {})
        total = sum(len(codes) for codes in found.values())
        lines.append(f'{reason}: {total} quota codes across {len(found)} services')
        for service, codes in sorted(found.items()):
            lines.append(f'  {service}  {len(codes)}  {" ".join(sorted(codes))}')
    lines.append(f'TOTAL: {len(rows)} implemented quota codes listed')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Implementierte Quota-Codes ohne Katalogeintrag melden')
    parser.add_argument('input', nargs='+', help='Lokale Service-Quotas-JSON-Exporte')
    parser.add_argument('--format', choices=('table', 'json'), default='table')
    parser.add_argument('--reason', choices=(UNKNOWN_QUOTA, UNKNOWN_SERVICE),
                        help='Nur diese Ursache ausgeben')
    args = parser.parse_args()
    rows = orphans(merge_catalogs(args.input))
    if args.reason:
        rows = [row for row in rows if row['reason'] == args.reason]
    print(json.dumps(rows, indent=2, ensure_ascii=False) if args.format == 'json'
          else render_table(rows))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
