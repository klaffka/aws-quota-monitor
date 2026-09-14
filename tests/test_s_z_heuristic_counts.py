from unittest.mock import Mock
from modules.qmchecks.misc_counts import get_current_quotastatus_misc

def test_s_z_heuristic_resource_counts():
    ctx = Mock(quotas={('servicecatalog', 'L-7C3CEC2B'): {}, ('scn', 'L-4AF12E50'): {}, ('timestream-influxdb', 'L-61ADAB7E'): {}})
    ctx.call.side_effect = lambda *args, **kwargs: [{'id': 'one'}, {'id': 'two'}]
    ctx.run.side_effect = lambda service, checks, skip: [check[2](ctx) for check in checks]
    assert [x['usage'] for x in get_current_quotastatus_misc(ctx=ctx)] == [2, 2, 2]
