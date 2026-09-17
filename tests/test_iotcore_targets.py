"""IoT Core scopes reached by inverting a walk or by reading a thing type."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import iotcore
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'
CERTIFICATE = f'arn:aws:iot:eu-central-1:{ACCOUNT}:cert/abc'
COGNITO = 'eu-central-1:11111111-2222-3333-4444-555555555555'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'iotcore', 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(code):
    return next(fn for quota, _name, fn in iotcore.CHECKS if quota == code)


def http_action(headers):
    return {'http': {'url': 'https://example.test/hook',
                     'headers': [{'key': f'k{index}', 'value': 'v'}
                                 for index in range(headers)]}}


def stub_rules(stub, rules):
    """Stub the topic rule walk: the listing, then one detail call per rule."""
    stub.add_response('list_topic_rules',
                      {'rules': [{'ruleName': name} for name, _ in rules]}, {})
    for name, actions in rules:
        stub.add_response('get_topic_rule',
                          {'rule': {'ruleName': name, 'actions': list(actions)}},
                          {'ruleName': name})


def test_the_action_carrying_the_most_http_headers_is_measured():
    ctx = context('L-5C16DE50')
    with Stubber(ctx.client('iot')) as stub:
        stub_rules(stub, [('quiet', [http_action(1)]),
                          ('busy', [{'republish': {'roleArn': 'arn:role', 'topic': 't'}},
                                    http_action(4)])])
        result = check('L-5C16DE50')(ctx)
        assert (result['usage'], result['resource_id']) == (4, 'busy#1')
        stub.assert_no_pending_responses()


def test_an_action_that_is_not_an_http_action_has_no_headers_to_measure():
    ctx = context('L-5C16DE50')
    with Stubber(ctx.client('iot')) as stub:
        stub_rules(stub, [('plain', [{'sqs': {'roleArn': 'arn:role',
                                              'queueUrl': 'https://q'}}])])
        assert check('L-5C16DE50')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_an_http_action_without_headers_counts_as_zero():
    """A hook that sets no header still holds none rather than dropping out."""
    ctx = context('L-5C16DE50')
    with Stubber(ctx.client('iot')) as stub:
        stub_rules(stub, [('bare', [{'http': {'url': 'https://example.test/hook'}}])])
        result = check('L-5C16DE50')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'bare#0')
        stub.assert_no_pending_responses()


def stub_policy_targets(stub, policies):
    """Stub the policy listing, then the targets of each policy."""
    stub.add_response('list_policies',
                      {'policies': [{'policyName': name} for name, _ in policies]}, {})
    for name, targets in policies:
        stub.add_response('list_targets_for_policy', {'targets': list(targets)},
                          {'policyName': name})


def test_policies_are_counted_per_target_rather_than_per_certificate():
    """A Cognito identity is a target too, so the walk is inverted to reach it."""
    ctx = context('L-BC2638B3')
    with Stubber(ctx.client('iot')) as stub:
        stub_policy_targets(stub, [('shared', [CERTIFICATE, COGNITO]),
                                   ('extra', [CERTIFICATE])])
        result = check('L-BC2638B3')(ctx)
        assert (result['usage'], result['resource_id']) == (2, CERTIFICATE)
        stub.assert_no_pending_responses()


def test_a_cognito_identity_can_hold_the_maximum():
    ctx = context('L-BC2638B3')
    with Stubber(ctx.client('iot')) as stub:
        stub_policy_targets(stub, [('one', [COGNITO]), ('two', [COGNITO]),
                                   ('three', [CERTIFICATE])])
        result = check('L-BC2638B3')(ctx)
        assert (result['usage'], result['resource_id']) == (2, COGNITO)
        stub.assert_no_pending_responses()


def test_a_policy_attached_to_nothing_leaves_the_maximum_alone():
    ctx = context('L-BC2638B3')
    with Stubber(ctx.client('iot')) as stub:
        stub_policy_targets(stub, [('detached', [])])
        assert check('L-BC2638B3')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_a_policy_without_a_name_is_reported():
    """Skipping an unnamed policy would undercount every target it holds."""
    ctx = context('L-BC2638B3')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_policies', {'policies': [{'policyArn': 'arn:p'}]}, {})
        with pytest.raises(NoData, match='name'):
            check('L-BC2638B3')(ctx)


def thing_type(name, attributes):
    return {'thingTypeName': name, 'thingTypeProperties': {'mqtt5Configuration': {
        'propagatingAttributes': [{'userPropertyKey': f'k{index}',
                                   'thingAttribute': 'a'}
                                  for index in range(attributes)]}}}


def test_the_thing_type_propagating_the_most_attributes_is_measured():
    ctx = context('L-FBACAF74')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_thing_types', {'thingTypes': [
            thing_type('quiet', 1), thing_type('busy', 3)]}, {})
        result = check('L-FBACAF74')(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'busy')
        stub.assert_no_pending_responses()


def test_a_thing_type_configuring_no_mqtt5_propagation_counts_as_zero():
    ctx = context('L-FBACAF74')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_thing_types', {'thingTypes': [
            {'thingTypeName': 'plain', 'thingTypeProperties': {}}]}, {})
        result = check('L-FBACAF74')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'plain')
        stub.assert_no_pending_responses()


def test_a_thing_type_without_a_name_is_reported():
    ctx = context('L-FBACAF74')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_thing_types', {'thingTypes': [{'thingTypeArn': 'arn:t'}]},
                          {})
        with pytest.raises(NoData, match='name'):
            check('L-FBACAF74')(ctx)


def test_the_header_check_reuses_the_walk_the_action_count_already_makes():
    """Both quotas read one topic rule listing, so the run asks for it once."""
    ctx = context('L-5C16DE50')
    with Stubber(ctx.client('iot')) as stub:
        stub_rules(stub, [('busy', [http_action(2), http_action(5)])])
        assert check('L-51309716')(ctx)['usage'] == 2
        assert check('L-5C16DE50')(ctx)['usage'] == 5
        stub.assert_no_pending_responses()
