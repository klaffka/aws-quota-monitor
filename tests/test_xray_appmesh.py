from unittest.mock import Mock

from modules.qmchecks.appmesh import routes_per_router
from modules.qmchecks.xray import CHECKS


def _xray_context():
    """A context answering the two listings and the tag listing behind them."""
    ctx = Mock()

    def calls(service, method, key=None, **kwargs):
        if method == 'get_groups':
            return [{'GroupARN': 'arn:group/one'}, {'GroupARN': 'arn:group/two'}]
        if method == 'get_sampling_rules':
            return [{'SamplingRule': {'RuleARN': 'arn:rule/one'}},
                    {'SamplingRule': {'RuleARN': 'arn:rule/two'}}]
        if method == 'list_tags_for_resource':
            return [{}] * (3 if kwargs['ResourceARN'].endswith('two') else 1)
        return [{'id': 'one'}, {'id': 'two'}]

    ctx.call.side_effect = calls
    return ctx


def test_xray_checks_use_paginated_resource_counts():
    """The two account counts read a listing; the tag scopes take a maximum."""
    ctx = _xray_context()
    usage = {code: check(ctx)['usage'] for code, _name, check in CHECKS}
    assert (usage['L-7F259013'], usage['L-8C0C998A']) == (2, 2)
    # The second resource of each kind carries three tags, the first one.
    assert (usage['L-E2DD2778'], usage['L-DB51D338']) == (3, 3)


def test_appmesh_routes_use_maximum_per_router():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'meshName': 'mesh'}],
        [{'virtualRouterName': 'router'}],
        [{'id': 'one'}, {'id': 'two'}],
    ]
    result = routes_per_router(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'mesh/router')
