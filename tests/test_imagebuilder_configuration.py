from pathlib import Path
from unittest.mock import Mock

import pytest

from modules.qmchecks import imagebuilder
from modules.qmcore.aws import NoData
from modules.qmcore.registry import custom_keys


class ImageBuilderContext:
    def __init__(self):
        self.data = {
            'components': [
                {'arn': 'component/a'},
                {'arn': 'component/b'},
            ],
            'component_details': {
                'component/a': {'arn': 'component/a', 'data': 'a' * 2048,
                                'parameters': [{'name': 'one', 'defaultValue': ['small']},
                                               {'name': 'two', 'defaultValue': ['value']}]},
                'component/b': {'arn': 'component/b', 'data': 'b', 'parameters': []},
            },
            'image_recipes': [{'arn': 'recipe/image'}],
            'image_recipe_details': {
                'recipe/image': {'arn': 'recipe/image', 'components': [
                    {'componentArn': 'component/a',
                     'parameters': [{'name': 'one', 'value': ['1234567']}]},
                    {'componentArn': 'component/b'},
                ]},
            },
            'container_recipes': [{'arn': 'recipe/container'}],
            'container_recipe_details': {
                'recipe/container': {'arn': 'recipe/container',
                                     'dockerfileTemplateData': 'd' * 1024,
                                     'components': [{'componentArn': 'component/a',
                                                     'parameters': [{'name': 'one',
                                                                     'value': ['12345678']}]}]},
            },
            'workflows': [{'arn': 'workflow/a'}],
            'workflow_details': {
                'workflow/a': {'arn': 'workflow/a', 'data': 'steps:\n  - name: one\n  - name: two\n',
                               'parameters': [{'name': 'first', 'defaultValue': ['123456']},
                                              {'name': 'second', 'defaultValue': []}]},
            },
            'distributions': [{'arn': 'distribution/a'}],
            'distribution_details': {
                'distribution/a': {'arn': 'distribution/a', 'distributions': [
                    {'region': 'eu-central-1',
                     'launchTemplateConfigurations': [{'launchTemplateId': 'one'},
                                                      {'launchTemplateId': 'two'}],
                     'ssmParameterConfigurations': [{'parameterName': 'one'}],
                     'amiDistributionConfiguration': {'targetAccountIds': ['1', '2', '3']}},
                    {'region': 'eu-west-1',
                     'launchTemplateConfigurations': [{'launchTemplateId': 'three'}],
                     'ssmParameterConfigurations': [{'parameterName': 'two'},
                                                    {'parameterName': 'three'}],
                     'amiDistributionConfiguration': {'targetAccountIds': ['4']}},
                ]},
            },
        }

    def call(self, service, method, key=None, **kwargs):
        assert service == 'imagebuilder'
        mapping = {
            'list_components': self.data['components'],
            'list_image_recipes': self.data['image_recipes'],
            'list_container_recipes': self.data['container_recipes'],
            'list_workflows': self.data['workflows'],
            'list_distribution_configurations': self.data['distributions'],
            'list_image_pipelines': [{'arn': 'pipeline/a'}],
            'list_infrastructure_configurations': [{'arn': 'infrastructure/a'}],
            'list_lifecycle_policies': [{'arn': 'lifecycle/a'}],
        }
        if method in mapping:
            return mapping[method]
        if method == 'get_component':
            return {'component': self.data['component_details'][kwargs['componentBuildVersionArn']]}
        if method == 'get_image_recipe':
            return {'imageRecipe': self.data['image_recipe_details'][kwargs['imageRecipeArn']]}
        if method == 'get_container_recipe':
            return {'containerRecipe':
                    self.data['container_recipe_details'][kwargs['containerRecipeArn']]}
        if method == 'get_workflow':
            return {'workflow': self.data['workflow_details'][kwargs['workflowBuildVersionArn']]}
        if method == 'get_distribution_configuration':
            return {'distributionConfiguration':
                    self.data['distribution_details'][kwargs['distributionConfigurationArn']]}
        raise AssertionError(method)


def test_imagebuilder_account_inventories_and_recipe_configuration():
    ctx = ImageBuilderContext()

    assert imagebuilder.account_count(ctx, 'list_image_recipes', 'imageRecipeSummaryList',
                                      'image recipe', owner='Self')['usage'] == 1
    assert imagebuilder.account_count(ctx, 'list_image_pipelines', 'imagePipelineList',
                                      'image pipeline')['usage'] == 1
    assert imagebuilder.components_per_recipe(ctx)['usage'] == 2
    assert imagebuilder.container_template_size(ctx)['usage'] == 1


def test_imagebuilder_component_limits_use_complete_details_without_exposing_values():
    ctx = ImageBuilderContext()

    assert imagebuilder.component_size(ctx)['usage'] == 2
    assert imagebuilder.component_parameters(ctx)['usage'] == 2
    assert imagebuilder.component_parameter_length(ctx)['usage'] == 8
    assert imagebuilder.component_parameter_length(ctx)['meta'] is None


def test_imagebuilder_workflow_limits_parse_utf8_yaml_documents():
    ctx = ImageBuilderContext()

    assert imagebuilder.workflow_stat(ctx, 'steps')['usage'] == 2
    assert imagebuilder.workflow_stat(ctx, 'parameters')['usage'] == 2
    assert imagebuilder.workflow_stat(ctx, 'parameter_length')['usage'] == 6
    assert imagebuilder.workflow_stat(ctx, 'size')['usage'] == len(
        ctx.data['workflow_details']['workflow/a']['data'].encode('utf-8')) / 1024


def test_imagebuilder_distribution_limits_are_scoped_to_one_target_region():
    ctx = ImageBuilderContext()

    launch = imagebuilder.distribution_maximum(ctx, 'launchTemplateConfigurations')
    parameters = imagebuilder.distribution_maximum(ctx, 'ssmParameterConfigurations')
    accounts = imagebuilder.distribution_maximum(ctx, 'targetAccountIds')
    assert (launch['usage'], launch['resource_id']) == (2, 'distribution/a/eu-central-1')
    assert (parameters['usage'], parameters['resource_id']) == (2, 'distribution/a/eu-west-1')
    assert accounts['usage'] == 3


def test_imagebuilder_invalid_configuration_is_no_data():
    ctx = ImageBuilderContext()
    ctx.data['workflow_details']['workflow/a']['data'] = 'steps: invalid'
    with pytest.raises(NoData, match='steps inventory'):
        imagebuilder.workflow_stat(ctx, 'steps')

    ctx = ImageBuilderContext()
    distributions = ctx.data['distribution_details']['distribution/a']['distributions']
    distributions[1]['region'] = 'eu-central-1'
    with pytest.raises(NoData, match='duplicate region'):
        imagebuilder.distribution_maximum(ctx, 'targetAccountIds')


def test_imagebuilder_extended_checks_are_registered_and_catalog_selected():
    assert len(imagebuilder.ALL_CHECKS) == 20
    assert {('imagebuilder', code) for code, _name, _check in imagebuilder.ALL_CHECKS} <= custom_keys()

    context = Mock(quotas={('imagebuilder', 'L-1DF98342'): {}})
    context.run.return_value = []
    assert imagebuilder.get_current_quotastatus_imagebuilder(ctx=context) == []
    selected = context.run.call_args.args[1]
    assert [code for code, _name, _check in selected] == [
        'L-6105A4EE', 'L-9B183655', 'L-0DF2752F', 'L-1DF98342',
    ]


def test_imagebuilder_configuration_checks_have_read_permissions():
    policy = (Path(__file__).parents[1] / 'deployment/main.tf').read_text(encoding='utf-8')
    for action in (
        'ListLifecyclePolicies', 'ListComponents', 'GetComponent', 'ListWorkflows',
        'GetWorkflow', 'ListImageRecipes', 'GetImageRecipe', 'ListContainerRecipes',
        'GetContainerRecipe', 'ListDistributionConfigurations',
        'GetDistributionConfiguration', 'ListImagePipelines',
        'ListInfrastructureConfigurations',
    ):
        assert f'"imagebuilder:{action}"' in policy
