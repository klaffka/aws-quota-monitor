"""Amazon Connect Cases domain and configuration inventories."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


RULE_TYPES = {'Required': 'required', 'Hidden': 'hidden', 'FieldOptions': 'fieldOptions'}
RELATED_TYPES = {'Contact': 'contact', 'Comment': 'comment', 'File': 'file', 'Sla': 'sla',
                 'ConnectCase': 'connectCase', 'Custom': 'custom'}


def required_id(item, field):
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise NoData(f'Cases inventory is missing {field}')
    return value


def domains(ctx):
    result = {}
    for item in ctx.call('connectcases', 'list_domains', 'domains'):
        identity = required_id(item, 'domainId')
        if identity in result and result[identity] != item:
            raise NoData('Cases domain changed during pagination')
        result[identity] = item
    return [result[key] for key in sorted(result)]


def templates_per_domain(ctx):
    values = []
    for domain in domains(ctx):
        identifier = domain['domainId']
        values.append((identifier, len(templates(ctx, identifier)), None))
    return maximum(values, 'CasesDomain', 'connectcases:ListTemplates')


def rules_per_domain(ctx):
    values = []
    for domain in domains(ctx):
        identifier = domain['domainId']
        values.append((identifier, len(case_rule_summaries(ctx, identifier)), None))
    return maximum(values, 'CasesDomain', 'connectcases:ListCaseRules')


def templates(ctx, domain_id):
    result = {}
    for item in ctx.call('connectcases', 'list_templates', 'templates', domainId=domain_id):
        identity = required_id(item, 'templateId')
        if identity in result and result[identity] != item:
            raise NoData('Cases template changed during pagination')
        result[identity] = item
    return [result[key] for key in sorted(result)]


def case_rule_summaries(ctx, domain_id):
    result = {}
    for item in ctx.call('connectcases', 'list_case_rules', 'caseRules', domainId=domain_id):
        identity = required_id(item, 'caseRuleId')
        if item.get('ruleType') not in RULE_TYPES:
            raise NoData('Cases rule inventory has an unknown rule type')
        if identity in result and result[identity] != item:
            raise NoData('Cases rule changed during pagination')
        result[identity] = item
    return result


def case_rule_details(ctx, domain_id):
    summaries = case_rule_summaries(ctx, domain_id)
    result = {}
    identities = sorted(summaries)
    for offset in range(0, len(identities), 50):
        requested = identities[offset:offset + 50]
        response = ctx.call('connectcases', 'batch_get_case_rule',
                            domainId=domain_id, caseRules=[{'id': identity} for identity in requested])
        if response.get('errors') or response.get('unprocessedCaseRules'):
            raise NoData('Cases rule batch was incomplete')
        items = response.get('caseRules')
        if not isinstance(items, list):
            raise NoData('Cases rule batch has no result list')
        for item in items:
            identity = required_id(item, 'caseRuleId')
            if identity not in requested or item.get('deleted') is True:
                raise NoData('Cases rule detail is deleted or has an unexpected identity')
            expected = RULE_TYPES[summaries[identity]['ruleType']]
            rule = item.get('rule')
            if not isinstance(rule, dict) or set(rule) != {expected} or not isinstance(rule[expected], dict):
                raise NoData('Cases rule detail has an inconsistent rule type')
            if identity in result and result[identity] != item:
                raise NoData('Cases rule detail changed during collection')
            result[identity] = item
        if set(requested) != set(result).intersection(requested):
            raise NoData('Cases rule batch omitted a requested rule')
    return result


def field_option_rule_measure(ctx, measure):
    values = []
    for domain in domains(ctx):
        did = domain['domainId']
        for identity, item in case_rule_details(ctx, did).items():
            if 'fieldOptions' not in item['rule']:
                continue
            mappings = item['rule']['fieldOptions'].get('parentChildFieldOptionsMappings')
            if not isinstance(mappings, list) or not mappings:
                raise NoData('Cases field-options rule has no mappings')
            child_count = 0
            for mapping in mappings:
                if not isinstance(mapping, dict) or not isinstance(mapping.get('parentFieldOptionValue'), str):
                    raise NoData('Cases field-options rule has an invalid parent value')
                children = mapping.get('childFieldOptionValues')
                if not isinstance(children, list) or any(not isinstance(value, str) for value in children):
                    raise NoData('Cases field-options rule has invalid child values')
                child_count += len(children)
            usage = len(mappings) if measure == 'parent_values' else child_count
            values.append((f'{did}/rule/{identity}', usage, None))
    return maximum(values, 'CasesFieldOptionsRule', 'connectcases:ListCaseRules+BatchGetCaseRule')


def field_option_rules_per_template(ctx):
    values = []
    for domain in domains(ctx):
        did = domain['domainId']
        summaries = case_rule_summaries(ctx, did)
        for summary in templates(ctx, did):
            identity = required_id(summary, 'templateId')
            detail = ctx.call('connectcases', 'get_template', domainId=did, templateId=identity)
            if detail.get('templateId') != identity or detail.get('deleted') is True:
                raise NoData('Cases template detail is deleted or has a different identity')
            rules = detail.get('rules')
            if not isinstance(rules, list):
                raise NoData('Cases template has no rule association list')
            count = 0
            for association in rules:
                if not isinstance(association, dict):
                    raise NoData('Cases template has an invalid rule association')
                rule_id = required_id(association, 'caseRuleId')
                if rule_id not in summaries:
                    raise NoData('Cases template references an unknown rule')
                field_id = association.get('fieldId')
                if field_id is not None and (not isinstance(field_id, str) or not field_id):
                    raise NoData('Cases template rule has an invalid field identity')
                count += summaries[rule_id]['ruleType'] == 'FieldOptions'
            values.append((f'{did}/template/{identity}', count, None))
    return maximum(values, 'CasesTemplate', 'connectcases:ListTemplates+GetTemplate+ListCaseRules')


def related_items(ctx, domain_id):
    result = {}
    for item in ctx.call('connectcases', 'search_all_related_items', 'relatedItems', domainId=domain_id):
        case_id = required_id(item, 'caseId')
        identity = required_id(item, 'relatedItemId')
        kind = item.get('type')
        content = item.get('content')
        expected = RELATED_TYPES.get(kind)
        if expected is None or not isinstance(content, dict) or set(content) != {expected} \
                or not isinstance(content[expected], dict):
            raise NoData('Cases related item has an inconsistent content type')
        key = (case_id, identity)
        if key in result and result[key] != item:
            raise NoData('Cases related item changed during pagination')
        result[key] = item
    return [result[key] for key in sorted(result)]


def related_item_measure(ctx, measure):
    values = []
    for domain in domains(ctx):
        did = domain['domainId']
        counts = {}
        for item in related_items(ctx, did):
            case_id = item['caseId']
            if measure == 'custom_fields':
                if item['type'] != 'Custom':
                    continue
                fields = item['content']['custom'].get('fields')
                if not isinstance(fields, list):
                    raise NoData('Cases custom related item has no field list')
                for field in fields:
                    if not isinstance(field, dict):
                        raise NoData('Cases custom related item has an invalid field')
                    required_id(field, 'id')
                    value = field.get('value')
                    if not isinstance(value, dict) or len(value) != 1:
                        raise NoData('Cases custom related item has an invalid field value')
                values.append((f"{did}/case/{case_id}/related/{item['relatedItemId']}", len(fields), None))
                continue
            include = measure == 'related_items' or (measure == 'files' and item['type'] == 'File') \
                or (measure == 'slas' and item['type'] == 'Sla')
            if include:
                counts[case_id] = counts.get(case_id, 0) + 1
        values.extend((f'{did}/case/{case_id}', count, None) for case_id, count in counts.items())
    return maximum(values, 'CasesCase' if measure != 'custom_fields' else 'CasesRelatedItem',
                   'connectcases:SearchAllRelatedItems')


def domain_children(ctx, method, key, resource_type):
    values = []
    for domain in domains(ctx):
        identity = domain['domainId']
        items = ctx.call('connectcases', method, key, domainId=identity)
        values.append((identity, len(items), None))
    return maximum(values, resource_type, f'connectcases:{method}')


def field_options(ctx):
    values = []
    for domain in domains(ctx):
        did = domain['domainId']
        fields = ctx.call('connectcases', 'list_fields', 'fields', domainId=did)
        for field in fields:
            field_type = field.get('type')
            if field_type not in {'Text', 'Number', 'Boolean', 'DateTime', 'SingleSelect', 'Url', 'User'}:
                raise NoData('Cases field has an unknown type')
            if field_type != 'SingleSelect':
                continue
            fid = required_id(field, 'fieldId')
            options = ctx.call('connectcases', 'list_field_options', 'options', domainId=did, fieldId=fid)
            values.append((f'{did}/field/{fid}', len(options), None))
    return maximum(values, 'CasesSingleSelectField', 'connectcases:ListFields+ListFieldOptions')


def layout_field_count(content):
    if not isinstance(content, dict) or set(content) != {'basic'} or not isinstance(content['basic'], dict):
        raise NoData('Cases layout has an unknown content type')
    count = 0
    for panel in ('topPanel', 'moreInfo'):
        sections = content['basic'].get(panel, {}).get('sections', [])
        if not isinstance(sections, list):
            raise NoData('Cases layout has an invalid section list')
        for section in sections:
            if not isinstance(section, dict) or set(section) != {'fieldGroup'}:
                raise NoData('Cases layout has an unknown section type')
            group = section['fieldGroup']
            if not isinstance(group, dict) or not isinstance(group.get('fields'), list):
                raise NoData('Cases layout field group is incomplete')
            for field in group['fields']:
                required_id(field, 'id')
                count += 1
    return count


def fields_per_layout(ctx):
    values = []
    for domain in domains(ctx):
        did = domain['domainId']
        for layout in ctx.call('connectcases', 'list_layouts', 'layouts', domainId=did):
            lid = required_id(layout, 'layoutId')
            data = ctx.call('connectcases', 'get_layout', domainId=did, layoutId=lid)
            if data.get('layoutId') != lid or data.get('deleted') is True:
                raise NoData('Cases layout detail is deleted or has a different identity')
            values.append((f'{did}/layout/{lid}', layout_field_count(data.get('content')), None))
    return maximum(values, 'CasesLayout', 'connectcases:ListLayouts+GetLayout')


CHECKS = [
    ('L-C2B81BC3', 'Domains', lambda c: dict(usage=len(domains(c)),
                                             source='connectcases:ListDomains', method='ACCOUNT_COUNT')),
    ('L-0482161A', 'Templates per domain', templates_per_domain),
    ('L-228D6D2D', 'Case rules per domain', rules_per_domain),
]

EXTENDED_CHECKS = [
    ('L-C5B69356', 'Fields per domain',
     lambda c: domain_children(c, 'list_fields', 'fields', 'CasesDomain')),
    ('L-D0ED993F', 'Layouts per domain',
     lambda c: domain_children(c, 'list_layouts', 'layouts', 'CasesDomain')),
    ('L-E52A0E46', 'Field options per field', field_options),
    ('L-5B5E62BD', 'Case fields per layout', fields_per_layout),
    ('L-C1AF8D37', 'Related items per case',
     lambda c: related_item_measure(c, 'related_items')),
    ('L-930905B5', 'Attached files per case',
     lambda c: related_item_measure(c, 'files')),
    ('L-A7158118', 'Attached SLAs per case',
     lambda c: related_item_measure(c, 'slas')),
    ('L-7D21A319', 'Fields per related item',
     lambda c: related_item_measure(c, 'custom_fields')),
    ('L-F43DCB55', 'Parent field values per field options case rule',
     lambda c: field_option_rule_measure(c, 'parent_values')),
    ('L-435DBDE3', 'Child field values per field options case rule',
     lambda c: field_option_rule_measure(c, 'child_values')),
    ('L-8F7DFC0D', 'Field options case rules per template', field_option_rules_per_template),
]
ALL_CHECKS = CHECKS + EXTENDED_CHECKS


def get_current_quotastatus_cases(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'cases' for service, _ in context.quotas):
        return []
    checks = CHECKS + [check for check in EXTENDED_CHECKS if ('cases', check[0]) in context.quotas]
    return context.run('cases', checks, skip)
