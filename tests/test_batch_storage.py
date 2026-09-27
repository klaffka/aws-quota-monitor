from unittest.mock import Mock

from modules.qmdb.db import QuotaLogDb


def entry(index):
    return {'PK': f'QUOTA#{index}', 'SK': 'TS#now', 'usageValue': 1.5}


def test_batches_persist_all_items_with_real_resource_serialization(aws_db):
    _, db = aws_db
    entries = [entry(i) for i in range(51)]
    outcomes = list(db.put_quota_entries(entries))
    assert outcomes == [(item, None) for item in entries]
    assert db.table.scan()['Count'] == 51


def fake_db():
    db = QuotaLogDb.__new__(QuotaLogDb)
    db.table = Mock()
    db.table.name = 'quota-table'
    return db


def test_retry_only_unprocessed_and_confirm_success_before_retry(monkeypatch):
    monkeypatch.setattr('modules.qmdb.db.time.sleep', lambda _: None)
    db = fake_db()
    first, second = entry(1), entry(2)
    db.table.meta.client.batch_write_item.side_effect = [
        {'UnprocessedItems': {'quota-table': [{'PutRequest': {'Item': second}}]}},
        {},
    ]
    results = db.put_quota_entries([first, second])
    assert next(results) == (first, None)
    assert db.table.meta.client.batch_write_item.call_count == 1
    assert list(results) == [(second, None)]
    retried = db.table.meta.client.batch_write_item.call_args.kwargs['RequestItems']['quota-table']
    assert len(retried) == 1 and retried[0]['PutRequest']['Item']['PK'] == second['PK']


def test_unprocessed_retries_are_bounded(monkeypatch):
    monkeypatch.setattr('modules.qmdb.db.time.sleep', lambda _: None)
    db = fake_db()
    item = entry(1)
    db.table.meta.client.batch_write_item.return_value = {
        'UnprocessedItems': {'quota-table': [{'PutRequest': {'Item': item}}]}}
    outcomes = list(db.put_quota_entries([item]))
    assert db.table.meta.client.batch_write_item.call_count == 5
    assert outcomes[0][0] == item and 'unprocessed' in outcomes[0][1]


def test_batch_failure_does_not_stop_later_batches():
    db = fake_db()
    db.table.meta.client.batch_write_item.side_effect = [RuntimeError('denied'), {}]
    outcomes = list(db.put_quota_entries([entry(i) for i in range(26)]))
    assert all(error == 'denied' for _, error in outcomes[:25])
    assert outcomes[-1] == (entry(25), None)


def test_duplicate_keys_are_not_sent_in_same_batch():
    db = fake_db()
    db.table.meta.client.batch_write_item.return_value = {}
    assert list(db.put_quota_entries([entry(1), entry(1)])) == [(entry(1), None)] * 2
    assert db.table.meta.client.batch_write_item.call_count == 2
