from unittest.mock import Mock

import pytest

from modules.qmchecks.mq import CHECKS as MQ_CHECKS, configuration_revisions
from modules.qmchecks.directoryservice import CHECKS as DS_CHECKS
from modules.qmchecks.opensearch import application_count, get_current_quotastatus_opensearch
from modules.qmcore.aws import NoData
from modules.qmcore.registry import custom_keys
from tests.iam_policy import granted_prefixes, grants


def test_mq_broker_inventory_count():
    ctx = Mock()
    ctx.call.return_value = [{'BrokerId': 'b1'}, {'BrokerId': 'b2'}]
    assert MQ_CHECKS[0][2](ctx)['usage'] == 2
    assert ctx.call.call_args.args[1] == 'list_brokers'


def test_mq_configuration_revisions_use_maximum_per_configuration():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'Id': 'one'}, {'Id': 'two'}],
        [{'Id': 'r1'}, {'Id': 'r2'}],
        [{'Id': 'r1'}],
    ]
    assert configuration_revisions(ctx)['usage'] == 2


def test_directory_service_counts_types():
    ctx = Mock()
    ctx.call.return_value = [
        {'Type': 'MicrosoftAD'}, {'Type': 'MicrosoftAD'}, {'Type': 'ADConnector'},
    ]
    assert DS_CHECKS[0][2](ctx)['usage'] == 2
    assert DS_CHECKS[1][2](ctx)['usage'] == 1


def test_opensearch_and_applications_are_independent_services():
    ctx = Mock(quotas={('es', 'L-076D529E'): {'Value': 100, 'Unit': 'None'},
                       ('es', 'L-AE676A72'): {'Value': 5, 'Unit': 'None'},
                       ('opensearch', 'L-B9142967'): {'Value': 30, 'Unit': 'None'}})
    def call(service, method, key=None, **kwargs):
        # The domain describe is fetched whole, so it answers with its response.
        if method == 'describe_elasticsearch_domains':
            return {'DomainStatusList': [
                {'DomainName': 'domain',
                 'ElasticsearchClusterConfig': {'DedicatedMasterCount': 3}}]}
        return ([{'DomainName': 'domain'}] if service == 'es' else
                [{'id': 'app', 'arn': 'arn:aws:opensearch:eu-central-1:123:application/app',
                  'status': 'ACTIVE'}])
    ctx.call.side_effect = call
    ctx.run.side_effect = lambda service, checks, skip: [
        {'serviceCode': service, 'quotaCode': code,
         'usageValue': fn(ctx)['usage']} for code, _, fn in checks]
    entries = get_current_quotastatus_opensearch(ctx=ctx)
    assert {(e['serviceCode'], e['quotaCode'], e['usageValue']) for e in entries} == {
        ('es', 'L-076D529E', 1), ('es', 'L-AE676A72', 3),
        ('opensearch', 'L-B9142967', 1),
    }


def test_opensearch_application_inventory_deduplicates_identical_pages():
    app = {'id': 'app', 'arn': 'arn:aws:opensearch:eu-central-1:123:application/app',
           'status': 'DELETING'}
    ctx = Mock()
    ctx.call.return_value = [app, dict(app)]
    assert application_count(ctx)['usage'] == 1


@pytest.mark.parametrize('items,match', [
    ([{'id': 'app', 'arn': 'arn:app', 'status': 'UNKNOWN'}], 'missing required'),
    ([{'id': 'app', 'arn': 'arn:app', 'status': 'ACTIVE'},
      {'id': 'app', 'arn': 'arn:app', 'status': 'FAILED'}], 'changed during pagination'),
    ([{'id': 'one', 'arn': 'arn:app', 'status': 'ACTIVE'},
      {'id': 'two', 'arn': 'arn:app', 'status': 'ACTIVE'}], 'duplicate ARN'),
])
def test_opensearch_application_inventory_rejects_incomplete_or_conflicting_items(items, match):
    ctx = Mock()
    ctx.call.return_value = items
    with pytest.raises(NoData, match=match):
        application_count(ctx)


def test_opensearch_checks_are_registered_with_the_iam_service_prefix():
    assert {('es', 'L-076D529E'), ('opensearch', 'L-B9142967')} <= custom_keys()
    assert grants('es:ListApplications')
    # OpenSearch authorises under `es`. A grant written for the SDK's client
    # name would authorise nothing, so the prefix must not appear at all --
    # asking whether one action is missing no longer works now that the policy
    # grants a service's read verbs with a wildcard.
    assert 'opensearch' not in granted_prefixes()
