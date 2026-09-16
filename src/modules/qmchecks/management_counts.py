"""Small management-service resource-count checks with direct list APIs."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env

CUSTOM_KEYS = {('servicediscovery', 'L-0FE3F50E'), ('acm-pca', 'L-799883CD'),
               ('servicediscovery', 'L-2DA90E5C'), ('servicediscovery', 'L-D95E8A57'),
               ('athena', 'L-FD9D80C2'), ('servicediscovery', 'L-D589BB26')}


def count(service, method, key):
    return lambda c: dict(usage=len(c.call(service, method, key)),
                          source=f'{service}:{method}', method='ACCOUNT_COUNT')


def namespace_filter(namespace_id):
    """ListServices has no namespace parameter; it takes a filter instead."""
    return {'Name': 'NAMESPACE_ID', 'Values': [namespace_id], 'Condition': 'EQ'}


def cloud_map_parent_max(ctx, method, key, **kwargs):
    values = []
    for namespace in ctx.call('servicediscovery', 'list_namespaces', 'Namespaces'):
        namespace_id = namespace.get('Id')
        if not namespace_id:
            continue
        for service in ctx.call('servicediscovery', 'list_services', 'Services',
                                Filters=[namespace_filter(namespace_id)]):
            service_id = service.get('Id')
            if service_id and method == 'list_instances':
                items = ctx.call('servicediscovery', method, key, ServiceId=service_id)
                values.append((service_id, len(items), None))
    return maximum(values, 'CloudMapService', f'servicediscovery:{method}')


def cloud_map_namespace_max(ctx):
    values = []
    for namespace in ctx.call('servicediscovery', 'list_namespaces', 'Namespaces'):
        namespace_id = namespace.get('Id')
        if not namespace_id:
            continue
        total = 0
        for service in ctx.call('servicediscovery', 'list_services', 'Services',
                                Filters=[namespace_filter(namespace_id)]):
            service_id = service.get('Id')
            if service_id:
                total += len(ctx.call('servicediscovery', 'list_instances', 'Instances',
                                      ServiceId=service_id))
        values.append((namespace_id, total, None))
    return maximum(values, 'CloudMapNamespace', 'servicediscovery:ListInstances')


def cloud_map_custom_attributes_max(ctx):
    values = []
    for namespace in ctx.call('servicediscovery', 'list_namespaces', 'Namespaces'):
        namespace_id = namespace.get('Id')
        if not namespace_id:
            continue
        for service in ctx.call('servicediscovery', 'list_services', 'Services',
                                Filters=[namespace_filter(namespace_id)]):
            service_id = service.get('Id')
            if not service_id:
                continue
            for instance in ctx.call('servicediscovery', 'list_instances', 'Instances', ServiceId=service_id):
                instance_id = instance.get('Id')
                if instance_id:
                    details = ctx.call('servicediscovery', 'get_instance',
                                       ServiceId=service_id, InstanceId=instance_id)
                    values.append((instance_id, len(details.get('Instance', {}).get('Attributes', {})), None))
    return maximum(values, 'CloudMapInstance', 'servicediscovery:GetInstance')


def get_current_quotastatus_management_counts(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    entries = []
    if any(service == 'servicediscovery' for service, _ in context.quotas):
        entries.extend(context.run('servicediscovery', [
            ('L-0FE3F50E', 'Namespaces per Region', count('servicediscovery', 'list_namespaces', 'Namespaces')),
            ('L-2DA90E5C', 'Instances per service',
             lambda c: cloud_map_parent_max(c, 'list_instances', 'Instances')),
            ('L-D95E8A57', 'Instances per namespace',
             cloud_map_namespace_max),
            ('L-D589BB26', 'Custom attributes per instance', cloud_map_custom_attributes_max),
        ], skip))
    if any(service == 'acm-pca' for service, _ in context.quotas):
        entries.extend(context.run('acm-pca', [
            ('L-799883CD', 'Number of private certificate authorities', count('acm-pca', 'list_certificate_authorities', 'CertificateAuthorities')),
        ], skip))
    if any(service == 'athena' for service, _ in context.quotas):
        entries.extend(context.run('athena', [
            ('L-FD9D80C2', 'Maximum number of workgroups per account', count('athena', 'list_work_groups', 'WorkGroups')),
        ], skip))
    return entries
