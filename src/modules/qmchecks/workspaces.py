"""Amazon WorkSpaces regional resource inventories."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def count(ctx, method, key):
    return dict(usage=len(ctx.call('workspaces', method, key)), source=f'workspaces:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-18CE281C', 'Images', lambda ctx: count(ctx, 'describe_workspace_images', 'Images')),
    ('L-843E43DA', 'Bundles', lambda ctx: count(ctx, 'describe_workspace_bundles', 'Bundles')),
    ('L-34278094', 'WorkSpaces', lambda ctx: count(ctx, 'describe_workspaces', 'Workspaces')),
    ('L-EEB759DE', 'Directories', lambda ctx: count(ctx, 'describe_workspace_directories', 'Directories')),
    ('L-0E312A12', 'IP access control groups', lambda ctx: count(ctx, 'describe_ip_groups', 'Result')),
    ('L-F61D0B79', 'IP access control groups per directory',
     lambda ctx: maximum(
         [(d.get('DirectoryId'), len(d.get('IpGroupIds', [])), None)
          for d in ctx.call('workspaces', 'describe_workspace_directories', 'Directories')],
         'Directory', 'workspaces:DescribeWorkspaceDirectories')),
    ('L-5782CB4D', 'Rules per IP access control group',
     lambda ctx: maximum(
         [(g.get('GroupId'), len(g.get('UserRules', [])), None)
          for g in ctx.call('workspaces', 'describe_ip_groups', 'Result')],
         'IPAccessControlGroup', 'workspaces:DescribeIpGroups')),
    ('L-0798A2C9', 'Connection aliases', lambda ctx: count(ctx, 'describe_connection_aliases', 'ConnectionAliases')),
]


def get_current_quotastatus_workspaces(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'workspaces' for service, _ in context.quotas): return []
    return context.run('workspaces', CHECKS, skip)
