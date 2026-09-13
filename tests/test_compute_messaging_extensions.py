from unittest.mock import Mock
from modules.qmchecks.eks import CHECKS as EKS
from modules.qmchecks.sns import CHECKS as SNS


def test_eks_nodegroups_and_sns_pending_subscriptions():
    context = Mock(); context.call.side_effect = [["cluster"], [{}]]
    assert EKS[1][2](context)['usage'] == 1
    context = Mock(); context.call.return_value = [{'SubscriptionArn': 'PendingConfirmation'}]
    assert SNS[1][2](context)['usage'] == 1
