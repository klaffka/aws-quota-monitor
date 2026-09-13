"""AWS IoT Core persistent account resource inventories."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def provisioning_template_versions(ctx):
    """Return the largest version inventory for any fleet template.

    The quota is scoped to one template, so an account-wide sum would be
    misleading.  ListProvisioningTemplateVersions is parent-scoped and the
    shared context handles pagination and failed inventories atomically.
    """
    values = []
    for template in ctx.call('iot', 'list_provisioning_templates', 'templates'):
        name = template.get('templateName') or template.get('name')
        if name:
            versions = ctx.call('iot', 'list_provisioning_template_versions', 'versions',
                                templateName=name)
            values.append((name, len(versions), None))
    return maximum(values, 'FleetProvisioningTemplate',
                   'iot:ListProvisioningTemplates+ListProvisioningTemplateVersions')


def policy_versions(ctx):
    """Return the largest named-policy version inventory.

    IoT limits named policy versions per policy.  Taking the maximum across
    policies preserves that parent scope and avoids inventing an account-wide
    quota by summing unrelated policies.
    """
    values = []
    for policy in ctx.call('iot', 'list_policies', 'policies'):
        name = policy.get('policyName') or policy.get('name')
        if name:
            versions = ctx.call('iot', 'list_policy_versions', 'policyVersions',
                                policyName=name)
            values.append((name, len(versions), None))
    return maximum(values, 'IoTNamedPolicy', 'iot:ListPolicies+ListPolicyVersions')


CHECKS = [
    ('L-345B62A1', 'Fleet provisioning templates',
     lambda c: dict(usage=len(c.call('iot', 'list_provisioning_templates', 'templates')),
                    source='iot:ListProvisioningTemplates', method='ACCOUNT_COUNT')),
    ('L-8AF17D80', 'Role aliases',
     lambda c: dict(usage=len(c.call('iot', 'list_role_aliases', 'roleAliases')),
                    source='iot:ListRoleAliases', method='ACCOUNT_COUNT')),
    ('L-78E3C43F', 'Authorizers per account',
     lambda c: dict(usage=len(c.call('iot', 'list_authorizers', 'authorizers')),
                    source='iot:ListAuthorizers', method='ACCOUNT_COUNT')),
    ('L-FC25158C', 'Active authorizers per account',
     lambda c: dict(usage=len([a for a in c.call('iot', 'list_authorizers', 'authorizers')
                               if a.get('status') == 'ACTIVE']),
                    source='iot:ListAuthorizers', method='ACCOUNT_COUNT')),
    ('L-954FA751', 'Topic rules per account',
     lambda c: dict(usage=len(c.call('iot', 'list_topic_rules', 'rules')),
                    source='iot:ListTopicRules', method='ACCOUNT_COUNT')),
    ('L-71FA7EC4', 'Fleet provisioning template versions per template',
     provisioning_template_versions),
    ('L-5F6C2444', 'Named policy versions per policy', policy_versions),
]


def get_current_quotastatus_iotcore(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'iotcore' for service, _ in context.quotas):
        return []
    return context.run('iotcore', CHECKS, skip)
