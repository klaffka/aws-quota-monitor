"""AWS License Manager user subscription and instance association quotas."""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

LMUS = 'license-manager-user-subscriptions'


def _normalized(value):
    """Compare product names without depending on AWS's spacing or casing."""
    return ''.join(character for character in str(value or '').upper()
                   if character.isalnum())


def identity_providers(ctx):
    found = []
    for summary in ctx.call(LMUS, 'list_identity_providers',
                            'IdentityProviderSummaries'):
        provider = summary.get('IdentityProvider')
        if not isinstance(provider, dict) or not provider:
            raise NoData('User subscription identity provider is missing')
        if provider not in found:
            found.append(provider)
    return found


def _subscriptions_by_product(ctx):
    counts = Counter()
    for provider in identity_providers(ctx):
        for user in ctx.call(LMUS, 'list_product_subscriptions',
                             'ProductUserSummaries', IdentityProvider=provider):
            product = user.get('Product')
            if not isinstance(product, str) or not product:
                raise NoData('Product subscription is missing its product')
            counts[_normalized(product)] += 1
    return counts


def _subscriptions(product):
    def check(ctx):
        usage = _subscriptions_by_product(ctx)[_normalized(product)]
        return dict(usage=usage, source=f'{LMUS}:ListProductSubscriptions',
                    method='ACCOUNT_COUNT')
    return check


def instance_associations_per_user(ctx):
    counts = Counter()
    providers = identity_providers(ctx)
    for instance in ctx.call(LMUS, 'list_instances', 'InstanceSummaries'):
        identity = instance.get('InstanceId')
        if not isinstance(identity, str) or not identity:
            raise NoData('User subscription instance is missing its identity')
        for provider in providers:
            for user in ctx.call(LMUS, 'list_user_associations',
                                 'InstanceUserSummaries', InstanceId=identity,
                                 IdentityProvider=provider):
                username = user.get('Username')
                if not isinstance(username, str) or not username:
                    raise NoData('Instance association is missing its user')
                counts[username] += 1
    return maximum(((username, count, None) for username, count in counts.items()),
                   'LicenseManagerUser', f'{LMUS}:ListUserAssociations')


CHECKS = [
    ('L-792C9CCF', 'User-based subscriptions for Office Professional Plus',
     _subscriptions('Office Professional Plus')),
    ('L-79A245D6', 'User-based subscriptions for Visual Studio Enterprise',
     _subscriptions('Visual Studio Enterprise')),
    ('L-FA5F53F9', 'User-based subscriptions for Visual Studio Professional',
     _subscriptions('Visual Studio Professional')),
    ('L-8BE7CFDB', 'Instance associations per user', instance_associations_per_user),
]


def get_current_quotastatus_license_manager_user_subscriptions(
        session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    service = 'license-manager-user-subscriptions'
    if not any(code == service for code, _ in context.quotas):
        return []
    return context.run(service, CHECKS, skip)
