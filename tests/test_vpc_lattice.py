import pytest

from modules.qmchecks import new_services as lattice
from modules.qmcore.aws import NoData
from modules.qmcore.registry import custom_keys


ACCOUNT = '123456789012'
OTHER_ACCOUNT = '210987654321'
REGION = 'eu-central-1'


def resource(kind, identifier, *, account=ACCOUNT, **fields):
    return {'id': identifier,
            'arn': f'arn:aws:vpc-lattice:{REGION}:{account}:{kind}/{identifier}',
            **fields}


def listener(service_id, identifier):
    return resource(f'service/{service_id}/listener', identifier)


def rule(service_id, listener_id, identifier):
    return resource(f'service/{service_id}/listener/{listener_id}/rule',
                    identifier)


def association(kind, identifier, network, status='ACTIVE', **fields):
    return resource(kind, identifier, status=status,
                    serviceNetworkId=network['id'],
                    serviceNetworkArn=network['arn'], **fields)


class Context:
    account = ACCOUNT
    region = REGION

    def __init__(self, responses):
        self.responses = responses

    def call(self, service, method, key=None, **kwargs):
        assert service == 'vpc-lattice'
        return self.responses.get((method, tuple(sorted(kwargs.items()))),
                                  [] if key else {})


def populated_context():
    n1 = resource('servicenetwork', 'sn-one')
    n2 = resource('servicenetwork', 'sn-two')
    s1 = resource('service', 'svc-one', status='ACTIVE')
    s2 = resource('service', 'svc-two', status='ACTIVE')
    t1 = resource('targetgroup', 'tg-one', status='ACTIVE',
                  serviceArns=[s1['arn']])
    t2 = resource('targetgroup', 'tg-two', status='DELETE_FAILED',
                  serviceArns=[s1['arn']])
    t3 = resource('targetgroup', 'tg-three', status='ACTIVE',
                  serviceArns=[s2['arn']])
    l1, l2, l3 = (listener(sid, lid) for sid, lid in (
        (s1['id'], 'listener-one'), (s1['id'], 'listener-two'),
        (s2['id'], 'listener-three')))
    group = resource('resourceconfiguration', 'rcfg-group', status='ACTIVE',
                     type='GROUP')
    child1 = resource('resourceconfiguration', 'rcfg-child-one', status='ACTIVE',
                      type='CHILD', resourceConfigurationGroupId=group['id'])
    child2 = resource('resourceconfiguration', 'rcfg-child-two',
                      status='UPDATE_FAILED', type='CHILD',
                      resourceConfigurationGroupId=group['id'])
    single = resource('resourceconfiguration', 'rcfg-single', status='ACTIVE',
                      type='SINGLE')
    gateways = [
        resource('resourcegateway', 'rgw-one', status='ACTIVE',
                 vpcIdentifier='vpc-one', securityGroupIds=['sg-one']),
        resource('resourcegateway', 'rgw-two', status='DELETE_FAILED',
                 vpcIdentifier='vpc-one', securityGroupIds=[]),
        resource('resourcegateway', 'rgw-three', status='ACTIVE',
                 vpcIdentifier='vpc-two', securityGroupIds=[]),
    ]
    va1 = association('servicenetworkvpcassociation', 'snva-one', n1,
                      vpcId='vpc-one')
    va2 = association('servicenetworkvpcassociation', 'snva-two', n1,
                      vpcId='vpc-two')
    va3 = association('servicenetworkvpcassociation', 'snva-three', n2,
                      vpcId='vpc-three')
    responses = {
        ('list_service_networks', ()): [n1, n2,
            resource('servicenetwork', 'sn-shared', account=OTHER_ACCOUNT)],
        ('list_services', ()): [s1, s2,
            resource('service', 'svc-failed', status='CREATE_FAILED')],
        ('list_target_groups', ()): [t1, t2, t3,
            resource('targetgroup', 'tg-failed', status='CREATE_FAILED')],
        ('list_listeners', (('serviceIdentifier', s1['id']),)): [l1, l2],
        ('list_listeners', (('serviceIdentifier', s2['id']),)): [l3],
        ('list_rules', (('listenerIdentifier', l1['id']),
                        ('serviceIdentifier', s1['id']))): [
            rule(s1['id'], l1['id'], 'rule-one'),
            rule(s1['id'], l1['id'], 'rule-two')],
        ('list_rules', (('listenerIdentifier', l2['id']),
                        ('serviceIdentifier', s1['id']))): [
            rule(s1['id'], l2['id'], 'rule-three')],
        ('list_rules', (('listenerIdentifier', l3['id']),
                        ('serviceIdentifier', s2['id']))): [],
        ('list_targets', (('targetGroupIdentifier', t1['id']),)): [
            {'id': 'i-one', 'port': 80, 'status': 'HEALTHY'},
            {'id': 'i-two', 'port': 80, 'status': 'DRAINING'}],
        ('list_targets', (('targetGroupIdentifier', t2['id']),)): [
            {'id': '10.0.0.1', 'port': 443, 'status': 'UNHEALTHY'}],
        ('list_targets', (('targetGroupIdentifier', t3['id']),)): [],
        ('list_resource_configurations', ()): [group, child1, child2, single,
            resource('resourceconfiguration', 'rcfg-shared',
                     account=OTHER_ACCOUNT, status='ACTIVE', type='SINGLE')],
        ('list_resource_configurations',
         (('resourceConfigurationGroupIdentifier', group['id']),)): [
             child1, child2],
        ('list_resource_gateways', ()): gateways,
        ('list_domain_verifications', ()): [
            resource('domainverification', 'dv-one', status='VERIFIED'),
            resource('domainverification', 'dv-two', status='PENDING'),
            resource('domainverification', 'dv-shared', account=OTHER_ACCOUNT,
                     status='VERIFIED')],
    }
    for network, service_count, vpc_items, endpoint_count, resource_count in (
            (n1, 2, [va1, va2], 2, 2), (n2, 1, [va3], 1, 1)):
        nid = network['id']
        responses[('list_service_network_service_associations',
                   (('serviceNetworkIdentifier', nid),))] = [
            association('servicenetworkserviceassociation',
                        f'snsa-{nid}-{i}', network)
            for i in range(service_count)]
        responses[('list_service_network_vpc_associations',
                   (('serviceNetworkIdentifier', nid),))] = vpc_items
        responses[('list_service_network_vpc_endpoint_associations',
                   (('serviceNetworkIdentifier', nid),))] = [
            {'id': f'snvpce-{nid}-{i}', 'vpcEndpointId': f'vpce-{nid}-{i}',
             'vpcId': f'vpc-{i}', 'vpcEndpointOwnerId': ACCOUNT,
             'state': 'Available', 'serviceNetworkArn': network['arn']}
            for i in range(endpoint_count)]
        responses[('list_service_network_resource_associations',
                   (('includeChildren', True),
                    ('serviceNetworkIdentifier', nid)))] = [
            association('servicenetworkresourceassociation',
                        f'snra-{nid}-{i}', network,
                        resourceConfigurationId=f'rcfg-{nid}-{i}')
            for i in range(resource_count)]
    for association_item, group_count in ((va1, 1), (va2, 2), (va3, 0)):
        association_id = association_item['id']
        responses[('get_service_network_vpc_association',
                   (('serviceNetworkVpcAssociationIdentifier', association_id),))] = {
            **association_item,
            'securityGroupIds': [f'sg-{i}' for i in range(group_count)]}
    return Context(responses)


def test_vpc_lattice_all_resource_quota_counts():
    results = [check(populated_context())
               for _code, _name, check in lattice.VPC_LATTICE_CHECKS]
    assert [result['usage'] for result in results] == [
        2, 2, 3, 2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    assert all(result['method'] in {'ACCOUNT_COUNT', 'PER_RESOURCE_MAX'}
               for result in results)


def test_vpc_lattice_checks_are_registered():
    expected = {('vpc-lattice', code)
                for code, _name, _check in lattice.VPC_LATTICE_CHECKS}
    assert expected <= custom_keys()


def test_vpc_lattice_rejects_unknown_resource_state():
    bad = resource('service', 'svc-one', status='UNKNOWN')
    with pytest.raises(NoData, match='unknown state'):
        lattice.services(Context({('list_services', ()): [bad]}))


def test_vpc_lattice_rejects_changed_duplicate():
    one = resource('servicenetwork', 'sn-one')
    changed = {**one, 'name': 'changed'}
    with pytest.raises(NoData, match='changed during pagination'):
        lattice.service_networks(Context({
            ('list_service_networks', ()): [one, changed]}))


def test_vpc_lattice_rejects_inconsistent_association_parent():
    ctx = populated_context()
    network = lattice.service_networks(ctx)['sn-one']
    key = ('list_service_network_service_associations',
           (('serviceNetworkIdentifier', network['id']),))
    ctx.responses[key][0]['serviceNetworkId'] = 'sn-other'
    with pytest.raises(NoData, match='inconsistent parent'):
        lattice.lattice_service_associations_per_network(ctx)
