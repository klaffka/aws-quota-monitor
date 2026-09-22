from datetime import datetime, UTC
from unittest.mock import Mock

import pytest

from modules.qmcore.utilization import ReportPending, read_report


NOW = datetime(2026, 9, 11, tzinfo=UTC)


def page(records=(), **fields):
    return {'ReportId': 'report-one', 'Status': 'COMPLETED', 'GeneratedAt': NOW,
            'TotalCount': 2, 'Quotas': list(records), **fields}


def test_complete_report_follows_pages_and_retains_report_identity():
    client = Mock()
    client.get_quota_utilization_report.side_effect = [
        page([{'ServiceCode': 'ec2', 'QuotaCode': 'one', 'Utilization': 101}], NextToken='next'),
        page([{'ServiceCode': 'eks', 'QuotaCode': 'two', 'Utilization': 0}])]
    report = read_report(client, 'report-one')
    assert report['TotalCount'] == len(report['Quotas']) == 2
    assert client.get_quota_utilization_report.call_args.kwargs == {
        'ReportId': 'report-one', 'NextToken': 'next', 'MaxResults': 1000}
    client.start_quota_utilization_report.assert_not_called()


@pytest.mark.parametrize('status', ['PENDING', 'IN_PROGRESS'])
def test_pending_report_requires_repolling_same_identity(status):
    client = Mock()
    client.get_quota_utilization_report.return_value = {'ReportId': 'report-one', 'Status': status}
    with pytest.raises(ReportPending):
        read_report(client, 'report-one')
    client.start_quota_utilization_report.assert_not_called()


@pytest.mark.parametrize('pages', [
    [page([{}])],
    [page([{}], NextToken='next'), page([{}], NextToken='next')],
    [page([{}], NextToken='next'), page([{}], ReportId='report-two')],
    [page([{}], NextToken='next'), page([{}], TotalCount=3)],
    [page([{}], NextToken='next'), page([{}], GeneratedAt=NOW.replace(hour=1))],
    [page([{}, {}], ErrorCode='PARTIAL')],
    [page([{}, {}], Status='FAILED')],
    [page([{}, {}], GeneratedAt=None)],
    [page([{}, {}], TotalCount=True)],
    [page([{}, {}], Quotas=None)],
])
def test_partial_inconsistent_and_failed_reports_are_never_returned(pages):
    client = Mock()
    client.get_quota_utilization_report.side_effect = pages
    with pytest.raises(RuntimeError):
        read_report(client, 'report-one')
