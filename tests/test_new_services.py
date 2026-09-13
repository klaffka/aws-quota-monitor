from unittest.mock import Mock

from modules.qmchecks.new_services import get_current_quotastatus_new_services


def test_new_service_resource_counts():
    ctx = Mock(quotas={('vpc-lattice', 'L-9CAD07FB'): {}, ('vpc-lattice', 'L-620C821E'): {},
                       ('vpc-lattice', 'L-BB11C6B9'): {}, ('thinclient', 'L-64C2BDF4'): {}})
    ctx.call.side_effect = [[{}], [{}, {}], [{}], [{}], [{}], [{}], [{}]]
    ctx.run.side_effect = lambda service, checks, skip: [
        {'serviceCode': service, 'quotaCode': code, 'usageValue': fn(ctx)['usage']}
        for code, _, fn in checks]
    entries = get_current_quotastatus_new_services(ctx=ctx)
    assert [e['usageValue'] for e in entries] == [1, 2, 1, 0, 0, 0, 1]
