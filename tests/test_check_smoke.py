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
    failures = [f"{result['quotaCode']}: {result['qualityReason'].splitlines()[0]}"
                for result in run_entry(entry, keys, populated=populated)
                if result['qualityStatus'] == 'ERROR'
                and (result['serviceCode'], result['quotaCode']) not in ALLOWED]
    assert not failures, module


@pytest.mark.parametrize('module, entry, keys', ENTRY_POINTS, ids=lambda value: str(value))
def test_every_entry_point_declares_the_quotas_it_measures(module, entry, keys):
    """CUSTOM_KEYS is what coverage counts; a quota missing from it is measured
    every ten minutes and reported to nobody."""
    from importlib import import_module

    declared = set(import_module(module).CUSTOM_KEYS)
    measured = {(result['serviceCode'], result['quotaCode'])
                for result in run_entry(entry, sorted(declared))}
    assert measured == declared, {'undeclared': sorted(measured - declared),
                                  'unmeasured': sorted(declared - measured)}
