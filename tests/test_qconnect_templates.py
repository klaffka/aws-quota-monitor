"""Amazon Q in Connect message templates and assistant associations."""
from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks.misc_counts import CHECKS
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 16, tzinfo=UTC)
BASES = ['kb-one', 'kb-two']
TEMPLATES = {'kb-one': ['mt-a', 'mt-b'], 'kb-two': ['mt-c']}


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'wisdom', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _name, fn in CHECKS['wisdom'] if quota == code)


def template(base, identifier):
    return {'messageTemplateArn': f'arn:aws:wisdom:::template/{identifier}',
            'messageTemplateId': identifier, 'knowledgeBaseArn': f'arn:aws:wisdom:::kb/{base}',
            'knowledgeBaseId': base, 'name': identifier, 'channelSubtype': 'EMAIL',
            'createdTime': MOMENT, 'lastModifiedTime': MOMENT, 'lastModifiedBy': 'me'}


def stub_templates(stub):
    stub.add_response('list_knowledge_bases', {'knowledgeBaseSummaries': [
        {'knowledgeBaseId': base, 'knowledgeBaseArn': f'arn:aws:wisdom:::kb/{base}',
         'name': base, 'knowledgeBaseType': 'CUSTOM', 'status': 'ACTIVE'}
        for base in BASES]}, {})
    for base, templates in TEMPLATES.items():
        stub.add_response('list_message_templates',
                          {'messageTemplateSummaries': [template(base, t) for t in templates]},
                          {'knowledgeBaseId': base})


def test_message_templates_use_the_largest_knowledge_base():
    ctx = context('L-8EAC5E16')
    with Stubber(ctx.client('qconnect')) as stub:
        stub_templates(stub)
        result = check('L-8EAC5E16')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'kb-one')
        stub.assert_no_pending_responses()


def test_versions_use_the_template_with_the_most_versions():
    ctx = context('L-F84C0EB2')
    with Stubber(ctx.client('qconnect')) as stub:
        stub_templates(stub)
        counts = {'mt-a': 1, 'mt-b': 3, 'mt-c': 2}
        for base, templates in TEMPLATES.items():
            for identifier in templates:
                stub.add_response('list_message_template_versions', {
                    'messageTemplateVersionSummaries': [
                        {'messageTemplateArn': f'arn:aws:wisdom:::template/{identifier}',
                         'messageTemplateId': identifier,
                         'knowledgeBaseArn': f'arn:aws:wisdom:::kb/{base}',
                         'knowledgeBaseId': base, 'name': identifier,
                         'channelSubtype': 'EMAIL', 'isActive': False,
                         'versionNumber': index + 1}
                        for index in range(counts[identifier])]},
                    {'knowledgeBaseId': base, 'messageTemplateId': identifier})
        result = check('L-F84C0EB2')(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'kb-one/mt-b')
        stub.assert_no_pending_responses()


def test_assistant_associations_use_the_busiest_assistant():
    ctx = context('L-DA307021')
    with Stubber(ctx.client('wisdom')) as stub:
        stub.add_response('list_assistants', {'assistantSummaries': [
            {'assistantId': 'a1', 'assistantArn': 'arn:assistant/1', 'name': 'one',
             'type': 'AGENT', 'status': 'ACTIVE'},
            {'assistantId': 'a2', 'assistantArn': 'arn:assistant/2', 'name': 'two',
             'type': 'AGENT', 'status': 'ACTIVE'}]}, {})
        for assistant, count in [('a1', 1), ('a2', 2)]:
            stub.add_response('list_assistant_associations', {
                'assistantAssociationSummaries': [
                    {'assistantAssociationId': f'{assistant}-{index}',
                     'assistantAssociationArn': f'arn:assoc/{assistant}{index}',
                     'assistantId': assistant, 'assistantArn': f'arn:assistant/{assistant}',
                     'associationType': 'KNOWLEDGE_BASE',
                     'associationData': {'knowledgeBaseAssociation': {}}}
                    for index in range(count)]}, {'assistantId': assistant})
        result = check('L-DA307021')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'a2')
        stub.assert_no_pending_responses()


def test_a_knowledge_base_without_an_identity_is_reported_as_no_data():
    from unittest.mock import Mock

    ctx = Mock()
    ctx.call.return_value = [{'name': 'nameless'}]
    with pytest.raises(NoData, match='missing its identity'):
        check('L-8EAC5E16')(ctx)
