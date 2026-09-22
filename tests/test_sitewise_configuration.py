
from modules.qmchecks.sitewise import (assets_per_model, children_per_asset,
                                       component_model_users, composite_depth,
                                       composites_per_model, enrichment_jobs,
                                       graph_maximum, hierarchy_definitions,
                                       interface_users, model_count,
                                       formula_maximum,
                                       properties_per_composite,
                                       properties_per_model, running_bulk_imports)
from tests.iam_policy import grants


class Context:
    def call(self, service, method, key=None, **kwargs):
        assert service == 'iotsitewise'
        model_types = {
            'root': 'ASSET_MODEL', 'child': 'ASSET_MODEL', 'component': 'COMPONENT_MODEL',
            'iface-root': 'INTERFACE', 'iface-child': 'INTERFACE',
        }
        if method == 'list_asset_models':
            requested = set(kwargs['assetModelTypes'])
            value = {'assetModelSummaries': [
                {'id': identifier, 'assetModelType': model_type}
                for identifier, model_type in model_types.items() if model_type in requested]}
        elif method == 'describe_asset_model':
            identifier = kwargs['assetModelId']
            children = {'root': [('h-root', 'child')],
                        'iface-root': [('h-iface', 'iface-child')]}.get(identifier, [])
            value = {
                'assetModelId': identifier,
                'assetModelType': model_types[identifier],
                'assetModelStatus': {'state': 'ACTIVE'},
                'assetModelHierarchies': [
                    {'id': hierarchy, 'childAssetModelId': child}
                    for hierarchy, child in children],
            }
        elif method == 'list_asset_model_properties':
            counts = {'root': 2 if kwargs['filter'] == 'BASE' else 4,
                      'child': 1, 'component': 3, 'iface-root': 2, 'iface-child': 1}
            properties = [
                {'id': f"{kwargs['assetModelId']}-p-{number}",
                 'type': {'measurement': {}}}
                for number in range(counts[kwargs['assetModelId']])]
            if kwargs['filter'] == 'ALL' and kwargs['assetModelId'] == 'root':
                properties[-1]['type'] = {'transform': {
                    'variables': [{'name': 'one'}, {'name': 'two'}],
                    'expression': 'avg(one) + max(two, concat("ignored(", "x"))'}}
            value = {'assetModelPropertySummaries': properties}
        elif method == 'list_asset_model_composite_models':
            summaries = ([{'id': 'composite-root', 'path': []},
                          {'id': 'composite-child',
                           'path': [{'id': 'composite-root'}]}]
                         if kwargs['assetModelId'] == 'root' else [])
            value = {'assetModelCompositeModelSummaries': summaries}
        elif method == 'describe_asset_model_composite_model':
            composite_id = kwargs['assetModelCompositeModelId']
            count = 4 if composite_id == 'composite-root' else 2
            value = {
                'assetModelId': kwargs['assetModelId'],
                'assetModelCompositeModelId': composite_id,
                'assetModelCompositeModelProperties': [
                    {'id': f'{composite_id}-p-{number}'} for number in range(count)],
            }
        elif method == 'list_composition_relationships':
            value = {'compositionRelationshipSummaries': [
                {'assetModelId': 'root', 'assetModelCompositeModelId': 'use-1'},
                {'assetModelId': 'root', 'assetModelCompositeModelId': 'use-2'},
            ]}
        elif method == 'list_interface_relationships':
            relationships = ([{'id': 'root'}, {'id': 'child'}]
                             if kwargs['interfaceAssetModelId'] == 'iface-root' else [])
            value = {'interfaceRelationshipSummaries': relationships}
        elif method == 'list_assets' and 'assetModelId' in kwargs:
            counts = {'root': 2, 'child': 1}
            model_id = kwargs['assetModelId']
            value = {'assetSummaries': [
                {'id': f'{model_id}-asset-{number}', 'assetModelId': model_id}
                for number in range(counts[model_id])]}
        elif method == 'list_assets':
            value = {'assetSummaries': [{'id': 'parent'}, {'id': 'other'}]}
        elif method == 'list_associated_assets':
            children = ([{'id': 'child-a'}, {'id': 'child-b'}]
                        if kwargs['assetId'] == 'parent' else [])
            value = {'assetSummaries': children}
        elif method == 'list_bulk_import_jobs':
            assert kwargs == {'filter': 'RUNNING'}
            value = {'jobSummaries': [{'id': 'bulk-1', 'status': 'RUNNING'},
                                      {'id': 'bulk-2', 'status': 'RUNNING'}]}
        elif method == 'list_workspaces':
            value = {'workspaceSummaries': [{'name': 'one'}, {'name': 'two'}]}
        elif method == 'list_enrichment_jobs':
            count = 2 if kwargs['workspaceName'] == 'one' else 1
            value = {'jobs': [
                {'jobId': f"{kwargs['workspaceName']}-{number}",
                 'workspaceName': kwargs['workspaceName'], 'jobType': 'EVENT_DETECTION'}
                for number in range(count)]}
        else:
            raise AssertionError(method)
        return value[key] if key else value


def test_sitewise_model_properties_and_hierarchy_graphs():
    ctx = Context()
    assert model_count(ctx, {'ASSET_MODEL', 'COMPONENT_MODEL'})['usage'] == 3
    assert model_count(ctx, {'INTERFACE'})['usage'] == 2
    assert properties_per_model(ctx, {'ASSET_MODEL'}, 'BASE')['usage'] == 2
    assert properties_per_model(ctx, {'ASSET_MODEL', 'COMPONENT_MODEL'})['usage'] == 4
    assert formula_maximum(ctx, 'variables')['usage'] == 2
    assert formula_maximum(ctx, 'functions')['usage'] == 3
    assert hierarchy_definitions(ctx, {'ASSET_MODEL'})['usage'] == 1
    assert graph_maximum(ctx, {'ASSET_MODEL'}, 'models')['usage'] == 2
    assert graph_maximum(ctx, {'ASSET_MODEL'}, 'depth')['usage'] == 2
    assert graph_maximum(ctx, {'ASSET_MODEL'}, 'parents')['usage'] == 1
    assert graph_maximum(ctx, {'INTERFACE'}, 'models')['usage'] == 2


def test_sitewise_composites_and_relationships():
    ctx = Context()
    assert composites_per_model(ctx)['usage'] == 2
    assert composite_depth(ctx)['usage'] == 2
    assert properties_per_composite(ctx)['usage'] == 4
    assert component_model_users(ctx)['usage'] == 1
    assert interface_users(ctx)['usage'] == 2


def test_sitewise_assets_and_jobs():
    ctx = Context()
    assert assets_per_model(ctx)['usage'] == 2
    assert children_per_asset(ctx)['usage'] == 2
    assert running_bulk_imports(ctx)['usage'] == 2
    assert enrichment_jobs(ctx)['usage'] == 3
    assert enrichment_jobs(ctx, per_workspace=True)['usage'] == 2


def test_sitewise_extended_read_permissions_are_deployed():
    for action in ('DescribeAssetModel', 'ListAssetModelProperties',
                   'ListAssetModelCompositeModels', 'DescribeAssetModelCompositeModel',
                   'ListCompositionRelationships', 'ListInterfaceRelationships',
                   'ListAssets', 'ListAssociatedAssets', 'ListBulkImportJobs',
                   'ListWorkspaces', 'ListEnrichmentJobs'):
        assert grants(f'iotsitewise:{action}')
