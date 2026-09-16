import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import appsync, codepipeline
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

API = 'abcdefghijklmnopqrstuvwxyz'
OTHER_API = 'zyxwvutsrqponmlkjihgfedcba'
PIPELINE = 'build'
OTHER_PIPELINE = 'release'


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(module, code):
    return next(fn for quota, _, fn in module.CHECKS if quota == code)


def graphql_api(identity, providers=0):
    api = {'apiId': identity, 'name': identity, 'authenticationType': 'API_KEY'}
    if providers:
        api['additionalAuthenticationProviders'] = [
            {'authenticationType': 'AWS_IAM'} for _ in range(providers)]
    return api


def test_authentication_providers_count_the_primary_type_too():
    ctx = context('appsync', 'L-E7CCBB11')
    with Stubber(ctx.client('appsync')) as stub:
        stub.add_response('list_graphql_apis', {'graphqlApis': [
            graphql_api(API), graphql_api(OTHER_API, providers=2)]}, {})
        result = appsync.authentication_providers_per_api(ctx)
        assert (result['usage'], result['resource_id']) == (3, OTHER_API)
        stub.assert_no_pending_responses()


def test_an_api_without_an_authentication_type_raises_nodata():
    ctx = context('appsync', 'L-E7CCBB11')
    with Stubber(ctx.client('appsync')) as stub:
        stub.add_response('list_graphql_apis', {'graphqlApis': [
            {'apiId': API, 'name': API}]}, {})
        with pytest.raises(NoData, match='no authentication type'):
            appsync.authentication_providers_per_api(ctx)


def test_api_keys_are_counted_per_api():
    ctx = context('appsync', 'L-06A0647C')
    with Stubber(ctx.client('appsync')) as stub:
        stub.add_response('list_graphql_apis', {'graphqlApis': [
            graphql_api(API), graphql_api(OTHER_API)]}, {})
        stub.add_response('list_api_keys', {'apiKeys': [{'id': 'k1'}]}, {'apiId': API})
        stub.add_response('list_api_keys', {'apiKeys': [{'id': 'k2'}, {'id': 'k3'}]},
                          {'apiId': OTHER_API})
        result = check(appsync, 'L-06A0647C')(ctx)
        assert (result['usage'], result['resource_id']) == (2, OTHER_API)
        stub.assert_no_pending_responses()


def test_pipeline_resolver_functions_are_counted_across_types():
    ctx = context('appsync', 'L-855DA767')
    with Stubber(ctx.client('appsync')) as stub:
        stub.add_response('list_graphql_apis', {'graphqlApis': [graphql_api(API)]}, {})
        stub.add_response('list_types', {'types': [{'name': 'Query'}]},
                          {'apiId': API, 'format': 'SDL'})
        stub.add_response('list_resolvers', {'resolvers': [
            {'typeName': 'Query', 'fieldName': 'items', 'kind': 'PIPELINE',
             'pipelineConfig': {'functions': ['f1', 'f2', 'f3']}},
            {'typeName': 'Query', 'fieldName': 'one', 'kind': 'UNIT'}]},
            {'apiId': API, 'typeName': 'Query'})
        result = appsync.functions_per_pipeline_resolver(ctx)
        assert (result['usage'], result['resource_id']) == (3, f'{API}/Query/items')
        stub.assert_no_pending_responses()


def test_event_apis_are_counted_separately_from_graphql_apis():
    ctx = context('appsync', 'L-D19E6EC4')
    with Stubber(ctx.client('appsync')) as stub:
        stub.add_response('list_apis', {'apis': [
            {'apiId': API, 'name': 'events'},
            {'apiId': OTHER_API, 'name': 'more-events'}]}, {})
        assert check(appsync, 'L-D19E6EC4')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def action(name, run_order=1):
    return {'name': name, 'runOrder': run_order,
            'actionTypeId': {'category': 'Build', 'owner': 'AWS',
                             'provider': 'CodeBuild', 'version': '1'}}


def stage(name, actions):
    return {'name': name, 'actions': actions}


def pipeline(name, stages):
    return {'name': name, 'roleArn': 'arn:aws:iam::123456789012:role/pipeline',
            'stages': stages, 'version': 1}


def stub_pipelines(stub, definitions):
    stub.add_response('list_pipelines', {'pipelines': [
        {'name': name} for name in definitions]}, {})
    for name, stages in definitions.items():
        stub.add_response('get_pipeline', {'pipeline': pipeline(name, stages)},
                          {'name': name})


def test_stage_and_action_counts_are_reported_at_each_level():
    definitions = {
        PIPELINE: [stage('source', [action('a')]),
                   stage('build', [action('b'), action('c', 2)])],
        OTHER_PIPELINE: [stage('source', [action('a')])],
    }
    for code, expected_usage, expected_id in (
            ('L-A0A99E23', 2, PIPELINE), ('L-1402209C', 3, PIPELINE),
            ('L-570F1605', 2, f'{PIPELINE}/build'),
            ('L-8DF1BAAD', 2, f'{PIPELINE}/build')):
        ctx = context('codepipeline', code)
        with Stubber(ctx.client('codepipeline')) as stub:
            stub_pipelines(stub, definitions)
            result = check(codepipeline, code)(ctx)
            assert (result['usage'], result['resource_id']) == (expected_usage,
                                                                expected_id), code
            stub.assert_no_pending_responses()


def test_parallel_actions_share_a_run_order():
    ctx = context('codepipeline', 'L-2B3011E2')
    with Stubber(ctx.client('codepipeline')) as stub:
        stub_pipelines(stub, {PIPELINE: [
            stage('build', [action('a'), action('b'), action('c', 2)])]})
        result = check(codepipeline, 'L-2B3011E2')(ctx)
        assert (result['usage'], result['resource_id']) == (2, f'{PIPELINE}/build')
        stub.assert_no_pending_responses()


def test_an_invalid_run_order_raises_nodata():
    # The SDK rejects a run order below 1, so this guards the helper directly.
    with pytest.raises(NoData, match='invalid run order'):
        codepipeline._run_orders({'actions': [{'name': 'a', 'runOrder': 0}]})


def test_active_executions_are_counted_per_pipeline():
    ctx = context('codepipeline', 'L-0097A9B4')
    with Stubber(ctx.client('codepipeline')) as stub:
        stub.add_response('list_pipelines', {'pipelines': [{'name': PIPELINE}]}, {})
        stub.add_response('list_pipeline_executions', {'pipelineExecutionSummaries': [
            {'pipelineExecutionId': 'e1', 'status': 'InProgress'},
            {'pipelineExecutionId': 'e2', 'status': 'Stopping'},
            {'pipelineExecutionId': 'e3', 'status': 'Succeeded'}]},
            {'pipelineName': PIPELINE})
        result = codepipeline.active_executions_per_pipeline(ctx)
        assert (result['usage'], result['resource_id']) == (2, PIPELINE)
        stub.assert_no_pending_responses()


def test_only_custom_action_types_are_counted():
    ctx = context('codepipeline', 'L-519D5A90')
    with Stubber(ctx.client('codepipeline')) as stub:
        stub.add_response('list_action_types', {'actionTypes': [
            {'id': {'category': 'Build', 'owner': 'Custom', 'provider': 'mine',
                    'version': '1'},
             'inputArtifactDetails': {'minimumCount': 0, 'maximumCount': 1},
             'outputArtifactDetails': {'minimumCount': 0, 'maximumCount': 1}},
            {'id': {'category': 'Build', 'owner': 'AWS', 'provider': 'CodeBuild',
                    'version': '1'},
             'inputArtifactDetails': {'minimumCount': 0, 'maximumCount': 1},
             'outputArtifactDetails': {'minimumCount': 0, 'maximumCount': 1}}]}, {})
        assert codepipeline.custom_action_types(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_every_check_is_registered_for_reporting():
    for module, service in ((appsync, 'appsync'), (codepipeline, 'codepipeline')):
        registered = {code for name, code in custom_keys() if name == service}
        assert {code for code, _, _ in module.CHECKS} <= registered, service
