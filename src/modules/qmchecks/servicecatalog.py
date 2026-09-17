"""AWS Service Catalog portfolio, product and AppRegistry inventories.

Portfolios and products carry their tags and TagOptions only in the describe
calls, so the per-resource limits read every portfolio and product in full.
"""
from collections import Counter

from botocore.exceptions import ClientError

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

SERVICECATALOG = 'servicecatalog'
APPREGISTRY = 'servicecatalog-appregistry'
ORGANIZATIONS = 'organizations'
# Organizations answers per service principal, and Service Catalog's is the
# only one this quota counts.
SERVICE_PRINCIPAL = 'servicecatalog.amazonaws.com'
# The account is not in an organization, so the quota has no subject here.
NOT_AN_ORGANIZATION = {'AWSOrganizationsNotInUseException', 'AccessDeniedException'}


def delegated_administrators(ctx):
    """Service Catalog itself cannot list these; Organizations owns them."""
    try:
        found = ctx.call(ORGANIZATIONS, 'list_delegated_administrators',
                         'DelegatedAdministrators', ServicePrincipal=SERVICE_PRINCIPAL)
    except ClientError as exc:
        if exc.response['Error']['Code'] in NOT_AN_ORGANIZATION:
            raise NoData('This account is not the management account of an '
                         'organization, so it cannot read its delegated '
                         'administrators') from None
        raise
    return dict(usage=len(found),
                source='organizations:ListDelegatedAdministrators',
                method='ACCOUNT_COUNT')


def portfolios(ctx):
    found = []
    for portfolio in ctx.call(SERVICECATALOG, 'list_portfolios', 'PortfolioDetails'):
        identity = portfolio.get('Id')
        if not isinstance(identity, str) or not identity:
            raise NoData('Service Catalog portfolio is missing its identity')
        found.append(identity)
    return found


def products(ctx):
    found = []
    for product in ctx.call(SERVICECATALOG, 'search_products_as_admin',
                            'ProductViewDetails'):
        summary = product.get('ProductViewSummary') or {}
        identity = summary.get('ProductId')
        if not isinstance(identity, str) or not identity:
            raise NoData('Service Catalog product is missing its identity')
        found.append(identity)
    return found


def _per_portfolio(method, key, resource_type='ServiceCatalogPortfolio'):
    def check(ctx):
        values = [(identity, len(ctx.call(SERVICECATALOG, method, key,
                                          PortfolioId=identity)), None)
                  for identity in portfolios(ctx)]
        operation = ''.join(part.capitalize() for part in method.split('_'))
        return maximum(values, resource_type, f'servicecatalog:{operation}')
    return check


def products_per_portfolio(ctx):
    values = [(identity, len(ctx.call(SERVICECATALOG, 'search_products_as_admin',
                                      'ProductViewDetails', PortfolioId=identity)), None)
              for identity in portfolios(ctx)]
    return maximum(values, 'ServiceCatalogPortfolio',
                   'servicecatalog:SearchProductsAsAdmin')


def provisioning_artifacts(ctx, product):
    """This operation takes no page token and returns every version at once."""
    response = ctx.call(SERVICECATALOG, 'list_provisioning_artifacts',
                        ProductId=product)
    details = response.get('ProvisioningArtifactDetails')
    if not isinstance(details, list):
        raise NoData('Service Catalog product has no provisioning artifact list')
    return details


def versions_per_product(ctx):
    values = [(product, len(provisioning_artifacts(ctx, product)), None)
              for product in products(ctx)]
    return maximum(values, 'ServiceCatalogProduct',
                   'servicecatalog:ListProvisioningArtifacts')


def service_actions_per_artifact(ctx):
    values = []
    for product in products(ctx):
        for artifact in provisioning_artifacts(ctx, product):
            identity = artifact.get('Id')
            if not isinstance(identity, str) or not identity:
                raise NoData('Service Catalog provisioning artifact has no identity')
            actions = ctx.call(SERVICECATALOG,
                               'list_service_actions_for_provisioning_artifact',
                               'ServiceActionSummaries', ProductId=product,
                               ProvisioningArtifactId=identity)
            values.append((f'{product}/{identity}', len(actions), None))
    return maximum(values, 'ServiceCatalogProvisioningArtifact',
                   'servicecatalog:ListServiceActionsForProvisioningArtifact')


def _described(ctx):
    """Describe every portfolio and product, which is where the tags live."""
    for identity in portfolios(ctx):
        yield identity, ctx.call(SERVICECATALOG, 'describe_portfolio', Id=identity)
    for identity in products(ctx):
        yield identity, ctx.call(SERVICECATALOG, 'describe_product_as_admin',
                                 Id=identity)


def _listed(response, field, subject):
    entries = response.get(field)
    if entries is None:
        return []
    if not isinstance(entries, list):
        raise NoData(f'Service Catalog {subject} has an invalid {field} list')
    return entries


def _tags_of(kind, describe, resource_type):
    def check(ctx):
        values = []
        for identity in (portfolios(ctx) if kind == 'portfolio' else products(ctx)):
            response = ctx.call(SERVICECATALOG, describe, Id=identity)
            values.append((identity, len(_listed(response, 'Tags', kind)), None))
        operation = ''.join(part.capitalize() for part in describe.split('_'))
        return maximum(values, resource_type, f'servicecatalog:{operation}')
    return check


def tag_options_per_resource(ctx):
    values = [(identity, len(_listed(response, 'TagOptions', 'resource')), None)
              for identity, response in _described(ctx)]
    return maximum(values, 'ServiceCatalogResource',
                   'servicecatalog:DescribePortfolio+DescribeProductAsAdmin')


def values_per_tag_option(ctx):
    counts = Counter()
    for option in ctx.call(SERVICECATALOG, 'list_tag_options', 'TagOptionDetails'):
        key = option.get('Key')
        if not isinstance(key, str) or not key:
            raise NoData('Service Catalog TagOption is missing its key')
        counts[key] += 1
    return maximum(((key, count, None) for key, count in counts.items()),
                   'ServiceCatalogTagOption', 'servicecatalog:ListTagOptions')


def applications(ctx):
    found = []
    for application in ctx.call(APPREGISTRY, 'list_applications', 'applications'):
        identity = application.get('id')
        if not isinstance(identity, str) or not identity:
            raise NoData('AppRegistry application is missing its identity')
        found.append(identity)
    return found


def _per_application(method, key, source):
    def check(ctx):
        values = [(identity, len(ctx.call(APPREGISTRY, method, key,
                                          application=identity)), None)
                  for identity in applications(ctx)]
        return maximum(values, 'AppRegistryApplication', source)
    return check


CHECKS = [
    ('L-CA761021', 'Delegated administrators per organization',
     delegated_administrators),
    ('L-C6458716', 'Portfolios per region',
     lambda ctx: dict(usage=len(portfolios(ctx)),
                      source='servicecatalog:ListPortfolios', method='ACCOUNT_COUNT')),
    ('L-764CF6A1', 'Products per region',
     lambda ctx: dict(usage=len(products(ctx)),
                      source='servicecatalog:SearchProductsAsAdmin',
                      method='ACCOUNT_COUNT')),
    ('L-BEE0DD19', 'Service actions per region',
     lambda ctx: dict(usage=len(ctx.call(SERVICECATALOG, 'list_service_actions',
                                         'ServiceActionSummaries')),
                      source='servicecatalog:ListServiceActions',
                      method='ACCOUNT_COUNT')),
    ('L-AB79E48B', 'Products per portfolio', products_per_portfolio),
    ('L-A5846085', 'Product versions per product', versions_per_product),
    ('L-A2FB1BD2', 'Shared accounts per portfolio',
     _per_portfolio('list_portfolio_access', 'AccountIds')),
    ('L-E8959660', 'Users, groups, and roles per portfolio',
     _per_portfolio('list_principals_for_portfolio', 'Principals')),
    ('L-77FEF8C5', 'Tags per portfolio',
     _tags_of('portfolio', 'describe_portfolio', 'ServiceCatalogPortfolio')),
    ('L-CC0BF186', 'Tags per product',
     _tags_of('product', 'describe_product_as_admin', 'ServiceCatalogProduct')),
    ('L-73A88F28', 'TagOptions per resource', tag_options_per_resource),
    ('L-79127A24', 'Values per TagOption', values_per_tag_option),
    ('L-58FC5582', 'Service action associations per provisioning artifact',
     service_actions_per_artifact),
    ('L-1639038A', 'Attribute groups per region',
     lambda ctx: dict(usage=len(ctx.call(APPREGISTRY, 'list_attribute_groups',
                                         'attributeGroups')),
                      source='servicecatalog-appregistry:ListAttributeGroups',
                      method='ACCOUNT_COUNT')),
    ('L-C533FF9A', 'Attribute groups per application',
     _per_application('list_attribute_groups_for_application',
                      'attributeGroupsDetails',
                      'servicecatalog-appregistry:ListAttributeGroupsForApplication')),
    ('L-360CDF2E', 'Resources per application',
     _per_application('list_associated_resources', 'resources',
                      'servicecatalog-appregistry:ListAssociatedResources')),
]


def get_current_quotastatus_servicecatalog(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'servicecatalog' for service, _ in context.quotas):
        return []
    return context.run('servicecatalog', CHECKS, skip)
