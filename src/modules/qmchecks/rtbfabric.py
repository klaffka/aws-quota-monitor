"""AWS RTB Fabric gateway, link and routing quotas.

The external inbound and outbound link quotas need the link's connectivity and
direction to be mapped onto AWS's external wording, which the API does not state
in those terms. Availability zones per gateway would have to be derived from the
gateway's subnets through EC2, and the two `supported` quotas describe a service
capability rather than an inventory. None of these is measured here.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

RTB = 'rtbfabric'


def gateways(ctx):
    """Return every requester and responder gateway ID in the Region."""
    found = []
    for method in ('list_requester_gateways', 'list_responder_gateways'):
        for identity in ctx.call(RTB, method, 'gatewayIds'):
            if not isinstance(identity, str) or not identity:
                raise NoData('RTB Fabric gateway is missing its identity')
            if identity not in found:
                found.append(identity)
    return found


def links(gateway, ctx):
    found = {}
    for link in ctx.call(RTB, 'list_links', 'links', gatewayId=gateway):
        identity = link.get('linkId')
        if not isinstance(identity, str) or not identity:
            raise NoData('RTB Fabric link is missing its identity')
        found[identity] = link
    return found


def links_per_gateway(ctx):
    values = [(gateway, len(links(gateway, ctx)), None) for gateway in gateways(ctx)]
    return maximum(values, 'RTBFabricGateway', 'rtbfabric:ListLinks')


def certificate_associations_per_gateway(ctx):
    values = []
    for gateway in gateways(ctx):
        associations = ctx.call(RTB, 'list_certificate_associations',
                                'certificateAssociations', gatewayId=gateway)
        for association in associations:
            if not isinstance(association.get('acmCertificateArn'), str):
                raise NoData('RTB Fabric certificate association has no certificate')
        values.append((gateway, len(associations), None))
    return maximum(values, 'RTBFabricGateway', 'rtbfabric:ListCertificateAssociations')


def routing_rules_per_link(ctx):
    values = []
    for gateway in gateways(ctx):
        for identity in links(gateway, ctx):
            rules = ctx.call(RTB, 'list_link_routing_rules', 'rules',
                             gatewayId=gateway, linkId=identity)
            for rule in rules:
                if not isinstance(rule.get('ruleId'), str):
                    raise NoData('RTB Fabric routing rule is missing its identity')
            values.append((identity, len(rules), None))
    return maximum(values, 'RTBFabricLink', 'rtbfabric:ListLinkRoutingRules')


def modules_per_flow(ctx):
    """Link summaries already carry the flow modules configured on them."""
    values = []
    for gateway in gateways(ctx):
        for identity, link in links(gateway, ctx).items():
            modules = link.get('flowModules') or []
            if not isinstance(modules, list):
                raise NoData('RTB Fabric link has an invalid flow module list')
            values.append((identity, len(modules), None))
    return maximum(values, 'RTBFabricLink', 'rtbfabric:ListLinks')


CHECKS = [
    ('L-A6B8AC62', 'Number of gateways',
     lambda ctx: dict(usage=len(gateways(ctx)),
                      source='rtbfabric:ListRequesterGateways+ListResponderGateways',
                      method='ACCOUNT_COUNT')),
    ('L-76B04EF7', 'Links per gateway', links_per_gateway),
    ('L-7A1DE2E7', 'Certificate associations per gateway',
     certificate_associations_per_gateway),
    ('L-E0D1ECDF', 'Routing rules per link', routing_rules_per_link),
    ('L-010B9A72', 'Modules per flow', modules_per_flow),
]


def get_current_quotastatus_rtbfabric(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'rtbfabric' for service, _ in context.quotas):
        return []
    return context.run('rtbfabric', CHECKS, skip)
