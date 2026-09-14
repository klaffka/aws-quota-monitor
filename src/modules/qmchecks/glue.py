"""AWS Glue regional resource, configuration, and active-run quotas."""
from modules.qmcore.aws import CheckContext, NoData, session_from_env
from modules.qmcore.aws import maximum


def count(ctx, method, key):
    return dict(usage=len(ctx.call('glue', method, key)), source=f'glue:{method}', method='ACCOUNT_COUNT')


def required(item, field, subject):
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise NoData(f'Glue {subject} is missing {field}')
    return value


def unique_items(items, field, subject):
    result = {}
    for item in items:
        if not isinstance(item, dict):
            raise NoData(f'Glue {subject} inventory contains an invalid item')
        identity = required(item, field, subject)
        if identity in result and result[identity] != item:
            raise NoData(f'Glue {subject} inventory changed during pagination')
        result[identity] = item
    return [result[key] for key in sorted(result)]


def database_names(ctx):
    return [required(item, 'Name', 'database')
            for item in unique_items(ctx.call('glue', 'get_databases', 'DatabaseList'),
                                     'Name', 'database')]


def table_names(ctx):
    result = []
    for database_name in database_names(ctx):
        tables = unique_items(ctx.call('glue', 'get_tables', 'TableList',
                                      DatabaseName=database_name), 'Name', 'table')
        result.extend((database_name, table['Name']) for table in tables)
    return result


def user_defined_functions(ctx, per_database=False):
    values = []
    for database_name in database_names(ctx):
        functions = unique_items(
            ctx.call('glue', 'get_user_defined_functions', 'UserDefinedFunctions',
                     DatabaseName=database_name), 'FunctionName', 'function')
        for function in functions:
            actual_database = function.get('DatabaseName')
            if actual_database not in {None, database_name}:
                raise NoData('Glue function belongs to a different database')
        values.append((database_name, len(functions), None))
    if per_database:
        return maximum(values, 'GlueDatabase', 'glue:GetDatabases+GetUserDefinedFunctions')
    return dict(usage=sum(value[1] for value in values),
                source='glue:GetDatabases+GetUserDefinedFunctions', method='ACCOUNT_COUNT')


def partitions(ctx, per_table=False):
    values = []
    for database_name, table_name in table_names(ctx):
        items = ctx.call('glue', 'get_partitions', 'Partitions', DatabaseName=database_name,
                         TableName=table_name, ExcludeColumnSchema=True)
        identities = set()
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get('Values'), list) \
                    or any(not isinstance(value, str) for value in item['Values']):
                raise NoData('Glue partition inventory contains an invalid identity')
            identity = tuple(item['Values'])
            if identity in identities:
                raise NoData('Glue partition inventory contains a duplicate identity')
            identities.add(identity)
        values.append((f'{database_name}/{table_name}', len(identities), None))
    if per_table:
        return maximum(values, 'GlueTable', 'glue:GetDatabases+GetTables+GetPartitions')
    return dict(usage=sum(value[1] for value in values),
                source='glue:GetDatabases+GetTables+GetPartitions', method='ACCOUNT_COUNT')


def integrations(ctx):
    items = unique_items(ctx.call('glue', 'describe_integrations', 'Integrations'),
                         'IntegrationArn', 'integration')
    return dict(usage=len(items), source='glue:DescribeIntegrations', method='ACCOUNT_COUNT')


def data_quality_rulesets(ctx):
    items = unique_items(ctx.call('glue', 'list_data_quality_rulesets', 'Rulesets'),
                         'Name', 'data-quality ruleset')
    return dict(usage=len(items), source='glue:ListDataQualityRulesets', method='ACCOUNT_COUNT')


def databases_per_catalog(ctx):
    catalogs = unique_items(ctx.call('glue', 'get_catalogs', 'CatalogList', Recursive=True,
                                     IncludeRoot=True), 'CatalogId', 'catalog')
    if not catalogs:
        raise NoData('Glue catalog inventory did not include the root catalog')
    values = []
    for catalog in catalogs:
        catalog_id = catalog['CatalogId']
        databases = unique_items(ctx.call('glue', 'get_databases', 'DatabaseList',
                                          CatalogId=catalog_id), 'Name', 'database')
        values.append((catalog_id, len(databases), None))
    return maximum(values, 'GlueCatalog', 'glue:GetCatalogs+GetDatabases')


def named_tag_expressions(ctx):
    items = unique_items(
        ctx.call('lakeformation', 'list_lf_tag_expressions', 'LFTagExpressions',
                 CatalogId=ctx.account), 'Name', 'named tag expression')
    return dict(usage=len(items), source='lakeformation:ListLFTagExpressions',
                method='ACCOUNT_COUNT')


def development_endpoint_dpus(ctx):
    factors = {'Standard': 1, 'G.1X': 1, 'G.2X': 2}
    values = []
    endpoints = unique_items(ctx.call('glue', 'get_dev_endpoints', 'DevEndpoints'),
                             'EndpointName', 'development endpoint')
    for endpoint in endpoints:
        nodes = endpoint.get('NumberOfNodes')
        if isinstance(nodes, int) and not isinstance(nodes, bool) and nodes >= 0:
            dpus = nodes
        else:
            worker_type = endpoint.get('WorkerType')
            workers = endpoint.get('NumberOfWorkers')
            if worker_type not in factors or not isinstance(workers, int) \
                    or isinstance(workers, bool) or workers < 0:
                raise NoData('Glue development endpoint has no valid DPU allocation')
            dpus = factors[worker_type] * workers
        values.append((endpoint['EndpointName'], dpus, None))
    return maximum(values, 'GlueDevEndpoint', 'glue:GetDevEndpoints')


def jobs_per_trigger(ctx):
    values = []
    for trigger in unique_items(ctx.call('glue', 'get_triggers', 'Triggers'), 'Name', 'trigger'):
        actions = trigger.get('Actions')
        if not isinstance(actions, list) or any(not isinstance(action, dict) for action in actions):
            raise NoData('Glue trigger has an invalid action list')
        jobs = [required(action, 'JobName', 'trigger job action')
                for action in actions if 'JobName' in action]
        values.append((trigger['Name'], len(jobs), None))
    return maximum(values, 'GlueTrigger', 'glue:GetTriggers')


JOB_STATES = {'STARTING', 'RUNNING', 'STOPPING', 'STOPPED', 'SUCCEEDED', 'FAILED',
              'TIMEOUT', 'ERROR', 'WAITING', 'EXPIRED'}
ACTIVE_JOB_STATES = {'STARTING', 'RUNNING', 'STOPPING'}


def job_runs(ctx, mode):
    values = []
    seen = set()
    for job in unique_items(ctx.call('glue', 'get_jobs', 'Jobs'), 'Name', 'job'):
        job_name = job['Name']
        active = queued = 0
        for run in ctx.call('glue', 'get_job_runs', 'JobRuns', JobName=job_name):
            if not isinstance(run, dict):
                raise NoData('Glue job-run inventory contains an invalid item')
            run_id = required(run, 'Id', 'job run')
            identity = (job_name, run_id)
            if identity in seen:
                raise NoData('Glue job-run inventory contains a duplicate identity')
            seen.add(identity)
            if run.get('JobName') not in {None, job_name}:
                raise NoData('Glue job run belongs to a different job')
            state = run.get('JobRunState')
            if state not in JOB_STATES:
                raise NoData('Glue job run has an unknown state')
            active += state in ACTIVE_JOB_STATES
            queued += state == 'WAITING'
        values.append((job_name, queued if mode == 'queued' else active, None))
    if mode == 'per_job':
        return maximum(values, 'GlueJob', 'glue:GetJobs+GetJobRuns')
    return dict(usage=sum(value[1] for value in values), source='glue:GetJobs+GetJobRuns',
                method='ACCOUNT_COUNT')


def running_crawlers(ctx):
    active = 0
    for crawler in unique_items(ctx.call('glue', 'get_crawlers', 'Crawlers'), 'Name', 'crawler'):
        state = crawler.get('State')
        if state not in {'READY', 'RUNNING', 'STOPPING'}:
            raise NoData('Glue crawler has an unknown state')
        active += state in {'RUNNING', 'STOPPING'}
    return dict(usage=active, source='glue:GetCrawlers', method='ACCOUNT_COUNT')


def ml_task_runs(ctx, per_transform=False):
    values = []
    seen = set()
    transforms = unique_items(ctx.call('glue', 'get_ml_transforms', 'Transforms'),
                              'TransformId', 'ML transform')
    valid_states = {'STARTING', 'RUNNING', 'STOPPING', 'STOPPED', 'SUCCEEDED',
                    'FAILED', 'TIMEOUT'}
    for transform in transforms:
        transform_id = transform['TransformId']
        active = 0
        for run in ctx.call('glue', 'get_ml_task_runs', 'TaskRuns', TransformId=transform_id):
            if not isinstance(run, dict):
                raise NoData('Glue ML task-run inventory contains an invalid item')
            run_id = required(run, 'TaskRunId', 'ML task run')
            identity = (transform_id, run_id)
            if identity in seen:
                raise NoData('Glue ML task-run inventory contains a duplicate identity')
            seen.add(identity)
            if run.get('TransformId') not in {None, transform_id}:
                raise NoData('Glue ML task run belongs to a different transform')
            state = run.get('Status')
            if state not in valid_states:
                raise NoData('Glue ML task run has an unknown state')
            active += state in {'STARTING', 'RUNNING', 'STOPPING'}
        values.append((transform_id, active, None))
    if per_transform:
        return maximum(values, 'GlueMLTransform', 'glue:GetMLTransforms+GetMLTaskRuns')
    return dict(usage=sum(value[1] for value in values),
                source='glue:GetMLTransforms+GetMLTaskRuns', method='ACCOUNT_COUNT')


def active_runs(ctx, method, key, id_field, *, kwargs=None):
    items = unique_items(ctx.call('glue', method, key, **(kwargs or {})), id_field, 'task run')
    active = 0
    valid_states = {'STARTING', 'RUNNING', 'STOPPING', 'STOPPED', 'SUCCEEDED',
                    'FAILED', 'TIMEOUT'}
    for item in items:
        state = item.get('Status')
        if state not in valid_states:
            raise NoData('Glue task run has an unknown state')
        active += state in {'STARTING', 'RUNNING', 'STOPPING'}
    return dict(usage=active, source=f'glue:{method}', method='ACCOUNT_COUNT')


def active_materialized_view_refreshes(ctx):
    return active_runs(ctx, 'list_materialized_view_refresh_task_runs',
                       'MaterializedViewRefreshTaskRuns', 'MaterializedViewRefreshTaskRunId',
                       kwargs={'CatalogId': ctx.account})


def active_column_statistics_tasks(ctx):
    identifiers = ctx.call('glue', 'list_column_statistics_task_runs',
                           'ColumnStatisticsTaskRunIds')
    if any(not isinstance(identifier, str) or not identifier for identifier in identifiers):
        raise NoData('Glue column-statistics task inventory has an invalid identity')
    if len(identifiers) != len(set(identifiers)):
        raise NoData('Glue column-statistics task inventory contains a duplicate identity')
    active = 0
    for identifier in identifiers:
        task = ctx.call('glue', 'get_column_statistics_task_run',
                        ColumnStatisticsTaskRunId=identifier).get('ColumnStatisticsTaskRun')
        if not isinstance(task, dict) or task.get('ColumnStatisticsTaskRunId') != identifier:
            raise NoData('Glue column-statistics task detail is inconsistent')
        state = task.get('Status')
        if state not in {'STARTING', 'RUNNING', 'SUCCEEDED', 'FAILED', 'STOPPED'}:
            raise NoData('Glue column-statistics task has an unknown state')
        active += state in {'STARTING', 'RUNNING'}
    return dict(usage=active,
                source='glue:ListColumnStatisticsTaskRuns+GetColumnStatisticsTaskRun',
                method='ACCOUNT_COUNT')


def tables(ctx):
    total = 0
    for database in ctx.call('glue', 'get_databases', 'DatabaseList'):
        name = database.get('Name')
        if name:
            total += len(ctx.call('glue', 'get_tables', 'TableList', DatabaseName=name))
    return dict(usage=total, source='glue:GetDatabases+GetTables', method='ACCOUNT_COUNT')


def tables_per_database(ctx):
    values = []
    for database in ctx.call('glue', 'get_databases', 'DatabaseList'):
        name = database.get('Name')
        if name:
            values.append((name, len(ctx.call('glue', 'get_tables', 'TableList', DatabaseName=name)), None))
    return maximum(values, 'GlueDatabase', 'glue:GetDatabases+GetTables')


def table_versions(ctx):
    total = 0
    for database in ctx.call('glue', 'get_databases', 'DatabaseList'):
        database_name = database.get('Name')
        if not database_name:
            continue
        for table in ctx.call('glue', 'get_tables', 'TableList', DatabaseName=database_name):
            table_name = table.get('Name')
            if table_name:
                versions = ctx.call('glue', 'get_table_versions', 'TableVersions',
                                    DatabaseName=database_name, TableName=table_name)
                total += len(versions)
    return dict(usage=total, source='glue:GetDatabases+GetTables+GetTableVersions', method='ACCOUNT_COUNT')


def table_versions_per_table(ctx):
    values = []
    for database in ctx.call('glue', 'get_databases', 'DatabaseList'):
        database_name = database.get('Name')
        if not database_name:
            continue
        for table in ctx.call('glue', 'get_tables', 'TableList', DatabaseName=database_name):
            table_name = table.get('Name')
            if table_name:
                versions = ctx.call('glue', 'get_table_versions', 'TableVersions',
                                    DatabaseName=database_name, TableName=table_name)
                values.append((f'{database_name}/{table_name}', len(versions), None))
    return maximum(values, 'GlueTable', 'glue:GetDatabases+GetTables+GetTableVersions')


CHECKS = [
    ('L-11FA2C1A', 'Number of crawlers', lambda ctx: count(ctx, 'get_crawlers', 'Crawlers')),
    ('L-F953935E', 'Max databases per account', lambda ctx: count(ctx, 'get_databases', 'DatabaseList')),
    ('L-611FDDE4', 'Max jobs per account', lambda ctx: count(ctx, 'get_jobs', 'Jobs')),
    ('L-7DD7C33A', 'Number of workflows', lambda ctx: count(ctx, 'list_workflows', 'Workflows')),
    ('L-4256D6D2', 'Max connections per account', lambda ctx: count(ctx, 'get_connections', 'ConnectionList')),
    ('L-F1653A6D', 'Max triggers per account', lambda ctx: count(ctx, 'get_triggers', 'Triggers')),
    ('L-94D025B7', 'Max tables per account', tables),
    ('L-B8497671', 'Max tables per database', tables_per_database),
    ('L-337244C9', 'Max table versions per account', table_versions),
    ('L-071ABE08', 'Max table versions per table', table_versions_per_table),
    ('L-83192DBF', 'Max security configurations per account', lambda ctx: count(ctx, 'get_security_configurations', 'SecurityConfigurations')),
    ('L-04CEE988', 'Number of machine learning transforms', lambda ctx: count(ctx, 'get_ml_transforms', 'Transforms')),
    ('L-64A88F0A', 'Number of Schema Registries', lambda ctx: count(ctx, 'list_registries', 'Registries')),
    ('L-D987EC31', 'Max functions per account', user_defined_functions),
    ('L-1DD415D5', 'Max functions per database',
     lambda ctx: user_defined_functions(ctx, per_database=True)),
    ('L-FEBBFA7A', 'Max partitions per account', partitions),
    ('L-2C3F5401', 'Max partitions per table', lambda ctx: partitions(ctx, per_table=True)),
    ('L-DBA56E2F', 'Max development endpoint per account',
     lambda ctx: count(ctx, 'get_dev_endpoints', 'DevEndpoints')),
    ('L-76EC689B', 'Max DPUs per dev endpoint', development_endpoint_dpus),
    ('L-A57B5BCE', 'Max databases per catalog', databases_per_catalog),
    ('L-EAC30D24', 'Max Named Tag Expressions', named_tag_expressions),
    ('L-F1AAB534', 'Number of integrations', integrations),
    ('L-87F5991C', 'Max data quality rulesets per account', data_quality_rulesets),
    ('L-EEC98450', 'Max jobs per trigger', jobs_per_trigger),
    ('L-5E4153CA', 'Max concurrent job runs per account', lambda ctx: job_runs(ctx, 'active')),
    ('L-F574AED9', 'Max concurrent job runs per job', lambda ctx: job_runs(ctx, 'per_job')),
    ('L-A457CBAB', 'Maximum number of queued job runs', lambda ctx: job_runs(ctx, 'queued')),
    ('L-4071B0E3', 'Number of crawlers running concurrently per account', running_crawlers),
    ('L-E15CE20A', 'Concurrent machine learning task runs per transform',
     lambda ctx: ml_task_runs(ctx, per_transform=True)),
    ('L-83A59AA6', 'Total concurrent machine learning task runs for transforms per account',
     ml_task_runs),
    ('L-C3952F6C', 'Max concurrent data quality ruleset evaluation runs per account',
     lambda ctx: active_runs(ctx, 'list_data_quality_ruleset_evaluation_runs',
                             'Runs', 'RunId')),
    ('L-ACAC12B6', 'Max concurrent data quality ruleset recommendation runs per account',
     lambda ctx: active_runs(ctx, 'list_data_quality_rule_recommendation_runs',
                             'Runs', 'RunId')),
    ('L-B4840D4D', 'The maximum number of concurrent materialized view refresh task runs.',
     active_materialized_view_refreshes),
    ('L-3890A802', 'Number of column statistics tasks running concurrently per account',
     active_column_statistics_tasks),
]


def get_current_quotastatus_glue(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'glue' for service, _ in context.quotas):
        return []
    return context.run('glue', CHECKS, skip)
