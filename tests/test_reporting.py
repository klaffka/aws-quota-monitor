import csv
import importlib
import json
from datetime import datetime, timedelta, timezone
from io import StringIO
from unittest.mock import Mock
import pytest
from modules.qmcore.aws import CheckContext
from modules.qmcore.model import measurement
from modules.qmcore.reporting import report_period, load_history, build_report, generate_csv_report

NOW = datetime(2026, 3, 1, tzinfo=timezone.utc)
CODE = 'L-8EA77D34'


def test_months_february_leap_year_and_year_rollover():
    for now, expected_start, days in [(NOW, '2026-02-01', 28),
        (datetime(2024,3,1,tzinfo=timezone.utc), '2024-02-01', 29),
        (datetime(2026,1,1,tzinfo=timezone.utc), '2025-12-01', 31)]:
        start, end = report_period({'period': 'previous_month'}, now)
        assert start.strftime('%Y-%m-%d') == expected_start
        assert (end-start).days == days
    assert report_period({'source': 'aws.events', 'time': '2024-03-01T00:00:00Z'}, NOW)[0].year == 2024


@pytest.mark.parametrize('value', [0, -1, 456, True, 1.5, 'abc'])
def test_bad_days(value):
    with pytest.raises(ValueError):
        report_period({'days_back': value}, NOW)


def test_manual_days_and_scheduler_validation(monkeypatch):
    monkeypatch.setenv('QM_REPORT_DAYS', '7')
    start, end = report_period({}, NOW)
    assert end == NOW and end-start == timedelta(days=7)
    assert report_period({'days_back': 3}, NOW)[0] == NOW-timedelta(days=3)
    with pytest.raises(ValueError):
        report_period({'source': 'eventbridge-scheduler', 'days_back': 30}, NOW)


def test_history_scoping_exclusive_end_legacy_and_csv(aws_db):
    session, db = aws_db
    start = NOW-timedelta(minutes=30)
    def add(usage, at, account='a', region='eu-central-1', version=2, limit=10):
        e = measurement(account, region, 'ec2', CODE, 'VPN endpoints', limit, usage, now=at)
        e['calculationVersion'] = version
        db.put_quota_entry(e)
    add(8, start)
    add(2, start+timedelta(minutes=10), limit=20)
    add(99, start+timedelta(minutes=5), version=1)
    add(100, NOW)
    add(100, start, account='other')
    add(100, start, region='us-east-1')
    history = load_history(db, 'a', 'eu-central-1', start, NOW)
    assert len(history) == 3
    ctx = CheckContext(session, account='a', now=NOW)
    rows, errors = build_report(ctx, db, [dict(ServiceCode='ec2', QuotaCode=CODE, QuotaName='VPN endpoints', Value=20, Unit='Count')], start, NOW)
    assert not errors
    row, = rows
    assert row['maxUsage'] == 8 and row['limitAtPeak'] == 10 and row['currentLimit'] == 20
    assert row['excludedSamples'] == 1 and row['qualityStatus'] == 'NO_DATA'
    exported, = list(csv.DictReader(StringIO(generate_csv_report(rows))))
    assert exported['Account'] == 'a' and exported['Region'] == 'eu-central-1'
    assert float(exported['Max Usage in Period']) == 8
    assert 'Current Month' not in generate_csv_report(rows)
    assert 'Measurement Type' in exported and exported['Measurement Type'] == 'RESOURCE_COUNT'
    assert exported['Period End Exclusive (UTC)'] == '2026-03-01T00:00:00Z'


def test_history_scan_pagination_and_error(aws_db):
    db = Mock()
    db.table.scan.side_effect = [{'Items': [], 'LastEvaluatedKey': {'PK': 'p', 'SK': 's'}}, {'Items': [{'x': 1}]}]
    assert load_history(db, 'a', 'r', NOW-timedelta(days=1), NOW) == [{'x': 1}]
    assert db.table.scan.call_args.kwargs['ExclusiveStartKey'] == {'PK': 'p', 'SK': 's'}
    db.table.scan.side_effect = [{'Items': [], 'LastEvaluatedKey': {'PK': 'p', 'SK': 's'}}, RuntimeError('denied')]
    with pytest.raises(RuntimeError):
        load_history(db, 'a', 'r', NOW-timedelta(days=1), NOW)


def test_partial_report_saved_then_lambda_raises(aws_db, monkeypatch):
    main = importlib.import_module('functions.reporting.main')
    session, db = aws_db
    session.client('s3').create_bucket(Bucket='report-test-bucket', CreateBucketConfiguration={'LocationConstraint': 'eu-central-1'})
    monkeypatch.setenv('QM_REPORT_BUCKET', 'report-test-bucket')
    monkeypatch.setattr(main, 'session_from_env', lambda: session)
    monkeypatch.setattr(main, 'get_catalog', lambda *a, **kw: ([], ['AccessDenied for service']))
    with pytest.raises(RuntimeError, match='Partial report saved'):
        main.lambda_handler({'days_back': 1}, None)
    objects = session.client('s3').list_objects_v2(Bucket='report-test-bucket')['Contents']
    assert len(objects) == 2
    sidecar = next(o for o in objects if o['Key'].endswith('.json'))
    data = json.loads(session.client('s3').get_object(Bucket='report-test-bucket', Key=sidecar['Key'])['Body'].read())
    assert data['status'] == 'PARTIAL' and data['errors']


def test_upload_failure_is_function_error(aws_db, monkeypatch):
    main = importlib.import_module('functions.reporting.main')
    monkeypatch.setattr(main, 'session_from_env', lambda: aws_db[0])
    monkeypatch.setenv('QM_REPORT_BUCKET', 'nonexistent-bucket')
    monkeypatch.setattr(main, 'get_catalog', lambda *a, **kw: ([], []))
    with pytest.raises(Exception, match='NoSuchBucket'):
        main.lambda_handler({'days_back': 1}, None)


def test_official_report_peak_limit_is_historical_not_current(aws_db, monkeypatch):
    from modules.qmcore.model import iso
    import modules.qmcore.reporting as reporting
    from test_metrics import quota
    session, db = aws_db
    ctx = CheckContext(session, account='a', now=NOW)
    at = NOW-timedelta(minutes=10)
    q = quota('q')
    stored = measurement('a', 'eu-central-1', 'ec2', 'q', 'quota', 80, 70,
                         now=at, source='official_metric')
    stored['peakAt'] = iso(at)
    db.put_quota_entry(stored)
    queried = dict(stored, limitValue=100, usageValue=70, peakAt=iso(at), sampleCount=4, aggregationSeconds=300)
    monkeypatch.setattr(reporting, 'fetch_metrics', lambda *a, **kw: [queried])
    rows, errors = build_report(ctx, db, [q], NOW-timedelta(days=1), NOW)
    assert not errors and rows[0]['currentLimit'] == 100 and rows[0]['limitAtPeak'] == 80
    queried['peakAt'] = iso(at-timedelta(minutes=5))
    rows, errors = build_report(ctx, db, [q], NOW-timedelta(days=1), NOW)
    assert rows[0]['limitAtPeak'] is None


def test_history_failure_does_not_discard_good_official_metric(aws_db, monkeypatch):
    import modules.qmcore.reporting as reporting
    from test_metrics import quota
    ctx = CheckContext(aws_db[0], account='a', now=NOW)
    db = Mock()
    db.table.scan.side_effect = RuntimeError('AccessDenied')
    queried = measurement('a', 'eu-central-1', 'ec2', 'q', 'quota', 100, 90, now=NOW, source='official_metric')
    monkeypatch.setattr(reporting, 'fetch_metrics', lambda *a, **kw: [queried])
    rows, errors = build_report(ctx, db, [quota('q')], NOW-timedelta(days=1), NOW)
    assert errors and rows[0]['maxUsage'] == 90 and rows[0]['qualityStatus'] == 'OK'


def test_report_queries_documented_metric_missing_from_catalog_metadata(aws_db, monkeypatch):
    import modules.qmcore.reporting as reporting
    ctx = CheckContext(aws_db[0], account='a', now=NOW)
    quota = {'ServiceCode': 'states', 'QuotaCode': 'L-15D902EC',
             'QuotaName': 'Open Map Runs', 'Unit': 'None', 'Value': 1000,
             'QuotaAppliedAtLevel': 'ACCOUNT'}
    selected = []
    def fetch(_ctx, quotas, *_args, **_kwargs):
        selected.extend(quotas)
        return []
    monkeypatch.setattr(reporting, 'fetch_metrics', fetch)
    build_report(ctx, aws_db[1], [quota], NOW - timedelta(days=1), NOW)
    assert [(q['ServiceCode'], q['QuotaCode']) for q in selected] == [('states', 'L-15D902EC')]
