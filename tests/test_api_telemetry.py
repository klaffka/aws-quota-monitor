from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmcore.aws import CheckContext
from modules.qmcore.telemetry import ApiTelemetry


def test_counts_paginated_requests_but_not_cache_hits():
    session = boto3.Session(region_name='eu-central-1')
    telemetry = ApiTelemetry(session)
    ctx = CheckContext(session, account='a')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_vpcs', {'Vpcs': [], 'NextToken': 'next'})
        stub.add_response('describe_vpcs', {'Vpcs': []})
        assert ctx.call('ec2', 'describe_vpcs', 'Vpcs') == []
        assert ctx.call('ec2', 'describe_vpcs', 'Vpcs') == []
    stats = telemetry.snapshot()['ec2']
    assert stats['calls'] == 2 and stats['errors'] == 0
    assert stats['apiSeconds'] >= 0


def test_errors_and_regional_clients_are_counted():
    session = boto3.Session(region_name='eu-central-1')
    telemetry = ApiTelemetry(session)
    ctx = CheckContext(session, account='a').in_region('us-east-1')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_client_error('describe_vpcs', service_error_code='AccessDenied')
        with pytest.raises(Exception, match='AccessDenied'):
            ctx.call('ec2', 'describe_vpcs', 'Vpcs')
    assert telemetry.snapshot()['ec2']['errors'] == 1


def test_transport_failure_and_retry_metadata():
    telemetry = ApiTelemetry(Mock())
    model = Mock()
    model.service_model.service_name = 'ec2'
    context = {}
    telemetry.before(model, context)
    telemetry.failed(context)
    telemetry.before(model, context)
    telemetry.after(context, Mock(status_code=200), {'ResponseMetadata': {'RetryAttempts': 2}})
    assert telemetry.snapshot()['ec2']['calls'] == 2
    assert telemetry.snapshot()['ec2']['retries'] == 2
    assert telemetry.snapshot()['ec2']['errors'] == 1
