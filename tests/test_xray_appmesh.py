from unittest.mock import Mock

from modules.qmchecks.appmesh import routes_per_router
from modules.qmchecks.xray import CHECKS


def test_xray_checks_use_paginated_resource_counts():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    assert all(check(ctx)['usage'] == 2 for _, _, check in CHECKS)


def test_appmesh_routes_use_maximum_per_router():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'meshName': 'mesh'}],
        [{'virtualRouterName': 'router'}],
        [{'id': 'one'}, {'id': 'two'}],
    ]
    result = routes_per_router(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'mesh/router')
