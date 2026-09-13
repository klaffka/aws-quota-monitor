from unittest.mock import Mock

from modules.qmchecks.lex import versions_per_bot
from modules.qmchecks.polly import CHECKS as POLLY_CHECKS
from modules.qmchecks.transcribe import CHECKS as TRANSCRIBE_CHECKS


def test_transcribe_checks_use_paginated_resource_keys():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    assert all(check(ctx)['usage'] == 2 for _, _, check in TRANSCRIBE_CHECKS)


def test_polly_counts_lexicons():
    ctx = Mock()
    ctx.call.return_value = [{'Name': 'one'}, {'Name': 'two'}]
    assert POLLY_CHECKS[0][2](ctx)['usage'] == 2


def test_lex_versions_use_maximum_per_bot():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'botId': 'bot-1'}, {'botId': 'bot-2'}],
        [{'botVersion': '1'}],
        [{'botVersion': '1'}, {'botVersion': '2'}],
    ]
    result = versions_per_bot(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'bot-2')
