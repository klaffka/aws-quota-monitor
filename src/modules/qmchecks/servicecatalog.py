"""AWS Service Catalog regional portfolio and product inventories."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-C6458716', 'Portfolios per region',
     lambda ctx: dict(usage=len(ctx.call('servicecatalog', 'list_portfolios', 'PortfolioDetails')),
                      source='servicecatalog:ListPortfolios', method='ACCOUNT_COUNT')),
    ('L-764CF6A1', 'Products per region',
     lambda ctx: dict(usage=len(ctx.call('servicecatalog', 'search_products_as_admin', 'ProductViewDetails')),
                      source='servicecatalog:SearchProductsAsAdmin', method='ACCOUNT_COUNT')),
    ('L-BEE0DD19', 'Service actions per region',
     lambda ctx: dict(usage=len(ctx.call('servicecatalog', 'list_service_actions', 'ServiceActionSummaries')),
                      source='servicecatalog:ListServiceActions', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_servicecatalog(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'servicecatalog' for service, _ in context.quotas):
        return []
    return context.run('servicecatalog', CHECKS, skip)
