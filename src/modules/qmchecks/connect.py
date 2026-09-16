"""Connect inventories compared with the applied limit of each instance."""
from functools import partial

from modules.qmcore.aws import CheckContext, NoData, session_from_env
from modules.qmcore.model import number


def instance_limit(ctx, code, arn):
    quota = ctx.call('service-quotas', 'get_service_quota', ServiceCode='connect',
                     QuotaCode=code, ContextId=arn)['Quota']
    scope = quota.get('QuotaContext') or {}
    if (quota.get('ErrorReason') or quota.get('ServiceCode') != 'connect'
            or quota.get('QuotaCode') != code or scope.get('ContextId') != arn
            or scope.get('ContextScope') != 'RESOURCE'):
        raise NoData('Connect applied quota does not resolve to the requested instance')
    limit = number(quota.get('Value'))
    if not limit:
        raise NoData('Connect instance quota has no valid positive applied limit')
    return limit


def per_instance(ctx, code, inventory):
    results = []
    for instance in ctx.call('connect', 'list_instances', 'InstanceSummaryList'):
        iid, arn = instance.get('Id'), instance.get('Arn')
        if not iid or not arn:
            raise NoData('Connect instance inventory is missing its ID or ARN')
        limit = instance_limit(ctx, code, arn)
        usage, child, source = inventory(ctx, iid)
        results.append(dict(usage=usage, limit=limit, resource_id=arn,
                            resource_type='ConnectInstance',
                            meta={'instanceId': iid, 'childResourceId': child},
                            source=source + '+servicequotas:GetServiceQuota',
                            method='PER_RESOURCE_MAX_UTILIZATION'))
    if not results:
        # With no instances there is no resource-specific applied limit to select.
        # The catalog default is only used for this empty inventory.
        return dict(usage=0, resource_type='ConnectInstance', source='connect:ListInstances',
                    method='PER_RESOURCE_MAX_UTILIZATION')
    return max(results, key=lambda result: result['usage'] / result['limit'])


def count_inventory(ctx, iid, method, key, filters=None):
    return len(ctx.call('connect', method, key, InstanceId=iid, **(filters or {}))), None, f'connect:{method}'


def parent_inventory(ctx, iid, parent_method, parent_key, child_method, child_key,
                     parameter, primary=False, manual=False):
    values = []
    for parent in ctx.call('connect', parent_method, parent_key, InstanceId=iid):
        pid = parent.get('Id')
        if not pid:
            raise NoData('Connect parent inventory is missing its ID')
        kwargs = {'InstanceId': iid, parameter: pid}
        children = ctx.call('connect', child_method, child_key, **kwargs)
        if primary:
            if any(not isinstance(child.get('Primary'), bool) for child in children):
                raise NoData('Connect data table attribute has no primary flag')
            count = sum(child['Primary'] for child in children)
        else:
            count = len(children)
        values.append((count, pid))
        if manual:
            # Normal and manual-assignment queue/channel combinations have
            # independent limits. Count each list separately, never sum them.
            children = ctx.call('connect', 'list_routing_profile_manual_assignment_queues',
                                'RoutingProfileManualAssignmentQueueConfigSummaryList', **kwargs)
            values.append((len(children), pid + '/manual-assignment'))
    usage, child = max(values, default=(0, None), key=lambda value: value[0])
    source = f'connect:{parent_method}+{child_method}'
    if manual:
        source += '+list_routing_profile_manual_assignment_queues'
    return usage, child, source


# Explicit quota codes and API filters; no quota-name inference at runtime.
LIST_SPECS = [
    ('L-22922690', 'Contact flows per instance', 'list_contact_flows', 'ContactFlowSummaryList', {}),
    ('L-19A87C94', 'Queues per instance', 'list_queues', 'QueueSummaryList', {'QueueTypes': ['STANDARD']}),
    ('L-68BBE2E8', 'Quick connects per instance', 'list_quick_connects', 'QuickConnectSummaryList', {}),
    ('L-F325A715', 'Security profiles per instance', 'list_security_profiles', 'SecurityProfileSummaryList', {}),
    ('L-20CD02F7', 'Hours of operation per instance', 'list_hours_of_operations', 'HoursOfOperationSummaryList', {}),
    ('L-D68AAAE4', 'User hierarchy groups per instance', 'list_user_hierarchy_groups', 'UserHierarchyGroupSummaryList', {}),
    ('L-9A46857E', 'Users per instance', 'list_users', 'UserSummaryList', {}),
    ('L-D3E7BE26', 'Routing profiles per instance', 'list_routing_profiles', 'RoutingProfileSummaryList', {}),
    ('L-8F812903', 'Phone numbers per instance', 'list_phone_numbers', 'PhoneNumberSummaryList', {}),
    ('L-0865B754', 'Prompts per instance', 'list_prompts', 'PromptSummaryList', {}),
    ('L-19755C7E', 'Flow modules per instance', 'list_contact_flow_modules', 'ContactFlowModulesSummaryList', {}),
    ('L-B93A6612', 'Amazon Lex bots per instance', 'list_lex_bots', 'LexBots', {}),
    ('L-CCEA7427', 'Amazon Lex V2 bot aliases per instance', 'list_bots', 'LexBots', {'LexVersion': 'V2'}),
    ('L-E3D2F503', 'AWS Lambda functions per instance', 'list_lambda_functions', 'LambdaFunctions', {}),
    ('L-D492D362', 'Data tables per instance', 'list_data_tables', 'DataTableSummaryList', {}),
    ('L-6402A996', 'Workspaces per instance', 'list_workspaces', 'WorkspaceSummaryList', {}),
    ('L-DFA239E1', 'Notifications per instance', 'list_notifications', 'NotificationSummaryList', {}),
    ('L-F4C86B27', 'Email addresses per instance', 'search_email_addresses', 'EmailAddresses', {}),
    ('L-3828FBF0', 'Predefined attributes per instance', 'list_predefined_attributes', 'PredefinedAttributeSummaryList', {}),
    ('L-D945C9A8', 'Agent status per instance', 'list_agent_statuses', 'AgentStatusSummaryList', {}),
]
INTEGRATION_SPECS = [
    ('L-FC6A5030', 'APPLICATION'),
    ('L-D55E707F', 'Q_MESSAGE_TEMPLATES'),
    ('L-790F20B4', 'EVENT'),
    ('L-2D7CA70C', 'WISDOM_KNOWLEDGE_BASE'),
    ('L-C8F22860', 'WISDOM_QUICK_RESPONSES'),
    ('L-FFE16A0F', 'WISDOM_ASSISTANT'),
    ('L-C7548958', 'PINPOINT_APP'),
    ('L-02421311', 'FILE_SCANNER'),
    ('L-0AA82C05', 'CASES_DOMAIN'),
]
PARENT_SPECS = [
    ('L-E10B281B', 'Overrides per hours of operation', 'list_hours_of_operations', 'HoursOfOperationSummaryList',
     'list_hours_of_operation_overrides', 'HoursOfOperationOverrideList', 'HoursOfOperationId', {}),
    ('L-50375162', 'Proficiencies per agent', 'list_users', 'UserSummaryList',
     'list_user_proficiencies', 'UserProficiencyList', 'UserId', {}),
    ('L-516BC0EB', 'Queue-channel combinations per routing profile', 'list_routing_profiles', 'RoutingProfileSummaryList',
     'list_routing_profile_queues', 'RoutingProfileQueueConfigSummaryList', 'RoutingProfileId', {'manual': True}),
    ('L-BF789E19', 'Attributes per data table', 'list_data_tables', 'DataTableSummaryList',
     'list_data_table_attributes', 'Attributes', 'DataTableId', {}),
    ('L-74395C97', 'Primary attributes per data table', 'list_data_tables', 'DataTableSummaryList',
     'list_data_table_attributes', 'Attributes', 'DataTableId', {'primary': True}),
    ('L-735CD262', 'Values per data table', 'list_data_tables', 'DataTableSummaryList',
     'list_data_table_values', 'Values', 'DataTableId', {}),
    ('L-7B867368', 'Additional email addresses per queue', 'list_queues', 'QueueSummaryList',
     'list_queue_email_addresses', 'EmailAddressMetadataList', 'QueueId', {}),
]
CHECKS = [
    ('L-AA17A6B9', 'Amazon Connect instance count',
     lambda ctx: dict(usage=len(ctx.call('connect', 'list_instances', 'InstanceSummaryList')),
                      source='connect:ListInstances', method='ACCOUNT_COUNT')),
]
CHECKS += [(code, name, partial(per_instance, code=code, inventory=partial(
    count_inventory, method=method, key=key, filters=filters)))
           for code, name, method, key, filters in LIST_SPECS]
CHECKS += [(code, f'{kind} integration associations per instance', partial(per_instance, code=code, inventory=partial(
    count_inventory, method='list_integration_associations', key='IntegrationAssociationSummaryList',
    filters={'IntegrationType': kind}))) for code, kind in INTEGRATION_SPECS]
CHECKS += [(code, name, partial(per_instance, code=code, inventory=partial(
    parent_inventory, parent_method=pm, parent_key=pk, child_method=cm,
    child_key=ck, parameter=parameter, **options)))
           for code, name, pm, pk, cm, ck, parameter, options in PARENT_SPECS]


def get_current_quotastatus_connect(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    checks = [check for check in CHECKS if ('connect', check[0]) in context.quotas]
    return context.run('connect', checks, skip) if checks else []
