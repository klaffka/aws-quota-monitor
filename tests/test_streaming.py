from unittest.mock import Mock

from modules.qmchecks.streaming import get_current_quotastatus_streaming


def test_streaming_resource_counts():
    ctx = Mock(quotas={('medialive', 'L-D1AFAF75'): {},
                       ('medialive', 'L-7BC53EAF'): {},
                       ('medialive', 'L-9E4BC4C0'): {},
                       ('medialive', 'L-A825B11C'): {},
                       ('mediapackage', 'L-352B8598'): {}})
    def calls(service, method, key, **kwargs):
        if method.endswith('channels'):
            return [{'id': 'channel'}]
        if 'cluster' in method:
            return [{}, {}]
        if method == 'list_origin_endpoints':
            # The endpoints carry an identity and the window the new scope reads.
            return [{'Id': f'endpoint-{index}', 'StartoverWindowSeconds': index * 60}
                    for index in range(3)]
        return [{}, {}, {}]

    ctx.call.side_effect = calls
    ctx.run.side_effect = lambda service, checks, skip: [
        {'serviceCode': service, 'quotaCode': code, 'usageValue': fn(ctx)['usage']}
        for code, _, fn in checks]
    entries = get_current_quotastatus_streaming(ctx=ctx)
    usage = {e['quotaCode']: e['usageValue'] for e in entries}
    assert [usage[code] for code in
            ('L-D1AFAF75', 'L-7BC53EAF', 'L-9E4BC4C0', 'L-A825B11C')] == [1, 2, 3, 3]
    assert (usage['L-352B8598'], usage['L-7F7EDDDF']) == (1, 3)
    # The third endpoint offers the longest startover window.
    assert usage['L-8D3D8B62'] == 120
