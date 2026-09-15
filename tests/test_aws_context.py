

def test_the_call_cache_accepts_datetime_arguments():
    """Several APIs take a time window, which the cache key must survive."""
    from datetime import datetime, timezone

    import boto3
    from botocore.stub import Stubber

    from modules.qmcore.aws import CheckContext

    moment = datetime(2026, 9, 15, tzinfo=timezone.utc)
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
