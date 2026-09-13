"""Systems Manager parameter quotas backed by the parameter inventory."""
from collections import defaultdict
from functools import partial
import re

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def parameters(ctx):
    return ctx.call('ssm', 'describe_parameters', 'Parameters')


def count_tier(ctx, tier):
    # The API omits Tier only for legacy standard parameters. Treating an
    # omitted tier as Standard follows the SSM API's default.
    return dict(usage=sum(p.get('Tier', 'Standard') == tier for p in parameters(ctx)),
                source='ssm:DescribeParameters', method='ACCOUNT_COUNT',
                meta={'tier': tier})


def documents(ctx):
    return ctx.call('ssm', 'list_documents', 'DocumentIdentifiers', Filters=[{'Key': 'Owner', 'Values': ['Self']}])


def required_id(item, field):
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise NoData(f'SSM inventory is missing {field}')
    return value


def version_total(items, parent, parent_field, version_field):
    versions = set()
    for item in items:
        if parent_field in item and item[parent_field] != parent:
            raise NoData('SSM version inventory contains another parent')
        version = required_id(item, version_field)
        if not re.fullmatch(r'[1-9][0-9]*', version):
            raise NoData('SSM version inventory has an unknown version')
        versions.add(version)
    if not versions:
        raise NoData('Existing SSM resource has an empty version inventory')
    return len(versions)


def document_versions(ctx, packages_only=False):
    values = []
    for document in documents(ctx):
        if packages_only:
            kind = required_id(document, 'DocumentType')
            if kind != 'Package':
                continue
        name = required_id(document, 'Name')
        versions = ctx.call('ssm', 'list_document_versions', 'DocumentVersions', Name=name)
        values.append((name, version_total(versions, name, 'Name', 'DocumentVersion'), None))
    return maximum(values, 'SSMDocument', 'ssm:ListDocuments+ListDocumentVersions')


def association_versions(ctx):
    values = []
    for association in associations(ctx):
        identity = required_id(association, 'AssociationId')
        versions = ctx.call('ssm', 'list_association_versions', 'AssociationVersions', AssociationId=identity)
        values.append((identity, version_total(versions, identity, 'AssociationId', 'AssociationVersion'), None))
    return maximum(values, 'SSMAssociation', 'ssm:ListAssociations+ListAssociationVersions')


def parameter_policies(ctx):
    values = []
    for parameter in parameters(ctx):
        tier = parameter.get('Tier', 'Standard')
        if tier not in {'Standard', 'Advanced'}:
            raise NoData('SSM parameter has an unknown tier')
        if tier != 'Advanced':
            continue
        name = required_id(parameter, 'Name')
        policies = parameter.get('Policies', [])
        if not isinstance(policies, list) or any(not isinstance(p, dict) for p in policies):
            raise NoData('SSM parameter has an invalid policy list')
        # All attached policies consume configuration slots, including failed
        # and finished policies. No parameter values are read; policy text
        # returned in metadata is not copied into measurements.
        values.append((name, len(policies), None))
    return maximum(values, 'SSMParameter', 'ssm:DescribeParameters')


def document_permissions(ctx, name):
    accounts, tokens, kwargs = set(), set(), {'Name': name, 'PermissionType': 'Share'}
    while True:
        page = ctx.call('ssm', 'describe_document_permission', **kwargs)
        if not any(key in page for key in ('AccountIds', 'AccountSharingInfoList')):
            raise NoData('SSM document permission response has no sharing inventory')
        direct = page.get('AccountIds', [])
        details = page.get('AccountSharingInfoList', [])
        if not isinstance(direct, list) or not isinstance(details, list):
            raise NoData('SSM document permission response has invalid sharing lists')
        # AccountIds is a legacy list limited to 20 entries in the SDK. Read
        # both response lists on every page, then union by account ID.
        ids = direct + [required_id(item, 'AccountId') for item in details]
        for identity in ids:
            if not isinstance(identity, str) or not re.fullmatch(r'(?i:all)|[0-9]{12}', identity):
                raise NoData('SSM document permission has an unknown account identity')
            accounts.add(identity.lower())
        token = page.get('NextToken')
        if not token:
            return accounts
        if not isinstance(token, str) or token in tokens:
            raise NoData('SSM document permission pagination did not advance')
        tokens.add(token)
        kwargs['NextToken'] = token


def document_shares(ctx, public=False):
    names = {required_id(document, 'Name') for document in documents(ctx)}
    values, public_count = [], 0
    for name in sorted(names):
        accounts = document_permissions(ctx, name)
        public_count += 'all' in accounts
        values.append((name, len(accounts - {'all'}), None))
    if public:
        return dict(usage=public_count, source='ssm:DescribeDocumentPermission', method='ACCOUNT_COUNT')
    return maximum(values, 'SSMDocument', 'ssm:DescribeDocumentPermission')


def maintenance_windows(ctx):
    return ctx.call('ssm', 'describe_maintenance_windows', 'WindowIdentities')


def patch_baselines(ctx):
    return ctx.call('ssm', 'describe_patch_baselines', 'BaselineIdentities')


def associations(ctx):
    return ctx.call('ssm', 'list_associations', 'Associations')


def patch_groups_per_baseline(ctx):
    groups = defaultdict(set)
    for mapping in ctx.call('ssm', 'describe_patch_groups', 'Mappings'):
        baseline = mapping.get('BaselineIdentity', {}).get('BaselineId')
        patch_group = mapping.get('PatchGroup')
        if baseline and patch_group:
            groups[baseline].add(patch_group)
    return maximum([(baseline, len(names), None) for baseline, names in groups.items()],
                   'PatchBaseline', 'ssm:DescribePatchGroups')


def maintenance_window_children(ctx, method, key, quota_type, source):
    values = []
    for window in maintenance_windows(ctx):
        wid = window.get('WindowId')
        if wid:
            values.append((wid, len(ctx.call('ssm', method, key, WindowId=wid)), None))
    return maximum(values, 'MaintenanceWindow', source)


ALL_CHECKS = [
    ('L-C3B871CB', 'Standard parameters', lambda ctx: count_tier(ctx, 'Standard')),
    ('L-527D1CD8', 'Advanced parameters', lambda ctx: count_tier(ctx, 'Advanced')),
    ('L-60D2045D', 'Systems Manager SSM documents',
     lambda ctx: dict(usage=len(documents(ctx)), source='ssm:ListDocuments', method='ACCOUNT_COUNT')),
    ('L-7727CE5B', 'Maintenance Windows',
     lambda ctx: dict(usage=len(maintenance_windows(ctx)), source='ssm:DescribeMaintenanceWindows', method='ACCOUNT_COUNT')),
    ('L-218CDBD4', 'Patch baselines',
     lambda ctx: dict(usage=len(patch_baselines(ctx)), source='ssm:DescribePatchBaselines', method='ACCOUNT_COUNT')),
    ('L-01B74EDA', 'Concurrent State Manager associations per region',
     lambda ctx: dict(usage=len(associations(ctx)), source='ssm:ListAssociations', method='ACCOUNT_COUNT')),
    ('L-F4012070', 'Patch groups per patch baseline', patch_groups_per_baseline),
    ('L-3D9CCA6E', 'Tasks per Maintenance Window', lambda c: maintenance_window_children(c, 'describe_maintenance_window_tasks', 'Tasks', 'Task', 'ssm:DescribeMaintenanceWindowTasks')),
    ('L-B1A84B8B', 'Targets per Maintenance Window', lambda c: maintenance_window_children(c, 'describe_maintenance_window_targets', 'Targets', 'Target', 'ssm:DescribeMaintenanceWindowTargets')),
    ('L-E9FF4011', 'Systems Manager document versions per document', document_versions),
]

CHECKS = ALL_CHECKS
EXTENDED_CHECKS = [
    ('L-2D5C8B1F', 'Distributor package versions', partial(document_versions, packages_only=True)),
    ('L-FB5A4449', 'Association versions', association_versions),
    ('L-C84673D4', 'Advanced parameter policies', parameter_policies),
    ('L-F5EE067E', 'Private shares per document', document_shares),
    ('L-E7B4BBE8', 'Publicly shared documents', partial(document_shares, public=True)),
]
ALL_CHECKS = CHECKS + EXTENDED_CHECKS


def get_current_quotastatus_ssm(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'ssm' for service, _ in context.quotas):
        return []
    checks = CHECKS + [check for check in EXTENDED_CHECKS if ('ssm', check[0]) in context.quotas]
    return context.run('ssm', checks, skip)
