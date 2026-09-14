"""EC2 Image Builder regional resource and configuration usage."""
from functools import partial

import yaml

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def unique(items, field, subject):
    result = {}
    for item in items:
        if not isinstance(item, dict):
            raise NoData(f'Image Builder {subject} inventory contains an invalid item')
        identity = item.get(field)
        if not isinstance(identity, str) or not identity:
            raise NoData(f'Image Builder {subject} is missing {field}')
        if identity in result and result[identity] != item:
            raise NoData(f'Image Builder {subject} inventory changed during pagination')
        result[identity] = item
    return [result[key] for key in sorted(result)]


def inventory(ctx, method, key, subject, **kwargs):
    return unique(ctx.call('imagebuilder', method, key, **kwargs), 'arn', subject)


def account_count(ctx, method, key, subject, **kwargs):
    return dict(usage=len(inventory(ctx, method, key, subject, **kwargs)),
                source=f'imagebuilder:{method}', method='ACCOUNT_COUNT')


def details(ctx, items, method, parameter, key, subject):
    result = []
    for item in items:
        arn = item['arn']
        response = ctx.call('imagebuilder', method, **{parameter: arn})
        detail = response.get(key) if isinstance(response, dict) else None
        if not isinstance(detail, dict) or detail.get('arn') != arn:
            raise NoData(f'Image Builder {subject} detail is inconsistent')
        result.append(detail)
    return result


def components(ctx):
    items = inventory(ctx, 'list_components', 'componentVersionList', 'component', owner='Self')
    return details(ctx, items, 'get_component', 'componentBuildVersionArn',
                   'component', 'component')


def image_recipes(ctx):
    items = inventory(ctx, 'list_image_recipes', 'imageRecipeSummaryList',
                      'image recipe', owner='Self')
    return details(ctx, items, 'get_image_recipe', 'imageRecipeArn',
                   'imageRecipe', 'image recipe')


def container_recipes(ctx):
    items = inventory(ctx, 'list_container_recipes', 'containerRecipeSummaryList',
                      'container recipe', owner='Self')
    return details(ctx, items, 'get_container_recipe', 'containerRecipeArn',
                   'containerRecipe', 'container recipe')


def workflows(ctx):
    items = inventory(ctx, 'list_workflows', 'workflowVersionList', 'workflow', owner='Self')
    return details(ctx, items, 'get_workflow', 'workflowBuildVersionArn',
                   'workflow', 'workflow')


def configurations(value, field, subject):
    items = value.get(field, [])
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise NoData(f'Image Builder {subject} has an invalid {field}')
    return items


def string_values(parameters, field, subject):
    result = []
    for parameter in parameters:
        values = parameter.get(field, [])
        if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
            raise NoData(f'Image Builder {subject} has invalid parameter values')
        result.extend(values)
    return result


def component_size(ctx):
    values = []
    for component in components(ctx):
        data = component.get('data')
        if not isinstance(data, str):
            raise NoData('Image Builder component is missing data')
        values.append((component['arn'], len(data.encode('utf-8')) / 1024, None))
    return maximum(values, 'ImageBuilderComponent',
                   'imagebuilder:ListComponents+GetComponent')


def component_parameters(ctx):
    values = []
    for component in components(ctx):
        parameters = configurations(component, 'parameters', 'component')
        values.append((component['arn'], len(parameters), None))
    return maximum(values, 'ImageBuilderComponent',
                   'imagebuilder:ListComponents+GetComponent')


def component_parameter_length(ctx):
    values = []
    for component in components(ctx):
        parameters = configurations(component, 'parameters', 'component')
        lengths = [len(value) for value in string_values(parameters, 'defaultValue', 'component')]
        values.append((component['arn'], max(lengths, default=0), None))
    for recipe in [*image_recipes(ctx), *container_recipes(ctx)]:
        lengths = []
        for component in configurations(recipe, 'components', 'recipe'):
            parameters = configurations(component, 'parameters', 'recipe component')
            lengths.extend(len(value) for value in string_values(parameters, 'value',
                                                                  'recipe component'))
        values.append((recipe['arn'], max(lengths, default=0), None))
    return maximum(values, 'ImageBuilderConfiguration',
                   'imagebuilder:ListComponents+GetComponent+ListImageRecipes+'
                   'GetImageRecipe+ListContainerRecipes+GetContainerRecipe')


def components_per_recipe(ctx):
    values = [(recipe['arn'], len(configurations(recipe, 'components', 'image recipe')), None)
              for recipe in image_recipes(ctx)]
    return maximum(values, 'ImageBuilderImageRecipe',
                   'imagebuilder:ListImageRecipes+GetImageRecipe')


def container_template_size(ctx):
    values = []
    for recipe in container_recipes(ctx):
        data = recipe.get('dockerfileTemplateData')
        if not isinstance(data, str):
            raise NoData('Image Builder container recipe is missing dockerfileTemplateData')
        values.append((recipe['arn'], len(data.encode('utf-8')) / 1024, None))
    return maximum(values, 'ImageBuilderContainerRecipe',
                   'imagebuilder:ListContainerRecipes+GetContainerRecipe')


def workflow_stat(ctx, field):
    values = []
    for workflow in workflows(ctx):
        if field == 'size':
            data = workflow.get('data')
            if not isinstance(data, str):
                raise NoData('Image Builder workflow is missing data')
            usage = len(data.encode('utf-8')) / 1024
        else:
            parameters = configurations(workflow, 'parameters', 'workflow')
            if field == 'parameters':
                usage = len(parameters)
            elif field == 'parameter_length':
                usage = max((len(value) for value in
                             string_values(parameters, 'defaultValue', 'workflow')), default=0)
            else:
                data = workflow.get('data')
                if not isinstance(data, str):
                    raise NoData('Image Builder workflow is missing data')
                try:
                    document = yaml.safe_load(data)
                except yaml.YAMLError as exc:
                    raise NoData(f'Image Builder workflow data is invalid YAML: {exc}') from exc
                steps = document.get('steps') if isinstance(document, dict) else None
                if not isinstance(steps, list) or any(not isinstance(step, dict) for step in steps):
                    raise NoData('Image Builder workflow has an invalid steps inventory')
                usage = len(steps)
        values.append((workflow['arn'], usage, None))
    return maximum(values, 'ImageBuilderWorkflow',
                   'imagebuilder:ListWorkflows+GetWorkflow')


def distribution_details(ctx):
    items = inventory(ctx, 'list_distribution_configurations',
                      'distributionConfigurationSummaryList', 'distribution configuration')
    return details(ctx, items, 'get_distribution_configuration',
                   'distributionConfigurationArn', 'distributionConfiguration',
                   'distribution configuration')


def distribution_maximum(ctx, field):
    values = []
    for configuration in distribution_details(ctx):
        seen_regions = set()
        for distribution in configurations(configuration, 'distributions',
                                           'distribution configuration'):
            region = distribution.get('region')
            if not isinstance(region, str) or not region or region in seen_regions:
                raise NoData('Image Builder distribution has an invalid or duplicate region')
            seen_regions.add(region)
            if field == 'targetAccountIds':
                ami = distribution.get('amiDistributionConfiguration') or {}
                if not isinstance(ami, dict):
                    raise NoData('Image Builder distribution has an invalid AMI configuration')
                items = ami.get(field, [])
            else:
                items = distribution.get(field, [])
            expected_type = str if field == 'targetAccountIds' else dict
            if not isinstance(items, list) or any(not isinstance(item, expected_type)
                                                  for item in items):
                raise NoData(f'Image Builder distribution has an invalid {field}')
            values.append((f"{configuration['arn']}/{region}", len(items), None))
    return maximum(values, 'ImageBuilderDistributionRegion',
                   'imagebuilder:ListDistributionConfigurations+GetDistributionConfiguration')

CHECKS = [
    ('L-6105A4EE', 'Lifecycle policies',
     partial(account_count, method='list_lifecycle_policies', key='lifecyclePolicySummaryList',
             subject='lifecycle policy')),
    ('L-9B183655', 'Components',
     partial(account_count, method='list_components', key='componentVersionList',
             subject='component', owner='Self')),
    ('L-0DF2752F', 'Image workflows',
     partial(account_count, method='list_workflows', key='workflowVersionList',
             subject='workflow', owner='Self')),
]

EXTENDED_CHECKS = [
    ('L-1DF98342', 'Image recipes',
     partial(account_count, method='list_image_recipes', key='imageRecipeSummaryList',
             subject='image recipe', owner='Self')),
    ('L-28A502FD', 'Container recipes',
     partial(account_count, method='list_container_recipes', key='containerRecipeSummaryList',
             subject='container recipe', owner='Self')),
    ('L-2BAA05D8', 'Distribution configurations',
     partial(account_count, method='list_distribution_configurations',
             key='distributionConfigurationSummaryList', subject='distribution configuration')),
    ('L-7A0E01E3', 'Image pipelines',
     partial(account_count, method='list_image_pipelines', key='imagePipelineList',
             subject='image pipeline')),
    ('L-D9EF98D9', 'Infrastructure configurations',
     partial(account_count, method='list_infrastructure_configurations',
             key='infrastructureConfigurationSummaryList', subject='infrastructure configuration')),
    ('L-D5DC1FB3', 'Component size', component_size),
    ('L-A58CFBED', 'Parameters per component', component_parameters),
    ('L-10D22E0D', 'Component parameter length', component_parameter_length),
    ('L-59EC76F6', 'Components per image recipe', components_per_recipe),
    ('L-84F5AB81', 'Docker template size', container_template_size),
    ('L-22EAF8F8', 'Image workflow size', partial(workflow_stat, field='size')),
    ('L-E49825CC', 'Parameters per image workflow', partial(workflow_stat, field='parameters')),
    ('L-A26B27A7', 'Image workflow parameter',
     partial(workflow_stat, field='parameter_length')),
    ('L-D9E1BB3C', 'Steps per image workflow', partial(workflow_stat, field='steps')),
    ('L-D5665818', 'Launch templates modified per distribution configuration Region',
     partial(distribution_maximum, field='launchTemplateConfigurations')),
    ('L-B588F8CA', 'SSM Parameters updated per distribution configuration Region',
     partial(distribution_maximum, field='ssmParameterConfigurations')),
    ('L-69312229', 'Concurrent AMI copies per distribution configuration',
     partial(distribution_maximum, field='targetAccountIds')),
]
ALL_CHECKS = CHECKS + EXTENDED_CHECKS


def get_current_quotastatus_imagebuilder(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'imagebuilder' for service, _ in context.quotas):
        return []
    checks = CHECKS + [check for check in EXTENDED_CHECKS
                       if ('imagebuilder', check[0]) in context.quotas]
    return context.run('imagebuilder', checks, skip)
