"""A check must measure the scope its quota is defined at.

model.py writes the check's own quotaName into every measurement, never the
catalog's, so a check that groups by the wrong scope reports a plausible
number against a limit that means something else. Nothing downstream can tell.
"""
import json
import re
from pathlib import Path

import boto3
from botocore.stub import Stubber

from modules.qmchecks.vpc import vpc
from modules.qmcore.aws import CheckContext
from tests.shape_harness import entries

CATALOG = Path('tests/fixtures/quota-catalog-union.json')
# "per <scope>", up to the next clause. A quota states the scope it counts at.
SCOPE = re.compile(r'\bper\s+([a-z0-9][a-z0-9 \-]*?)(?=$|,|\s+(?:per|and|in|with|for)\b)',
                   re.IGNORECASE)
# Wording the catalog and the checks spell differently while meaning the same
# scope. Each entry states why the difference is cosmetic.
SAME_SCOPE = {
    ('airflow', 'L-67D41C6B'): 'catalog appends the environment sizes after the scope',
    ('bedrock', 'L-FAF1E3E4'): 'the catalog dataset is an automatic evaluation dataset',
    ('bedrock', 'L-FD0CC292'): 'the catalog job is an automatic evaluation job',
    ('cloudformation', 'L-7E146E2E'): 'a module version belongs to a module type',
    ('cloudformation', 'L-EA1018E8'): 'the catalog resource is a private resource type',
    ('connect', 'L-516BC0EB'): 'every routing profile belongs to one instance',
    ('connect', 'L-E10B281B'): 'overrides are counted per hours-of-operation, which the instance owns',
    ('iotsitewise', 'L-179151C6'): 'AWS account and account name the same scope',
    ('iotsitewise', 'L-37C04251'): 'AWS account and account name the same scope',
    ('iotsitewise', 'L-A5652910'): 'AWS account and account name the same scope',
    ('iotsitewise', 'L-CB5C18A8'): 'AWS account and account name the same scope',
    ('rekognition', 'L-01C8D885'): 'the catalog adds a liveness clause to the account scope',
    ('rekognition', 'L-0B2CE4DD'): 'the catalog names the Custom Labels project in full',
    ('route53profiles', 'L-D9B2356C'): 'the catalog sentence ends in a full stop',
    ('vpc', 'L-5F53652F'): 'only a public NAT gateway carries elastic IP addresses',
    ('wafv2', 'L-291AF103'): 'the catalog states where the set lives, not what it counts',
}


def scopes(name):
    return {re.sub(r'\s+', ' ', match.group(1)).strip().lower().rstrip('s')
            for match in SCOPE.finditer(name or '')}


def catalog_names():
    rows = json.loads(CATALOG.read_text(encoding='utf-8'))
    rows = rows['Quotas'] if isinstance(rows, dict) else rows
    names = {}
    for quota in rows:
        names.setdefault((quota['ServiceCode'], quota['QuotaCode']), quota.get('QuotaName') or '')
    return names


def test_no_check_counts_at_a_different_scope_than_its_quota():
    """Per-resource maximum against a regional limit understates usage silently."""
    names = catalog_names()
    disagreeing = []
    for _module, service, checks in entries():
        for code, name, _fn in checks:
            catalog = names.get((service, code))
            if catalog is None or (service, code) in SAME_SCOPE:
                continue
            declared, documented = scopes(name), scopes(catalog)
            if declared and documented and declared != documented:
                disagreeing.append(f'{service}/{code}: {sorted(declared)} vs {sorted(documented)}')
    assert not disagreeing, disagreeing


def test_the_same_scope_list_only_covers_names_that_still_differ():
    """An entry whose wording now matches is an entry that must go."""
    names = catalog_names()
    stale = set(SAME_SCOPE)
    for _module, service, checks in entries():
        for code, name, _fn in checks:
            catalog = names.get((service, code))
            if catalog is None:
                continue
            declared, documented = scopes(name), scopes(catalog)
            if declared and documented and declared != documented:
                stale.discard((service, code))
    assert not stale, f'entries whose wording now agrees: {sorted(stale)}'


def test_network_interfaces_are_counted_across_the_whole_region():
    """The quota is regional and account-scoped, so the AZ maximum undercounts it."""
    ctx = CheckContext(boto3.Session(region_name='eu-central-1'),
                       [{'ServiceCode': 'vpc', 'QuotaCode': 'L-DF5E4CA3', 'Value': 5000}],
                       account='123456789012')
    check = next(fn for code, _name, fn in vpc.CHECKS if code == 'L-DF5E4CA3')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_network_interfaces', {'NetworkInterfaces': [
            {'NetworkInterfaceId': 'eni-1', 'AvailabilityZone': 'eu-central-1a'},
            {'NetworkInterfaceId': 'eni-2', 'AvailabilityZone': 'eu-central-1a'},
            {'NetworkInterfaceId': 'eni-3', 'AvailabilityZone': 'eu-central-1b'}]},
            {'Filters': [{'Name': 'owner-id', 'Values': ['123456789012']}]})
        result = check(ctx)
        assert result['usage'] == 3
        stub.assert_no_pending_responses()
