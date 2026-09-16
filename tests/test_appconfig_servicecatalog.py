from unittest.mock import Mock

from modules.qmchecks.appconfig import maximum_per_application
from modules.qmchecks.servicecatalog import CHECKS


def test_appconfig_maximum_is_per_application():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'Id': 'app-1'}, {'Id': 'app-2'}],
        [{'Id': 'env-1'}, {'Id': 'env-2'}],
        [{'Id': 'env-3'}],
    ]
    result = maximum_per_application(ctx, 'list_environments')
    assert (result['usage'], result['resource_id']) == (2, 'app-1')


def test_servicecatalog_counts_paginated_portfolios_and_products():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'Id': 'portfolio-1'}],
        [{'ProductViewSummary': {'ProductId': 'product-1'}},
         {'ProductViewSummary': {'ProductId': 'product-2'}}],
    ]
    by_code = {code: check for code, _, check in CHECKS}
    assert by_code['L-C6458716'](ctx)['usage'] == 1
    assert by_code['L-764CF6A1'](ctx)['usage'] == 2
