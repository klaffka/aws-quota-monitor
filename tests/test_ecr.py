from unittest.mock import Mock

from modules.qmchecks.ecr import repositories, images_per_repository


def test_ecr_repository_inventory_is_account_scoped():
    ctx = Mock(account='123456789012')
    ctx.call.return_value = [{'repositoryName': 'one'}, {'repositoryName': 'two'}]
    assert len(repositories(ctx)) == 2
    assert ctx.call.call_args.args[:3] == ('ecr', 'describe_repositories', 'repositories')
    assert ctx.call.call_args.kwargs == {'registryId': '123456789012'}


def test_ecr_images_use_maximum_per_repository():
    ctx = Mock(account='123456789012')
    ctx.call.side_effect = [
        [{'repositoryName': 'one'}, {'repositoryName': 'two'}],
        [{'imageDigest': 'a'}, {'imageDigest': 'b'}],
        [{'imageDigest': 'c'}],
    ]
    result = images_per_repository(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'one')
