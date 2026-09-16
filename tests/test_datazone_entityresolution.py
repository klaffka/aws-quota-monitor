from unittest.mock import Mock

from modules.qmchecks.entityresolution import CHECKS as ENTITY
from modules.qmchecks.datazone import maximum_per_domain


def test_entity_resolution_resource_counts():
    ctx = Mock()
    ctx.call.side_effect = [[{'workflowId': 'w'}], [{'workflowId': 'm'}], [{'id': 'ns'}], [{'schemaMappingId': 's'}]]
    assert [check[2](ctx)['usage'] for check in ENTITY] == [1, 1, 1, 1]


def test_datazone_counts_are_maximum_per_domain():
    ctx = Mock()
    ctx.call.side_effect = [[{'id': 'domain-1'}, {'id': 'domain-2'}],
                            [{'id': 'asset-1'}, {'id': 'asset-2'}], [{'id': 'asset-3'}]]
    result = maximum_per_domain(ctx, 'list_assets', 'items')
    assert (result['usage'], result['resource_id']) == (2, 'domain-1')


def test_datazone_environments_are_counted_per_domain():
    check = next(item[2] for item in __import__('modules.qmchecks.datazone', fromlist=['CHECKS']).CHECKS
                 if item[0] == 'L-EDF6298B')
    ctx = Mock()
    # The listing is scoped to a project, so the domain sums its projects.
    ctx.call.side_effect = [[{'id': 'domain-1'}], [{'id': 'project-1'}],
                            [{'id': 'env-1'}, {'id': 'env-2'}]]
    result = check(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'domain-1')
