from unittest.mock import Mock

from modules.qmchecks.codebuild import CHECKS as BUILD
from modules.qmchecks.codepipeline import CHECKS as PIPELINE
from modules.qmchecks.codeartifact import repositories_per_domain
from modules.qmchecks.logs import CHECKS as LOGS


def test_codebuild_pipeline_and_logs_counts():
    ctx = Mock()
    # CodeBuild lists project names; the others list objects.
    ctx.call.side_effect = [['project'], [{'name': 'pipeline'}],
                            [{'logGroupName': 'group'}]]
    assert BUILD[0][2](ctx)['usage'] == 1
    assert PIPELINE[0][2](ctx)['usage'] == 1
    assert LOGS[0][2](ctx)['usage'] == 1


def test_codeartifact_repositories_are_maximum_per_domain():
    ctx = Mock()
    ctx.call.side_effect = [[{'name': 'domain-a'}, {'name': 'domain-b'}],
                            [{'name': 'r1'}, {'name': 'r2'}], [{'name': 'r3'}]]
    result = repositories_per_domain(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'domain-a')
