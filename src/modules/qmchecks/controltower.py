"""AWS Control Tower organizational unit quota.

The two concurrent operation quotas count account and OU operations in flight,
which Control Tower does not list.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

ORGANIZATIONS = 'organizations'


def organizational_units(ctx):
    """Walk the organization tree from its roots, breadth first."""
    found = []
    pending = []
    for root in ctx.call(ORGANIZATIONS, 'list_roots', 'Roots'):
        identity = root.get('Id')
        if not isinstance(identity, str) or not identity:
            raise NoData('Organization root is missing its identity')
        pending.append(identity)
    while pending:
        parent = pending.pop()
        for unit in ctx.call(ORGANIZATIONS, 'list_organizational_units_for_parent',
                             'OrganizationalUnits', ParentId=parent):
            identity = unit.get('Id')
            if not isinstance(identity, str) or not identity:
                raise NoData('Organizational unit is missing its identity')
            if identity in found:
                continue
            found.append(identity)
            pending.append(identity)
    return found


def accounts_per_organizational_unit(ctx):
    values = []
    for unit in organizational_units(ctx):
        accounts = ctx.call(ORGANIZATIONS, 'list_accounts_for_parent', 'Accounts',
                            ParentId=unit)
        for account in accounts:
            if not isinstance(account.get('Id'), str):
                raise NoData('Organization account is missing its identity')
        values.append((unit, len(accounts), None))
    return maximum(values, 'OrganizationalUnit',
                   'organizations:ListAccountsForParent')


CHECKS = [('L-E9464183', 'Number of accounts in a single OU quota',
           accounts_per_organizational_unit)]


def get_current_quotastatus_controltower(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'controltower' for service, _ in context.quotas):
        return []
    return context.run('controltower', CHECKS, skip)
