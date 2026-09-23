import importlib
from datetime import datetime, timedelta, UTC
from unittest.mock import Mock
import pytest
from modules.qmcore.aws import CheckContext
from modules.qmcore.catalog import get_catalog
from modules.qmcore.model import measurement
from test_metrics import quota

NOW = datetime(2026, 3, 1, tzinfo=UTC)


def test_catalog_cache_daily_expiry_and_namespace(aws_db, monkeypatch):
    session, db = aws_db
    import modules.qmcore.catalog as catalog
    fetch = Mock(return_value=([quota()], []))
    monkeypatch.setattr(catalog, 'fetch_catalog', fetch)
    ctx = CheckContext(session, account='a', now=NOW)
    assert get_catalog(ctx, db)[0][0]['QuotaCode'] == 'q'
    assert get_catalog(ctx, db)[0][0]['QuotaCode'] == 'q'
    assert fetch.call_count == 1
    ctx.now += timedelta(days=1)
    get_catalog(ctx, db)
    assert fetch.call_count == 2
    ctx.account = 'b'
    get_catalog(ctx, db)
    assert fetch.call_count == 3
    assert all(i['PK'].startswith('CATALOG#') for i in db.table.scan()['Items'])
    assert db.table.name == 'test-quota-table' and db.dynamodb.meta.client.meta.region_name == 'eu-central-1'


def test_incomplete_catalog_does_not_replace_snapshot(aws_db, monkeypatch):
    import modules.qmcore.catalog as catalog
    session, db = aws_db
    ctx = CheckContext(session, account='a', now=NOW)
    monkeypatch.setattr(catalog, 'fetch_catalog', lambda c: ([quota()], []))
    get_catalog(ctx, db)
    original = db.get_quota_entry('CATALOG#a#eu-central-1', 'LATEST')
    monkeypatch.setattr(catalog, 'fetch_catalog', lambda c: ([], ['Throttling']))
    _, errors = get_catalog(ctx, db, force=True)
    assert errors
    assert db.get_quota_entry('CATALOG#a#eu-central-1', 'LATEST') == original


def test_legacy_or_malformed_pointer_refreshes_catalog(aws_db, monkeypatch):
    import modules.qmcore.catalog as catalog
    session, db = aws_db
    ctx = CheckContext(session, account='a', now=NOW)
    db.put_quota_entry({'PK': 'CATALOG#a#eu-central-1', 'SK': 'LATEST',
                        'generation': 'old', 'count': 1, 'refreshedAt': int(NOW.timestamp())})
    fetch = Mock(return_value=([quota('refreshed')], []))
    monkeypatch.setattr(catalog, 'fetch_catalog', fetch)
    result, errors = get_catalog(ctx, db)
    assert not errors and result[0]['QuotaCode'] == 'refreshed'
    assert fetch.call_count == 1


def test_partial_cached_generation_refreshes_instead_of_returning_partial(aws_db, monkeypatch):
    import modules.qmcore.catalog as catalog
    session, db = aws_db
    ctx = CheckContext(session, account='a', now=NOW)
    monkeypatch.setattr(catalog, 'fetch_catalog', lambda c: ([quota('complete')], []))
    get_catalog(ctx, db)
    pointer = db.get_quota_entry('CATALOG#a#eu-central-1', 'LATEST')
    db.table.delete_item(Key={'PK': 'CATALOG#a#eu-central-1',
                              'SK': f"{pointer['generation']}#ec2#complete"})
    fetch = Mock(return_value=([quota('rebuilt')], []))
    monkeypatch.setattr(catalog, 'fetch_catalog', fetch)
    result, errors = get_catalog(ctx, db)
    assert not errors and result[0]['QuotaCode'] == 'rebuilt'
    assert fetch.call_count == 1


def collector_setup(aws_db, monkeypatch, entries, metric_quotas=()):
    main = importlib.import_module('functions.quota-collector.main')
    session, _db = aws_db
    monkeypatch.setattr(main, 'session_from_env', lambda: session)
    monkeypatch.setattr(main, 'get_catalog', lambda *a: (list(metric_quotas), []))
    monkeypatch.setattr(main, 'get_current_quotastatus_ec2', lambda **kw: entries)
    monkeypatch.setattr(main, 'get_current_quotastatus_vpc', lambda **kw: [])
    monkeypatch.setattr(main, 'get_current_quotastatus_lambda', lambda **kw: [])
    monkeypatch.setattr(main, 'get_current_quotastatus_account_services', lambda *a, **kw: [])
    monkeypatch.setattr(main, 'get_current_quotastatus_elb', lambda *a, **kw: [])
    return main


def test_collector_saves_successes_and_errors_then_raises(aws_db, monkeypatch):
    good = measurement('a','eu-central-1','ec2','good','good',10,8,now=NOW)
    bad = measurement('a','eu-central-1','ec2','bad','bad',now=NOW,status='ERROR',reason='AccessDenied')
    main = collector_setup(aws_db, monkeypatch, [good, bad])
    with pytest.raises(RuntimeError, match='successful measurements saved'):
        main.lambda_handler({}, None)
    items = aws_db[1].table.scan()['Items']
    assert {i['qualityStatus'] for i in items if i['PK'].startswith('QUOTA#')} == {'OK', 'ERROR'}


def test_compatible_metric_skips_resource_check_and_alerts_once(aws_db, monkeypatch):
    main = collector_setup(aws_db, monkeypatch, [], [quota('shared')])
    custom = Mock(return_value=[])
    monkeypatch.setattr(main, 'get_current_quotastatus_ec2', custom)
    metric = measurement('a','eu-central-1','ec2','shared','shared',100,90,now=NOW,source='official_metric')
    monkeypatch.setattr(main, 'fetch_metrics', lambda *a, **k: [metric])
    alerts = Mock()
    monkeypatch.setattr(main, 'QuotaAlert', lambda *a, **kw: alerts)
    result = main.lambda_handler({}, None)
    assert result['statusCode'] == 200
    assert custom.call_args.kwargs['skip'] == {('ec2','shared')}
    alerts.check_and_alert.assert_called_once_with(metric)


def test_compatible_metric_remains_selected_when_resource_registry_has_same_key(aws_db, monkeypatch):
    main = collector_setup(aws_db, monkeypatch, [], [quota('shared')])
    custom = Mock(return_value=[])
    monkeypatch.setattr(main, 'get_current_quotastatus_ec2', custom)
    metric = measurement('a', 'eu-central-1', 'ec2', 'shared', 'shared', 100, 90,
                         now=NOW, source='official_metric')
    selected = {}
    def fetch(_ctx, quotas, *_args, **_kwargs):
        selected['keys'] = {(q['ServiceCode'], q['QuotaCode']) for q in quotas}
        return [metric]
    monkeypatch.setattr(main, 'fetch_metrics', fetch)
    monkeypatch.setattr(main, 'QuotaAlert', lambda *a, **kw: Mock())
    main.lambda_handler({}, None)
    assert selected['keys'] == {('ec2', 'shared')}
    assert custom.call_args.kwargs['skip'] == {('ec2', 'shared')}


def test_documented_metric_missing_from_catalog_metadata_is_collected(aws_db, monkeypatch):
    q = {'ServiceCode': 'states', 'QuotaCode': 'L-B8A5B662', 'QuotaName': 'Open executions',
         'Unit': 'None', 'Value': 1000000, 'QuotaAppliedAtLevel': 'ACCOUNT'}
    main = collector_setup(aws_db, monkeypatch, [], [q])
    selected = {}
    metric = measurement('a', 'eu-central-1', 'states', 'L-B8A5B662', 'Open executions',
                         1000000, 100, now=NOW, source='official_metric')
    def fetch(_ctx, quotas, *_args, **_kwargs):
        selected['keys'] = {(quota['ServiceCode'], quota['QuotaCode']) for quota in quotas}
        return [metric]
    monkeypatch.setattr(main, 'fetch_metrics', fetch)
    monkeypatch.setattr(main, 'QuotaAlert', lambda *a, **kw: Mock())
    main.lambda_handler({}, None)
    assert selected['keys'] == {('states', 'L-B8A5B662')}


def test_catalog_keeps_only_complete_services_with_paginated_discovery(monkeypatch):
    from modules.qmcore.catalog import fetch_catalog
    client = Mock()
    client.can_paginate.return_value = True
    services, quotas = Mock(), Mock()
    client.get_paginator.side_effect = [services, quotas, quotas]
    services.paginate.return_value = [{'Services': [{'ServiceCode': 'ec2'}]}, {'Services': [{'ServiceCode': 'lambda'}]}]
    quotas.paginate.side_effect = [[{'Quotas': [quota()]}], RuntimeError('AccessDenied')]
    result, errors = fetch_catalog(client)
    assert len(result) == 1 and len(errors) == 1 and 'lambda' in errors[0]


def test_dynamodb_honors_nondefault_session_region(monkeypatch):
    from modules.qmdb.db import QuotaLogDb
    session = Mock(region_name='us-west-2')
    QuotaLogDb(session)
    assert session.resource.call_args.kwargs['region_name'] == 'us-west-2'
    assert session.resource.return_value.Table.call_args.args == ('qm-quotalog',)


def test_incomplete_catalog_does_not_transition_alert_state(aws_db, monkeypatch):
    main = collector_setup(aws_db, monkeypatch, [], [quota('partial')])
    alerts = Mock()
    monkeypatch.setattr(main, 'QuotaAlert', lambda *a, **kw: alerts)
    monkeypatch.setattr(main, 'get_catalog', lambda *a, **kw: ([quota('partial')], ['AccessDenied for service']))
    metric = measurement('a', 'eu-central-1', 'ec2', 'partial', 'partial', 100, 95,
                         now=NOW, source='official_metric')
    monkeypatch.setattr(main, 'fetch_metrics', lambda *a, **k: [metric])
    with pytest.raises(RuntimeError, match='Collector incomplete'):
        main.lambda_handler({}, None)
    alerts.check_and_alert.assert_not_called()


def test_empty_catalog_is_operational_failure(aws_db, monkeypatch):
    main = collector_setup(aws_db, monkeypatch, [], [])
    alerts = Mock()
    monkeypatch.setattr(main, 'QuotaAlert', lambda *a, **kw: alerts)
    monkeypatch.setattr(main, 'get_catalog', lambda *a, **kw: ([], []))
    with pytest.raises(RuntimeError, match='Collector incomplete'):
        main.lambda_handler({}, None)
    alerts.check_and_alert.assert_not_called()
