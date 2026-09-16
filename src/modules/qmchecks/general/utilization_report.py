"""Compatibility helper backed by real Service Quotas and CloudWatch APIs."""
from datetime import timedelta
from modules.qmcore.aws import CheckContext, session_from_env
from modules.qmcore.catalog import get_catalog
from modules.qmcore.metrics import fetch_metrics
from modules.qmdb.db import QuotaLogDb


def quota_utilization_report(service_code=None, session=None):
    session = session or session_from_env()
    ctx = CheckContext(session)
    quotas, errors = get_catalog(ctx, QuotaLogDb(session))
    if errors:
        raise RuntimeError(f'Catalog incomplete: {errors}')
    selected = [q for q in quotas if q.get('UsageMetric') and
                (service_code is None or q['ServiceCode'] == service_code)]
    return fetch_metrics(ctx, selected, ctx.now - timedelta(minutes=20), ctx.now)


def process_quota_utilization_report(utilization_report, session=None):
    return utilization_report
