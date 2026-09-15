"""AWS License Manager Linux subscription discovery quota."""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

LINUX_SUBSCRIPTIONS = 'license-manager-linux-subscriptions'


def discovered_resources(ctx):
    found = set()
    for instance in ctx.call(LINUX_SUBSCRIPTIONS, 'list_linux_subscription_instances',
                             'Instances'):
        identity = instance.get('InstanceID')
        if not isinstance(identity, str) or not identity:
            raise NoData('Linux subscription instance is missing its identity')
        found.add(identity)
    return dict(usage=len(found),
                source=f'{LINUX_SUBSCRIPTIONS}:ListLinuxSubscriptionInstances',
                method='ACCOUNT_COUNT')


CHECKS = [('L-5373D1AB', 'Number of discovered resources', discovered_resources)]


def get_current_quotastatus_license_manager_linux_subscriptions(
        session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    service = 'license-manager-linux-subscriptions'
    if not any(code == service for code, _ in context.quotas):
        return []
    return context.run(service, CHECKS, skip)
