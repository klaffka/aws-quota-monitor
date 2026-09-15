"""AWS Fault Injection Service template and running-experiment quotas."""
import json

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


ACTIVE_EXPERIMENT_STATES = {'pending', 'initiating', 'running', 'stopping'}
TERMINAL_EXPERIMENT_STATES = {'completed', 'stopped', 'failed', 'cancelled'}
ACTIVE_ACTION_STATES = {'initiating', 'running', 'stopping'}
KNOWN_ACTION_STATES = ACTIVE_ACTION_STATES | {
    'pending', 'completed', 'cancelled', 'stopped', 'failed', 'skipped'
}


# These quota descriptions name the AWS FIS action whose resolved targets are
# limited.  The boolean indicates that the quota only applies to dynamic
# tag/parameter target selection.  The two False entries apply to all targets.
TARGET_CHECKS = (
    ('L-4BEF8075', 'Target ManagedResources for aws:arc:start-zonal-autoshift action.',
     'aws:arc:start-zonal-autoshift', True),
    ('L-1F59732D', 'Target Subnets for aws:network:disrupt-connectivity',
     'aws:network:disrupt-connectivity', True),
    ('L-0A7016E5', 'Target Tasks for aws:ecs:task-kill-process',
     'aws:ecs:task-kill-process', True),
    ('L-E7DA8AFD', 'Target Kinesis data streams for aws:kinesis:stream-expired-iterator-exception action.',
     'aws:kinesis:stream-expired-iterator-exception', True),
    ('L-397A8E65', 'Target Pods for aws:eks:pod-io-stress', 'aws:eks:pod-io-stress', True),
    ('L-52F5389C', 'Target Tasks for aws:ecs:task-network-packet-loss',
     'aws:ecs:task-network-packet-loss', True),
    ('L-B34128D0', 'Target Tasks for aws:ecs:task-network-latency',
     'aws:ecs:task-network-latency', True),
    ('L-97338E0D', 'Target Auto Scaling groups for aws:ec2:asg-insufficient-instance-capacity-error',
     'aws:ec2:asg-insufficient-instance-capacity-error', True),
    ('L-143DCE03', 'Target Virtual Interfaces for aws:directconnect:virtual-interface',
     'aws:directconnect:virtual-interface-disconnect', True),
    ('L-C3959863', 'Target Kinesis data streams for aws:kinesis:stream-provisioned-throughput-exception action.',
     'aws:kinesis:stream-provisioned-throughput-exception', True),
    ('L-100E963F', 'Target Subnets for aws:network:route-table-disrupt-cross-region-connectivity',
     'aws:network:route-table-disrupt-cross-region-connectivity', True),
    ('L-5A59540D', 'Target Pods for aws:eks:pod-cpu-stress', 'aws:eks:pod-cpu-stress', True),
    ('L-4939706C', 'Target Tasks for aws:ecs:task-io-stress', 'aws:ecs:task-io-stress', True),
    ('L-5AC5092A', 'Target Pods for aws:eks:pod-network-latency',
     'aws:eks:pod-network-latency', True),
    ('L-C32797AE', 'Target functions for aws:lambda:invocation-error action.',
     'aws:lambda:invocation-error', True),
    ('L-B2CDA938', 'Target Clusters for aws:ecs:drain-container-instances',
     'aws:ecs:drain-container-instances', True),
    ('L-31F77559', 'Target multi-Region clusters for aws:memorydb:multi-region-cluster-pause-replication action.',
     'aws:memorydb:multi-region-cluster-pause-replication', True),
    ('L-D0A62255', 'Target Instances for aws:ssm:send-command', 'aws:ssm:send-command', True),
    ('L-4E30A9A5', 'Target functions for aws:lambda:invocation-http-integration-response action.',
     'aws:lambda:invocation-http-integration-response', True),
    ('L-FA07612D', 'Target Aurora DSQL clusters for aws:dsql:cluster-connection-failure action.',
     'aws:dsql:cluster-connection-failure', True),
    ('L-B993CA05', 'Target Volumes for aws:ebs:pause-volume-io', 'aws:ebs:pause-volume-io', True),
    ('L-C901BF0F', 'Target Tasks for aws:ecs:task-cpu-stress', 'aws:ecs:task-cpu-stress', True),
    ('L-48D12416', 'Target Tasks for aws:ecs:stop-task', 'aws:ecs:stop-task', True),
    ('L-08B3DB00', 'Target Pods for aws:eks:pod-delete', 'aws:eks:pod-delete', True),
    ('L-9C6F1F94', 'Target Instances for aws:ec2:reboot-instances',
     'aws:ec2:reboot-instances', True),
    ('L-2CF2B517', 'Target TransitGateways for aws:network:transit-gateway-disrupt-cross-region-connectivity',
     'aws:network:transit-gateway-disrupt-cross-region-connectivity', True),
    ('L-CCA14F79', 'Target Nodegroups for aws:eks:terminate-nodegroup-instances',
     'aws:eks:terminate-nodegroup-instances', True),
    ('L-F3F4B54A', 'Target SpotInstances for aws:ec2:send-spot-instance-interruptions',
     'aws:ec2:send-spot-instance-interruptions', True),
    ('L-4B06CB4E', 'Target Buckets for aws:s3:bucket-pause-replication',
     'aws:s3:bucket-pause-replication', True),
    ('L-5035601B', 'Target Tasks for aws:ecs:task-network-blackhole-port',
     'aws:ecs:task-network-blackhole-port', True),
    ('L-3F98B425', 'Target Instances for aws:ec2:stop-instances', 'aws:ec2:stop-instances', True),
    ('L-CFF34A14', 'Target Pods for aws:eks:pod-network-packet-loss',
     'aws:eks:pod-network-packet-loss', True),
    ('L-7D222253', 'Target Clusters for aws:rds:failover-db-cluster',
     'aws:rds:failover-db-cluster', True),
    ('L-9BD15E96', 'Target ReplicationGroups for aws:elasticache:replicationgroup-interrupt-az-power',
     'aws:elasticache:replicationgroup-interrupt-az-power', False),
    ('L-6CBFC7D2', 'Target DBInstances for aws:rds:reboot-db-instances',
     'aws:rds:reboot-db-instances', True),
    ('L-52F95FBE', 'Target Pods for aws:eks:pod-network-blackhole-port',
     'aws:eks:pod-network-blackhole-port', True),
    ('L-9FC608C5', 'Target tables for aws:dynamodb:global-table-pause-replication action',
     'aws:dynamodb:global-table-pause-replication', False),
    ('L-B8FF73F5', 'Target Pods for aws:eks:pod-memory-stress',
     'aws:eks:pod-memory-stress', True),
    ('L-EE64095D', 'Target Instances for aws:ec2:terminate-instances',
     'aws:ec2:terminate-instances', True),
    ('L-06C992A0', 'Target functions for aws:lambda:invocation-add-delay action.',
     'aws:lambda:invocation-add-delay', True),
)


def required_string(item, field, subject):
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise NoData(f'FIS {subject} is missing {field}')
    return value


def experiment_templates(ctx):
    summaries = {}
    for item in ctx.call('fis', 'list_experiment_templates', 'experimentTemplates'):
        identity = required_string(item, 'id', 'experiment template')
        if identity in summaries and summaries[identity] != item:
            raise NoData('FIS experiment template changed during pagination')
        summaries[identity] = item
    details = []
    for identity in sorted(summaries):
        item = ctx.call('fis', 'get_experiment_template', id=identity).get(
            'experimentTemplate')
        if not isinstance(item, dict) or item.get('id') != identity:
            raise NoData('FIS experiment template detail has a different identity')
        for field, expected in (('actions', dict), ('stopConditions', list), ('targets', dict)):
            if not isinstance(item.get(field), expected):
                raise NoData(f'FIS experiment template has no {field} inventory')
        count = item.get('targetAccountConfigurationsCount', 0)
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise NoData('FIS experiment template has an invalid target account count')
        details.append(item)
    return details


def template_maximum(ctx, field, resource_type):
    values = [(item['id'], len(item[field]), None) for item in experiment_templates(ctx)]
    return maximum(values, resource_type,
                   'fis:ListExperimentTemplates+GetExperimentTemplate')


def target_accounts_per_template(ctx):
    values = [(item['id'], item.get('targetAccountConfigurationsCount', 0), None)
              for item in experiment_templates(ctx)]
    return maximum(values, 'FisExperimentTemplate',
                   'fis:ListExperimentTemplates+GetExperimentTemplate')


def active_experiments(ctx):
    summaries = {}
    for item in ctx.call('fis', 'list_experiments', 'experiments'):
        identity = required_string(item, 'id', 'experiment')
        state = item.get('state')
        status = state.get('status') if isinstance(state, dict) else None
        if status not in ACTIVE_EXPERIMENT_STATES | TERMINAL_EXPERIMENT_STATES:
            raise NoData('FIS experiment has an unknown state')
        if identity in summaries and summaries[identity] != item:
            raise NoData('FIS experiment changed during pagination')
        summaries[identity] = item
    details = []
    for identity in sorted(summaries):
        summary_status = summaries[identity]['state']['status']
        if summary_status in TERMINAL_EXPERIMENT_STATES:
            continue
        item = ctx.call('fis', 'get_experiment', id=identity).get('experiment')
        if not isinstance(item, dict) or item.get('id') != identity:
            raise NoData('FIS experiment detail has a different identity')
        state = item.get('state')
        status = state.get('status') if isinstance(state, dict) else None
        if status != summary_status:
            raise NoData('FIS experiment state changed during collection')
        if not isinstance(item.get('actions'), dict) or not isinstance(item.get('targets'), dict):
            raise NoData('FIS experiment has no action or target inventory')
        details.append(item)
    return details


def parallel_actions(ctx):
    values = []
    for experiment in active_experiments(ctx):
        count = 0
        for action in experiment['actions'].values():
            if not isinstance(action, dict) or not isinstance(action.get('state'), dict):
                raise NoData('FIS experiment action has no state')
            status = action['state'].get('status')
            if status not in KNOWN_ACTION_STATES:
                raise NoData('FIS experiment action has an unknown state')
            count += status in ACTIVE_ACTION_STATES
        values.append((experiment['id'], count, None))
    return maximum(values, 'FisExperiment', 'fis:ListExperiments+GetExperiment')


def dynamically_selected(target):
    return bool(target.get('resourceTags')) or bool(target.get('parameters'))


def resolved_target_usage(ctx, action_id, dynamic_only):
    values = []
    for experiment in active_experiments(ctx):
        status = experiment['state']['status']
        relevant_names = set()
        for action in experiment['actions'].values():
            if not isinstance(action, dict):
                raise NoData('FIS experiment has an invalid action')
            if action.get('actionId') != action_id:
                continue
            action_targets = action.get('targets')
            if not isinstance(action_targets, dict):
                raise NoData('FIS experiment action has no target map')
            for target_name in action_targets.values():
                if not isinstance(target_name, str) or target_name not in experiment['targets']:
                    raise NoData('FIS experiment action references an unknown target')
                target = experiment['targets'][target_name]
                if not isinstance(target, dict) or not isinstance(target.get('resourceType'), str):
                    raise NoData('FIS experiment has an invalid target definition')
                if not dynamic_only or dynamically_selected(target):
                    relevant_names.add(target_name)
        if not relevant_names:
            values.append((experiment['id'], 0, None))
            continue
        # AWS exposes resolved targets only after target resolution finishes.
        # Returning zero during either earlier state would silently undercount.
        if status in {'pending', 'initiating'}:
            raise NoData('FIS target resolution has not finished for an active experiment')
        if experiment.get('targetAccountConfigurationsCount', 0):
            raise NoData('FIS resolved targets do not expose a documented target-account identity')
        resolved = ctx.call('fis', 'list_experiment_resolved_targets', 'resolvedTargets',
                            experimentId=experiment['id'])
        identities = set()
        for item in resolved:
            if not isinstance(item, dict):
                raise NoData('FIS resolved target inventory contains an invalid item')
            target_name = required_string(item, 'targetName', 'resolved target')
            if target_name not in experiment['targets']:
                raise NoData('FIS resolved target references an unknown target')
            resource_type = required_string(item, 'resourceType', 'resolved target')
            if resource_type != experiment['targets'][target_name].get('resourceType'):
                raise NoData('FIS resolved target has a mismatched resource type')
            information = item.get('targetInformation')
            if not isinstance(information, dict) or not information or any(
                    not isinstance(key, str) or not key or not isinstance(value, str) or not value
                    for key, value in information.items()):
                raise NoData('FIS resolved target has invalid target information')
            if target_name in relevant_names:
                identities.add((resource_type, json.dumps(information, sort_keys=True,
                                                          separators=(',', ':'))))
        values.append((experiment['id'], len(identities), None))
    return maximum(values, 'FisExperiment',
                   'fis:ListExperiments+GetExperiment+ListExperimentResolvedTargets')


CHECKS = [
    ('L-0BFE6B67', 'Actions per experiment template',
     lambda ctx: template_maximum(ctx, 'actions', 'FisExperimentTemplate')),
    ('L-872EC72B', 'Stop conditions per experiment template',
     lambda ctx: template_maximum(ctx, 'stopConditions', 'FisExperimentTemplate')),
    ('L-47D4AE5B', 'Target account configurations per experiment template',
     target_accounts_per_template),
    ('L-EB051440', 'Parallel actions per experiment', parallel_actions),
]
CHECKS.extend((code, name,
               lambda ctx, action_id=action_id, dynamic_only=dynamic_only:
               resolved_target_usage(ctx, action_id, dynamic_only))
              for code, name, action_id, dynamic_only in TARGET_CHECKS)


def get_current_quotastatus_fis(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'fis' for service, _ in context.quotas):
        return []
    return context.run('fis', CHECKS, skip)
