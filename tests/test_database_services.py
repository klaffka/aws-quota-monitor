from unittest.mock import Mock

from modules.qmchecks.dynamodb import CHECKS as DDB
from modules.qmchecks.elasticache import CHECKS as CACHE
from modules.qmchecks.docdb import CHECKS as DOCDB
from modules.qmchecks.neptune import CHECKS as NEPTUNE


def test_database_resource_counts():
    ctx = Mock()
    ctx.call.return_value = [{'Resource': 'resource'}]
    assert DDB[0][2](ctx)['usage'] == 1
    assert [c[2](ctx)['usage'] for c in CACHE] == [1] * len(CACHE)
    assert [c[2](ctx)['usage'] for c in DOCDB] == [1] * len(DOCDB)
    # Parent-scoped endpoint checks require a cluster identifier in the inventory.
    assert [c[2](ctx)['usage'] for c in NEPTUNE[:3]] == [1, 1, 1]
