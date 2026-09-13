from unittest.mock import Mock

from modules.qmchecks.mq import CHECKS as MQ_CHECKS, configuration_revisions
from modules.qmchecks.directoryservice import CHECKS as DS_CHECKS
from modules.qmchecks.opensearch import get_current_quotastatus_opensearch


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
                       ('opensearch', 'L-B9142967'): {'Value': 30, 'Unit': 'None'}})
    def call(service, method, key=None, **kwargs):
        return [{'DomainName': 'domain'}] if service == 'es' else [{'Id': 'app'}]
    ctx.call.side_effect = call
    ctx.run.side_effect = lambda service, checks, skip: [
        {'serviceCode': service, 'quotaCode': code,
         'usageValue': fn(ctx)['usage']} for code, _, fn in checks]
    entries = get_current_quotastatus_opensearch(ctx=ctx)
    assert {(e['serviceCode'], e['quotaCode'], e['usageValue']) for e in entries} == {
        ('es', 'L-076D529E', 1), ('opensearch', 'L-B9142967', 1),
    }
