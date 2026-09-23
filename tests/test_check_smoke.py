"""Run every registered check against a shape-accurate synthetic account.

The suite's Mock-based tests fabricate their own responses, so they cannot see
a wrong operation, a rejected parameter or a response key the API never
returns. This drives the real check through the real CheckContext against
botocore's own service model instead. A check that reaches ERROR here reaches
ERROR in production too, where nothing but a DynamoDB row records it.
"""
import pytest

from tests.shape_harness import entries, entry_points, run, run_entry

# Checks the harness cannot represent. Each needs a reason, and the set may
# only shrink: it is the list of checks nothing offline can vouch for.
ALLOWED = {
    # AddressFamily has no enum, so the generated value is not ipv4 or ipv6 and
    # the family-keyed tally raises before the check can count anything.
    ('vpc', 'L-0EA8095F'): 'prefix-list address family is generated, not ipv4/ipv6',
    ('vpc', 'L-93826ACB'): 'prefix-list address family is generated, not ipv4/ipv6',
    # Network address usage comes from CloudWatch, not from a modelled API.
    ('vpc', 'L-BB24F6E5'): 'network address usage needs a CloudWatch inventory',
    ('vpc', 'L-CD17FD4B'): 'network address usage needs a CloudWatch inventory',
    # A populated Environment.Error means the function's environment is broken;
    # the check refuses it, and the generated response always fills that member.
    ('lambda', 'L-6581F036'): 'generated GetFunctionConfiguration reports an environment error',
}

MODULES = sorted({(module, service) for module, service, _ in entries()})
CHECKS = {(module, service): checks for module, service, checks in entries()}


def failures(module, service, populated):
    results, _sites = run(service, CHECKS[(module, service)], populated=populated)
    return [f"{result['quotaCode']}: {result['qualityReason'].splitlines()[0]}"
            for result in results
            if result['qualityStatus'] == 'ERROR'
            and (service, result['quotaCode']) not in ALLOWED]


@pytest.mark.parametrize('module, service', MODULES, ids=lambda value: value)
def test_every_check_measures_a_populated_account(module, service):
    """A wrong operation, parameter or response key surfaces here, not in production."""
    assert not failures(module, service, populated=True)


@pytest.mark.parametrize('module, service', MODULES, ids=lambda value: value)
def test_every_check_survives_an_empty_account(module, service):
    """A fresh account returns empty inventories; no check may fail on one."""
    assert not failures(module, service, populated=False)


def test_the_allowlist_only_covers_checks_that_still_need_it():
    """An entry that no longer fails is an entry that must go."""
    stale = set(ALLOWED)
    for module, service in MODULES:
        for populated in (True, False):
            results, _ = run(service, CHECKS[(module, service)], populated=populated)
            for result in results:
                if result['qualityStatus'] == 'ERROR':
                    stale.discard((service, result['quotaCode']))
    assert not stale, f'allowlisted checks that now pass: {sorted(stale)}'


ENTRY_POINTS = sorted(entry_points())


@pytest.mark.parametrize('module, entry, keys', ENTRY_POINTS, ids=lambda value: str(value))
@pytest.mark.parametrize('populated', [True, False], ids=['populated', 'empty'])
def test_every_entry_point_module_runs_without_error(module, entry, keys, populated):
    """These modules build their checks when called, so CHECKS discovery misses them."""
    results, _sites = run_entry(entry, keys, populated=populated)
    failures = [f"{result['quotaCode']}: {result['qualityReason'].splitlines()[0]}"
                for result in results
                if result['qualityStatus'] == 'ERROR'
                and (result['serviceCode'], result['quotaCode']) not in ALLOWED]
    assert not failures, module


@pytest.mark.parametrize('module, entry, keys', ENTRY_POINTS, ids=lambda value: str(value))
def test_every_entry_point_declares_the_quotas_it_measures(module, entry, keys):
    """CUSTOM_KEYS is what coverage counts; a quota missing from it is measured
    every ten minutes and reported to nobody."""
    from importlib import import_module

    declared = set(import_module(module).CUSTOM_KEYS)
    results, _sites = run_entry(entry, sorted(declared))
    measured = {(result['serviceCode'], result['quotaCode']) for result in results}
    assert measured == declared, {'undeclared': sorted(measured - declared),
                                  'unmeasured': sorted(declared - measured)}


# Checks the harness drives no further than their first call. Against
# synthesised data each one reaches NO_DATA and stops, so every call it would
# make afterwards is recorded nowhere and tests/test_iam_action_prefixes.py
# cannot check the grant behind it. That is how four of the six Greengrass
# grants in 4d51a49 came to be added by hand.
#
# The reasons are semantic, not cosmetic: a Bedrock batch job needs a base model
# the module's own mapping resolves, a Connect quota needs to resolve to the
# instance it was requested for. Generating ARN-shaped strings and healthy enum
# values instead was measured and moves 274 of these to 263 while recording no
# additional call site, so the census records them rather than pretending to
# drive them.
#
# The map may only shrink. A check that starts running to completion must be
# removed from it, and a new entry is a new check nothing offline exercises past
# its first call.
UNEXERCISED = {
    'AWS Outposts site is missing required account identity data': {
        ('outposts', 'L-0B277C74'), ('outposts', 'L-3D389D34'),
    },
    'Application Auto Scaling inventory has an inconsistent namespace': {
        ('application-autoscaling', 'L-95848B5F'),
        ('application-autoscaling', 'L-9C25247C'),
        ('application-autoscaling', 'L-B395C81B'),
    },
    'Automated Reasoning policy identity is missing or inconsistent': {
        ('bedrock', 'L-07EE48DE'), ('bedrock', 'L-31B8EB64'), ('bedrock', 'L-54C7BE29'),
        ('bedrock', 'L-83504243'), ('bedrock', 'L-C4A2EDC7'), ('bedrock', 'L-F32E9946'),
    },
    'Batch job base model is not a foundation-model ARN': {
        ('bedrock', 'L-059C1AAB'), ('bedrock', 'L-07844084'), ('bedrock', 'L-10F69CA1'),
        ('bedrock', 'L-1570CF9E'), ('bedrock', 'L-1AC1CABC'), ('bedrock', 'L-220B8A25'),
        ('bedrock', 'L-3030E098'), ('bedrock', 'L-329D7443'), ('bedrock', 'L-391478D2'),
        ('bedrock', 'L-3CCB3548'), ('bedrock', 'L-50CC95A8'), ('bedrock', 'L-564C017C'),
        ('bedrock', 'L-5C48945B'), ('bedrock', 'L-5D367E5C'), ('bedrock', 'L-62E2A345'),
        ('bedrock', 'L-63020993'), ('bedrock', 'L-652C224A'), ('bedrock', 'L-79EFF176'),
        ('bedrock', 'L-7B9A79C8'), ('bedrock', 'L-7F2C6F33'), ('bedrock', 'L-87CD099E'),
        ('bedrock', 'L-89923E2C'), ('bedrock', 'L-8CC57EDA'), ('bedrock', 'L-91E3DBE2'),
        ('bedrock', 'L-95CB8E2F'), ('bedrock', 'L-9A0F509C'), ('bedrock', 'L-A0300844'),
        ('bedrock', 'L-A0AAB785'), ('bedrock', 'L-A986092E'), ('bedrock', 'L-B0F56DCF'),
        ('bedrock', 'L-C05EB25B'), ('bedrock', 'L-E2ED42E6'), ('bedrock', 'L-E453CCF3'),
        ('bedrock', 'L-E455959C'), ('bedrock', 'L-E83AC604'), ('bedrock', 'L-F30EAB98'),
        ('bedrock', 'L-FE130012'), ('bedrock', 'L-FE24F76E'), ('bedrock', 'L-FEA282F8'),
    },
    'Bedrock evaluation has no unambiguous configuration': {
        ('bedrock', 'L-61D10141'), ('bedrock', 'L-E939CCA4'), ('bedrock', 'L-FDA23835'),
    },
    'Bedrock inventory has an unknown version': {
        ('bedrock', 'L-08D49FA4'), ('bedrock', 'L-0F2A24D7'), ('bedrock', 'L-17987C44'),
        ('bedrock', 'L-2D84F8A3'), ('bedrock', 'L-32F1CE34'), ('bedrock', 'L-39128CD1'),
        ('bedrock', 'L-4F4FC597'), ('bedrock', 'L-517574A2'), ('bedrock', 'L-6CA39F00'),
        ('bedrock', 'L-6F08AA6D'), ('bedrock', 'L-7847F21F'), ('bedrock', 'L-8175E285'),
        ('bedrock', 'L-81F241B6'), ('bedrock', 'L-83D7FD1C'), ('bedrock', 'L-85DABFD4'),
        ('bedrock', 'L-8DBDC30B'), ('bedrock', 'L-99EDA841'), ('bedrock', 'L-A9C9E017'),
        ('bedrock', 'L-B536331C'), ('bedrock', 'L-CCB99FFA'), ('bedrock', 'L-D471AEAB'),
        ('bedrock', 'L-DF49A520'), ('bedrock', 'L-E211B5EA'), ('bedrock', 'L-FBBE47CA'),
    },
    'Blueprint version inventory has an unresolved version': {
        ('bedrock', 'L-21EE8B55'), ('bedrock', 'L-D3894D44'),
    },
    'Cases inventory is missing id': {
        ('cases', 'L-5B5E62BD'),
    },
    'Cases related item has an inconsistent content type': {
        ('cases', 'L-7D21A319'), ('cases', 'L-930905B5'), ('cases', 'L-A7158118'),
        ('cases', 'L-C1AF8D37'),
    },
    'Cases rule batch was incomplete': {
        ('cases', 'L-435DBDE3'), ('cases', 'L-F43DCB55'),
    },
    'Clean Rooms ML instance reservation is unverified in state CREATE_PENDING': {
        ('cleanrooms-ml', 'L-3D21F23B'), ('cleanrooms-ml', 'L-FF7AD06D'),
    },
    'CloudFormation stack has no processed template': {
        ('cloudformation', 'L-05BC894F'), ('cloudformation', 'L-1FFB6C73'),
        ('cloudformation', 'L-38FD7965'), ('cloudformation', 'L-3B2D14A7'),
        ('cloudformation', 'L-63D096B8'), ('cloudformation', 'L-722F1E58'),
        ('cloudformation', 'L-72B9A393'), ('cloudformation', 'L-7C7532D4'),
        ('cloudformation', 'L-84B50260'), ('cloudformation', 'L-87D14FB7'),
        ('cloudformation', 'L-D663BAB9'),
    },
    'CloudFormation template is not an object': {
        ('cloudformation', 'L-125EDA8C'),
    },
    'CloudFormation type inventory returned another extension kind': {
        ('cloudformation', 'L-091DF7D9'), ('cloudformation', 'L-24E9F9ED'),
        ('cloudformation', 'L-7E146E2E'), ('cloudformation', 'L-DCC58E6D'),
    },
    'CloudTrail trail has no valid ARN': {
        ('cloudtrail', 'L-203ED99D'), ('cloudtrail', 'L-71DEA5C6'), ('cloudtrail', 'L-9387CED7'),
    },
    'CodeBuild project disappeared while being read': {
        ('codebuild', 'L-33638FE6'), ('codebuild', 'L-4167E76F'),
        ('codebuild', 'L-BECF4531'), ('codebuild', 'L-EDB7A61A'),
    },
    'Connect applied quota does not resolve to the requested instance': {
        ('connect', 'L-02421311'), ('connect', 'L-0865B754'), ('connect', 'L-0AA82C05'),
        ('connect', 'L-19755C7E'), ('connect', 'L-19A87C94'), ('connect', 'L-20CD02F7'),
        ('connect', 'L-22922690'), ('connect', 'L-2D7CA70C'), ('connect', 'L-3828FBF0'),
        ('connect', 'L-50375162'), ('connect', 'L-516BC0EB'), ('connect', 'L-6402A996'),
        ('connect', 'L-68BBE2E8'), ('connect', 'L-735CD262'), ('connect', 'L-74395C97'),
        ('connect', 'L-790F20B4'), ('connect', 'L-7B867368'), ('connect', 'L-8F812903'),
        ('connect', 'L-9A46857E'), ('connect', 'L-B93A6612'), ('connect', 'L-BF789E19'),
        ('connect', 'L-C7548958'), ('connect', 'L-C8F22860'), ('connect', 'L-CCEA7427'),
        ('connect', 'L-D3E7BE26'), ('connect', 'L-D492D362'), ('connect', 'L-D55E707F'),
        ('connect', 'L-D68AAAE4'), ('connect', 'L-D945C9A8'), ('connect', 'L-DFA239E1'),
        ('connect', 'L-E10B281B'), ('connect', 'L-E3D2F503'), ('connect', 'L-F325A715'),
        ('connect', 'L-F4C86B27'), ('connect', 'L-FC6A5030'), ('connect', 'L-FFE16A0F'),
    },
    'Connect campaign state could not be read': {
        ('connect-campaigns', 'L-7F7B4C39'),
    },
    'Custom Labels project inventory returned another feature': {
        ('rekognition', 'L-0B2CE4DD'), ('rekognition', 'L-14D0BC19'),
        ('rekognition', 'L-4FA65ECB'), ('rekognition', 'L-5E225387'),
        ('rekognition', 'L-9CF05323'), ('rekognition', 'L-B3EE7891'),
        ('rekognition', 'L-F1558568'),
    },
    'DLM sharing rule has invalid target accounts': {
        ('dlm', 'L-DCA05F2F'),
    },
    'FinSpace volume detail is inconsistent': {
        ('finspace', 'L-2B5C0922'),
    },
    'Firewall Manager managed service data is not valid JSON': {
        ('fms', 'L-743D9B7E'),
    },
    'Greengrass group names a definition version that is not an ARN': {
        ('greengrass', 'L-172983AD'), ('greengrass', 'L-56EE2BF6'),
        ('greengrass', 'L-59276CBA'), ('greengrass', 'L-966A9851'),
        ('greengrass', 'L-AC2D5DCC'), ('greengrass', 'L-F7F6CD87'),
    },
    'Image Builder workflow has an invalid steps inventory': {
        ('imagebuilder', 'L-D9E1BB3C'),
    },
    'Inspector assessment run has no ARN': {
        ('inspector', 'L-12943E2F'),
    },
    'Inspector assessment target has no ARN': {
        ('inspector', 'L-E1AFB5F4'),
    },
    'Inspector assessment template has no ARN': {
        ('inspector', 'L-7A3AEC10'),
    },
    'IoT SiteWise model configuration is not in a stable ACTIVE state': {
        ('iotsitewise', 'L-1526C0DE'), ('iotsitewise', 'L-23AAE9E6'),
        ('iotsitewise', 'L-6F52837A'), ('iotsitewise', 'L-7E24D4D3'),
        ('iotsitewise', 'L-A5BAACA9'), ('iotsitewise', 'L-BEF0A9F6'),
        ('iotsitewise', 'L-C90B3537'), ('iotsitewise', 'L-CEBEAFA0'),
        ('iotsitewise', 'L-D8008DC7'), ('iotsitewise', 'L-E789A464'),
    },
    'IoT SiteWise returned a model of an unexpected type': {
        ('iotsitewise', 'L-002F6D60'), ('iotsitewise', 'L-0114DD6D'),
        ('iotsitewise', 'L-2AE3919B'), ('iotsitewise', 'L-37C04251'),
        ('iotsitewise', 'L-622D18F7'), ('iotsitewise', 'L-9EE97145'),
        ('iotsitewise', 'L-C6919A10'), ('iotsitewise', 'L-F1B7F675'),
    },
    'IoT SiteWise returned a non-running bulk import job': {
        ('iotsitewise', 'L-1DE0546B'),
    },
    'KMS key has an inconsistent ARN': {
        ('kms', 'L-0E66C9C0'), ('kms', 'L-340F62FB'), ('kms', 'L-C2F1777E'),
        ('kms', 'L-D594A657'),
    },
    'Lex bot configuration is changing': {
        ('lex', 'L-311093B9'), ('lex', 'L-3D56827F'), ('lex', 'L-4F321B43'),
        ('lex', 'L-52297D95'), ('lex', 'L-606F3490'), ('lex', 'L-77D6C60C'),
        ('lex', 'L-824BBA1D'), ('lex', 'L-9030FC28'), ('lex', 'L-9E828085'),
        ('lex', 'L-ED50DA7C'),
    },
    'Lex bot version has an invalid identity': {
        ('lex', 'L-BCD96794'),
    },
    'Network Firewall rule-group detail is inconsistent': {
        ('network-firewall', 'L-3E253D9A'), ('network-firewall', 'L-9E55B2E0'),
        ('network-firewall', 'L-CEEC5053'),
    },
    'OpenSearch Serverless lifecycle-policy batch was incomplete': {
        ('aoss', 'L-7077B8EB'),
    },
    'OpenSearch Serverless policy detail is inconsistent': {
        ('aoss', 'L-877395DB'),
    },
    'OpenSearch Serverless security-config detail is inconsistent': {
        ('aoss', 'L-51EC5B57'),
    },
    'PCA Connector AD connector has an inconsistent ARN': {
        ('pca-connector-ad', 'L-351D0DCC'), ('pca-connector-ad', 'L-B2C010E5'),
        ('pca-connector-ad', 'L-FB47817C'),
    },
    'PCA Connector SCEP connector has an inconsistent ARN': {
        ('pca-connector-scep', 'L-CB21FAEA'), ('pca-connector-scep', 'L-D42FC980'),
    },
    'Payment Cryptography alias has an invalid name': {
        ('payment-cryptography', 'L-10DEBB19'),
    },
    'Personalize batch inference job has an inconsistent ARN': {
        ('personalize', 'L-69B72005'),
    },
    'Personalize dataset group has an inconsistent ARN': {
        ('personalize', 'L-052ECD67'), ('personalize', 'L-14011066'),
        ('personalize', 'L-4D685096'), ('personalize', 'L-A11DBE93'),
        ('personalize', 'L-B9CFBC8B'), ('personalize', 'L-D9DD83B7'),
    },
    'Personalize schema has an inconsistent ARN': {
        ('personalize', 'L-037D5A71'),
    },
    'Personalize solution version has an inconsistent ARN': {
        ('personalize', 'L-9C16B368'),
    },
    'Proton connection inventory has an inconsistent account scope': {
        ('proton', 'L-6CC8209C'),
    },
    'Recycle Bin rule is missing a valid Identifier': {
        ('rbin', 'L-629917A2'), ('rbin', 'L-BCC6359E'),
    },
    'Rekognition media analysis job has an unresolved concurrent reservation': {
        ('rekognition', 'L-22FA69BA'),
    },
    'Rekognition stream processor has an unresolved type': {
        ('rekognition', 'L-0A2A7683'), ('rekognition', 'L-3269D948'),
        ('rekognition', 'L-70336415'), ('rekognition', 'L-8D9029A2'),
    },
    'Route 53 Profiles resource association is inconsistent': {
        ('route53profiles', 'L-0B404E57'), ('route53profiles', 'L-BA3424AB'),
        ('route53resolver', 'L-8B4B9B75'), ('route53resolver', 'L-F8A07EF1'),
    },
    'SQS delivery delay is not a number': {
        ('sqs', 'L-A7816957'),
    },
    'SQS in-flight message count is not a number': {
        ('sqs', 'L-C491D5A4'),
    },
    'SQS maximum message size is not a number': {
        ('sqs', 'L-49DA5CEC'),
    },
    'SQS message retention period is not a number': {
        ('sqs', 'L-2DA3E3B2'),
    },
    'SQS visibility timeout is not a number': {
        ('sqs', 'L-B2A3B9D5'),
    },
    'SSM document permission has an unknown account identity': {
        ('ssm', 'L-E7B4BBE8'), ('ssm', 'L-F5EE067E'),
    },
    'SSM version inventory has an unknown version': {
        ('ssm', 'L-E9FF4011'), ('ssm', 'L-FB5A4449'),
    },
    'Shield protection has no resource ARN': {
        ('shield', 'L-0BACF966'), ('shield', 'L-BBD47253'),
    },
    'Storage Gateway has an unknown gateway type': {
        ('storagegateway', 'L-14F83003'), ('storagegateway', 'L-2EC26EAB'),
        ('storagegateway', 'L-59D49F15'), ('storagegateway', 'L-99E991AF'),
        ('storagegateway', 'L-F5915598'), ('storagegateway', 'L-FF1BE522'),
    },
    'Storage Gateway volume has an unknown type': {
        ('storagegateway', 'L-2E88EE16'), ('storagegateway', 'L-5308FBCA'),
        ('storagegateway', 'L-6F75AC83'), ('storagegateway', 'L-81A6E497'),
    },
    'VM Import/Export import image task has an unknown status': {
        ('vmimportexport', 'L-66ABAAD5'),
    },
    'VPC Lattice domain verification has an inconsistent ARN': {
        ('vpc-lattice', 'L-73D0F278'),
    },
    'VPC Lattice resource configuration has an inconsistent ARN': {
        ('vpc-lattice', 'L-5FF8F9B9'), ('vpc-lattice', 'L-9BC96FEF'),
    },
    'VPC Lattice resource gateway has an inconsistent ARN': {
        ('vpc-lattice', 'L-0DCA4434'),
    },
    'VPC Lattice service has an inconsistent ARN': {
        ('vpc-lattice', 'L-3DEC3B9F'), ('vpc-lattice', 'L-620C821E'),
        ('vpc-lattice', 'L-CF78395E'), ('vpc-lattice', 'L-D64E952E'),
    },
    'VPC Lattice service network has an inconsistent ARN': {
        ('vpc-lattice', 'L-6095700C'), ('vpc-lattice', 'L-75D4A19E'),
        ('vpc-lattice', 'L-89DEA27F'), ('vpc-lattice', 'L-9CAD07FB'),
        ('vpc-lattice', 'L-CA6A1CC5'), ('vpc-lattice', 'L-EF6E2D62'),
    },
    'VPC Lattice target group has an inconsistent ARN': {
        ('vpc-lattice', 'L-BB11C6B9'), ('vpc-lattice', 'L-D71303F3'),
    },
}


def census():
    """Group every check that stops at NO_DATA by the reason it reports."""
    found = {}
    for module, service in MODULES:
        results, _sites = run(service, CHECKS[(module, service)])
        for result in results:
            if result['qualityStatus'] == 'NO_DATA':
                found.setdefault(result['qualityReason'], set()).add(
                    (result['serviceCode'], result['quotaCode']))
    for _module, entry, keys in ENTRY_POINTS:
        results, _sites = run_entry(entry, keys)
        for result in results:
            if result['qualityStatus'] == 'NO_DATA':
                found.setdefault(result['qualityReason'], set()).add(
                    (result['serviceCode'], result['quotaCode']))
    return found


def test_no_check_stops_early_without_being_recorded():
    """A check the harness cannot drive past its first call is a check whose
    later IAM grants nothing verifies. Each one is listed, with its reason."""
    found = census()
    appeared = {reason: sorted(codes - UNEXERCISED.get(reason, set()))
                for reason, codes in found.items()
                if codes - UNEXERCISED.get(reason, set())}
    resolved = {reason: sorted(codes - found.get(reason, set()))
                for reason, codes in UNEXERCISED.items()
                if codes - found.get(reason, set())}
    assert not appeared, f'checks that now stop at NO_DATA unrecorded: {appeared}'
    assert not resolved, f'checks that no longer stop early; drop them: {resolved}'
