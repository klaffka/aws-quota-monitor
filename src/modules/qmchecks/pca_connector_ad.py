"""AWS Private CA Connector for Active Directory resource quotas."""
from collections import Counter

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


SERVICE = 'pca-connector-ad'
CONNECTOR_STATES = {'CREATING', 'ACTIVE', 'DELETING', 'FAILED'}
TEMPLATE_STATES = {'ACTIVE', 'DELETING'}


def _validate_arn(arn, ctx, prefix, subject):
    parts = arn.split(':', 5) if isinstance(arn, str) else []
    if (len(parts) != 6 or parts[0] != 'arn' or parts[2] != SERVICE
            or parts[3] != ctx.region or parts[4] != ctx.account
            or not parts[5].startswith(prefix)
            or len(parts[5]) <= len(prefix)):
        raise NoData(f'PCA Connector AD {subject} has an inconsistent ARN')


def connectors(ctx):
    result = {}
    for item in ctx.call(SERVICE, 'list_connectors', 'Connectors'):
        if not isinstance(item, dict):
            raise NoData('PCA Connector AD inventory contains an invalid connector')
        arn = item.get('Arn')
        _validate_arn(arn, ctx, 'connector/', 'connector')
        if item.get('Status') not in CONNECTOR_STATES:
            raise NoData('PCA Connector AD connector has an unknown state')
        if arn in result:
            if result[arn] != item:
                raise NoData('PCA Connector AD connector changed during pagination')
            continue
        result[arn] = item
    return result


def connector_count(ctx):
    return dict(usage=len(connectors(ctx)), source=f'{SERVICE}:ListConnectors',
                method='ACCOUNT_COUNT')


def templates(ctx):
    parents = connectors(ctx)
    result = {}
    for connector_arn, connector in parents.items():
        if connector['Status'] != 'ACTIVE':
            raise NoData('PCA Connector AD connector child inventory is unresolved')
        items = ctx.call(SERVICE, 'list_templates', 'Templates',
                         ConnectorArn=connector_arn)
        for item in items:
            if not isinstance(item, dict):
                raise NoData('PCA Connector AD inventory contains an invalid template')
            arn = item.get('Arn')
            _validate_arn(arn, ctx, f'{connector_arn.split(":", 5)[5]}/template/',
                          'template')
            if (item.get('ConnectorArn') != connector_arn
                    or item.get('Status') not in TEMPLATE_STATES):
                raise NoData('PCA Connector AD template has an inconsistent parent or state')
            if arn in result:
                if result[arn] != item:
                    raise NoData('PCA Connector AD template changed during pagination')
                continue
            result[arn] = item
    return parents, result


def templates_per_connector(ctx):
    parents, items = templates(ctx)
    counts = Counter(item['ConnectorArn'] for item in items.values())
    return maximum(((arn, counts[arn], None) for arn in parents),
                   'PcaConnectorAdConnector',
                   f'{SERVICE}:ListConnectors+ListTemplates')


def access_entries_per_template(ctx):
    _, known_templates = templates(ctx)
    values = []
    for template_arn, template in known_templates.items():
        if template['Status'] != 'ACTIVE':
            raise NoData('PCA Connector AD template child inventory is unresolved')
        entries = {}
        for item in ctx.call(SERVICE, 'list_template_group_access_control_entries',
                             'AccessControlEntries', TemplateArn=template_arn):
            if not isinstance(item, dict):
                raise NoData('PCA Connector AD inventory contains an invalid access entry')
            sid = item.get('GroupSecurityIdentifier')
            if (item.get('TemplateArn') != template_arn
                    or not isinstance(sid, str) or not sid.startswith('S-')):
                raise NoData('PCA Connector AD access entry has an inconsistent parent or SID')
            if sid in entries:
                if entries[sid] != item:
                    raise NoData('PCA Connector AD access entry changed during pagination')
                continue
            entries[sid] = item
        values.append((template_arn, len(entries), None))
    return maximum(values, 'PcaConnectorAdTemplate',
                   f'{SERVICE}:ListConnectors+ListTemplates+'
                   'ListTemplateGroupAccessControlEntries')


CHECKS = [
    ('L-351D0DCC', 'Number of connectors', connector_count),
    ('L-FB47817C', 'Number of templates per connector', templates_per_connector),
    ('L-B2C010E5', 'Number of group access control entries per template',
     access_entries_per_template),
]


def get_current_quotastatus_pca_connector_ad(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == SERVICE for service, _ in context.quotas):
        return []
    return context.run(SERVICE, CHECKS, skip)
