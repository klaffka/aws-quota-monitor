"""AWS Telco Network Builder package, instance and operation quotas."""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

TNB = 'tnb'
OPERATION_STATES = {'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLING', 'CANCELLED'}
ONGOING_STATES = {'PROCESSING', 'CANCELLING'}


def _inventory(method, key, subject):
    def check(ctx):
        found = set()
        for item in ctx.call(TNB, method, key):
            identity = item.get('id')
            if not isinstance(identity, str) or not identity:
                raise NoData(f'Telco Network Builder {subject} is missing its identity')
            found.add(identity)
        return dict(usage=len(found), source=f'tnb:{_operation(method)}',
                    method='ACCOUNT_COUNT')
    return check


def _operation(method):
    return ''.join(part.capitalize() if part != 'sol' else 'Sol'
                   for part in method.split('_'))


def ongoing_operations(ctx):
    usage = 0
    for operation in ctx.call(TNB, 'list_sol_network_operations', 'networkOperations'):
        state = operation.get('operationState')
        if state not in OPERATION_STATES:
            raise NoData('Telco Network Builder operation has an unknown state')
        usage += state in ONGOING_STATES
    return dict(usage=usage, source='tnb:ListSolNetworkOperations',
                method='ACCOUNT_COUNT')


CHECKS = [
    ('L-08069DBD', 'Function packages',
     _inventory('list_sol_function_packages', 'functionPackages', 'function package')),
    ('L-3328748B', 'Network packages',
     _inventory('list_sol_network_packages', 'networkPackages', 'network package')),
    ('L-C92FB107', 'Network service instances',
     _inventory('list_sol_network_instances', 'networkInstances', 'network instance')),
    ('L-81A3E723', 'Concurrent ongoing network service operations', ongoing_operations),
]


def get_current_quotastatus_tnb(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'tnb' for service, _ in context.quotas):
        return []
    return context.run('tnb', CHECKS, skip)
