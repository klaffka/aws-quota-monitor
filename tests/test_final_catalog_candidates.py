from unittest.mock import Mock

from modules.qmchecks.internetmonitor import CHECKS as INTERNET
from modules.qmchecks.route53profiles import CHECKS as PROFILES
from modules.qmchecks.docdb_elastic import CHECKS as DOCDB
from modules.qmchecks.databrew import CHECKS as DATABREW
from modules.qmchecks.cognito_identity import CHECKS as IDENTITY


def test_final_catalog_candidates_count_paginated_results():
    for checks in (INTERNET, PROFILES, DOCDB, DATABREW, IDENTITY):
        context = Mock()
        context.call.return_value = [{}]
        assert checks[0][2](context)['usage'] == 1
