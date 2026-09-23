"""AWS IoT SiteWise regional resource, model, and hierarchy quotas.

The dashboard and gateway quotas are left open. `DescribeDashboard` returns
`dashboardDefinition` and `DescribeGatewayCapabilityConfiguration` returns
`capabilityConfiguration`, and the service model types both as a plain string
holding a document, so counting the visualizations, their metrics or the OPC UA
sources inside one would mean parsing a format the model does not describe. The
property dependency quotas need the formula expressions of an asset model
resolved against each other, which no operation reports.
"""
from botocore.exceptions import ClientError

from modules.qmcore.aws import CheckContext, NoData, Unsupported, maximum, session_from_env


def required(item, field, subject):
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise NoData(f'IoT SiteWise {subject} is missing {field}')
    return value


def unique(items, field, subject):
    result = {}
    for item in items:
        if not isinstance(item, dict):
            raise NoData(f'IoT SiteWise {subject} inventory contains an invalid item')
        identity = required(item, field, subject)
        if identity in result and result[identity] != item:
            raise NoData(f'IoT SiteWise {subject} inventory changed during pagination')
        result[identity] = item
    return [result[key] for key in sorted(result)]


def count(ctx, method, key):
    return dict(usage=len(ctx.call('iotsitewise', method, key)),
                source=f'iotsitewise:{method}', method='ACCOUNT_COUNT')


def portals(ctx):
    return [required(portal, 'id', 'portal')
            for portal in ctx.call('iotsitewise', 'list_portals', 'portalSummaries')]


def projects(ctx):
    """Return every project id. Projects are listed under one portal at a time,
    and the listing is read in full before descending so the request order does
    not depend on what the caller does with each project."""
    return [(portal, required(project, 'id', 'project'))
            for portal in portals(ctx)
            for project in ctx.call('iotsitewise', 'list_projects', 'projectSummaries',
                                    portalId=portal)]


def projects_per_portal(ctx):
    return maximum([(portal, len(ctx.call('iotsitewise', 'list_projects',
                                          'projectSummaries', portalId=portal)), None)
                    for portal in portals(ctx)],
                   'IoTSiteWisePortal', 'iotsitewise:ListPortals+ListProjects')


def per_project(ctx, method, key):
    return maximum([(project, len(ctx.call('iotsitewise', method, key, projectId=project)), None)
                    for _portal, project in projects(ctx)],
                   'IoTSiteWiseProject', f'iotsitewise:ListProjects+{method}')


def models(ctx, model_types):
    # ListAssetModels rejects INTERFACE combined with another type ("The given
    # filter is not supported"), so each type is listed on its own.
    items = unique([item for model_type in sorted(model_types)
                    for item in ctx.call('iotsitewise', 'list_asset_models', 'assetModelSummaries',
                                         assetModelTypes=[model_type])], 'id', 'model')
    for item in items:
        if item.get('assetModelType') not in model_types:
            raise NoData('IoT SiteWise returned a model of an unexpected type')
    return items


def model_count(ctx, model_types):
    return dict(usage=len(models(ctx, model_types)), source='iotsitewise:ListAssetModels',
                method='ACCOUNT_COUNT')


def model_detail(ctx, model):
    identifier = model['id']
    detail = ctx.call('iotsitewise', 'describe_asset_model', assetModelId=identifier)
    if detail.get('assetModelId') != identifier \
            or detail.get('assetModelType') != model.get('assetModelType'):
        raise NoData('IoT SiteWise model detail is inconsistent')
    status = detail.get('assetModelStatus')
    if not isinstance(status, dict) or status.get('state') != 'ACTIVE':
        raise NoData('IoT SiteWise model configuration is not in a stable ACTIVE state')
    return detail


def model_properties(ctx, model, filter_name):
    items = unique(ctx.call('iotsitewise', 'list_asset_model_properties',
                            'assetModelPropertySummaries', assetModelId=model['id'],
                            filter=filter_name), 'id', 'model property')
    if filter_name == 'BASE' and any(item.get('assetModelCompositeModelId') for item in items):
        raise NoData('IoT SiteWise base-property inventory contains a composite property')
    return items


def properties_per_model(ctx, model_types, filter_name='ALL'):
    values = []
    for model in models(ctx, model_types):
        model_detail(ctx, model)
        values.append((model['id'], len(model_properties(ctx, model, filter_name)), None))
    return maximum(values, 'IoTSiteWiseAssetModel',
                   'iotsitewise:ListAssetModels+DescribeAssetModel+ListAssetModelProperties')


def function_count(expression):
    count = index = 0
    quote = None
    while index < len(expression):
        character = expression[index]
        if quote:
            if character == '\\':
                index += 2
                continue
            if character == quote:
                quote = None
            index += 1
            continue
        if character in {'"', "'"}:
            quote = character
            index += 1
            continue
        if character.isalpha() or character == '_':
            end = index + 1
            while end < len(expression) and (expression[end].isalnum() or expression[end] == '_'):
                end += 1
            following = end
            while following < len(expression) and expression[following].isspace():
                following += 1
            count += following < len(expression) and expression[following] == '('
            index = end
            continue
        index += 1
    if quote:
        raise NoData('IoT SiteWise formula expression has an unterminated string')
    return count


def formula_maximum(ctx, field):
    values = []
    for model in models(ctx, {'ASSET_MODEL', 'COMPONENT_MODEL', 'INTERFACE'}):
        model_detail(ctx, model)
        for prop in model_properties(ctx, model, 'ALL'):
            property_type = prop.get('type')
            if not isinstance(property_type, dict):
                raise NoData('IoT SiteWise property has no valid type')
            formula_kind = ('transform' if 'transform' in property_type else
                            'metric' if 'metric' in property_type else None)
            if formula_kind is None:
                continue
            formula = property_type[formula_kind]
            if not isinstance(formula, dict):
                raise NoData('IoT SiteWise formula property is invalid')
            variables = formula.get('variables', [])
            expression = formula.get('expression', '')
            if not isinstance(variables, list) or any(not isinstance(item, dict) for item in variables) \
                    or not isinstance(expression, str):
                raise NoData('IoT SiteWise formula configuration is incomplete')
            usage = len(variables) if field == 'variables' else function_count(expression)
            values.append((f"{model['id']}/{prop['id']}", usage, None))
    return maximum(values, 'IoTSiteWiseAssetModelProperty',
                   'iotsitewise:ListAssetModels+DescribeAssetModel+ListAssetModelProperties')


def hierarchy_definitions(ctx, model_types):
    values = []
    for model in models(ctx, model_types):
        hierarchies = model_detail(ctx, model).get('assetModelHierarchies')
        if not isinstance(hierarchies, list) or any(not isinstance(item, dict) for item in hierarchies):
            raise NoData('IoT SiteWise model has an invalid hierarchy inventory')
        identities = [required(item, 'id', 'model hierarchy') for item in hierarchies]
        if len(identities) != len(set(identities)):
            raise NoData('IoT SiteWise model has duplicate hierarchy identities')
        for item in hierarchies:
            required(item, 'childAssetModelId', 'model hierarchy')
        values.append((model['id'], len(hierarchies), None))
    return maximum(values, 'IoTSiteWiseAssetModel',
                   'iotsitewise:ListAssetModels+DescribeAssetModel')


def model_graph(ctx, model_types):
    inventory = models(ctx, model_types)
    known = {item['id'] for item in inventory}
    graph = {}
    for model in inventory:
        children = set()
        for hierarchy in model_detail(ctx, model).get('assetModelHierarchies', []):
            child = required(hierarchy, 'childAssetModelId', 'model hierarchy')
            if child not in known:
                raise NoData('IoT SiteWise hierarchy references an unknown model')
            children.add(child)
        graph[model['id']] = children
    return graph


def descendants(graph, root, visiting=None):
    visiting = set() if visiting is None else visiting
    if root in visiting:
        raise NoData('IoT SiteWise model hierarchy contains a cycle')
    result = {root}
    for child in graph[root]:
        result.update(descendants(graph, child, visiting | {root}))
    return result


def depth(graph, root, visiting=None):
    visiting = set() if visiting is None else visiting
    if root in visiting:
        raise NoData('IoT SiteWise model hierarchy contains a cycle')
    return 1 + max((depth(graph, child, visiting | {root}) for child in graph[root]), default=0)


def graph_maximum(ctx, model_types, mode):
    graph = model_graph(ctx, model_types)
    if mode == 'parents':
        parents = {node: set() for node in graph}
        for parent, children in graph.items():
            for child in children:
                parents[child].add(parent)
        values = [(node, len(parent_ids), None) for node, parent_ids in parents.items()]
    else:
        values = [(root, len(descendants(graph, root)) if mode == 'models' else depth(graph, root), None)
                  for root in graph]
    return maximum(values, 'IoTSiteWiseAssetModel',
                   'iotsitewise:ListAssetModels+DescribeAssetModel')


def composite_models(ctx):
    result = []
    for model in models(ctx, {'ASSET_MODEL', 'COMPONENT_MODEL'}):
        model_detail(ctx, model)
        summaries = unique(ctx.call('iotsitewise', 'list_asset_model_composite_models',
                                    'assetModelCompositeModelSummaries', assetModelId=model['id']),
                           'id', 'composite model')
        result.append((model, summaries))
    return result


def composites_per_model(ctx):
    values = [(model['id'], len(summaries), None)
              for model, summaries in composite_models(ctx)]
    return maximum(values, 'IoTSiteWiseAssetModel',
                   'iotsitewise:ListAssetModels+ListAssetModelCompositeModels')


def composite_depth(ctx):
    values = []
    for model, summaries in composite_models(ctx):
        current = 0
        for summary in summaries:
            path = summary.get('path')
            if not isinstance(path, list) or any(not isinstance(item, dict) or not item.get('id')
                                                  for item in path):
                raise NoData('IoT SiteWise composite model has an invalid path')
            current = max(current, len(path) + 1)
        values.append((model['id'], current, None))
    return maximum(values, 'IoTSiteWiseAssetModel',
                   'iotsitewise:ListAssetModels+ListAssetModelCompositeModels')


def properties_per_composite(ctx):
    values = []
    for model in models(ctx, {'COMPONENT_MODEL'}):
        model_detail(ctx, model)
        values.append((model['id'], len(model_properties(ctx, model, 'ALL')), None))
    for model, summaries in composite_models(ctx):
        for summary in summaries:
            composite_id = summary['id']
            detail = ctx.call('iotsitewise', 'describe_asset_model_composite_model',
                              assetModelId=model['id'], assetModelCompositeModelId=composite_id)
            if detail.get('assetModelId') != model['id'] \
                    or detail.get('assetModelCompositeModelId') != composite_id:
                raise NoData('IoT SiteWise composite-model detail is inconsistent')
            properties = detail.get('assetModelCompositeModelProperties')
            if not isinstance(properties, list) or any(not isinstance(item, dict) for item in properties):
                raise NoData('IoT SiteWise composite model has an invalid property inventory')
            property_ids = [required(item, 'id', 'composite property') for item in properties]
            if len(property_ids) != len(set(property_ids)):
                raise NoData('IoT SiteWise composite model has duplicate property identities')
            values.append((f"{model['id']}/{composite_id}", len(properties), None))
    return maximum(values, 'IoTSiteWiseCompositeModel',
                   'iotsitewise:ListAssetModels+ListAssetModelCompositeModels+'
                   'DescribeAssetModelCompositeModel')


def component_model_users(ctx):
    values = []
    for model in models(ctx, {'COMPONENT_MODEL'}):
        relationships = unique(ctx.call('iotsitewise', 'list_composition_relationships',
                                        'compositionRelationshipSummaries', assetModelId=model['id']),
                               'assetModelCompositeModelId', 'composition relationship')
        parent_ids = {required(item, 'assetModelId', 'composition relationship')
                      for item in relationships}
        values.append((model['id'], len(parent_ids), None))
    return maximum(values, 'IoTSiteWiseComponentModel',
                   'iotsitewise:ListAssetModels+ListCompositionRelationships')


def interface_users(ctx):
    values = []
    for model in models(ctx, {'INTERFACE'}):
        relationships = unique(ctx.call('iotsitewise', 'list_interface_relationships',
                                        'interfaceRelationshipSummaries',
                                        interfaceAssetModelId=model['id']),
                               'id', 'interface relationship')
        values.append((model['id'], len(relationships), None))
    return maximum(values, 'IoTSiteWiseInterface',
                   'iotsitewise:ListAssetModels+ListInterfaceRelationships')


def assets_by_model(ctx):
    """Return (model id, its assets) for every asset model. ListAssets lists all
    assets only per model, and assets are created from ASSET_MODEL models only,
    so walking those models is the complete inventory."""
    result = []
    for model in models(ctx, {'ASSET_MODEL'}):
        assets = unique(ctx.call('iotsitewise', 'list_assets', 'assetSummaries',
                                 assetModelId=model['id']), 'id', 'asset')
        if any(asset.get('assetModelId') != model['id'] for asset in assets):
            raise NoData('IoT SiteWise asset belongs to a different model')
        result.append((model['id'], assets))
    return result


def assets_per_model(ctx):
    return maximum([(model, len(assets), None) for model, assets in assets_by_model(ctx)],
                   'IoTSiteWiseAssetModel', 'iotsitewise:ListAssetModels+ListAssets')


def children_per_asset(ctx):
    # A parent can sit anywhere in a hierarchy, so every asset is a candidate,
    # not just the TOP_LEVEL ones.
    assets = unique([asset for _model, items in assets_by_model(ctx) for asset in items],
                    'id', 'asset')
    values = []
    for asset in assets:
        children = unique(ctx.call('iotsitewise', 'list_associated_assets', 'assetSummaries',
                                   assetId=asset['id'], traversalDirection='CHILD'),
                          'id', 'child asset')
        values.append((asset['id'], len(children), None))
    return maximum(values, 'IoTSiteWiseAsset',
                   'iotsitewise:ListAssetModels+ListAssets+ListAssociatedAssets')


def running_bulk_imports(ctx):
    jobs = unique(ctx.call('iotsitewise', 'list_bulk_import_jobs', 'jobSummaries',
                           filter='RUNNING'), 'id', 'bulk import job')
    if any(job.get('status') != 'RUNNING' for job in jobs):
        raise NoData('IoT SiteWise returned a non-running bulk import job')
    return dict(usage=len(jobs), source='iotsitewise:ListBulkImportJobs', method='ACCOUNT_COUNT')


def workspace_inventory(ctx):
    try:
        items = ctx.call('iotsitewise', 'list_workspaces', 'workspaceSummaries')
    except ClientError as exc:
        # Regions where workspaces have not launched answer every call this way.
        error = exc.response.get('Error', {})
        if error.get('Code') == 'InvalidRequestException' \
                and 'This feature is not supported yet' in (error.get('Message') or ''):
            raise Unsupported('IoT SiteWise workspaces are not available in this Region') from None
        raise
    return unique(items, 'name', 'workspace')


def enrichment_jobs(ctx, per_workspace=False):
    workspaces = workspace_inventory(ctx)
    seen = set()
    values = []
    for workspace in workspaces:
        name = workspace['name']
        jobs = unique(ctx.call('iotsitewise', 'list_enrichment_jobs', 'jobs',
                               workspaceName=name, jobType='EVENT_DETECTION'),
                      'jobId', 'enrichment job')
        for job in jobs:
            identity = job['jobId']
            if identity in seen or job.get('workspaceName') not in {None, name} \
                    or job.get('jobType') not in {None, 'EVENT_DETECTION'}:
                raise NoData('IoT SiteWise enrichment-job inventory is inconsistent')
            seen.add(identity)
        values.append((name, len(jobs), None))
    if per_workspace:
        return maximum(values, 'IoTSiteWiseWorkspace',
                       'iotsitewise:ListWorkspaces+ListEnrichmentJobs')
    return dict(usage=sum(value[1] for value in values),
                source='iotsitewise:ListWorkspaces+ListEnrichmentJobs', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-CB5C18A8', 'Asset models per Region per account',
     lambda ctx: model_count(ctx, {'ASSET_MODEL', 'COMPONENT_MODEL'})),
    ('L-A5652910', 'Portals per Region per account', lambda ctx: count(ctx, 'list_portals', 'portalSummaries')),
    ('L-116F669B', 'Number of projects per portal', projects_per_portal),
    ('L-81C6A4F0', 'Number of dashboards per project',
     lambda ctx: per_project(ctx, 'list_dashboards', 'dashboardSummaries')),
    ('L-AF558AF7', 'Number of root assets per project',
     lambda ctx: per_project(ctx, 'list_project_assets', 'assetIds')),
    ('L-179151C6', 'Gateways per Region per account', lambda ctx: count(ctx, 'list_gateways', 'gatewaySummaries')),
    ('L-37C04251', 'Number of interface per Region per account',
     lambda ctx: model_count(ctx, {'INTERFACE'})),
    ('L-D8008DC7', 'Number of properties at root of each asset model of type ASSET_MODEL',
     lambda ctx: properties_per_model(ctx, {'ASSET_MODEL'}, 'BASE')),
    ('L-1526C0DE', 'Number of properties per asset model',
     lambda ctx: properties_per_model(ctx, {'ASSET_MODEL', 'COMPONENT_MODEL'})),
    ('L-002F6D60', 'Number of properties per interface',
     lambda ctx: properties_per_model(ctx, {'INTERFACE'})),
    ('L-23AAE9E6', 'Number of property variables per property formula expression',
     lambda ctx: formula_maximum(ctx, 'variables')),
    ('L-6F52837A', 'Number of functions per property formula expression',
     lambda ctx: formula_maximum(ctx, 'functions')),
    ('L-CEBEAFA0', 'Number of hierarchy definitions per asset model',
     lambda ctx: hierarchy_definitions(ctx, {'ASSET_MODEL'})),
    ('L-622D18F7', 'Number of hierarchy definitions per interface',
     lambda ctx: hierarchy_definitions(ctx, {'INTERFACE'})),
    ('L-E789A464', 'Number of asset models per hierarchy tree',
     lambda ctx: graph_maximum(ctx, {'ASSET_MODEL'}, 'models')),
    ('L-7E24D4D3', 'Depth of asset model hierarchy tree',
     lambda ctx: graph_maximum(ctx, {'ASSET_MODEL'}, 'depth')),
    ('L-A5BAACA9', 'Number of parent asset models per child asset model',
     lambda ctx: graph_maximum(ctx, {'ASSET_MODEL'}, 'parents')),
    ('L-C6919A10', 'Number of interface per hierarchy tree',
     lambda ctx: graph_maximum(ctx, {'INTERFACE'}, 'models')),
    ('L-2AE3919B', 'Depth of interface hierarchy tree',
     lambda ctx: graph_maximum(ctx, {'INTERFACE'}, 'depth')),
    ('L-C90B3537', 'Number of composite models per asset model', composites_per_model),
    ('L-BEF0A9F6', 'Composite model depth', composite_depth),
    ('L-9EE97145', 'Number of properties per composite model', properties_per_composite),
    ('L-0114DD6D', 'Number of unique asset models that use the same component model',
     component_model_users),
    ('L-F1B7F675', 'Number of unique asset models that use the same interface model', interface_users),
    ('L-7D3E8B47', 'Number of assets per asset model', assets_per_model),
    ('L-350DA9CF', 'Number of child assets per parent asset', children_per_asset),
    ('L-1DE0546B', 'Number of concurrent running bulk import jobs', running_bulk_imports),
    ('L-4C1CF6CB', 'Number of event detection enrichment jobs per account', enrichment_jobs),
    ('L-55758B95', 'Number of event detection enrichment jobs for Workspace',
     lambda ctx: enrichment_jobs(ctx, per_workspace=True)),
]


def get_current_quotastatus_sitewise(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'iotsitewise' for service, _ in context.quotas):
        return []
    return context.run('iotsitewise', CHECKS, skip)
