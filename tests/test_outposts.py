from pathlib import Path
from unittest.mock import Mock

import pytest

from modules.qmchecks.outposts import CHECKS, outposts_per_site, site_count, sites
from modules.qmcore.aws import NoData
from modules.qmcore.registry import custom_keys


ACCOUNT = '111111111111'
REGION = 'eu-central-1'


def site(identity, **values):
    return {'SiteId': identity, 'AccountId': ACCOUNT,
            'SiteArn': f'arn:aws:outposts:{REGION}:{ACCOUNT}:site/{identity}', **values}


def outpost(identity, site_id, **values):
    return {'OutpostId': identity, 'OwnerId': ACCOUNT, 'SiteId': site_id,
            'OutpostArn': f'arn:aws:outposts:{REGION}:{ACCOUNT}:outpost/{identity}',
            'SiteArn': f'arn:aws:outposts:{REGION}:{ACCOUNT}:site/{site_id}',
            'LifeCycleStatus': 'ACTIVE', **values}


def context(site_items, outpost_items):
    ctx = Mock(account=ACCOUNT, region=REGION)
    ctx.call.side_effect = lambda service, method, key: (
        site_items if method == 'list_sites' else outpost_items)
    return ctx


def test_outposts_counts_sites_and_maximum_outposts_per_site():
    ctx = context(
        [site('os-one'), site('os-two'), site('os-three')],
        [outpost('op-one', 'os-one'), outpost('op-two', 'os-one'),
         outpost('op-three', 'os-two')])
    assert site_count(ctx)['usage'] == 3
    result = outposts_per_site(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'os-one')


def test_outposts_deduplicates_identical_repeated_pages():
    site_item = site('os-one')
    outpost_item = outpost('op-one', 'os-one')
    ctx = context([site_item, dict(site_item)], [outpost_item, dict(outpost_item)])
    assert len(sites(ctx)) == 1
    assert outposts_per_site(ctx)['usage'] == 1


def test_outposts_rejects_conflicting_resource_identity():
    ctx = context([site('os-one'), site('os-one', Name='changed')], [])
    with pytest.raises(NoData, match='changed during pagination'):
        sites(ctx)

    ctx = context([site('os-one')],
                  [outpost('op-one', 'os-one'),
                   outpost('op-one', 'os-one', Name='changed')])
    with pytest.raises(NoData, match='changed during pagination'):
        outposts_per_site(ctx)


@pytest.mark.parametrize('site_items,outpost_items,match', [
    ([site('os-one', AccountId='222222222222')], [], 'account identity'),
    ([site('os-one')], [outpost('op-one', 'os-missing')], 'owner or parent'),
    ([site('os-one')], [outpost('op-one', 'os-one', OwnerId='222222222222')],
     'owner or parent'),
    ([site('os-one')], [outpost('op-one', 'os-one', LifeCycleStatus='')],
     'owner or parent'),
])
def test_outposts_rejects_incomplete_owner_and_parent_data(
        site_items, outpost_items, match):
    with pytest.raises(NoData, match=match):
        outposts_per_site(context(site_items, outpost_items))


def test_outposts_checks_are_registered_with_read_permissions():
    assert {('outposts', code) for code, _, _ in CHECKS} <= custom_keys()
    policy = (Path(__file__).parents[1] / 'deployment/main.tf').read_text(encoding='utf-8')
    for action in ('ListSites', 'ListOutposts'):
        assert f'"outposts:{action}"' in policy
