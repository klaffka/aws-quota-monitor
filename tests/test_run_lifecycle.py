from datetime import datetime, timedelta, UTC
from unittest.mock import Mock
import json

import pytest

from modules.qmcore.runs import RunBusy, RunLease, run_window
from modules.qmcore.catalog import get_catalog
from modules.qmcore.aws import CheckContext, NoData
from modules.qmchecks.bedrock import _max_nested
from test_catalog_collector import collector_setup
from test_metrics import quota
from modules.qmcore.model import measurement

NOW = datetime(2026, 9, 25, 12, tzinfo=UTC)


def test_scheduled_window_is_stable_across_retry_and_delivery_id():
    event = {'source': 'aws.events', 'time': '2026-09-25T10:00:00Z', 'id': 'first'}
    first = run_window(event, NOW)
    assert first == run_window({**event, 'id': 'duplicate'}, NOW + timedelta(hours=1))
    assert first[2] - first[1] == timedelta(days=1)


@pytest.mark.parametrize('event', [
    {'source': 'aws.events'}, {'runId': 'manual'},
    {'time': '2026-09-25T10:00:00'}, {'time': '2026-09-25T14:00:00Z'},
    {'time': '2026-08-01T10:00:00Z'},
])
def test_invalid_run_time_rejected(event):
    with pytest.raises(ValueError):
        run_window(event, NOW)


def test_lease_excludes_overlap_retries_failure_and_suppresses_completion(aws_db):
    db = aws_db[1]
    first = RunLease(db, 'a', 'eu-central-1', 'id', clock=lambda: NOW)
    other = RunLease(db, 'a', 'eu-central-1', 'id', clock=lambda: NOW)
    assert first.acquire()
    with pytest.raises(RunBusy):
        other.acquire()
    first.finish(False)
    assert other.acquire()
    other.finish(True)
    assert not first.acquire()


def test_expired_owner_cannot_complete_reclaimed_lease(aws_db):
    first = RunLease(aws_db[1], 'a', 'r', 'id', clock=lambda: NOW)
    other = RunLease(aws_db[1], 'a', 'r', 'id', clock=lambda: NOW + timedelta(minutes=17))
    assert first.acquire() and other.acquire()
    with pytest.raises(Exception, match='ConditionalCheckFailed'):
        first.finish(True)
    other.finish(True)


def test_catalog_roundtrip_preserves_account_and_multiple_resource_contexts(aws_db, monkeypatch):
    items = [quota('same')]
    for resource in ['one', 'two']:
        items.append({**quota('same'), 'QuotaAppliedAtLevel': 'RESOURCE',
                      'QuotaContext': {'ContextId': resource}})
    fetch = Mock(return_value=(items, []))
    monkeypatch.setattr('modules.qmcore.catalog.fetch_catalog', fetch)
    ctx = CheckContext(aws_db[0], account='a', now=NOW)
    get_catalog(ctx, aws_db[1])
    loaded, errors = get_catalog(ctx, aws_db[1])
    assert not errors and len(loaded) == 3
    assert {q['catalogContextId'] for q in loaded} == {None, 'one', 'two'}
    assert fetch.call_count == 1


def test_incomplete_parent_inventory_is_not_zero():
    with pytest.raises(NoData, match='without id'):
        _max_nested(Mock(), lambda ctx: [{}], 'id', 'list_children', 'items')


def test_completed_scheduled_delivery_does_not_collect_twice(aws_db, monkeypatch):
    main = collector_setup(aws_db, monkeypatch, [], [quota()])
    metric = measurement('a', 'eu-central-1', 'ec2', 'q', 'quota', 100, 1)
    fetch = Mock(return_value=[metric])
    monkeypatch.setattr(main, 'fetch_metrics', fetch)
    monkeypatch.setattr(main, 'QuotaAlert', lambda *a, **k: Mock())
    event = {'source': 'aws.events', 'time': datetime.now(UTC).isoformat(), 'validation': True}
    assert main.lambda_handler(event, None)['statusCode'] == 200
    assert json.loads(main.lambda_handler(event, None)['body'])['duplicate']
    assert fetch.call_count == 1


def test_retry_uses_fixed_window_and_same_measurement_key(aws_db, monkeypatch):
    main = collector_setup(aws_db, monkeypatch, [], [quota()])
    end = datetime.now(UTC).replace(microsecond=0) - timedelta(hours=1)
    event = {'source': 'aws.events', 'time': end.isoformat(), 'validation': True}
    good = measurement('a', 'eu-central-1', 'ec2', 'q', 'quota', 100, 1)
    # Only catalog and storage failures are retried; check errors complete the run.
    monkeypatch.setattr(main, 'get_catalog', Mock(side_effect=[RuntimeError('throttled'), ([quota()], [])]))
    fetch = Mock(side_effect=[[good], [good]])
    monkeypatch.setattr(main, 'fetch_metrics', fetch)
    with pytest.raises(RuntimeError, match='Collector incomplete'):
        main.lambda_handler(event, None)
    main.lambda_handler(event, None)
    assert all(call.args[2:] == (end - timedelta(days=1), end) for call in fetch.call_args_list)
    stored = [q for q in aws_db[1].table.scan()['Items'] if q['PK'].startswith('QUOTA#')]
    assert len(stored) == 1 and stored[0]['qualityStatus'] == 'OK'


def _items(db, prefix):
    return [item for item in db.table.scan()['Items'] if item['PK'].startswith(prefix)]


def _heartbeats(session):
    return session.client('cloudwatch').list_metrics(Namespace='QuotaMonitor')['Metrics']


def test_check_errors_complete_the_run_without_retry_or_heartbeat(aws_db, monkeypatch):
    session, db = aws_db
    bad = measurement('a', 'eu-central-1', 'ec2', 'bad', 'bad', now=NOW, status='ERROR', reason='AccessDenied')
    main = collector_setup(aws_db, monkeypatch, [bad], [quota()])
    monkeypatch.setattr(main, 'fetch_metrics', lambda *a, **k: [])
    result = main.lambda_handler({}, None)
    assert result['statusCode'] == 200 and json.loads(result['body'])['errors'] == 1
    run, = _items(db, 'RUN#')
    assert run['qualityStatus'] == 'ERROR'
    assert _items(db, 'EXECUTION#')[0]['state'] == 'COMPLETE'
    assert not _heartbeats(session)


def test_overlapping_delivery_is_a_no_op(aws_db, monkeypatch):
    session, db = aws_db
    main = collector_setup(aws_db, monkeypatch, [], [quota()])
    collect = Mock()
    monkeypatch.setattr(main, 'collect', collect)
    event = {'source': 'aws.events', 'time': '2026-09-25T10:00:00Z'}
    run_id = run_window(event, datetime.now(UTC))[0]
    account = session.client('sts').get_caller_identity()['Account']
    assert RunLease(db, account, 'eu-central-1', run_id).acquire()
    result = main.lambda_handler(event, None)
    assert json.loads(result['body']) == {'runId': run_id, 'busy': True}
    collect.assert_not_called()


def test_lease_bookkeeping_failure_keeps_the_run_outcome(aws_db, monkeypatch):
    main = collector_setup(aws_db, monkeypatch, [], [quota()])
    monkeypatch.setattr(main, 'fetch_metrics', lambda *a, **k: [])
    monkeypatch.setattr(main.RunLease, 'finish', Mock(side_effect=RuntimeError('lease lost')))
    assert main.lambda_handler({}, None)['statusCode'] == 200
    monkeypatch.setattr(main, 'collect', Mock(side_effect=ValueError('original')))
    with pytest.raises(ValueError, match='original'):
        main.lambda_handler({}, None)


def test_stale_replay_stores_without_alerts_or_heartbeat(aws_db, monkeypatch):
    session, db = aws_db
    metric = measurement('a', 'eu-central-1', 'ec2', 'q', 'quota', 100, 95, now=NOW, source='official_metric')
    main = collector_setup(aws_db, monkeypatch, [], [quota()])
    monkeypatch.setattr(main, 'fetch_metrics', lambda *a, **k: [metric])
    alerts = Mock()
    monkeypatch.setattr(main, 'QuotaAlert', lambda *a, **kw: alerts)
    stale = (datetime.now(UTC) - timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%SZ')
    assert main.lambda_handler({'time': stale}, None)['statusCode'] == 200
    alerts.check_and_alert.assert_not_called()
    assert _items(db, 'RUN#')[0]['alertsEnabled'] is False
    assert not _heartbeats(session)


def test_history_ignores_inventory_observed_outside_the_window():
    from modules.qmcore.reporting import aggregate_history
    start, end = NOW - timedelta(days=1), NOW
    late = measurement('a', 'eu-central-1', 'ec2', 'late', 'late', 10, 5, now=NOW + timedelta(days=2))
    inside = measurement('a', 'eu-central-1', 'ec2', 'in', 'in', 10, 5, now=NOW - timedelta(hours=1))
    metric = measurement('a', 'eu-central-1', 'ec2', 'metric', 'metric', 10, 5,
                         now=NOW + timedelta(days=2), source='official_metric')
    groups = aggregate_history([late, inside, metric], start, end)
    assert {key[3] for key in groups} == {'in', 'metric'}
