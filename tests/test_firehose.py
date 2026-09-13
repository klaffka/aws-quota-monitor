from unittest.mock import Mock

from modules.qmchecks.firehose import delivery_streams


def test_firehose_delivery_stream_inventory_is_counted():
    ctx = Mock()
    ctx.call.return_value = ['stream-one', 'stream-two']
    assert len(delivery_streams(ctx)) == 2
    assert ctx.call.call_args.args[:3] == ('firehose', 'list_delivery_streams', 'DeliveryStreamNames')
