
import pytest

from modules.qmchecks.rbin import rule_count, tags_per_rule
from modules.qmcore.aws import NoData
from tests.iam_policy import grants


class RecycleBinContext:
    def __init__(self):
        self.rules = {
            'EBS_SNAPSHOT': [{'Identifier': 'RULE0000002'}],
            'EC2_IMAGE': [{'Identifier': 'RULE0000001'}],
            'EBS_VOLUME': [],
        }
        self.details = {
            'RULE0000001': {
                'Identifier': 'RULE0000001',
                'ResourceType': 'EC2_IMAGE',
                'ResourceTags': [
                    {'ResourceTagKey': 'environment', 'ResourceTagValue': 'prod'},
                ],
            },
            'RULE0000002': {
                'Identifier': 'RULE0000002',
                'ResourceType': 'EBS_SNAPSHOT',
                'ResourceTags': [
                    {'ResourceTagKey': 'environment', 'ResourceTagValue': 'dev'},
                    {'ResourceTagKey': 'owner'},
                    {'ResourceTagKey': 'cost-center', 'ResourceTagValue': ''},
                ],
                'ExcludeResourceTags': [
                    {'ResourceTagKey': 'temporary', 'ResourceTagValue': 'true'},
                ],
            },
        }

    def call(self, service, method, key=None, **kwargs):
        assert service == 'rbin'
        if method == 'list_rules':
            assert key == 'Rules'
            return self.rules[kwargs['ResourceType']]
        if method == 'get_rule':
            return self.details[kwargs['Identifier']]
        raise AssertionError(method)


def test_rbin_tags_uses_maximum_single_rule_and_excludes_exclusion_tags():
    ctx = RecycleBinContext()
    assert rule_count(ctx)['usage'] == 2
    result = tags_per_rule(ctx)
    assert (result['usage'], result['resource_id']) == (3, 'RULE0000002')
    assert result['meta'] is None


def test_rbin_tags_rejects_duplicate_pairs_and_inconsistent_details():
    ctx = RecycleBinContext()
    ctx.details['RULE0000001']['ResourceTags'].append(
        {'ResourceTagKey': 'environment', 'ResourceTagValue': 'prod'})
    with pytest.raises(NoData, match='duplicate resource-tag pairs'):
        tags_per_rule(ctx)

    ctx = RecycleBinContext()
    ctx.details['RULE0000001']['ResourceType'] = 'EBS_SNAPSHOT'
    with pytest.raises(NoData, match='detail is inconsistent'):
        tags_per_rule(ctx)


def test_rbin_configuration_check_has_read_permission():
    assert grants('rbin:GetRule')
