from unittest.mock import Mock

from modules.qmchecks.omics import CHECKS


def test_omics_resource_checks_use_paginated_output_keys():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    assert all(check(ctx)['usage'] == 2 for _, _, check in CHECKS)
