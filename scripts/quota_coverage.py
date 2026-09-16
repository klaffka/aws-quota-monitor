#!/usr/bin/env python3
"""Compare a Service Quotas export with resource checks and compatible metrics.

This utility is intentionally offline: it reads JSON and imports the local check
registry, but never creates an AWS client.
"""
from __future__ import annotations

import argparse
import json
import re
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


PER_SECOND = re.compile(r'\bTPS\b|per second|throttle rate', re.IGNORECASE)
# Anchored, because Textract uses "throttle limit for max number of adapters per
# account" and similar wording for quotas that really are resource counts.
OPERATION_THROTTLE = re.compile(r'^\S+(?: API)? throttle limit$', re.IGNORECASE)
# SSM Contacts words the same thing as "<Operation> API throttle quota" and
# "Voice engagement throttle quota". Ten of its sixteen already fall to the
# period rule because they state a one-second window; the other six describe
# the same request rates and differ only in carrying no period.
THROTTLE_QUOTA = re.compile(r'throttle quota$', re.IGNORECASE)
# IoT writes a bare "<Operation> rate"; one token before the word keeps the
# rule on operation names and off wordings like "Job execution roll out rate".
OPERATION_RATE = re.compile(r'^\S+ rate$', re.IGNORECASE)
# Every "<Operation> rate quota" in the catalog has a matching "<Operation>
# burst quota", which the burst rule already excludes: the pair is the refill
# rate and the depth of one token bucket. tests/test_quota_coverage.py asserts
# the pairing against the committed catalog.
RATE_QUOTA = re.compile(r'rate quota$', re.IGNORECASE)
# "Rate of GetSchema requests", "Request rate for DeleteAsset": Service Quotas
# states these per second. None of the 555 such entries names a longer window,
# and the guard keeps a future "Rate of X per day" in the measurable base.
RATE_PREFIX = re.compile(r'^(rate of|request rate for)\b', re.IGNORECASE)
LONGER_WINDOW = re.compile(r'\bper (minute|hour|day|week|month|year)\b', re.IGNORECASE)
# Step Functions writes a bucket's depth as "<Operation> throttle token bucket
# size" and ECS its refill as "... (or bucket refill rate)".
BUCKET_DEPTH = re.compile(r'throttle token bucket size$|bucket refill rate\)?$',
                          re.IGNORECASE)
# EMR words the same thing as "Replenishment rate of <Operation> calls" and
# "The maximum rate at which your bucket replenishes ...".
REPLENISHMENT = re.compile(r'replenish', re.IGNORECASE)

def _name(quota: dict) -> str:
    return quota.get('QuotaName') or ''


def _per_second(quota: dict) -> bool:
    """Read the measurement window AWS states for the quota itself.

    A quota whose period is one second is a request rate whatever its name
    says, which catches the many `Rate of <Operation> API requests` entries
    that no wording rule matches.
    """
    period = quota.get('Period') or {}
    return (period.get('PeriodUnit'), period.get('PeriodValue')) == ('SECOND', 1)


UNMEASURABLE_RULES = (
    # An EC2 request bucket's depth and refill are not observable per account.
    ('TOKEN_BUCKET', lambda quota: _name(quota).endswith(
        ('request bucket maximum capacity', 'request bucket refill rate'))
        or bool(BUCKET_DEPTH.search(_name(quota)))
        or bool(REPLENISHMENT.search(_name(quota)))),
    # One-minute CloudWatch sums cannot establish a per-second peak. Where AWS
    # publishes a usage metric for such a quota it counts as covered before
    # these rules are consulted, and no custom check measures one today.
    ('API_RATE', lambda quota: bool(PER_SECOND.search(_name(quota)))
                               or bool(OPERATION_THROTTLE.match(_name(quota)))
                               or bool(THROTTLE_QUOTA.search(_name(quota)))
                               or bool(RATE_QUOTA.search(_name(quota)))
                               or bool(OPERATION_RATE.match(_name(quota)))
                               or (bool(RATE_PREFIX.match(_name(quota)))
                                   and not LONGER_WINDOW.search(_name(quota)))),
    # Burst allowances are token buckets too, but EFS bursting throughput is a
    # published metric rather than a request bucket.
    ('API_BURST', lambda quota: 'burst' in _name(quota).lower()
                                and 'throughput' not in _name(quota).lower()),
    # Last, so a quota that one of the wording rules already explains keeps
    # that reason and the published figures stay comparable.
    ('PERIOD_RATE', _per_second),
)


# A bound on one payload or document exists only while a request is in flight,
# and a bound stated in time units is a period rather than a count however the
# name reads: CodeDeploy's "Minutes until a deployment fails" and "AWS Lambda
# deployment run in hours" are the deployment's clock, not an inventory.
#
# The time units are matched in the plural only, because English uses the
# singular attributively: Connect's "Historical actuals 15 or 30 minute interval
# file count" counts files and merely describes their interval, while every
# quota that really names a period writes "hours", "minutes" or "seconds".
SIZE_OR_PERIOD = re.compile(
    r'\b(size|length|bytes|kb|mb|gb|kib|mib|gib|tib|characters?|payload|duration|'
    r'timeout|retention|expiration|age|depth|ttl|width|resolution|bitrate|'
    r'hours|minutes|seconds|milliseconds)\b',
    re.IGNORECASE)
# A rate no exclusion rule matched, because the name names neither a window nor
# an operation. These stay measurable, but a check would have to invent a window.
# A window stated in whole days is matched explicitly and first, because it also
# names an hour: "Basic image scans per 24 hours" counts sends over a day, not a
# duration, and "emails ... per 24-hour period" is the same shape spelled out.
DAY_WINDOW = re.compile(r'per \d+[- ]?hours?\b|per \d+[- ]?hour period\b'
                        r'|during a \d+-hour period\b', re.IGNORECASE)
RATE_SHAPED = re.compile(r'\brate\b|\bthroughput\b|\bper (second|minute|hour|day)\b',
                         re.IGNORECASE)


# A volume of data inside one job, file or request. "Records per batch inference
# job" reads like a count, but it bounds the payload rather than an inventory.
VOLUME = re.compile(r'\b(records?|tokens?|rows?|columns?|data points?|characters?) per\b'
                    r'|\bsum of training and validation\b|\bamount of\b'
                    r'|\bper (call|request|invocation)\b|\bin a \w+ call\b',
                    re.IGNORECASE)
# The same bound, written with the operation named in between: "Blueprints per
# Start Inference request", "Files to ingest per IngestKnowledgeBaseDocuments
# job". The operation name is capitalised, which is what separates these from
# "Reports per instance" and every other per-parent inventory.
NAMED_REQUEST = re.compile(r'\bper [A-Z][\w-]*(?: [\w-]+)* (request|job)\b')


# Service Quotas still lists these services, but botocore ships no client for
# them under any name, so no inventory can be read however the quota is worded:
# AWS retired the service (IoT Analytics, IoT Events, QLDB, RoboMaker, Lookout
# for Metrics, Lookout for Vision, CloudWatch Evidently, SimSpace Weaver) or has
# never published an API for it (CloudShell, Kiro, Q Developer transformation,
# Amazon Connect Decisions). ``test_every_service_listed_as_dropped_really_has_no
# _client`` fails if botocore ships one again, so the list cannot go stale in the
# flattering direction.
SDK_REMOVED = frozenset({
    'cloudshell', 'evidently', 'iotanalytics', 'iotevents', 'kiro',
    'lookoutmetrics', 'lookoutvision', 'qldb', 'qt-platform', 'robomaker',
    'scn', 'simspaceweaver',
})


# A quota AWS counts over every account in the organization. This collector
# holds one account's credentials, so what the other members hold is invisible
# to it however readable the local half is: EC2 capacity blocks are reported
# per account and per organization side by side, and only the first is
# answerable here. A quota this matches that some API does answer, such as
# Service Catalog's delegated administrators, counts as covered before the
# shapes are consulted and never reaches this rule.
ORGANIZATION_SCOPED = re.compile(
    r'per (AWS )?organization\b|across the organization|organization-wide', re.IGNORECASE)


def gap_shape(quota: dict) -> str:
    """Classify a measurable, uncovered quota by what its name describes.

    The shape says what the remaining work is: a countable quota needs an
    inventory, the others need a source that does not exist yet.

    A service the SDK no longer reaches is asked first, because its names still
    read as counts and would otherwise promise work no API can do.
    """
    if quota.get('ServiceCode') in SDK_REMOVED:
        return 'no_sdk_client'
    name = _name(quota)
    if ORGANIZATION_SCOPED.search(name):
        return 'cross_account'
    if DAY_WINDOW.search(name) or RATE_SHAPED.search(name):
        return 'rate_shaped'
    if SIZE_OR_PERIOD.search(name) or VOLUME.search(name) or NAMED_REQUEST.search(name):
        return 'size_or_period'
    return 'countable'


def unmeasurable(quota: dict) -> str | None:
    """Return why this quota's usage cannot be counted at all, or None.

    Counting the resources behind these quotas is not a matter of writing
    another check: the occupancy of a token bucket and the peak of a
    per-second rate are not derivable from the telemetry AWS exposes. Keeping
    them in the denominator makes coverage look permanently unreachable, so
    they are reported separately rather than silently dropped.
    """
    for reason, matches in UNMEASURABLE_RULES:
        if matches(quota):
            return reason
    return None


def catalog_coverage(quotas: list[dict], implemented: set[tuple[str, str]] | None = None) -> list[dict]:
    implemented = implemented if implemented is not None else custom_keys()
    implemented = {(service_code(service), code) for service, code in implemented}
    unique = {(q['ServiceCode'], q['QuotaCode']): q
              for q in account_catalog([normalize_quota(q) for q in quotas])}
    services = defaultdict(lambda: {'total': 0, 'implemented': 0, 'compatibleMetric': 0,
                                    'covered': 0, 'uncovered': 0, 'unmeasurable': 0,
                                    'countable': 0, 'size_or_period': 0, 'rate_shaped': 0,
                                    'no_sdk_client': 0, 'cross_account': 0,
                                    'uncoveredCodes': []})
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
            if unmeasurable(quota) is not None:
                row['unmeasurable'] += 1
            else:
                row[gap_shape(quota)] += 1
    result = []
    for service, row in sorted(services.items()):
        total, measurable = row['total'], row['total'] - row['unmeasurable']
        result.append({**row, 'serviceCode': service, 'measurable': measurable,
                       'coveredPct': round(row['covered'] / total * 100, 1) if total else None,
                       'measurablePct': (round(row['covered'] / measurable * 100, 1)
                                         if measurable else None),
                       'implementedPct': round(row['implemented'] / total * 100, 1) if total else None})
    return result


def _percent(covered: int, base: int) -> str:
    return f'{covered / base * 100:.1f}%' if base else '-'


def render_table(rows: list[dict]) -> str:
    headers = ('Service', 'Total', 'Custom', 'Metric', 'Covered', 'Coverage', 'Uncovered',
               'Unmeas', 'OfMeasurable')
    values = [(r['serviceCode'], str(r['total']), str(r['implemented']), str(r['compatibleMetric']),
               str(r['covered']), '-' if r['coveredPct'] is None else f"{r['coveredPct']:.1f}%",
               str(r['uncovered']), str(r['unmeasurable']),
               '-' if r['measurablePct'] is None else f"{r['measurablePct']:.1f}%") for r in rows]
    total = sum(r['total'] for r in rows)
    covered = sum(r['covered'] for r in rows)
    unmeasurable_total = sum(r['unmeasurable'] for r in rows)
    values.append(('TOTAL', str(total), str(sum(r['implemented'] for r in rows)),
                   str(sum(r['compatibleMetric'] for r in rows)), str(covered),
                   _percent(covered, total), str(total - covered), str(unmeasurable_total),
                   _percent(covered, total - unmeasurable_total)))
    all_rows = [headers, *values]
    widths = [max(len(row[i]) for row in all_rows) for i in range(len(headers))]
    return '\n'.join('  '.join(value.ljust(widths[i]) for i, value in enumerate(row))
                     for row in all_rows)


MEASURES = ('total', 'implemented', 'compatibleMetric', 'covered', 'uncovered',
            'unmeasurable', 'measurable')


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


GAP_SHAPES = (
    ('countable', 'the name describes a count; whether an API exposes that inventory has to be checked quota by quota'),
    ('size_or_period', 'the bound applies to one payload or document, or states a '
                       'period in time units, so there is no inventory to count'),
    ('rate_shaped', 'a rate no exclusion rule matches, because the name states '
                    'neither a window nor an operation'),
    ('no_sdk_client', 'botocore ships no client for the service any more, so no '
                      'inventory can be read until AWS restores one'),
    ('cross_account', 'the quota is counted over every account in the organization, '
                      'which one account\'s credentials cannot see'),
)
GAP_LABELS = {'countable': 'countable', 'size_or_period': 'size or period',
              'rate_shaped': 'rate-shaped', 'no_sdk_client': 'no SDK client',
              'cross_account': 'organization-wide'}


def render_gaps(rows: list[dict], limit: int = 12) -> str:
    """Render the measurable-but-uncovered quotas by shape and by service.

    Hand-maintained, this section drifted from the catalog within a week; the
    shape rules live in ``gap_shape`` so the table can be regenerated.
    """
    current = totals(rows)
    shapes = {shape: sum(row[shape] for row in rows) for shape, _note in GAP_SHAPES}
    open_measurable = current['uncovered'] - current['unmeasurable']
    lines = [f'{open_measurable:,} quotas are measurable and still uncovered. Sorting them by '
             'what their', 'names describe shows what the remaining work actually is:', '',
             '| Shape | Quotas | What it would take |', '| --- | ---: | --- |']
    for shape, note in GAP_SHAPES:
        lines.append(f'| {GAP_LABELS[shape]} | {shapes[shape]:,} | {note} |')
    lines += ['', 'The countable ones are spread thin. The twelve largest holdings:', '',
              '| Service | Catalog | Covered | Uncovered | Unmeasurable | Countable |',
              '| --- | ---: | ---: | ---: | ---: | ---: |']
    ranked = sorted(rows, key=lambda row: (-row['countable'], row['serviceCode']))[:limit]
    for row in ranked:
        lines.append(f"| {row['serviceCode']} | {row['total']} | {row['covered']} | "
                     f"{row['uncovered']} | {row['unmeasurable']} | {row['countable']} |")
    return '\n'.join(lines)


def update_progress(rows: list[dict], path: str) -> None:
    """Rewrite the progress document's union column and headline percentages.

    The document is edited by hand for everything else, but these figures move
    with every check and were repeatedly left stale.
    """
    current = totals(rows)
    document = Path(path).read_text(encoding='utf-8')
    for measure in MEASURES:
        document = re.sub(rf'^\| {measure} \| [\d,]+ \|',
                          f'| {measure} | {current[measure]:,} |',
                          document, count=1, flags=re.MULTILINE)
    whole = current['covered'] / current['total'] * 100
    measurable = current['covered'] / current['measurable'] * 100
    document = re.sub(r'\*\*[\d.]+%\*\* of the whole union',
                      f'**{whole:.2f}%** of the whole union', document, count=1)
    document = re.sub(r'\*\*[\d.]+%\*\* of the [\d,]+ quotas',
                      f"**{measurable:.2f}%** of the {current['measurable']:,} quotas",
                      document, count=1)
    # The gap section is generated whole, between its heading and the prose that
    # explains which of the largest holdings are blocked and why.
    document = re.sub(r'(## Largest remaining gaps\n\n).*?(\n\nThe two tables above)',
                      lambda match: match.group(1) + render_gaps(rows) + match.group(2),
                      document, count=1, flags=re.DOTALL)
    Path(path).write_text(document, encoding='utf-8')


def compare_baseline(rows: list[dict], path: str) -> list[str]:
    """Return one message per measure that regressed against the baseline."""
    baseline = json.loads(Path(path).read_text(encoding='utf-8'))
    current = totals(rows)
    failures = []
    for measure in ('implemented', 'compatibleMetric', 'covered'):
        expected = baseline.get(measure)
        if expected is not None and current[measure] < expected:
            failures.append(f'{measure} fell from {expected} to {current[measure]}')
    # Excluding more quotas as unmeasurable raises the reported share without
    # measuring anything, so growth needs the same review as a regression.
    expected = baseline.get('unmeasurable')
    if expected is not None and current['unmeasurable'] > expected:
        failures.append(f'unmeasurable grew from {expected} to {current["unmeasurable"]}')
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
    parser.add_argument('--update-progress', metavar='PATH',
                        help='Zahlen im Fortschrittsdokument aktualisieren')
    parser.add_argument('--gaps', action='store_true',
                        help='Messbare, noch offene Quotas nach Form ausgeben')
    args = parser.parse_args()
    merged = merge_catalogs(args.input)
    if args.write_catalog:
        print(f'{write_catalog(merged, args.write_catalog)} Quotas -> {args.write_catalog}')
    rows = catalog_coverage(merged)
    print(json.dumps(rows, indent=2, ensure_ascii=False) if args.format == 'json'
          else render_gaps(rows) if args.gaps else render_table(rows))
    if args.update_progress:
        update_progress(rows, args.update_progress)
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
