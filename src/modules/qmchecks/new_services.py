"""Resource-count quotas for newer AWS control-plane services."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def count(api, method, key):
    return lambda c: dict(usage=len(c.call(api, method, key)),
                          source=f'{api}:{method}', method='ACCOUNT_COUNT')


def lattice_listeners_per_service(c):
    values = []
    for service in c.call('vpc-lattice', 'list_services', 'items'):
        sid = service.get('id')
        if sid:
            values.append((sid, len(c.call('vpc-lattice', 'list_listeners', 'items',
                                           serviceIdentifier=sid)), None))
    return maximum(values, 'VPCService', 'vpc-lattice:ListListeners')


def lattice_target_groups_per_service(c):
    counts = {}
    for target_group in c.call('vpc-lattice', 'list_target_groups', 'items'):
        for service_arn in target_group.get('serviceArns', []):
            counts[service_arn] = counts.get(service_arn, 0) + 1
    return maximum([(arn, count, None) for arn, count in counts.items()],
                   'VPCService', 'vpc-lattice:ListTargetGroups')


def lattice_rules_per_listener(c):
    values = []
    for service in c.call('vpc-lattice', 'list_services', 'items'):
        sid = service.get('id')
        if not sid:
            continue
        for listener in c.call('vpc-lattice', 'list_listeners', 'items', serviceIdentifier=sid):
            lid = listener.get('id')
            if lid:
                values.append((lid, len(c.call('vpc-lattice', 'list_rules', 'items',
                                                serviceIdentifier=sid,
                                                listenerIdentifier=lid)), None))
    return maximum(values, 'VPCListener', 'vpc-lattice:ListRules')


def get_current_quotastatus_new_services(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    entries = []
    if any(service == 'vpc-lattice' for service, _ in context.quotas):
        entries.extend(context.run('vpc-lattice', [
            ('L-9CAD07FB', 'Service networks per region', count('vpc-lattice', 'list_service_networks', 'items')),
            ('L-620C821E', 'Services per region', count('vpc-lattice', 'list_services', 'items')),
            ('L-BB11C6B9', 'Target groups per region', count('vpc-lattice', 'list_target_groups', 'items')),
            ('L-D64E952E', 'Listeners per service', lattice_listeners_per_service),
            ('L-3DEC3B9F', 'Target groups per service', lattice_target_groups_per_service),
            ('L-CF78395E', 'Rules per listener', lattice_rules_per_listener),
        ], skip))
    if any(service == 'thinclient' for service, _ in context.quotas):
        entries.extend(context.run('thinclient', [
            ('L-64C2BDF4', 'Number of Environments', count('workspaces-thin-client', 'list_environments', 'environments')),
        ], skip))
    return entries
