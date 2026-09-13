"""Persistent-resource inventories for small service modules."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env

def _sso_instances(c):
    return c.call('sso-admin', 'list_instances', 'Instances')

def _permission_sets(c):
    return sum(len(c.call('sso-admin', 'list_permission_sets', 'PermissionSets', InstanceArn=i['InstanceArn'])) for i in _sso_instances(c))

def _identity_store_count(c, method):
    return sum(len(c.call('identitystore', method, 'Users' if method == 'list_users' else 'Groups', IdentityStoreId=i['IdentityStoreId'])) for i in _sso_instances(c))


def _parent_max(ctx, parent_method, parent_key, parent_id, child_method, child_key,
                resource_type, source, response_field=None):
    values = []
    for parent in ctx.call('wellarchitected', parent_method, parent_key):
        identifier = parent.get(parent_id)
        if not identifier:
            continue
        response = ctx.call('wellarchitected', child_method, response_field or child_key,
                            **{parent_id: identifier})
        items = response if isinstance(response, list) else response.get(response_field or child_key, [])
        values.append((identifier, len(items), None))
    return maximum(values, resource_type, source)


def review_template_lenses(ctx):
    values = []
    for template in ctx.call('wellarchitected', 'list_review_templates', 'ReviewTemplates'):
        arn = template.get('TemplateArn')
        if not arn:
            continue
        response = ctx.call('wellarchitected', 'get_review_template', TemplateArn=arn)
        values.append((arn, len(response.get('ReviewTemplate', {}).get('Lenses', [])), None))
    return maximum(values, 'ReviewTemplate', 'wellarchitected:ListReviewTemplates+GetReviewTemplate')


def workload_lenses(ctx):
    values = []
    for workload in ctx.call('wellarchitected', 'list_workloads', 'WorkloadSummaries'):
        wid = workload.get('WorkloadId')
        if not wid:
            continue
        response = ctx.call('wellarchitected', 'get_workload', WorkloadId=wid)
        values.append((wid, len(response.get('Workload', {}).get('Lenses', [])), None))
    return maximum(values, 'Workload', 'wellarchitected:ListWorkloads+GetWorkload')


def milestones_per_workload(ctx):
    values = []
    for workload in ctx.call('wellarchitected', 'list_workloads', 'WorkloadSummaries'):
        wid = workload.get('WorkloadId')
        if wid:
            values.append((wid, len(ctx.call('wellarchitected', 'list_milestones', 'MilestoneSummaries', WorkloadId=wid)), None))
    return maximum(values, 'Workload', 'wellarchitected:ListWorkloads+ListMilestones')


def wisdom_content_per_knowledge_base(ctx):
    values = []
    for base in ctx.call('wisdom', 'list_knowledge_bases', 'knowledgeBaseSummaries'):
        identifier = base.get('knowledgeBaseId')
        if identifier:
            values.append((identifier, len(ctx.call('wisdom', 'list_contents', 'contentSummaries',
                                                    knowledgeBaseId=identifier)), None))
    return maximum(values, 'WisdomKnowledgeBase', 'wisdom:ListContents')

CHECKS = {
    'servicecatalog': [('L-7C3CEC2B', 'Applications per region', lambda c: dict(usage=len(c.call('servicecatalog-appregistry', 'list_applications', 'applications')), source='servicecatalog-appregistry:ListApplications', method='ACCOUNT_COUNT'))],
    'scn': [('L-4AF12E50', 'AWS Supply Chain instances per account', lambda c: dict(usage=len(c.call('supplychain', 'list_instances', 'instances')), source='supplychain:ListInstances', method='ACCOUNT_COUNT'))],
    'timestream-influxdb': [('L-61ADAB7E', 'Database instances per account', lambda c: dict(usage=len(c.call('timestream-influxdb', 'list_db_instances', 'dbInstances')), source='timestream-influxdb:ListDbInstances', method='ACCOUNT_COUNT'))],
    'wisdom': [
        ('L-B9FB65B0', 'Knowledge bases per account', lambda c: dict(usage=len(c.call('wisdom', 'list_knowledge_bases', 'knowledgeBaseSummaries')), source='wisdom:ListKnowledgeBases', method='ACCOUNT_COUNT')),
        ('L-5558F50C', 'Assistants per account', lambda c: dict(usage=len(c.call('wisdom', 'list_assistants', 'assistantSummaries')), source='wisdom:ListAssistants', method='ACCOUNT_COUNT')),
        ('L-80B507B3', 'Content per knowledge base', wisdom_content_per_knowledge_base),
    ],
    'sso': [
        ('L-B44C7A29', 'Permission sets allowed in IAM Identity Center', lambda c: dict(usage=_permission_sets(c), source='sso-admin:ListPermissionSets', method='ACCOUNT_COUNT')),
        ('L-89954265', 'Permission sets allowed per AWS account', lambda c: dict(usage=_permission_sets(c), source='sso-admin:ListPermissionSets', method='ACCOUNT_COUNT')),
        ('L-7E1D4E33', 'Groups supported in IAM Identity Center', lambda c: dict(usage=_identity_store_count(c, 'list_groups'), source='identitystore:ListGroups', method='ACCOUNT_COUNT')),
        ('L-3C8D41A0', 'Users supported in IAM Identity Center', lambda c: dict(usage=_identity_store_count(c, 'list_users'), source='identitystore:ListUsers', method='ACCOUNT_COUNT')),
    ],
    'social-messaging': [('L-8479D5F2', 'WhatsApp Business Accounts per account', lambda c: dict(usage=len(c.call('socialmessaging', 'list_linked_whatsapp_business_accounts', 'linkedAccounts')), source='socialmessaging:ListLinkedWhatsAppBusinessAccounts', method='ACCOUNT_COUNT'))],
    'ssm-quicksetup': [('L-D1C554CF', 'Configuration managers per account', lambda c: dict(usage=len(c.call('ssm-quicksetup', 'list_configuration_managers', 'ConfigurationManagersList')), source='ssm-quicksetup:ListConfigurationManagers', method='ACCOUNT_COUNT'))],
    'ssm-sap': [('L-C8103580', 'SAP applications per Region in account', lambda c: dict(usage=len(c.call('ssm-sap', 'list_applications', 'Applications')), source='ssm-sap:ListApplications', method='ACCOUNT_COUNT'))],
    'glacier': [('L-D1C67346', 'Vaults per account', lambda c: dict(usage=len(c.call('glacier', 'list_vaults', 'VaultList')), source='glacier:ListVaults', method='ACCOUNT_COUNT'))],
    'dataexchange': [('L-52E2E63A', 'Data sets per account', lambda c: dict(usage=len(c.call('dataexchange', 'list_data_sets', 'DataSets')), source='dataexchange:ListDataSets', method='ACCOUNT_COUNT'))],
    'rbin': [('L-629917A2', 'Rules per Region', lambda c: dict(usage=len(c.call('rbin', 'list_rules', 'Rules')), source='rbin:ListRules', method='ACCOUNT_COUNT'))],
    'dlm': [('L-5407D8DA', 'Policies per Region', lambda c: dict(usage=len(c.call('dlm', 'get_lifecycle_policies', 'Policies')), source='dlm:GetLifecyclePolicies', method='ACCOUNT_COUNT'))],
    'ssm-contacts': [
        ('L-7DD2017D', 'Contacts per account', lambda c: dict(usage=len(c.call('ssm-contacts', 'list_contacts', 'Contacts')), source='ssm-contacts:ListContacts', method='ACCOUNT_COUNT')),
        ('L-4EA3AB3A', 'Rotations per account', lambda c: dict(usage=len(c.call('ssm-contacts', 'list_rotations', 'Rotations')), source='ssm-contacts:ListRotations', method='ACCOUNT_COUNT')),
    ],
    'wellarchitected': [
        ('L-D69BFA30', 'Review templates per account per Region', lambda c: dict(usage=len(c.call('wellarchitected', 'list_review_templates', 'ReviewTemplates')), source='wellarchitected:ListReviewTemplates', method='ACCOUNT_COUNT')),
        ('L-BAE0003F', 'Lenses per account per Region', lambda c: dict(usage=len(c.call('wellarchitected', 'list_lenses', 'LensSummaries')), source='wellarchitected:ListLenses', method='ACCOUNT_COUNT')),
        ('L-ACECEBBD', 'Workloads per account per Region', lambda c: dict(usage=len(c.call('wellarchitected', 'list_workloads', 'WorkloadSummaries')), source='wellarchitected:ListWorkloads', method='ACCOUNT_COUNT')),
        ('L-B9D3FEAA', 'Lenses per review template', review_template_lenses),
        ('L-66BC6D27', 'Lenses per workload', workload_lenses),
        ('L-CA783EAE', 'Milestones per workload', milestones_per_workload),
    ],
}

def get_current_quotastatus_misc(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    results = []
    for service, checks in CHECKS.items():
        if any(s == service for s, _ in context.quotas):
            results.extend(context.run(service, checks, skip))
    return results
