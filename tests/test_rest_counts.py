from unittest.mock import Mock

from modules.qmchecks.rest_counts import get_current_quotastatus_rest_counts


def test_rest_catalog_resource_counts():
    ctx = Mock(quotas={('application-signals', 'L-3FECAFD0'): {},
                       ('aps', 'L-8873DB23'): {}, ('voiceid', 'L-CF9F1A9B'): {}})
    def calls(service, method, key=None, **kwargs):
        if service == 'application-signals':
            return [{}]
        if service == 'amp':
            return [{}, {}]
        if method == 'list_domains':
            return [{'DomainId': 'domain-1'}]
        return [{}]
    ctx.call.side_effect = calls
    ctx.run.side_effect = lambda service, checks, skip: [
        {'serviceCode': service, 'quotaCode': code, 'usageValue': fn(ctx)['usage']}
        for code, _, fn in checks]
    entries = get_current_quotastatus_rest_counts(ctx=ctx)
    assert [e['usageValue'] for e in entries] == [1, 2, 1, 1, 1, 1, 1]
