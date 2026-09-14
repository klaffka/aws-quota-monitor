from unittest.mock import Mock
from modules.qmchecks.cognito import CHECKS as COGNITO
from modules.qmchecks.appstream import CHECKS as APPSTREAM

def test_cognito_custom_domains():
    ctx = Mock()
    ctx.call.side_effect = [[{'Id': 'p1'}, {'Id': 'p2'}],
                            {'UserPool': {'CustomDomain': 'one'}},
                            {'UserPool': {}}]
    check = next(c for c in COGNITO if c[0] == 'L-71267F98')
    assert check[2](ctx)['usage'] == 1

def test_appstream_active_fleets():
    ctx = Mock()
    ctx.call.return_value = [{'State': 'RUNNING'}, {'State': 'STOPPED'}]
    check = next(c for c in APPSTREAM if c[0] == 'L-3FEADC0C')
    assert check[2](ctx)['usage'] == 1
