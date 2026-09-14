from unittest.mock import Mock

def test_s3_replication_rules_per_bucket():
    from modules.qmchecks.s3 import replication_rules_per_bucket
    ctx = Mock()
    ctx.call.side_effect = [[{'Name': 'a'}, {'Name': 'b'}],
                            {'ReplicationConfiguration': {'Rules': [{}, {}]}},
                            {'ReplicationConfiguration': {'Rules': [{}]}}]
    assert replication_rules_per_bucket(ctx)['usage'] == 2


def test_s3_lifecycle_rules_per_bucket():
    from modules.qmchecks.s3 import lifecycle_rules_per_bucket
    ctx = Mock()
    ctx.call.side_effect = [[{'Name': 'a'}, {'Name': 'b'}],
                            {'Rules': [{}, {}, {}]}, {'Rules': [{}]}]
    assert lifecycle_rules_per_bucket(ctx)['usage'] == 3


def test_s3_bucket_notifications_and_tags():
    from modules.qmchecks.s3 import bucket_event_notifications_per_bucket, bucket_tags_per_bucket
    ctx = Mock()
    ctx.call.side_effect = [[{'Name': 'a'}, {'Name': 'b'}],
                            {'TopicConfigurations': [{}], 'QueueConfigurations': [{}, {}]},
                            {'LambdaFunctionConfigurations': [{}]}]
    assert bucket_event_notifications_per_bucket(ctx)['usage'] == 3
    ctx = Mock()
    ctx.call.side_effect = [[{'Name': 'a'}, {'Name': 'b'}],
                            {'TagSet': [{}, {}]}, {'TagSet': [{}]}]
    assert bucket_tags_per_bucket(ctx)['usage'] == 2

def test_workspaces_ip_groups_per_directory():
    from modules.qmchecks.workspaces import CHECKS
    ctx = Mock()
    ctx.call.return_value = [{'DirectoryId': 'd1', 'IpGroupIds': ['a']}, {'DirectoryId': 'd2', 'IpGroupIds': ['a', 'b']}]
    check = next(c for c in CHECKS if c[0] == 'L-F61D0B79')
    assert check[2](ctx)['usage'] == 2


def test_workspaces_rules_per_ip_group():
    from modules.qmchecks.workspaces import CHECKS
    ctx = Mock()
    ctx.call.return_value = [
        {'GroupId': 'g1', 'UserRules': [{'権限': 1}]},
        {'GroupId': 'g2', 'UserRules': [{}, {}, {}]},
    ]
    check = next(c for c in CHECKS if c[0] == 'L-5782CB4D')
    assert check[2](ctx)['usage'] == 3


def test_sns_filter_policies_are_maximum_per_topic_and_account_total():
    from modules.qmchecks.sns import filter_policies_per_account, filter_policies_per_topic
    subscriptions = [
        {'SubscriptionArn': 'arn:1', 'TopicArn': 'topic-a'},
        {'SubscriptionArn': 'arn:2', 'TopicArn': 'topic-a'},
        {'SubscriptionArn': 'arn:3', 'TopicArn': 'topic-b'},
        {'SubscriptionArn': 'PendingConfirmation', 'TopicArn': 'topic-b'},
    ]
    ctx = Mock()
    ctx.call.side_effect = [subscriptions,
                            {'Attributes': {'FilterPolicy': '{}'}},
                            {'Attributes': {}},
                            {'Attributes': {'FilterPolicy': '{"x":["y"]}'}}]
    assert filter_policies_per_topic(ctx)['usage'] == 1

    ctx = Mock()
    ctx.call.side_effect = [subscriptions,
                            {'Attributes': {'FilterPolicy': '{}'}},
                            {'Attributes': {}},
                            {'Attributes': {'FilterPolicy': '{"x":["y"]}'}}]
    assert filter_policies_per_account(ctx)['usage'] == 2

    from modules.qmchecks.sns import subscriptions_per_topic
    ctx = Mock()
    ctx.call.side_effect = [
        [{'TopicArn': 't1'}, {'TopicArn': 't2'}],
        [{}, {}, {}], [{}],
    ]
    assert subscriptions_per_topic(ctx)['usage'] == 3


def test_wafv2_parent_scoped_counts():
    from modules.qmchecks.wafv2 import CHECKS
    ctx = Mock()
    ctx.call.side_effect = [
        [{'Id': 'i1', 'Name': 'one'}, {'Id': 'i2', 'Name': 'two'}],
        {'IPSet': {'Addresses': ['1', '2', '3']}}, {'IPSet': {'Addresses': ['4']}},
    ]
    check = next(c for c in CHECKS if c[0] == 'L-B24834C1')
    assert check[2](ctx)['usage'] == 3

    ctx = Mock()
    ctx.call.side_effect = [
        [{'Id': 'r1', 'Name': 'one'}],
        {'RegexPatternSet': {'RegularExpressionList': [{}, {}]}},
    ]
    check = next(c for c in CHECKS if c[0] == 'L-291AF103')
    assert check[2](ctx)['usage'] == 2

    ctx = Mock()
    ctx.call.side_effect = [
        [{'Id': 'a1', 'ARN': 'arn:one'}, {'Id': 'a2', 'ARN': 'arn:two'}],
        {'ResourceArns': ['alb-1', 'alb-2']}, {'ResourceArns': []},
    ]
    check = next(c for c in CHECKS if c[0] == 'L-C5E4D334')
    assert check[2](ctx)['usage'] == 2


def test_cloud_map_custom_attributes_per_instance():
    from modules.qmchecks.management_counts import cloud_map_custom_attributes_max
    ctx = Mock()
    ctx.call.side_effect = [
        [{'Id': 'n1'}], [{'Id': 's1'}], [{'Id': 'i1'}, {'Id': 'i2'}],
        {'Instance': {'Attributes': {'A': '1', 'B': '2'}}},
        {'Instance': {'Attributes': {'A': '1'}}},
    ]
    assert cloud_map_custom_attributes_max(ctx)['usage'] == 2


def test_iotcore_role_aliases():
    from modules.qmchecks.iotcore import CHECKS
    ctx = Mock()
    ctx.call.return_value = ['a', 'b', 'c']
    check = next(c for c in CHECKS if c[0] == 'L-8AF17D80')
    assert check[2](ctx)['usage'] == 3


def test_swf_parent_scoped_counts():
    from modules.qmchecks.swf import CHECKS
    from modules.qmchecks.swf import open_workflows_per_domain, workflow_types_per_domain
    ctx = Mock()
    ctx.call.side_effect = [
        [{'name': 'd1'}, {'name': 'd2'}],
        [{}, {}], [{}], [{}, {}, {}], [{}],
    ]
    assert workflow_types_per_domain(ctx)['usage'] == 4
    ctx = Mock()
    ctx.call.side_effect = [[{'name': 'd1'}, {'name': 'd2'}], {'count': 4}, {'count': 2}]
    assert open_workflows_per_domain(ctx)['usage'] == 4


def test_voice_id_parent_scoped_counts():
    from modules.qmchecks.rest_counts import voice_id_parent_max
    ctx = Mock()
    ctx.call.side_effect = [
        [{'DomainId': 'd1'}, {'DomainId': 'd2'}],
        [{}, {}], [{}],
    ]
    assert voice_id_parent_max(ctx, 'list_watchlists', 'WatchlistSummaries')['usage'] == 2


def test_legacy_waf_parent_scoped_counts():
    from modules.qmchecks.waf_regional import CHECKS
    ctx = Mock()
    ctx.call.side_effect = [
        [{'WebACLId': 'a1'}, {'WebACLId': 'a2'}],
        {'WebACL': {'Rules': [{}, {}]}}, {'WebACL': {'Rules': [{}]}},
    ]
    check = next(c for c in CHECKS if c[0] == 'L-9692AA5E')
    assert check[2](ctx)['usage'] == 2


def test_ssm_maintenance_window_children():
    from modules.qmchecks.ssm import CHECKS
    ctx = Mock()
    ctx.call.side_effect = [
        [{'WindowId': 'w1'}, {'WindowId': 'w2'}],
        [{}, {}], [{}],
    ]
    check = next(c for c in CHECKS if c[0] == 'L-3D9CCA6E')
    assert check[2](ctx)['usage'] == 2


def test_workspaces_connection_aliases():
    from modules.qmchecks.workspaces import CHECKS
    ctx = Mock()
    ctx.call.return_value = [{}, {}, {}]
    check = next(c for c in CHECKS if c[0] == 'L-0798A2C9')
    assert check[2](ctx)['usage'] == 3


def test_wisdom_content_per_knowledge_base():
    from modules.qmchecks.misc_counts import wisdom_content_per_knowledge_base
    ctx = Mock()
    ctx.call.side_effect = [[{'knowledgeBaseId': 'k1'}, {'knowledgeBaseId': 'k2'}],
                            [{}, {}], [{}]]
    assert wisdom_content_per_knowledge_base(ctx)['usage'] == 2


def test_wafv2_service_associations_per_web_acl():
    from modules.qmchecks.wafv2 import associations_per_web_acl
    ctx = Mock()
    ctx.call.side_effect = [[{'ARN': 'a1'}, {'ARN': 'a2'}],
                            {'ResourceArns': ['r1', 'r2']}, {'ResourceArns': []}]
    assert associations_per_web_acl(ctx, 'API_GATEWAY')['usage'] == 2

    ctx = Mock()
    ctx.call.side_effect = [[{'ARN': 'a1'}], {'ResourceArns': ['r1']}]
    assert associations_per_web_acl(ctx, 'COGNITO_USER_POOL')['usage'] == 1
