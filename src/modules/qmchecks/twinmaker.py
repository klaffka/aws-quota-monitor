"""AWS IoT TwinMaker workspace and component type inventories.

`Components per entity` and the metadata transfer job queue are left to the
audit: components are listed per entity, and a workspace holds tens of
thousands of entities, while ListMetadataTransferJobs requires a source and a
destination type, so a queue total would mean walking every combination. The
component type scopes are different: a workspace holds few component types, so
the detail of each one is read.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

TWINMAKER = 'iottwinmaker'


def workspaces(ctx):
    for workspace in ctx.call(TWINMAKER, 'list_workspaces', 'workspaceSummaries'):
        identity = workspace.get('workspaceId')
        if not isinstance(identity, str) or not identity:
            raise NoData('IoT TwinMaker workspace is missing its identity')
        yield identity


def per_workspace(ctx, method, key):
    return maximum([(identity, len(ctx.call(TWINMAKER, method, key, workspaceId=identity)), None)
                    for identity in workspaces(ctx)],
                   'TwinMakerWorkspace', f'iottwinmaker:ListWorkspaces+{method}')


def _component_types(ctx):
    """Yield (workspace, component type, detail) for every component type."""
    for workspace in workspaces(ctx):
        for summary in ctx.call(TWINMAKER, 'list_component_types', 'componentTypeSummaries',
                                workspaceId=workspace):
            identity = summary.get('componentTypeId')
            if not isinstance(identity, str) or not identity:
                raise NoData('IoT TwinMaker component type is missing its identity')
            detail = ctx.call(TWINMAKER, 'get_component_type', workspaceId=workspace,
                              componentTypeId=identity)
            if detail.get('componentTypeId') != identity:
                raise NoData('IoT TwinMaker component type detail has a different identity')
            yield workspace, identity, detail


def _per_component_type(ctx, member):
    return maximum([(f'{workspace}/{identity}', len(detail.get(member) or ()), None)
                    for workspace, identity, detail in _component_types(ctx)],
                   'TwinMakerComponentType',
                   'iottwinmaker:ListComponentTypes+GetComponentType')


CHECKS = [('L-3BCB51AD', 'Workspaces in this account in the current Region',
           lambda ctx: dict(usage=len(ctx.call(TWINMAKER, 'list_workspaces', 'workspaceSummaries')),
                            source='iottwinmaker:ListWorkspaces', method='ACCOUNT_COUNT')),
          ('L-ADB4D9B9', 'Entities per workspace',
           lambda ctx: per_workspace(ctx, 'list_entities', 'entitySummaries')),
          ('L-8E0F7923', 'Scenes per workspace',
           lambda ctx: per_workspace(ctx, 'list_scenes', 'sceneSummaries')),
          ('L-E97A4C92', 'Component types per workspace',
           lambda ctx: per_workspace(ctx, 'list_component_types', 'componentTypeSummaries')),
          ('L-D8DF6F6C', 'Properties per component type or component',
           lambda ctx: _per_component_type(ctx, 'propertyDefinitions')),
          ('L-0169BFDB', 'Parent component types per child component type',
           lambda ctx: _per_component_type(ctx, 'extendsFrom'))]


def get_current_quotastatus_twinmaker(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == TWINMAKER for service, _ in context.quotas):
        return []
    return context.run(TWINMAKER, CHECKS, skip)
