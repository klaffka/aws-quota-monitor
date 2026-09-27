import json
import logging
import os
import sys
from pathlib import Path
from datetime import timedelta

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.qmcore.aws import CheckContext, session_from_env
from modules.qmcore.catalog import account_catalog, get_catalog
from modules.qmcore.coverage import build_coverage
from modules.qmcore.metrics import compatible, fetch_metrics
from modules.qmcore.model import iso
from modules.qmcore.registry import collectors
from modules.qmcore.runs import RunBusy, RunLease, run_window
from modules.qmalerting.alerting import QuotaAlert
from modules.qmdb.db import QuotaLogDb

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    from time import perf_counter
    from modules.qmcore.telemetry import ApiTelemetry
    started = perf_counter()
    session = session_from_env()
    telemetry = ApiTelemetry(session)
    db = QuotaLogDb(session)
    ctx = CheckContext(session)
    run_id, start, end = run_window(event, ctx.now)
    lease = RunLease(db, ctx.account, ctx.region, run_id)
    try:
        if not lease.acquire():
            return {'statusCode': 200, 'body': json.dumps({'runId': run_id, 'duplicate': True})}
    except RunBusy:
        # A duplicate delivery or early retry overlaps a live invocation; that
        # invocation reports the outcome, and the heartbeat alarm catches a lost one.
        logger.warning('Run %s is held by another invocation; skipping', run_id)
        return {'statusCode': 200, 'body': json.dumps({'runId': run_id, 'busy': True})}
    try:
        result = collect(event or {}, ctx, db, telemetry, started, run_id, start, end)
    except Exception:
        finish_lease(lease, False)
        raise
    finish_lease(lease, True)
    return result


def finish_lease(lease, success):
    # Lease bookkeeping must neither mask a collector error nor fail a run
    # whose measurements are already stored.
    try:
        lease.finish(success)
    except Exception:
        logger.exception('Could not mark run lease %s', 'COMPLETE' if success else 'FAILED')


def collect(event, ctx, db, telemetry, started, run_id, start, end):
    from time import perf_counter
    alerts = QuotaAlert(ctx.session, threshold_pct=os.getenv('QM_ALERT_THRESHOLD', '80'), db=db)
    errors = []
    try:
        quotas, catalog_errors = get_catalog(ctx, db)
    except Exception as exc:
        quotas, catalog_errors = [], [f'catalog: {exc}']
    errors.extend(catalog_errors)
    # Never transition alert state from a partial or missing catalog. A
    # partial snapshot can otherwise look like a valid low-usage observation
    # and emit a false recovery for quotas omitted by the failed refresh.
    catalog_usable = bool(quotas) and not catalog_errors
    if not catalog_usable:
        errors.append('catalog: empty or incomplete quota catalog')
    ctx.quotas = {(q['ServiceCode'], q['QuotaCode']): q for q in account_catalog(quotas)}
    official = {(q['ServiceCode'], q['QuotaCode']) for q in quotas if compatible(q)}
    ctx.metric_start, ctx.metric_end = start, end
    entries, check_times = [], {}
    for module_name, collector in collectors():
        before = perf_counter()
        try:
            entries.extend(collector(ctx=ctx, skip=official))
        except Exception as exc:
            errors.append(f'collector:{module_name}: {exc}')
        check_times[module_name] = round(perf_counter() - before, 3)
    # A compatible official metric is the single source of truth for its
    # quota, including quotas that also have a resource-check implementation.
    # Incompatible metrics fall back to that resource check and are not emitted
    # as a second UNSUPPORTED measurement.
    metric_quotas = [q for q in quotas if compatible(q)]
    entries.extend(fetch_metrics(ctx, metric_quotas, start, end))
    for entry in entries:
        # Stable retry slot; collectedAt still reflects the actual inventory time.
        entry.update(SK=f'TS#{iso(end)}', runId=run_id, scheduledAt=iso(end))
        if entry['qualityStatus'] == 'ERROR':
            errors.append(f"{entry['serviceCode']}/{entry['quotaCode']}: {entry['qualityReason']}")
    # Catalog and storage failures are usually transient and worth a retry;
    # check errors repeat deterministically, and a retry re-buys every metric.
    retryable = not catalog_usable
    alerts_enabled = catalog_usable and not event.get('validation') and ctx.now - end <= timedelta(hours=26)
    for entry, store_error in db.put_quota_entries(entries):
        if store_error is not None:
            errors.append(f"store:{entry['quotaCode']}: {store_error}")
            retryable = True
            continue
        if alerts_enabled:
            try:
                alerts.check_and_alert(entry)
            except Exception as exc:
                errors.append(f"alert:{entry['quotaCode']}: {exc}")
    coverage = build_coverage(quotas, entries)
    db.put_quota_entry({'PK': f'COVERAGE#{ctx.account}#{ctx.region}', 'SK': f'TS#{iso(end)}',
                        **coverage, 'ttl': int(ctx.now.timestamp()) + 64 * 86400})
    # Run records also identify failures that occur before a quota is discovered.
    performance = {'durationSeconds': round(perf_counter() - started, 3),
                   'apiByService': telemetry.snapshot(), 'checkSecondsByModule': check_times}
    logger.info('Collector performance: %s', json.dumps(performance, sort_keys=True))
    db.put_quota_entry({'PK': f'RUN#{ctx.account}#{ctx.region}', 'SK': f'TS#{iso(end)}',
                        **performance, 'runId': run_id, 'scheduledAt': iso(end),
                        'collectedAt': iso(ctx.now), 'alertsEnabled': alerts_enabled,
                        'windowStart': iso(start), 'windowEnd': iso(end),
                        'qualityStatus': 'ERROR' if errors else 'OK', 'errors': errors,
                        'measurementCount': len(entries), 'ttl': int(ctx.now.timestamp()) + 64 * 86400})
    if errors:
        logger.error('Partial collector run: %s', errors)
        if retryable:
            raise RuntimeError(f'Collector incomplete: {len(errors)} errors; successful measurements saved')
    elif ctx.now - end <= timedelta(hours=26) and not event.get('validation'):
        ctx.client('cloudwatch').put_metric_data(Namespace='QuotaMonitor', MetricData=[{
        'MetricName': 'CollectorSuccess', 'Dimensions': [{'Name': 'Account', 'Value': ctx.account},
            {'Name': 'Region', 'Value': ctx.region}], 'Value': 1, 'Unit': 'Count'}])
    return {'statusCode': 200, 'body': json.dumps({'measurements': len(entries), 'runId': run_id,
                                                   'errors': len(errors)})}


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(lambda_handler({}, None), indent=2))
