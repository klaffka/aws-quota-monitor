from unittest.mock import Mock

from modules.qmchecks.ec2.ec2 import elastic_ip_count
from modules.qmchecks.ssm import (ALL_CHECKS, associations, document_versions, documents,
                                  maintenance_windows, patch_baselines)


def test_ec2_elastic_ip_count_only_counts_vpc_addresses():
    ctx = Mock()
    ctx.call.return_value = [
        {'AllocationId': 'eip-1', 'Domain': 'vpc'},
        {'AllocationId': 'eip-2', 'Domain': 'standard'},
        {'AllocationId': 'eip-3'},
    ]
    assert elastic_ip_count(ctx)['usage'] == 1
    assert ctx.call.call_args.args[:3] == ('ec2', 'describe_addresses', 'Addresses')


def test_ssm_resource_counts_use_paginated_inventory_apis():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'Name': 'doc'}], [{'WindowId': 'mw-1'}],
        [{'BaselineId': 'pb-1'}, {'BaselineId': 'pb-2'}], [{'AssociationId': 'a-1'}],
    ]
    assert len(documents(ctx)) == 1
    assert len(maintenance_windows(ctx)) == 1
    assert len(patch_baselines(ctx)) == 2
    assert len(associations(ctx)) == 1
    assert {code for code, _name, _fn in ALL_CHECKS} >= {
        'L-60D2045D', 'L-7727CE5B', 'L-218CDBD4', 'L-01B74EDA'}


def test_ssm_document_versions_use_maximum_per_document():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'Name': 'one'}, {'Name': 'two'}],
        [{'DocumentVersion': '1'}, {'DocumentVersion': '2'}],
        [{'DocumentVersion': '1'}],
    ]
    assert document_versions(ctx)['usage'] == 2
