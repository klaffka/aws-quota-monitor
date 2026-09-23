"""DMS serverless, subnet-group and data-migration scopes."""
from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import dms_resources as dms
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 15, tzinfo=UTC)


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'dms', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _name, fn in dms.CHECKS if quota == code)


MIGRATIONS = {'DataMigrations': [
    {'DataMigrationName': 'running', 'MigrationProjectArn': 'arn:project/a',
     'DataMigrationStartTime': MOMENT},
    {'DataMigrationName': 'finished', 'MigrationProjectArn': 'arn:project/a',
     'DataMigrationStartTime': MOMENT, 'DataMigrationEndTime': MOMENT},
    {'DataMigrationName': 'never-started', 'MigrationProjectArn': 'arn:project/a'},
    {'DataMigrationName': 'other', 'MigrationProjectArn': 'arn:project/b',
     'DataMigrationStartTime': MOMENT}]}


def test_only_started_and_unfinished_migrations_count_as_running():
    """The status field carries no documented values, so the timestamps decide."""
    ctx = context('L-FBEA20FB')
    with Stubber(ctx.client('dms')) as stub:
        stub.add_response('describe_data_migrations', MIGRATIONS, {})
        assert check('L-FBEA20FB')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_migrations_use_the_busiest_migration_project():
    ctx = context('L-62EFB27A')
    with Stubber(ctx.client('dms')) as stub:
        stub.add_response('describe_data_migrations', MIGRATIONS, {})
        result = check('L-62EFB27A')(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'arn:project/a')
        stub.assert_no_pending_responses()


def test_a_migration_without_a_project_is_reported_as_no_data():
    from unittest.mock import Mock

    ctx = Mock()
    ctx.call.return_value = [{'DataMigrationName': 'orphan'}]
    with pytest.raises(NoData, match='names no migration project'):
        check('L-62EFB27A')(ctx)


def test_subnets_use_the_largest_subnet_group():
    ctx = context('L-4182EDE9')
    with Stubber(ctx.client('dms')) as stub:
        stub.add_response('describe_replication_subnet_groups', {'ReplicationSubnetGroups': [
            {'ReplicationSubnetGroupIdentifier': 'small',
             'Subnets': [{'SubnetIdentifier': 'subnet-1'}]},
            {'ReplicationSubnetGroupIdentifier': 'large',
             'Subnets': [{'SubnetIdentifier': 'subnet-2'},
                         {'SubnetIdentifier': 'subnet-3'}]}]}, {})
        result = check('L-4182EDE9')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'large')
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('code, operation, key, item', [
    ('L-D97343A2', 'describe_event_subscriptions', 'EventSubscriptionsList',
     {'CustSubscriptionId': 'one'}),
    ('L-E569F59D', 'describe_replications', 'Replications',
     {'ReplicationConfigIdentifier': 'one'}),
    ('L-8D962DAE', 'describe_fleet_advisor_collectors', 'Collectors',
     {'CollectorReferencedId': 'one'}),
])
def test_account_totals_read_their_documented_response_key(code, operation, key, item):
    ctx = context(code)
    with Stubber(ctx.client('dms')) as stub:
        stub.add_response(operation, {key: [item, dict(item)]}, {})
        assert check(code)(ctx)['usage'] == 2
        stub.assert_no_pending_responses()
