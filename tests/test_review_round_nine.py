from unittest.mock import Mock

from modules.qmchecks.airflow import CHECKS as AIRFLOW
from modules.qmchecks.cases import CHECKS as CASES


def test_mwaa_environments_are_account_count():
    ctx = Mock()
    ctx.call.return_value = [{'Name': 'env'}]
    assert AIRFLOW[0][2](ctx)['usage'] == 1


def test_cases_templates_are_maximum_per_domain():
    ctx = Mock()
    ctx.call.side_effect = [[{'domainId': 'domain'}], [{'templateId': 'template'}]]
    assert CASES[0][2](ctx)['usage'] == 1
    ctx.call.side_effect = [[{'domainId': 'domain'}], [{'templateId': 'template'}]]
    result = CASES[1][2](ctx)
    assert (result['usage'], result['resource_id']) == (1, 'domain')
