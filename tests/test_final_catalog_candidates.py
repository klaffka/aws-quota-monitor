from unittest.mock import Mock

from modules.qmchecks.internetmonitor import CHECKS as INTERNET
from modules.qmchecks.docdb_elastic import CHECKS as DOCDB
from modules.qmchecks.databrew import CHECKS as DATABREW
from modules.qmchecks.cognito_identity import CHECKS as IDENTITY


def test_final_catalog_candidates_count_paginated_results():
    for checks in (INTERNET, DOCDB, DATABREW, IDENTITY):
        context = Mock()
        context.call.return_value = [{'MonitorName': 'one', 'name': 'one'}]
        assert checks[0][2](context)['usage'] == 1
