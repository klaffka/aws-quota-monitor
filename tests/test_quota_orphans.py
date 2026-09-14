from pathlib import Path

from scripts.quota_coverage import merge_catalogs
from scripts.quota_orphans import (UNKNOWN_QUOTA, UNKNOWN_SERVICE, orphans,
                                   render_table)

# The exports under data/ are untracked, so the committed union is the source.
CATALOGS = ('tests/fixtures/quota-catalog-union.json',)


def test_missing_code_and_missing_service_are_reported_separately():
    quotas = [{'serviceCode': 'example', 'quotaCode': 'known'}]
    rows = orphans(quotas, {('example', 'known'), ('example', 'typo'),
                            ('elsewhere', 'any')})
    assert rows == [{'serviceCode': 'elsewhere', 'quotaCode': 'any',
                     'reason': UNKNOWN_SERVICE},
                    {'serviceCode': 'example', 'quotaCode': 'typo',
                     'reason': UNKNOWN_QUOTA}]
    assert 'UNKNOWN_QUOTA: 1 quota codes across 1 services' in render_table(rows)


def test_service_aliases_are_resolved_before_comparing():
    quotas = [{'serviceCode': 'AWSCloudMap', 'quotaCode': 'shared'}]
    assert orphans(quotas, {('servicediscovery', 'shared')}) == []


def test_a_second_export_removes_orphans_that_the_first_one_lacks():
    first = [{'serviceCode': 'example', 'quotaCode': 'one'}]
    second = [{'ServiceCode': 'example', 'QuotaCode': 'two'}]
    implemented = {('example', 'one'), ('example', 'two')}
    assert len(orphans(first, implemented)) == 1
    assert orphans(first + second, implemented) == []


def test_every_implemented_quota_code_exists_in_a_known_catalog():
    """Guard against quota codes that no catalog contains, such as typos."""
    for path in CATALOGS:
        assert Path(path).is_file(), path
    found = orphans(merge_catalogs(list(CATALOGS)))
    assert found == [], f'implemented codes without a catalog entry: {found[:10]}'
