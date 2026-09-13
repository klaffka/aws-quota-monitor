from unittest.mock import Mock

from modules.qmchecks.ssm import patch_groups_per_baseline
from modules.qmchecks.misc_counts import milestones_per_workload, review_template_lenses, workload_lenses


def test_ssm_patch_groups_are_deduplicated_per_baseline():
    ctx = Mock()
    ctx.call.return_value = [
        {'PatchGroup': 'prod', 'BaselineIdentity': {'BaselineId': 'pb-1'}},
        {'PatchGroup': 'prod', 'BaselineIdentity': {'BaselineId': 'pb-1'}},
        {'PatchGroup': 'dev', 'BaselineIdentity': {'BaselineId': 'pb-1'}},
        {'PatchGroup': 'prod', 'BaselineIdentity': {'BaselineId': 'pb-2'}},
    ]
    result = patch_groups_per_baseline(ctx)
    assert result['usage'] == 2
    assert result['resource_id'] == 'pb-1'


def test_wellarchitected_parent_scoped_counts_use_detail_apis():
    ctx = Mock()

    def call(_service, method, key=None, **kwargs):
        if method == 'list_review_templates':
            return [{'TemplateArn': 'template-1'}]
        if method == 'get_review_template':
            return {'ReviewTemplate': {'Lenses': ['a', 'b']}}
        if method == 'list_workloads':
            return [{'WorkloadId': 'workload-1'}]
        if method == 'get_workload':
            return {'Workload': {'Lenses': ['a', 'b', 'c']}}
        if method == 'list_milestones':
            return [{'MilestoneNumber': 1}, {'MilestoneNumber': 2}]
        raise AssertionError((method, key, kwargs))

    ctx.call.side_effect = call
    assert review_template_lenses(ctx)['usage'] == 2
    assert workload_lenses(ctx)['usage'] == 3
    assert milestones_per_workload(ctx)['usage'] == 2
