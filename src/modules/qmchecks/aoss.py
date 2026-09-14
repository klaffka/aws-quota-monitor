"""Amazon OpenSearch Serverless policy, group, and capacity quotas."""
import json

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def identity(item, field='name'):
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise NoData(f'OpenSearch Serverless inventory is missing {field}')
    return value


def inventory(ctx, method, key, **kwargs):
    result = {}
    for item in ctx.call('opensearchserverless', method, key, **kwargs):
        name = identity(item, 'id' if method == 'list_security_configs' else 'name')
        if name in result and result[name] != item:
            raise NoData('OpenSearch Serverless inventory changed during pagination')
        result[name] = item
    return [result[name] for name in sorted(result)]


def count(ctx, method, key, **kwargs):
    return dict(usage=len(inventory(ctx, method, key, **kwargs)),
                source=f'opensearchserverless:{method}', method='ACCOUNT_COUNT')


def document_bytes(value):
    if isinstance(value, str):
        return len(value.encode('utf-8'))
    if not isinstance(value, (dict, list)):
        raise NoData('OpenSearch Serverless policy has no JSON document')
    return len(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))


def policy_size(ctx, kind):
    configs = {
        'encryption': ('list_security_policies', 'securityPolicySummaries',
                       'get_security_policy', 'securityPolicyDetail'),
        'network': ('list_security_policies', 'securityPolicySummaries',
                    'get_security_policy', 'securityPolicyDetail'),
        'data': ('list_access_policies', 'accessPolicySummaries',
                 'get_access_policy', 'accessPolicyDetail'),
    }
    list_method, list_key, get_method, detail_key = configs[kind]
    values = []
    for summary in inventory(ctx, list_method, list_key, type=kind):
        name = identity(summary)
        detail = ctx.call('opensearchserverless', get_method, type=kind, name=name).get(detail_key)
        if not isinstance(detail, dict) or detail.get('name') != name or detail.get('type') != kind:
            raise NoData('OpenSearch Serverless policy detail is inconsistent')
        values.append((name, document_bytes(detail.get('policy')), None))
    return maximum(values, 'AossPolicy',
                   f'opensearchserverless:{list_method}+{get_method}')


def retention_policy_size(ctx):
    summaries = inventory(ctx, 'list_lifecycle_policies', 'lifecyclePolicySummaries',
                          type='retention')
    values = []
    for offset in range(0, len(summaries), 20):
        requested = [{'type': 'retention', 'name': identity(item)}
                     for item in summaries[offset:offset + 20]]
        response = ctx.call('opensearchserverless', 'batch_get_lifecycle_policy',
                            identifiers=requested)
        if response.get('lifecyclePolicyErrorDetails'):
            raise NoData('OpenSearch Serverless lifecycle-policy batch was incomplete')
        details = response.get('lifecyclePolicyDetails')
        if not isinstance(details, list):
            raise NoData('OpenSearch Serverless lifecycle-policy batch has no details')
        returned = set()
        for detail in details:
            name = identity(detail)
            if detail.get('type') != 'retention' or name not in {x['name'] for x in requested}:
                raise NoData('OpenSearch Serverless lifecycle-policy detail is inconsistent')
            returned.add(name)
            values.append((name, document_bytes(detail.get('policy')), None))
        if returned != {x['name'] for x in requested}:
            raise NoData('OpenSearch Serverless lifecycle-policy batch omitted a policy')
    return maximum(values, 'AossPolicy',
                   'opensearchserverless:ListLifecyclePolicies+BatchGetLifecyclePolicy')


def security_configs(ctx, kind):
    return inventory(ctx, 'list_security_configs', 'securityConfigSummaries', type=kind)


def security_config_size(ctx, kind):
    field = 'samlOptions' if kind == 'saml' else 'iamIdentityCenterOptions'
    values = []
    for summary in security_configs(ctx, kind):
        identifier = identity(summary, 'id')
        detail = ctx.call('opensearchserverless', 'get_security_config', id=identifier).get(
            'securityConfigDetail')
        if not isinstance(detail, dict) or detail.get('id') != identifier or detail.get('type') != kind:
            raise NoData('OpenSearch Serverless security-config detail is inconsistent')
        options = detail.get(field)
        if not isinstance(options, dict):
            raise NoData('OpenSearch Serverless security config has no options')
        size = (len(options.get('metadata', '').encode('utf-8')) if kind == 'saml'
                else document_bytes(options))
        values.append((identifier, size, None))
    return maximum(values, 'AossSecurityConfig',
                   'opensearchserverless:ListSecurityConfigs+GetSecurityConfig')


def collection_groups(ctx):
    groups = inventory(ctx, 'list_collection_groups', 'collectionGroupSummaries')
    for group in groups:
        if group.get('generation') not in {'CLASSIC', 'NEXTGEN'}:
            raise NoData('OpenSearch Serverless collection group has an unknown generation')
        count_value = group.get('numberOfCollections')
        if not isinstance(count_value, int) or isinstance(count_value, bool) or count_value < 0:
            raise NoData('OpenSearch Serverless collection group has an invalid collection count')
        if not isinstance(group.get('capacityLimits'), dict):
            raise NoData('OpenSearch Serverless collection group has no capacity limits')
    return groups


def collections_per_group(ctx, generation):
    values = [(identity(group), group['numberOfCollections'], None)
              for group in collection_groups(ctx) if group['generation'] == generation]
    return maximum(values, 'AossCollectionGroup', 'opensearchserverless:ListCollectionGroups')


def group_capacity(ctx, field):
    values = []
    for group in collection_groups(ctx):
        value = group['capacityLimits'].get(field, 96)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            raise NoData('OpenSearch Serverless collection group has an invalid capacity limit')
        values.append((identity(group), value, None))
    return maximum(values, 'AossCollectionGroup', 'opensearchserverless:ListCollectionGroups')


def account_capacity(ctx, field):
    detail = ctx.call('opensearchserverless', 'get_account_settings').get('accountSettingsDetail')
    limits = detail.get('capacityLimits') if isinstance(detail, dict) else None
    value = limits.get(field, 10) if isinstance(limits, dict) else 10
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        raise NoData('OpenSearch Serverless account has an invalid capacity limit')
    return dict(usage=value, source='opensearchserverless:GetAccountSettings', method='ACCOUNT_SETTING')


def allocated_capacity(ctx, field):
    account = account_capacity(ctx, field)['usage']
    # Empty groups do not consume or enforce their configured OCU limits.
    usage = account + sum(group['capacityLimits'].get(field, 96)
                          for group in collection_groups(ctx) if group['numberOfCollections'])
    return dict(usage=usage, source='opensearchserverless:GetAccountSettings+ListCollectionGroups',
                method='ACCOUNT_SUM')


CHECKS = [
    ('L-1D4405ED', 'SAML providers per region', lambda c: count(c, 'list_security_configs', 'securityConfigSummaries', type='saml')),
    ('L-92280D4D', 'Network policies per region', lambda c: count(c, 'list_security_policies', 'securityPolicySummaries', type='network')),
    ('L-3EDA8079', 'Encryption policies per region', lambda c: count(c, 'list_security_policies', 'securityPolicySummaries', type='encryption')),
    ('L-C3AEE11F', 'Data access policies per region', lambda c: count(c, 'list_access_policies', 'accessPolicySummaries', type='data')),
    ('L-F447691F', 'Retention policies', lambda c: count(c, 'list_lifecycle_policies', 'lifecyclePolicySummaries', type='retention')),
    ('L-993355FF', 'Maximum collection groups', lambda c: count(c, 'list_collection_groups', 'collectionGroupSummaries')),
    ('L-2005AF7E', 'Encryption policy size per policy', lambda c: policy_size(c, 'encryption')),
    ('L-877395DB', 'Network policy size per policy', lambda c: policy_size(c, 'network')),
    ('L-81F90FD2', 'Data access policy size per policy', lambda c: policy_size(c, 'data')),
    ('L-7077B8EB', 'Retention policy size', retention_policy_size),
    ('L-380319CD', 'SAML provider size per policy', lambda c: security_config_size(c, 'saml')),
    ('L-51EC5B57', 'IAM Identity Center security config size', lambda c: security_config_size(c, 'iamidentitycenter')),
    ('L-D5F2517B', 'IAM Identity Center applications', lambda c: count(c, 'list_security_configs', 'securityConfigSummaries', type='iamidentitycenter')),
    ('L-1A85D401', 'Collections per Collection Group (Classic)', lambda c: collections_per_group(c, 'CLASSIC')),
    ('L-E04A9F70', 'Collections per Collection Group (NextGen)', lambda c: collections_per_group(c, 'NEXTGEN')),
    ('L-50FA809B', 'Default indexing MAX OCU setting', lambda c: account_capacity(c, 'maxIndexingCapacityInOCU')),
    ('L-4E98D4EB', 'Default search MAX OCU setting', lambda c: account_capacity(c, 'maxSearchCapacityInOCU')),
    ('L-FBAA6E20', 'Default indexing MAX Collection Group OCU setting', lambda c: group_capacity(c, 'maxIndexingCapacityInOCU')),
    ('L-1F7A5B5B', 'Default search MAX Collection Group OCU setting', lambda c: group_capacity(c, 'maxSearchCapacityInOCU')),
    ('L-B813BFF3', 'Maximum indexing capacity (OCUs)', lambda c: allocated_capacity(c, 'maxIndexingCapacityInOCU')),
    ('L-B0736F4C', 'Maximum search capacity (OCUs)', lambda c: allocated_capacity(c, 'maxSearchCapacityInOCU')),
]


def get_current_quotastatus_aoss(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'aoss' for service, _ in context.quotas):
        return []
    return context.run('aoss', CHECKS, skip)
