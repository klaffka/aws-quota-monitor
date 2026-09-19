"""AWS License Manager configuration, license, grant and token quotas.

The instance aggregation quotas count what License Manager tracks across an
organization rather than a listable inventory, `Total number counted entitlements
per checkout` bounds a single checkout, and `GetAccessTokens calls` is a rate.

The asset group and ruleset scopes need no call of their own: both listings
return the whole object rather than a summary, so the rules of a ruleset and the
rulesets a group associates arrive with the inventory the account counts already
read.
"""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

LICENSE_MANAGER = 'license-manager'
# An entitlement is counted when its unit is a plain count; the other units
# meter capacity and are not consumed per checkout.
COUNTED_UNITS = {'Count'}


def _count(method, key, source):
    return lambda ctx: dict(usage=len(ctx.call(LICENSE_MANAGER, method, key)),
                            source=source, method='ACCOUNT_COUNT')


def licenses(ctx):
    found = {}
    for license_ in ctx.call(LICENSE_MANAGER, 'list_licenses', 'Licenses'):
        arn = license_.get('LicenseArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('License is missing its ARN')
        found[arn] = license_
    return found


def _entitlements(counted):
    """Split each license's entitlements by whether their unit is a count."""
    def check(ctx):
        values = []
        for arn, license_ in licenses(ctx).items():
            entitlements = license_.get('Entitlements')
            if not isinstance(entitlements, list):
                raise NoData('License has no entitlements')
            usage = 0
            for entitlement in entitlements:
                unit = entitlement.get('Unit')
                if not isinstance(unit, str) or not unit:
                    raise NoData('License entitlement has no unit')
                usage += (unit in COUNTED_UNITS) is counted
            values.append((arn, usage, None))
        return maximum(values, 'License', 'license-manager:ListLicenses')
    return check


def grants_per_license(ctx):
    counts = Counter({arn: 0 for arn in licenses(ctx)})
    for grant in ctx.call(LICENSE_MANAGER, 'list_distributed_grants', 'Grants'):
        arn = grant.get('LicenseArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('License grant names no license')
        counts[arn] += 1
    return maximum(((arn, count, None) for arn, count in counts.items()),
                   'License', 'license-manager:ListDistributedGrants')


def tokens_per_license(ctx):
    counts = Counter({arn: 0 for arn in licenses(ctx)})
    for token in ctx.call(LICENSE_MANAGER, 'list_tokens', 'Tokens'):
        arn = token.get('LicenseArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('License token names no license')
        counts[arn] += 1
    return maximum(((arn, count, None) for arn, count in counts.items()),
                   'License', 'license-manager:ListTokens')


def received_licenses_per_product(ctx):
    counts = Counter()
    for license_ in ctx.call(LICENSE_MANAGER, 'list_received_licenses', 'Licenses'):
        product = license_.get('ProductName')
        if not isinstance(product, str) or not product:
            raise NoData('Received license names no product')
        counts[product] += 1
    return maximum(((product, count, None) for product, count in counts.items()),
                   'LicenseProduct', 'license-manager:ListReceivedLicenses')


def associations_per_resource(ctx):
    """Invert the per-configuration listing, the only direction AWS offers."""
    counts = Counter()
    for configuration in ctx.call(LICENSE_MANAGER, 'list_license_configurations',
                                  'LicenseConfigurations'):
        arn = configuration.get('LicenseConfigurationArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('License configuration is missing its ARN')
        for association in ctx.call(LICENSE_MANAGER,
                                    'list_associations_for_license_configuration',
                                    'LicenseConfigurationAssociations',
                                    LicenseConfigurationArn=arn):
            resource = association.get('ResourceArn')
            if not isinstance(resource, str) or not resource:
                raise NoData('License configuration association names no resource')
            counts[resource] += 1
    return maximum(((resource, count, None) for resource, count in counts.items()),
                   'LicensedResource',
                   'license-manager:ListAssociationsForLicenseConfiguration')


def _asset_maximum(method, key, field, resource_type):
    """Measure one list carried by the objects a listing already returns."""
    def check(ctx):
        values = []
        for item in ctx.call(LICENSE_MANAGER, method, key):
            arn = item.get(f'{resource_type}Arn')
            if not isinstance(arn, str) or not arn:
                raise NoData(f'License Manager {key} entry is missing its ARN')
            held = item.get(field) or []
            if not isinstance(held, list):
                raise NoData(f'License Manager {key} entry has an invalid {field} list')
            values.append((arn, len(held), None))
        return maximum(values, resource_type,
                       f'license-manager:{"".join(part.title() for part in method.split("_"))}')
    return check


CHECKS = [
    ('L-CDB75D7A', 'License configurations',
     _count('list_license_configurations', 'LicenseConfigurations',
            'license-manager:ListLicenseConfigurations')),
    ('L-9FBEFBCB', 'Number of Report generators',
     _count('list_license_manager_report_generators', 'ReportGenerators',
            'license-manager:ListLicenseManagerReportGenerators')),
    ('L-C45FDCC5', 'Number of licenses you can create',
     lambda ctx: dict(usage=len(licenses(ctx)),
                      source='license-manager:ListLicenses', method='ACCOUNT_COUNT')),
    ('L-D603D41E', 'License asset groups per account',
     _count('list_license_asset_groups', 'LicenseAssetGroups',
            'license-manager:ListLicenseAssetGroups')),
    ('L-9FC671A7', 'Custom license asset rulesets per account',
     _count('list_license_asset_rulesets', 'LicenseAssetRulesets',
            'license-manager:ListLicenseAssetRulesets')),
    ('L-A6872F54', 'Rules per custom license asset ruleset',
     _asset_maximum('list_license_asset_rulesets', 'LicenseAssetRulesets',
                    'Rules', 'LicenseAssetRuleset')),
    ('L-60C1FE55', 'License asset rulesets per asset group',
     _asset_maximum('list_license_asset_groups', 'LicenseAssetGroups',
                    'AssociatedLicenseAssetRulesetARNs', 'LicenseAssetGroup')),
    ('L-55F04DE6', 'Number of grants per license', grants_per_license),
    ('L-992B7443', 'Number of tokens per account and license', tokens_per_license),
    ('L-48BF1E76', 'Number of received licenses per product',
     received_licenses_per_product),
    ('L-0B08C8C5', 'License configuration associations per resource',
     associations_per_resource),
    ('L-D92A2CE4', 'Total number counted entitlements per license',
     _entitlements(True)),
    ('L-CA3CD2C4', 'Total number uncounted entitlements per license',
     _entitlements(False)),
]


def get_current_quotastatus_license_manager(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'license-manager' for service, _ in context.quotas):
        return []
    return context.run('license-manager', CHECKS, skip)
