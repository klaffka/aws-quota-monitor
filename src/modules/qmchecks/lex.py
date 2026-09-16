"""Amazon Lex V2 regional bot and build-time configuration quotas."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


LEX = 'lexv2-models'
BOT_STATES = {
    'Creating', 'Available', 'Inactive', 'Deleting', 'Failed', 'Versioning',
    'Importing', 'Updating',
}
STABLE_BOT_STATES = {'Available', 'Inactive'}
BOT_TYPES = {'Bot', 'BotNetwork'}
LOCALE_STATES = {
    'Creating', 'Building', 'Built', 'ReadyExpressTesting', 'Failed',
    'Deleting', 'NotBuilt', 'Importing', 'Processing',
}
STABLE_LOCALE_STATES = {'Built', 'ReadyExpressTesting', 'Failed', 'NotBuilt'}


def _dedupe(items, identity, subject):
    result = {}
    for item in items:
        if not isinstance(item, dict):
            raise NoData(f'Lex {subject} inventory contains an invalid item')
        identifier = item.get(identity)
        if not isinstance(identifier, str) or not identifier:
            raise NoData(f'Lex {subject} is missing its identity')
        if identifier in result:
            if result[identifier] != item:
                raise NoData(f'Lex {subject} changed during pagination')
            continue
        result[identifier] = item
    return result


def _identifier(value, subject):
    if (not isinstance(value, str) or len(value) != 10
            or not value.isalnum()):
        raise NoData(f'Lex {subject} has an invalid identity')
    return value


def _strings(items, field, subject, kind):
    """Return a required string field from a list of AWS structures."""
    if items is None:
        return []
    if not isinstance(items, list):
        raise NoData(f'Lex {subject} has an invalid {kind} inventory')
    result = []
    for item in items:
        value = item.get(field) if isinstance(item, dict) else None
        if not isinstance(value, str) or not value:
            raise NoData(f'Lex {subject} has an invalid {kind}')
        result.append(value)
    return result


def _utterances(value, subject):
    return _strings(value, 'utterance', subject, 'sample utterance')


def _code_units(value):
    """Return Unicode code units, matching the Lex quota definition."""
    return len(value.encode('utf-16-le')) // 2


def bots(ctx):
    # Repeated traversals are served by the context's own call cache.
    found = _dedupe(ctx.call(LEX, 'list_bots', 'botSummaries'),
                    'botId', 'bot')
    result = {}
    for bot_id, item in found.items():
        _identifier(bot_id, 'bot')
        if not isinstance(item.get('botName'), str) or not item['botName']:
            raise NoData('Lex bot is missing its name')
        if item.get('botStatus') not in BOT_STATES:
            raise NoData('Lex bot has an unknown state')
        if item.get('botType', 'Bot') not in BOT_TYPES:
            raise NoData('Lex bot has an unknown type')
        if item.get('botType', 'Bot') == 'Bot':
            result[bot_id] = item
    return result


def bot_versions(bot, ctx):
    found = _dedupe(
        ctx.call(LEX, 'list_bot_versions', 'botVersionSummaries',
                 botId=bot['botId']),
        'botVersion', 'bot version')
    for version, item in found.items():
        if version != 'DRAFT' and (not version.isdigit() or len(version) > 5):
            raise NoData('Lex bot version has an invalid identity')
        if item.get('botName') != bot['botName']:
            raise NoData('Lex bot version has an inconsistent parent')
        if item.get('botStatus') not in BOT_STATES:
            raise NoData('Lex bot version has an unknown state')
    if 'DRAFT' not in found:
        found['DRAFT'] = {
            'botVersion': 'DRAFT', 'botName': bot['botName'],
            'botStatus': bot['botStatus'],
        }
    return found


def versions_per_bot(ctx):
    values = []
    for bot in bots(ctx).values():
        versions = bot_versions(bot, ctx)
        count = sum(version != 'DRAFT' for version in versions)
        values.append((bot['botId'], count, None))
    return maximum(values, 'LexBot', 'lexv2-models:ListBots+ListBotVersions')


def _slot_utterances(setting, subject):
    if not isinstance(setting, dict):
        raise NoData(f'Lex {subject} is missing its elicitation settings')
    return _utterances(setting.get('sampleUtterances'), subject)


def _slots(bot, version, locale, intent, ctx):
    kwargs = {
        'botId': bot['botId'], 'botVersion': version,
        'localeId': locale['localeId'], 'intentId': intent['intentId'],
    }
    found = _dedupe(ctx.call(LEX, 'list_slots', 'slotSummaries', **kwargs),
                    'slotId', 'slot')
    result = []
    for slot_id, summary in found.items():
        _identifier(slot_id, 'slot')
        detail = ctx.call(LEX, 'describe_slot', slotId=slot_id, **kwargs)
        if (not isinstance(detail, dict) or detail.get('slotId') != slot_id
                or detail.get('slotName') != summary.get('slotName')
                or any(detail.get(field) != value
                       for field, value in kwargs.items())):
            raise NoData('Lex slot has an inconsistent parent or detail')
        result.append({
            'id': slot_id,
            'utterances': _slot_utterances(
                detail.get('valueElicitationSetting'), 'slot'),
        })
        subslots = detail.get('subSlotSetting')
        if subslots is None:
            continue
        specifications = (subslots.get('slotSpecifications')
                          if isinstance(subslots, dict) else None)
        if not isinstance(specifications, dict):
            raise NoData('Lex composite slot has an invalid subslot inventory')
        for name, specification in specifications.items():
            if (not isinstance(name, str) or not name
                    or not isinstance(specification, dict)):
                raise NoData('Lex composite slot has an invalid subslot')
            result.append({
                'id': f'{slot_id}/{name}',
                'utterances': _slot_utterances(
                    specification.get('valueElicitationSetting'), 'subslot'),
            })
    return result


def _intents(bot, version, locale, ctx):
    kwargs = {'botId': bot['botId'], 'botVersion': version,
              'localeId': locale['localeId']}
    found = _dedupe(ctx.call(LEX, 'list_intents', 'intentSummaries', **kwargs),
                    'intentId', 'intent')
    result = []
    for intent_id, summary in found.items():
        _identifier(intent_id, 'intent')
        detail = ctx.call(LEX, 'describe_intent', intentId=intent_id, **kwargs)
        if (not isinstance(detail, dict) or detail.get('intentId') != intent_id
                or detail.get('intentName') != summary.get('intentName')
                or any(detail.get(field) != value
                       for field, value in kwargs.items())):
            raise NoData('Lex intent has an inconsistent parent or detail')
        intent = {
            'id': intent_id,
            'utterances': _utterances(detail.get('sampleUtterances'), 'intent'),
        }
        intent['slots'] = _slots(bot, version, locale, detail, ctx)
        result.append(intent)
    return result


def _slot_types(bot, version, locale, ctx):
    kwargs = {'botId': bot['botId'], 'botVersion': version,
              'localeId': locale['localeId']}
    found = _dedupe(
        ctx.call(LEX, 'list_slot_types', 'slotTypeSummaries', **kwargs),
        'slotTypeId', 'slot type')
    result = []
    for slot_type_id, summary in found.items():
        _identifier(slot_type_id, 'slot type')
        detail = ctx.call(
            LEX, 'describe_slot_type', slotTypeId=slot_type_id, **kwargs)
        if (not isinstance(detail, dict)
                or detail.get('slotTypeId') != slot_type_id
                or detail.get('slotTypeName') != summary.get('slotTypeName')
                or any(detail.get(field) != value
                       for field, value in kwargs.items())):
            raise NoData('Lex slot type has an inconsistent parent or detail')
        values = detail.get('slotTypeValues', [])
        if not isinstance(values, list):
            raise NoData('Lex slot type has an invalid value inventory')
        strings = []
        for value in values:
            sample = value.get('sampleValue') if isinstance(value, dict) else None
            canonical = sample.get('value') if isinstance(sample, dict) else None
            if not isinstance(canonical, str) or not canonical:
                raise NoData('Lex slot type has an invalid value')
            # Synonyms are SampleValue structures, not plain strings.
            synonyms = _strings(value.get('synonyms'), 'value',
                                'slot type', 'synonym')
            strings.extend((canonical, *synonyms))
        result.append({'id': slot_type_id, 'values': strings})
    return result


def model_inventory(ctx):
    result = []
    for bot in bots(ctx).values():
        if bot['botStatus'] not in STABLE_BOT_STATES:
            raise NoData('Lex bot configuration is changing')
        for version, version_item in bot_versions(bot, ctx).items():
            if version_item['botStatus'] not in STABLE_BOT_STATES:
                raise NoData('Lex bot version configuration is changing')
            locales = _dedupe(
                ctx.call(LEX, 'list_bot_locales', 'botLocaleSummaries',
                         botId=bot['botId'], botVersion=version),
                'localeId', 'bot locale')
            for locale_id, locale in locales.items():
                if not isinstance(locale_id, str) or not locale_id:
                    raise NoData('Lex bot locale has an invalid identity')
                if locale.get('botLocaleStatus') not in LOCALE_STATES:
                    raise NoData('Lex bot locale has an unknown state')
                if locale['botLocaleStatus'] not in STABLE_LOCALE_STATES:
                    raise NoData('Lex bot locale configuration is changing')
                result.append({
                    'id': f"{bot['botId']}:{version}:{locale_id}",
                    'intents': _intents(bot, version, locale, ctx),
                    'slot_types': _slot_types(bot, version, locale, ctx),
                })
    return result


def _per_locale(ctx, value, source):
    return maximum(((locale['id'], value(locale), None)
                    for locale in model_inventory(ctx)),
                   'LexBotLocale', source)


def _all_utterances(locale):
    for intent in locale['intents']:
        yield from intent['utterances']
        for slot in intent['slots']:
            yield from slot['utterances']


def slots_per_intent(ctx):
    values = ((intent['id'], len(intent['slots']), None)
              for locale in model_inventory(ctx)
              for intent in locale['intents'])
    return maximum(values, 'LexIntent', 'lexv2-models:ListSlots+DescribeSlot')


def utterances_per_intent(ctx):
    values = ((intent['id'], len(intent['utterances']), None)
              for locale in model_inventory(ctx)
              for intent in locale['intents'])
    return maximum(values, 'LexIntent', 'lexv2-models:DescribeIntent')


def utterances_per_slot(ctx):
    values = ((slot['id'], len(slot['utterances']), None)
              for locale in model_inventory(ctx)
              for intent in locale['intents'] for slot in intent['slots'])
    return maximum(values, 'LexSlot', 'lexv2-models:DescribeSlot')


def characters_per_utterance(ctx):
    values = ((locale['id'], _code_units(utterance), None)
              for locale in model_inventory(ctx)
              for utterance in _all_utterances(locale))
    return maximum(values, 'LexSampleUtterance',
                   'lexv2-models:DescribeIntent+DescribeSlot')


def values_per_slot_type(ctx):
    values = ((slot_type['id'], len(slot_type['values']), None)
              for locale in model_inventory(ctx)
              for slot_type in locale['slot_types'])
    return maximum(values, 'LexSlotType', 'lexv2-models:DescribeSlotType')


def characters_per_slot_value(ctx):
    values = ((slot_type['id'], _code_units(value), None)
              for locale in model_inventory(ctx)
              for slot_type in locale['slot_types']
              for value in slot_type['values'])
    return maximum(values, 'LexSlotTypeValue',
                   'lexv2-models:DescribeSlotType')


CHECKS = [
    ('L-36FA8BD2', 'Bots per account',
     lambda ctx: dict(usage=len(bots(ctx)), source='lexv2-models:ListBots',
                      method='ACCOUNT_COUNT')),
    ('L-BCD96794', 'Versions per bot', versions_per_bot),
    ('L-3D56827F', 'Custom slot types per bot locale',
     lambda ctx: _per_locale(
         ctx, lambda locale: len(locale['slot_types']),
         'lexv2-models:ListSlotTypes')),
    ('L-824BBA1D', 'Custom slot type values and synonyms per bot locale',
     lambda ctx: _per_locale(
         ctx, lambda locale: sum(len(item['values'])
                                 for item in locale['slot_types']),
         'lexv2-models:ListSlotTypes+DescribeSlotType')),
    ('L-9030FC28', 'Slots per bot locale',
     lambda ctx: _per_locale(
         ctx, lambda locale: sum(len(intent['slots'])
                                 for intent in locale['intents']),
         'lexv2-models:ListIntents+ListSlots+DescribeSlot')),
    ('L-606F3490', 'Total characters in sample utterances per bot locale',
     lambda ctx: _per_locale(
         ctx, lambda locale: sum(map(_code_units, _all_utterances(locale))),
         'lexv2-models:DescribeIntent+DescribeSlot')),
    ('L-311093B9', 'Slots per intent', slots_per_intent),
    ('L-ED50DA7C', 'Sample utterances per intent', utterances_per_intent),
    ('L-77D6C60C', 'Sample utterances per slot', utterances_per_slot),
    ('L-4F321B43', 'Characters per sample utterance',
     characters_per_utterance),
    ('L-52297D95', 'Values and synonyms per custom slot type',
     values_per_slot_type),
    ('L-9E828085', 'Characters per custom slot type value',
     characters_per_slot_value),
]


def get_current_quotastatus_lex(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'lex' for service, _ in context.quotas):
        return []
    return context.run('lex', CHECKS, skip)
