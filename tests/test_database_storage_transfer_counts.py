from unittest.mock import Mock

from modules.qmchecks.transfer import vpc_endpoint_servers


def test_transfer_vpc_endpoint_server_count_filters_endpoint_type():
    ctx = Mock()
    ctx.call.return_value = [
        {'ServerId': 'sftp', 'EndpointType': 'VPC_ENDPOINT'},
        {'ServerId': 'public', 'EndpointType': 'PUBLIC'},
        {'ServerId': 'other', 'EndpointType': 'VPC_ENDPOINT'},
    ]
    result = vpc_endpoint_servers(ctx)
    assert result['usage'] == 2
    assert result['source'] == 'transfer:ListServers'
