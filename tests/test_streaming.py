from unittest.mock import Mock

from modules.qmchecks.streaming import get_current_quotastatus_streaming


def test_streaming_resource_counts():
    ctx = Mock(quotas={('medialive', 'L-D1AFAF75'): {},
                       ('medialive', 'L-7BC53EAF'): {},
                       ('medialive', 'L-9E4BC4C0'): {},
                       ('medialive', 'L-A825B11C'): {},
                       ('mediapackage', 'L-352B8598'): {}})
    ctx.call.side_effect = lambda service, method, key, **kwargs: [{'id': 'channel'}] if method.endswith('channels') else ([{}, {}] if 'cluster' in method else [{}, {}, {}])
    ctx.run.side_effect = lambda service, checks, skip: [
        {'serviceCode': service, 'quotaCode': code, 'usageValue': fn(ctx)['usage']}
        for code, _, fn in checks]
    entries = get_current_quotastatus_streaming(ctx=ctx)
    assert [e['usageValue'] for e in entries] == [1, 2, 3, 3, 1, 3]
