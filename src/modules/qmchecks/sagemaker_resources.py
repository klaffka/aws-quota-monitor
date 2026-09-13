"""SageMaker resource-count quotas backed by paginated list APIs."""
from modules.qmcore.aws import CheckContext, session_from_env


ALL_CHECKS = [
    ('L-04CE2E67', 'Total number of notebook instances',
     lambda c: dict(usage=len(c.call('sagemaker', 'list_notebook_instances', 'NotebookInstances')),
                    source='sagemaker:ListNotebookInstances', method='ACCOUNT_COUNT')),
    ('L-E8EADE50', 'Maximum number of pipelines allowed per account',
     lambda c: dict(usage=len(c.call('sagemaker', 'list_pipelines', 'PipelineSummaries')),
                    source='sagemaker:ListPipelines', method='ACCOUNT_COUNT')),
    ('L-6BC1B1A9', 'Maximum number of MLflow Tracking Servers',
     lambda c: dict(usage=len(c.call('sagemaker', 'list_mlflow_tracking_servers', 'TrackingServerSummaries')),
                    source='sagemaker:ListMlflowTrackingServers', method='ACCOUNT_COUNT')),
    ('L-8E5333B4', 'Maximum number of Studio spaces allowed per account',
     lambda c: dict(usage=len(c.call('sagemaker', 'list_spaces', 'Spaces')),
                    source='sagemaker:ListSpaces', method='ACCOUNT_COUNT')),
    ('L-5CED4195', 'Maximum number of SageMaker Projects allowed per account',
     lambda c: dict(usage=len(c.call('sagemaker', 'list_projects', 'ProjectSummaryList')),
                    source='sagemaker:ListProjects', method='ACCOUNT_COUNT')),
    ('L-9A82FBCA', 'Maximum number of SageMaker Model Package allowed per account',
     lambda c: dict(usage=len(c.call('sagemaker', 'list_model_packages', 'ModelPackageSummaryList')),
                    source='sagemaker:ListModelPackages', method='ACCOUNT_COUNT')),
    ('L-BC8DC54C', 'Maximum number of SageMaker Model Package Groups allowed per account',
     lambda c: dict(usage=len(c.call('sagemaker', 'list_model_package_groups', 'ModelPackageGroupSummaryList')),
                    source='sagemaker:ListModelPackageGroups', method='ACCOUNT_COUNT')),
    ('L-B683BCB0', 'Total domains',
     lambda c: dict(usage=len(c.call('sagemaker', 'list_domains', 'Domains')),
                    source='sagemaker:ListDomains', method='ACCOUNT_COUNT')),
    ('L-AC46C40F', 'Maximum number of Studio user profiles allowed per account',
     lambda c: dict(usage=len(c.call('sagemaker', 'list_user_profiles', 'UserProfiles')),
                    source='sagemaker:ListUserProfiles', method='ACCOUNT_COUNT')),
    ('L-1BAEE5A7', 'Number of workteams',
     lambda c: dict(usage=len(c.call('sagemaker', 'list_workteams', 'Workteams')),
                    source='sagemaker:ListWorkteams', method='ACCOUNT_COUNT')),
    ('L-3036C9CA', 'Maximum number of A2I human task UIs',
     lambda c: dict(usage=len(c.call('sagemaker', 'list_human_task_uis', 'HumanTaskUiSummaries')),
                    source='sagemaker:ListHumanTaskUis', method='ACCOUNT_COUNT')),
    ('L-73C1B556', 'Maximum number of A2I flow definitions',
     lambda c: dict(usage=len(c.call('sagemaker', 'list_flow_definitions', 'FlowDefinitionSummaries')),
                    source='sagemaker:ListFlowDefinitions', method='ACCOUNT_COUNT')),
    ('L-A0C828DC', 'Total number of experiments',
     lambda c: dict(usage=len(c.call('sagemaker', 'list_experiments', 'ExperimentSummaries')),
                    source='sagemaker:ListExperiments', method='ACCOUNT_COUNT')),
    ('L-E1A153C2', 'Total number of trials',
     lambda c: dict(usage=len(c.call('sagemaker', 'list_trials', 'TrialSummaries')),
                    source='sagemaker:ListTrials', method='ACCOUNT_COUNT')),
    ('L-DDDC1D15', 'Maximum number of SageMakerImage images allowed per account',
     lambda c: dict(usage=len(c.call('sagemaker', 'list_images', 'Images')),
                    source='sagemaker:ListImages', method='ACCOUNT_COUNT')),
    ('L-9966108C', 'Total Monitoring Schedules',
     lambda c: dict(usage=len(c.call('sagemaker', 'list_monitoring_schedules', 'MonitoringScheduleSummaries')),
                    source='sagemaker:ListMonitoringSchedules', method='ACCOUNT_COUNT')),
    ('L-7A3DF611', 'Number of instances across active endpoints',
     lambda c: dict(usage=sum(
         variant.get('InitialInstanceCount', 0)
         for endpoint in c.call('sagemaker', 'list_endpoints', 'Endpoints')
         if endpoint.get('EndpointStatus') in {'InService', 'Creating', 'Updating'}
         for detail in [c.call('sagemaker', 'describe_endpoint',
                               None, EndpointName=endpoint.get('EndpointName'))]
         for variant in c.call('sagemaker', 'describe_endpoint_config', 'ProductionVariants',
                               EndpointConfigName=detail.get('EndpointConfigName'))),
                    source='sagemaker:DescribeEndpointConfig', method='ACCOUNT_COUNT')),
]

# Preserve the historical four-entry CHECKS export for compatibility with
# callers that used this module directly. The collector uses the complete
# catalog-backed set below.
CHECKS = ALL_CHECKS[:4]


def get_current_quotastatus_sagemaker_resources(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'sagemaker' for service, _ in context.quotas):
        return []
    return context.run('sagemaker', ALL_CHECKS, skip)
