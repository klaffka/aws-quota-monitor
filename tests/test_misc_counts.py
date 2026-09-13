from unittest.mock import Mock
from modules.qmchecks.misc_counts import get_current_quotastatus_misc

def test_misc_persistent_resource_counts_are_paginated():
    ctx = Mock(quotas={('glacier', 'L-D1C67346'): {}, ('dataexchange', 'L-52E2E63A'): {}, ('rbin', 'L-629917A2'): {}, ('dlm', 'L-5407D8DA'): {}, ('ssm-contacts', 'L-7DD2017D'): {}, ('ssm-contacts', 'L-4EA3AB3A'): {}, ('wellarchitected', 'L-D69BFA30'): {}, ('wellarchitected', 'L-BAE0003F'): {}, ('wellarchitected', 'L-ACECEBBD'): {}})
    ctx.run.side_effect = lambda service, checks, skip: [check[2](ctx) for check in checks]
    def call(_service, method, key=None, **kwargs):
        if method == 'list_review_templates':
            return [{'TemplateArn': 'template-1'}]
        if method == 'get_review_template':
            return {'ReviewTemplate': {'Lenses': ['lens']}}
        if method == 'list_workloads':
            return [{'WorkloadId': 'workload-1'}]
        if method == 'get_workload':
            return {'Workload': {'Lenses': ['lens']}}
        if method == 'list_milestones':
            return [{'MilestoneNumber': 1}]
        return [{'id': 'resource'}]
    ctx.call.side_effect = call
    assert len(get_current_quotastatus_misc(ctx=ctx)) == 12
    assert ctx.call.call_count == 15
