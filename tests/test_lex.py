import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import lex
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

BOT = 'BOT0000001'
OTHER = 'BOT0000002'
NETWORK = 'NET0000001'
INTENT = 'INT0000001'
SLOT = 'SLT0000001'
SLOT_TYPE = 'STY0000001'
LOCALE = 'de_DE'
DRAFT = {'botId': BOT, 'botVersion': 'DRAFT', 'localeId': LOCALE}
PROMPT = {'message': {'plainTextMessage': {'value': 'Wie viele?'}}}


def context(code='L-36FA8BD2'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'lex', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def bot(identity=BOT, status='Available', kind='Bot'):
    return {'botId': identity, 'botName': f'bot-{identity}', 'botStatus': status,
            'botType': kind}


def version(name='DRAFT', identity=BOT, status='Available'):
    return {'botVersion': name, 'botName': f'bot-{identity}', 'botStatus': status}


def utterances(*values):
    return [{'utterance': value} for value in values]


def slot_detail(*sample, subslot=None):
    detail = dict(DRAFT, intentId=INTENT, slotId=SLOT, slotName='slot',
                  valueElicitationSetting={'slotConstraint': 'Optional',
                                           'sampleUtterances': utterances(*sample)})
    if subslot is not None:
        detail['subSlotSetting'] = {'slotSpecifications': {'Sub': {
            'slotTypeId': 'AMAZON.Number',
            'valueElicitationSetting': {
                'promptSpecification': {'messageGroups': [PROMPT], 'maxRetries': 1},
                'sampleUtterances': utterances(*subslot)}}}}
    return detail


def slot_type_value(value, *synonyms):
    # AWS rejects an empty synonym list, so omit the key when there are none.
    result = {'sampleValue': {'value': value}}
    if synonyms:
        result['synonyms'] = [{'value': item} for item in synonyms]
    return result


def stub_locale(stub, intents=(), slot_types=(), status='Built'):
    """Queue one bot/DRAFT/locale traversal with the given detail responses."""
    stub.add_response('list_bot_locales', {'botLocaleSummaries': [
        {'localeId': LOCALE, 'botLocaleStatus': status}]},
        {'botId': BOT, 'botVersion': 'DRAFT'})
    if status not in lex.STABLE_LOCALE_STATES:
        return
    stub.add_response('list_intents', {'intentSummaries': [
        {'intentId': detail['intentId'], 'intentName': detail['intentName']}
        for detail, _ in intents]}, DRAFT)
    for detail, slots in intents:
        stub.add_response('describe_intent', detail,
                          dict(DRAFT, intentId=detail['intentId']))
        stub.add_response('list_slots', {'slotSummaries': [
            {'slotId': slot['slotId'], 'slotName': slot['slotName']}
            for slot in slots]}, dict(DRAFT, intentId=detail['intentId']))
        for slot in slots:
            stub.add_response('describe_slot', slot,
                              dict(DRAFT, intentId=detail['intentId'],
                                   slotId=slot['slotId']))
    stub.add_response('list_slot_types', {'slotTypeSummaries': [
        {'slotTypeId': detail['slotTypeId'], 'slotTypeName': detail['slotTypeName']}
        for detail in slot_types]}, DRAFT)
    for detail in slot_types:
        stub.add_response('describe_slot_type', detail,
                          dict(DRAFT, slotTypeId=detail['slotTypeId']))


def populated(stub, sample=('hallo', 'guten tag')):
    intent = dict(DRAFT, intentId=INTENT, intentName='intent',
                  sampleUtterances=utterances(*sample))
    slot = slot_detail('wie viele?', subslot=['ab'])
    slot_type = dict(DRAFT, slotTypeId=SLOT_TYPE, slotTypeName='colour',
                     slotTypeValues=[slot_type_value('rot', 'karmin', 'scharlach'),
                                     slot_type_value('blau')])
    stub.add_response('list_bots', {'botSummaries': [bot()]}, {})
    stub.add_response('list_bot_versions', {'botId': BOT, 'botVersionSummaries': [version()]},
                      {'botId': BOT})
    stub_locale(stub, intents=[(intent, [slot])], slot_types=[slot_type])


def check(code):
    return next(fn for quota, _, fn in lex.CHECKS if quota == code)


def test_code_units_follow_the_utf16_quota_definition():
    assert lex._code_units('abc') == 3
    assert lex._code_units('ä') == 1
    # Non-BMP characters occupy two UTF-16 code units.
    assert lex._code_units('😀') == 2


def test_bot_networks_and_unknown_states_are_separated_from_bots():
    ctx = context()
    with Stubber(ctx.client('lexv2-models')) as stub:
        stub.add_response('list_bots', {'botSummaries': [
            bot(), bot(NETWORK, kind='BotNetwork')]}, {})
        assert list(lex.bots(ctx)) == [BOT]
        assert check('L-36FA8BD2')(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_unknown_bot_state_raises_nodata():
    ctx = context()
    with Stubber(ctx.client('lexv2-models')) as stub:
        stub.add_response('list_bots', {'botSummaries': [bot(status='Retired')]}, {})
        with pytest.raises(NoData, match='unknown state'):
            lex.bots(ctx)


def test_inventory_changing_during_pagination_raises_nodata():
    ctx = context()
    with Stubber(ctx.client('lexv2-models')) as stub:
        stub.add_response('list_bots', {'botSummaries': [bot()], 'nextToken': 'next'}, {})
        stub.add_response('list_bots', {'botSummaries': [bot(status='Inactive')]},
                          {'nextToken': 'next'})
        with pytest.raises(NoData, match='changed during pagination'):
            lex.bots(ctx)


def test_versions_per_bot_excludes_draft_and_reports_the_largest_bot():
    ctx = context('L-BCD96794')
    with Stubber(ctx.client('lexv2-models')) as stub:
        stub.add_response('list_bots', {'botSummaries': [bot(), bot(OTHER)]}, {})
        stub.add_response('list_bot_versions', {'botId': BOT, 'botVersionSummaries': [
            version(), version('1')]}, {'botId': BOT})
        stub.add_response('list_bot_versions', {'botId': OTHER, 'botVersionSummaries': [
            version('1', OTHER), version('2', OTHER)]}, {'botId': OTHER})
        result = lex.versions_per_bot(ctx)
        # The unlisted DRAFT of the second bot is synthesized but never counted.
        assert (result['usage'], result['resource_id']) == (2, OTHER)
        stub.assert_no_pending_responses()


def test_unstable_locale_raises_nodata_instead_of_undercounting():
    ctx = context('L-9030FC28')
    with Stubber(ctx.client('lexv2-models')) as stub:
        stub.add_response('list_bots', {'botSummaries': [bot()]}, {})
        stub.add_response('list_bot_versions', {'botId': BOT, 'botVersionSummaries': [version()]},
                          {'botId': BOT})
        stub_locale(stub, status='Building')
        with pytest.raises(NoData, match='locale configuration is changing'):
            lex.model_inventory(ctx)


def test_slot_type_synonyms_are_read_from_sample_value_structures():
    ctx = context('L-52297D95')
    with Stubber(ctx.client('lexv2-models')) as stub:
        populated(stub)
        # 'rot' plus two synonyms plus 'blau'.
        assert check('L-824BBA1D')(ctx)['usage'] == 4
        assert lex.values_per_slot_type(ctx)['usage'] == 4
        assert lex.characters_per_slot_value(ctx)['usage'] == len('scharlach')
        stub.assert_no_pending_responses()


def test_locale_counts_cover_intents_slots_and_subslots():
    ctx = context('L-9030FC28')
    with Stubber(ctx.client('lexv2-models')) as stub:
        populated(stub)
        locale_id = f'{BOT}:DRAFT:{LOCALE}'
        # The composite subslot counts as its own slot.
        slots = check('L-9030FC28')(ctx)
        assert (slots['usage'], slots['resource_id']) == (2, locale_id)
        assert check('L-3D56827F')(ctx)['usage'] == 1
        assert lex.slots_per_intent(ctx)['usage'] == 2
        assert lex.utterances_per_intent(ctx)['usage'] == 2
        assert lex.utterances_per_slot(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_utterance_characters_are_summed_and_maximised_per_locale():
    ctx = context('L-606F3490')
    with Stubber(ctx.client('lexv2-models')) as stub:
        populated(stub, sample=('hallo', '😀'))
        # 'hallo' + emoji + 'wie viele?' + subslot 'ab'.
        assert check('L-606F3490')(ctx)['usage'] == 5 + 2 + 10 + 2
        assert lex.characters_per_utterance(ctx)['usage'] == len('wie viele?')
        stub.assert_no_pending_responses()


def test_detail_with_an_inconsistent_parent_raises_nodata():
    ctx = context('L-311093B9')
    with Stubber(ctx.client('lexv2-models')) as stub:
        stub.add_response('list_bots', {'botSummaries': [bot()]}, {})
        stub.add_response('list_bot_versions', {'botId': BOT, 'botVersionSummaries': [version()]},
                          {'botId': BOT})
        stub.add_response('list_bot_locales', {'botLocaleSummaries': [
            {'localeId': LOCALE, 'botLocaleStatus': 'Built'}]},
            {'botId': BOT, 'botVersion': 'DRAFT'})
        stub.add_response('list_intents', {'intentSummaries': [
            {'intentId': INTENT, 'intentName': 'intent'}]}, DRAFT)
        stub.add_response('describe_intent', dict(DRAFT, intentId=INTENT,
                                                  intentName='renamed'),
                          dict(DRAFT, intentId=INTENT))
        with pytest.raises(NoData, match='inconsistent parent'):
            lex.model_inventory(ctx)


def test_short_identifiers_are_rejected():
    # The SDK already rejects short ids in responses, so this guards the helper.
    assert lex._identifier(BOT, 'bot') == BOT
    for value in ('short', f'{BOT}1', 'BOT-000001', None):
        with pytest.raises(NoData, match='invalid identity'):
            lex._identifier(value, 'bot')


def test_every_lex_check_is_registered_for_reporting():
    registered = {code for service, code in custom_keys() if service == 'lex'}
    assert {code for code, _, _ in lex.CHECKS} <= registered
