"""AWS Shield Advanced protection quotas, counted per protected resource type."""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

SHIELD = 'shield'


def protections(ctx):
    found = {}
    for protection in ctx.call(SHIELD, 'list_protections', 'Protections'):
        identity = protection.get('Id')
        if not isinstance(identity, str) or not identity:
            raise NoData('Shield protection is missing its identity')
        arn = protection.get('ResourceArn')
        if not isinstance(arn, str) or not arn.startswith('arn:'):
            raise NoData('Shield protection has no resource ARN')
        found[identity] = arn
    return found


def _protected(service, resource_prefix=None):
    """Count protections whose resource ARN names this service and resource."""
    def check(ctx):
        usage = 0
        for arn in protections(ctx).values():
            parts = arn.split(':', 5)
            if len(parts) < 6:
                raise NoData('Shield protection has a malformed resource ARN')
            if parts[2] != service:
                continue
            usage += resource_prefix is None or parts[5].startswith(resource_prefix)
        return dict(usage=usage, source='shield:ListProtections',
                    method='ACCOUNT_COUNT')
    return check


CHECKS = [
    ('L-0BACF966', 'Elastic IP address protections',
     _protected('ec2', 'eip-allocation/')),
    ('L-BBD47253', 'Elastic Load Balancing load balancer protections',
     _protected('elasticloadbalancing')),
]


def get_current_quotastatus_shield(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'shield' for service, _ in context.quotas):
        return []
    return context.run('shield', CHECKS, skip)
