"""Data Automation project blueprints, agent schemas and optimization jobs."""
from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import bedrock, bedrock_data_automation as automation
from modules.qmchecks import bedrock_optimization as optimization
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 16, tzinfo=UTC)
PROJECT = 'arn:aws:bedrock:eu-central-1:123456789012:data-automation-project/one'
OTHER = 'arn:aws:bedrock:eu-central-1:123456789012:data-automation-project/two'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'bedrock', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code, checks):
    return next(fn for quota, _name, fn in checks if quota == code)


def blueprint_arn(name):
    return f'arn:aws:bedrock:eu-central-1:123456789012:blueprint/{name}'


def stub_project(stub, arn, blueprints, stage='LIVE'):
    stub.add_response('get_data_automation_project', {'project': {
        'projectArn': arn, 'projectStage': stage, 'projectName': arn.rsplit('/', 1)[-1],
        'creationTime': MOMENT, 'lastModifiedTime': MOMENT, 'status': 'COMPLETED',
        'customOutputConfiguration': {
            'blueprints': [{'blueprintArn': blueprint_arn(name)} for name, _kind in blueprints]}}},
        {'projectArn': arn, 'projectStage': stage})
    for name, kind in blueprints:
        stub.add_response('get_blueprint', {'blueprint': {
            'blueprintArn': blueprint_arn(name), 'schema': '{}', 'type': kind,
            'creationTime': MOMENT, 'lastModifiedTime': MOMENT,
            'blueprintName': name, 'blueprintVersion': '1', 'blueprintStage': 'LIVE'}},
            {'blueprintArn': blueprint_arn(name)})


@pytest.mark.parametrize('code, expected', [
    ('L-15868B7E', 2),   # Images
    ('L-A938DC68', 1),   # Documents
    ('L-6BF35027', 0),   # Audios
    ('L-F5FD68DB', 1),   # Videos
])
def test_each_modality_counts_only_its_own_blueprints(code, expected):
    """One quota per modality, so a project's blueprints must be told apart."""
    ctx = context(code)
    with Stubber(ctx.client(automation.SERVICE)) as stub:
        stub.add_response('list_data_automation_projects', {'projects': [
            {'projectArn': PROJECT, 'projectStage': 'LIVE', 'projectName': 'one',
             'creationTime': MOMENT},
            {'projectArn': OTHER, 'projectStage': 'LIVE', 'projectName': 'two',
             'creationTime': MOMENT}]},
            {'resourceOwner': 'ACCOUNT', 'projectStageFilter': 'ALL'})
        stub_project(stub, PROJECT, [('a', 'IMAGE'), ('b', 'IMAGE'), ('c', 'DOCUMENT')])
        stub_project(stub, OTHER, [('d', 'VIDEO')])
        result = check(code, automation.CHECKS)(ctx)
        assert result['usage'] == expected
        assert result['method'] == 'PER_RESOURCE_MAX'
        stub.assert_no_pending_responses()


def test_a_modality_the_split_does_not_know_is_reported_rather_than_dropped():
    """A fifth modality would otherwise vanish from all four counts at once."""
    ctx = context('L-15868B7E')
    with Stubber(ctx.client(automation.SERVICE)) as stub:
        stub.add_response('list_data_automation_projects', {'projects': [
            {'projectArn': PROJECT, 'projectStage': 'LIVE', 'projectName': 'one',
             'creationTime': MOMENT}]},
            {'resourceOwner': 'ACCOUNT', 'projectStageFilter': 'ALL'})
        stub.add_response('get_data_automation_project', {'project': {
            'projectArn': PROJECT, 'projectStage': 'LIVE', 'projectName': 'one',
            'creationTime': MOMENT, 'lastModifiedTime': MOMENT, 'status': 'COMPLETED',
            'customOutputConfiguration': {'blueprints': [{'blueprintArn': blueprint_arn('a')}]}}},
            {'projectArn': PROJECT, 'projectStage': 'LIVE'})
        stub.add_response('get_blueprint', {'blueprint': {
            'blueprintArn': blueprint_arn('a'), 'schema': '{}', 'type': 'HOLOGRAM',
            'creationTime': MOMENT, 'lastModifiedTime': MOMENT,
            'blueprintName': 'a', 'blueprintVersion': '1', 'blueprintStage': 'LIVE'}},
            {'blueprintArn': blueprint_arn('a')})
        with pytest.raises(NoData, match='modality'):
            check('L-15868B7E', automation.CHECKS)(ctx)


def test_a_project_without_blueprints_still_counts_as_zero():
    """Dropping it would report the largest project rather than the maximum."""
    ctx = context('L-15868B7E')
    with Stubber(ctx.client(automation.SERVICE)) as stub:
        stub.add_response('list_data_automation_projects', {'projects': [
            {'projectArn': PROJECT, 'projectStage': 'LIVE', 'projectName': 'one',
             'creationTime': MOMENT}]},
            {'resourceOwner': 'ACCOUNT', 'projectStageFilter': 'ALL'})
        stub.add_response('get_data_automation_project', {'project': {
            'projectArn': PROJECT, 'projectStage': 'LIVE', 'projectName': 'one',
            'creationTime': MOMENT, 'lastModifiedTime': MOMENT, 'status': 'COMPLETED'}},
            {'projectArn': PROJECT, 'projectStage': 'LIVE'})
        result = check('L-15868B7E', automation.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (0, f'{PROJECT}/LIVE')


def stub_agents(stub, functions):
    stub.add_response('list_agents', {'agentSummaries': [
        {'agentId': 'agent-1', 'agentName': 'one', 'agentStatus': 'PREPARED',
         'updatedAt': MOMENT}]}, {})
    stub.add_response('list_agent_action_groups', {'actionGroupSummaries': [
        {'actionGroupId': 'group-1', 'actionGroupName': 'g', 'actionGroupState': 'ENABLED',
         'updatedAt': MOMENT}]}, {'agentId': 'agent-1', 'agentVersion': 'DRAFT'})
    stub.add_response('get_agent_action_group', {'agentActionGroup': {
        'agentId': 'agent-1', 'agentVersion': 'DRAFT', 'actionGroupId': 'group-1',
        'actionGroupName': 'g', 'createdAt': MOMENT, 'updatedAt': MOMENT,
        'actionGroupState': 'ENABLED', 'functionSchema': {'functions': functions}}},
        {'agentId': 'agent-1', 'agentVersion': 'DRAFT', 'actionGroupId': 'group-1'})


def test_the_largest_function_decides_the_parameter_count():
    ctx = context('L-4B4330A0')
    with Stubber(ctx.client('bedrock-agent')) as stub:
        stub_agents(stub, [
            {'name': 'small', 'parameters': {'a': {'type': 'string'}}},
            {'name': 'large', 'parameters': {'a': {'type': 'string'}, 'b': {'type': 'number'},
                                             'c': {'type': 'boolean'}}}])
        result = check('L-4B4330A0', bedrock.CHECKS)(ctx)
        assert result['usage'] == 3
        assert result['resource_id'] == 'agent-1/group-1/large'
        stub.assert_no_pending_responses()


def test_a_function_without_parameters_counts_as_zero():
    ctx = context('L-4B4330A0')
    with Stubber(ctx.client('bedrock-agent')) as stub:
        stub_agents(stub, [{'name': 'bare'}])
        assert check('L-4B4330A0', bedrock.CHECKS)(ctx)['usage'] == 0


def test_collaborators_are_counted_per_agent():
    ctx = context('L-EAFCD549')
    with Stubber(ctx.client('bedrock-agent')) as stub:
        stub.add_response('list_agents', {'agentSummaries': [
            {'agentId': 'agent-1', 'agentName': 'one', 'agentStatus': 'PREPARED',
             'updatedAt': MOMENT},
            {'agentId': 'agent-2', 'agentName': 'two', 'agentStatus': 'PREPARED',
             'updatedAt': MOMENT}]}, {})
        stub.add_response('list_agent_collaborators', {'agentCollaboratorSummaries': [
            {'agentId': 'agent-1', 'agentVersion': 'DRAFT', 'agentDescriptor': {},
             'collaboratorId': 'c1', 'collaboratorName': 'c1', 'collaborationInstruction': 'x',
             'createdAt': MOMENT, 'lastUpdatedAt': MOMENT, 'relayConversationHistory': 'DISABLED'}]},
            {'agentId': 'agent-1', 'agentVersion': 'DRAFT'})
        stub.add_response('list_agent_collaborators', {'agentCollaboratorSummaries': []},
                          {'agentId': 'agent-2', 'agentVersion': 'DRAFT'})
        result = check('L-EAFCD549', bedrock.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (1, 'agent-1')
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('code, expected', [('L-7380B9B2', 2), ('L-B46DD052', 2),
                                            ('L-0B66D421', 3), ('L-986C4672', 3)])
def test_optimization_jobs_split_by_whether_they_are_still_running(code, expected):
    """Both exports name these quotas, and each names them with its own code."""
    ctx = context(code)
    with Stubber(ctx.client('bedrock')) as stub:
        stub.add_response('list_advanced_prompt_optimization_jobs', {'jobSummaries': [
            {'jobArn': 'arn:job/1', 'jobName': 'a', 'jobStatus': 'InProgress',
             'creationTime': MOMENT, 'lastModifiedTime': MOMENT},
            {'jobArn': 'arn:job/2', 'jobName': 'b', 'jobStatus': 'Stopping',
             'creationTime': MOMENT, 'lastModifiedTime': MOMENT},
            {'jobArn': 'arn:job/3', 'jobName': 'c', 'jobStatus': 'Completed',
             'creationTime': MOMENT, 'lastModifiedTime': MOMENT},
            {'jobArn': 'arn:job/4', 'jobName': 'd', 'jobStatus': 'Failed',
             'creationTime': MOMENT, 'lastModifiedTime': MOMENT},
            {'jobArn': 'arn:job/5', 'jobName': 'e', 'jobStatus': 'Deleting',
             'creationTime': MOMENT, 'lastModifiedTime': MOMENT}]}, {})
        result = check(code, optimization.CHECKS)(ctx)
        assert result['usage'] == expected
        assert result['method'] == 'ACCOUNT_COUNT'
        stub.assert_no_pending_responses()


def test_an_unknown_optimization_status_is_reported_rather_than_guessed():
    ctx = context('L-7380B9B2')
    with Stubber(ctx.client('bedrock')) as stub:
        stub.add_response('list_advanced_prompt_optimization_jobs', {'jobSummaries': [
            {'jobArn': 'arn:job/1', 'jobName': 'a', 'jobStatus': 'Reticulating',
             'creationTime': MOMENT, 'lastModifiedTime': MOMENT}]}, {})
        with pytest.raises(NoData, match='status'):
            check('L-7380B9B2', optimization.CHECKS)(ctx)


@pytest.mark.parametrize('managed, known', [
    ('L-5C7643AC', 'L-60DA3E0D'),   # Knowledge bases per account
    ('L-F02D918A', 'L-679D8304'),   # Data sources per knowledge base
])
def test_the_managed_knowledge_base_codes_reuse_the_same_measurement(managed, known):
    """AWS renamed the product and reissued the codes; the inventory is one API."""
    assert check(managed, bedrock.CHECKS) is check(known, bedrock.CHECKS)


def test_the_managed_concurrent_ingestion_code_reuses_the_same_measurement():
    from modules.qmchecks import bedrock_throughput as throughput
    assert (check('L-D74F6A4C', throughput.CHECKS)
            is check('L-31BC8F89', throughput.CHECKS))
