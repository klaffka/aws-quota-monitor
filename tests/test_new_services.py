from unittest.mock import Mock

from modules.qmchecks.new_services import (
    get_current_quotastatus_new_services,
)


def test_new_service_resource_counts():
    ctx = Mock(quotas={('vpc-lattice', 'L-9CAD07FB'): {},
                       ('thinclient', 'L-64C2BDF4'): {}})
    ctx.run.side_effect = lambda service, checks, skip: [
        {'serviceCode': service, 'quotaCode': code} for code, _, _ in checks]
    entries = get_current_quotastatus_new_services(ctx=ctx)
    assert [(entry['serviceCode'], entry['quotaCode']) for entry in entries] == [
        ('vpc-lattice', 'L-9CAD07FB'), ('thinclient', 'L-64C2BDF4')]
    assert [entry.args[0] for entry in ctx.run.call_args_list] == [
        'vpc-lattice', 'thinclient']
    assert [[check[0] for check in entry.args[1]]
            for entry in ctx.run.call_args_list] == [
                ['L-9CAD07FB'], ['L-64C2BDF4']]
    assert all(entry.args[2] == () for entry in ctx.run.call_args_list)
