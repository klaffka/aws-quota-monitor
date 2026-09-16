from unittest.mock import Mock

from modules.qmchecks.entityresolution import CHECKS as ENTITY
from modules.qmchecks.datazone import maximum_per_domain


def test_entity_resolution_resource_counts():
    # The plain inventories; the job-concurrency checks walk each workflow and
    # are covered by tests/test_entityresolution_and_backup_jobs.py.
    ctx = Mock()
    ctx.call.side_effect = [[{'workflowId': 'w'}], [{'workflowId': 'm'}], [{'id': 'ns'}], [{'schemaMappingId': 's'}]]
    counted = ['L-60DAF647', 'L-C5A3094C', 'L-FBA1B7BB', 'L-00E43259']
    by_code = {code: fn for code, _name, fn in ENTITY}
    assert [by_code[code](ctx)['usage'] for code in counted] == [1, 1, 1, 1]


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
