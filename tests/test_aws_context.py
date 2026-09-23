from datetime import UTC


def test_the_call_cache_accepts_datetime_arguments():
    """Several APIs take a time window, which the cache key must survive."""
    from datetime import datetime

    import boto3
    from botocore.stub import Stubber

    from modules.qmcore.aws import CheckContext

    moment = datetime(2026, 9, 15, tzinfo=UTC)
    ctx = CheckContext(boto3.Session(region_name='eu-central-1'),
                       account='123456789012', now=moment)
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_audit_tasks', {'tasks': [{'taskId': 't1'}]},
                          {'startTime': moment, 'endTime': moment})
        first = ctx.call('iot', 'list_audit_tasks', 'tasks',
                         startTime=moment, endTime=moment)
        # The second call is served from the cache, so the stub sees one request.
        second = ctx.call('iot', 'list_audit_tasks', 'tasks',
                          startTime=moment, endTime=moment)
        assert first == second == [{'taskId': 't1'}]
        stub.assert_no_pending_responses()


def test_paginate_follows_the_service_catalog_page_token():
    """NextPageToken comes back as PageToken; a missed page undercounts silently."""
    from unittest.mock import Mock

    from modules.qmcore.aws import paginate

    client = Mock()
    client.can_paginate.return_value = False
    client.list_portfolio_access.side_effect = [
        {'AccountIds': ['111111111111'], 'NextPageToken': 'next'},
        {'AccountIds': ['222222222222']},
    ]
    assert paginate(client, 'list_portfolio_access', 'AccountIds',
                    PortfolioId='port-1') == ['111111111111', '222222222222']
    assert client.list_portfolio_access.call_args.kwargs == {
        'PortfolioId': 'port-1', 'PageToken': 'next'}


def test_paginate_follows_the_lightsail_next_page_token():
    """Lightsail spells the cursor nextPageToken; page two was dropped silently."""
    from unittest.mock import Mock

    from modules.qmcore.aws import paginate

    client = Mock()
    client.can_paginate.return_value = False
    client.get_distributions.side_effect = [
        {'distributions': [{'name': 'one'}], 'nextPageToken': 'next'},
        {'distributions': [{'name': 'two'}]},
    ]
    assert paginate(client, 'get_distributions', 'distributions') == [
        {'name': 'one'}, {'name': 'two'}]
    assert client.get_distributions.call_args.kwargs == {'pageToken': 'next'}
