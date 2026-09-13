from unittest.mock import Mock
from pathlib import Path

from modules.qmchecks.glue import (CHECKS as GLUE_CHECKS, active_column_statistics_tasks,
                                  active_materialized_view_refreshes, active_runs,
                                  data_quality_rulesets, databases_per_catalog,
                                  development_endpoint_dpus, integrations, job_runs,
                                  jobs_per_trigger, ml_task_runs, named_tag_expressions, partitions,
                                  running_crawlers, table_versions,
                                  table_versions_per_table, tables_per_database,
                                  user_defined_functions)
from modules.qmchecks.emr import CHECKS as EMR_CHECKS
from modules.qmchecks.datasync import CHECKS as DATASYNC_CHECKS
from modules.qmchecks.sagemaker import CHECKS as SAGEMAKER_CHECKS


def test_glue_resource_counts():
    ctx = Mock()
    def call(_service, method, key=None, **kwargs):
        if method == 'get_databases':
            return [{'Name': 'db'}]
        if method == 'get_tables':
            return [{'Name': 'table'}]
        return [{'Name': method}]
    ctx.call.side_effect = call
    assert [check[2](ctx)['usage'] for check in GLUE_CHECKS[:13]] == [1] * 13


def test_glue_parent_scoped_table_counts():
    ctx = Mock()

    def call(_service, method, key=None, **kwargs):
        if method == 'get_databases':
            return [{'Name': 'db-a'}, {'Name': 'db-b'}]
        if method == 'get_tables':
            return ([{'Name': 't1'}, {'Name': 't2'}]
                    if kwargs['DatabaseName'] == 'db-a' else [{'Name': 't3'}])
        if method == 'get_table_versions':
            return [{'VersionId': 'v1'}, {'VersionId': 'v2'}, {'VersionId': 'v3'}]
        raise AssertionError(method)

    ctx.call.side_effect = call
    assert tables_per_database(ctx)['usage'] == 2
    assert table_versions(ctx)['usage'] == 9
    assert table_versions_per_table(ctx)['usage'] == 3


class GlueContext:
    account = '123456789012'

    def call(self, _service, method, key=None, **kwargs):
        if method == 'list_lf_tag_expressions':
            assert kwargs == {'CatalogId': self.account}
            value = {'LFTagExpressions': [{'Name': 'expression'}]}
        elif method == 'get_databases':
            value = {'DatabaseList': [{'Name': 'db-a'}, {'Name': 'db-b'}]}
        elif method == 'get_tables':
            tables = [{'Name': 'a-1'}, {'Name': 'a-2'}] if kwargs['DatabaseName'] == 'db-a' \
                else [{'Name': 'b-1'}]
            value = {'TableList': tables}
        elif method == 'get_user_defined_functions':
            functions = ([{'FunctionName': 'f-1', 'DatabaseName': 'db-a'},
                          {'FunctionName': 'f-2', 'DatabaseName': 'db-a'}]
                         if kwargs['DatabaseName'] == 'db-a' else [])
            value = {'UserDefinedFunctions': functions}
        elif method == 'get_catalogs':
            assert kwargs == {'Recursive': True, 'IncludeRoot': True}
            value = {'CatalogList': [{'CatalogId': self.account}, {'CatalogId': 'catalog-2'}]}
        elif method == 'get_dev_endpoints':
            value = {'DevEndpoints': [
                {'EndpointName': 'nodes', 'NumberOfNodes': 3},
                {'EndpointName': 'workers', 'WorkerType': 'G.2X', 'NumberOfWorkers': 4}]}
        elif method == 'get_partitions':
            count = 2 if kwargs['TableName'] == 'a-1' else 1
            value = {'Partitions': [{'Values': [str(number)]} for number in range(count)]}
        elif method == 'get_jobs':
            value = {'Jobs': [{'Name': 'job-a'}, {'Name': 'job-b'}]}
        elif method == 'get_job_runs':
            states = (['STARTING', 'WAITING', 'SUCCEEDED']
                      if kwargs['JobName'] == 'job-a' else ['RUNNING', 'STOPPING'])
            value = {'JobRuns': [{'Id': f"{kwargs['JobName']}-{number}",
                                  'JobName': kwargs['JobName'], 'JobRunState': state}
                                 for number, state in enumerate(states)]}
        elif method == 'get_crawlers':
            value = {'Crawlers': [{'Name': 'c-ready', 'State': 'READY'},
                                  {'Name': 'c-running', 'State': 'RUNNING'},
                                  {'Name': 'c-stopping', 'State': 'STOPPING'}]}
        elif method == 'get_ml_transforms':
            value = {'Transforms': [{'TransformId': 't-1'}, {'TransformId': 't-2'}]}
        elif method == 'get_ml_task_runs':
            states = ['RUNNING', 'SUCCEEDED'] if kwargs['TransformId'] == 't-1' else ['STARTING']
            value = {'TaskRuns': [{'TaskRunId': f"{kwargs['TransformId']}-{number}",
                                  'TransformId': kwargs['TransformId'], 'Status': state}
                                 for number, state in enumerate(states)]}
        elif method == 'get_triggers':
            value = {'Triggers': [{'Name': 'trigger', 'Actions': [
                {'JobName': 'job-a'}, {'JobName': 'job-b'}, {'CrawlerName': 'crawler'}]}]}
        elif method == 'describe_integrations':
            value = {'Integrations': [{'IntegrationArn': 'arn:integration'}]}
        elif method == 'list_data_quality_rulesets':
            value = {'Rulesets': [{'Name': 'rules'}]}
        elif method in {'list_data_quality_ruleset_evaluation_runs',
                        'list_data_quality_rule_recommendation_runs'}:
            value = {'Runs': [{'RunId': 'run-active', 'Status': 'RUNNING'},
                              {'RunId': 'run-done', 'Status': 'SUCCEEDED'}]}
        elif method == 'list_materialized_view_refresh_task_runs':
            assert kwargs == {'CatalogId': self.account}
            value = {'MaterializedViewRefreshTaskRuns': [
                {'MaterializedViewRefreshTaskRunId': 'refresh', 'Status': 'STARTING'}]}
        elif method == 'list_column_statistics_task_runs':
            value = {'ColumnStatisticsTaskRunIds': ['stats-active', 'stats-done']}
        elif method == 'get_column_statistics_task_run':
            state = 'RUNNING' if kwargs['ColumnStatisticsTaskRunId'] == 'stats-active' else 'SUCCEEDED'
            value = {'ColumnStatisticsTaskRun': {
                'ColumnStatisticsTaskRunId': kwargs['ColumnStatisticsTaskRunId'],
                'Status': state}}
        else:
            raise AssertionError(method)
        return value[key] if key else value


def test_glue_functions_and_partitions_cover_account_and_parent_scopes():
    ctx = GlueContext()
    assert user_defined_functions(ctx)['usage'] == 2
    assert user_defined_functions(ctx, per_database=True)['usage'] == 2
    assert partitions(ctx)['usage'] == 4
    assert partitions(ctx, per_table=True)['usage'] == 2
    assert databases_per_catalog(ctx)['usage'] == 2
    assert development_endpoint_dpus(ctx)['usage'] == 8
    assert named_tag_expressions(ctx)['usage'] == 1


def test_glue_concurrency_uses_explicit_active_and_queued_states():
    ctx = GlueContext()
    assert job_runs(ctx, 'active')['usage'] == 3
    assert job_runs(ctx, 'per_job')['usage'] == 2
    assert job_runs(ctx, 'queued')['usage'] == 1
    assert running_crawlers(ctx)['usage'] == 2
    assert ml_task_runs(ctx)['usage'] == 2
    assert ml_task_runs(ctx, per_transform=True)['usage'] == 1


def test_glue_configuration_and_task_inventories():
    ctx = GlueContext()
    assert integrations(ctx)['usage'] == 1
    assert data_quality_rulesets(ctx)['usage'] == 1
    assert jobs_per_trigger(ctx)['usage'] == 2
    assert active_runs(ctx, 'list_data_quality_ruleset_evaluation_runs',
                       'Runs', 'RunId')['usage'] == 1
    assert active_runs(ctx, 'list_data_quality_rule_recommendation_runs',
                       'Runs', 'RunId')['usage'] == 1
    assert active_materialized_view_refreshes(ctx)['usage'] == 1
    assert active_column_statistics_tasks(ctx)['usage'] == 1


def test_glue_extended_read_permissions_are_deployed():
    policy = (Path(__file__).parents[1] / 'deployment/main.tf').read_text(encoding='utf-8')
    actions = ('GetUserDefinedFunctions', 'GetPartitions', 'GetDevEndpoints', 'GetCatalogs',
               'DescribeIntegrations', 'ListDataQualityRulesets', 'GetJobRuns',
               'GetMLTaskRuns', 'ListDataQualityRulesetEvaluationRuns',
               'ListDataQualityRuleRecommendationRuns',
               'ListMaterializedViewRefreshTaskRuns', 'ListColumnStatisticsTaskRuns',
               'GetColumnStatisticsTaskRun', 'ListLFTagExpressions')
    for action in actions:
        prefix = 'lakeformation' if action == 'ListLFTagExpressions' else 'glue'
        assert f'"{prefix}:{action}"' in policy


def test_emr_counts_only_active_cluster_states():
    ctx = Mock()
    ctx.call.return_value = [{'Id': 'j-1'}]
    assert EMR_CHECKS[0][2](ctx)['usage'] == 1
    assert ctx.call.call_args.kwargs['ClusterStates'] == ['STARTING', 'BOOTSTRAPPING', 'RUNNING', 'WAITING', 'TERMINATING']


def test_datasync_and_sagemaker_inventories():
    ctx = Mock()
    ctx.call.side_effect = [[{'TaskArn': 'task'}], [{'NotebookInstanceName': 'nb'}],
                            [{'PipelineName': 'pipeline'}]]
    assert DATASYNC_CHECKS[0][2](ctx)['usage'] == 1
    assert [check[2](ctx)['usage'] for check in SAGEMAKER_CHECKS] == [1, 1]
