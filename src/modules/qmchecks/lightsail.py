"""Amazon Lightsail instance, storage, distribution and container quotas.

`Minimum block storage disk space` states a floor rather than a ceiling, keys
per bucket would need an object listing, and the browser-based RDP and SSH
connection quotas count live sessions that no API reports.
"""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

LIGHTSAIL = 'lightsail'
CERTIFICATE_STATES = {'PENDING_VALIDATION', 'ISSUED', 'INACTIVE', 'EXPIRED',
                      'VALIDATION_TIMED_OUT', 'REVOKED', 'FAILED'}
ACTIVE_CERTIFICATE_STATES = {'ISSUED'}


def count(ctx, method, key):
    return dict(usage=len(ctx.call(LIGHTSAIL, method, key)),
                source=f'lightsail:{method}', method='ACCOUNT_COUNT')


def _named(items, field, subject):
    for item in items:
        name = item.get(field)
        if not isinstance(name, str) or not name:
            raise NoData(f'Lightsail {subject} is missing its name')
        yield name, item


def distributions(ctx):
    return dict(_named(ctx.call(LIGHTSAIL, 'get_distributions', 'distributions'),
                       'name', 'distribution'))


def container_services(ctx):
    return dict(_named(ctx.call(LIGHTSAIL, 'get_container_services',
                                'containerServices'),
                       'containerServiceName', 'container service'))


def disks(ctx):
    return dict(_named(ctx.call(LIGHTSAIL, 'get_disks', 'disks'), 'name', 'disk'))


def _disk_size(disk):
    size = disk.get('sizeInGb')
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise NoData('Lightsail disk has no size')
    return size


def disks_per_instance(ctx):
    counts = Counter()
    for _, disk in disks(ctx).items():
        attached = disk.get('attachedTo')
        if attached is None:
            continue
        if not isinstance(attached, str) or not attached:
            raise NoData('Lightsail disk has an invalid attachment')
        counts[attached] += 1
    return maximum(((instance, value, None) for instance, value in counts.items()),
                   'LightsailInstance', 'lightsail:GetDisks')


def largest_disk(ctx):
    values = [(name, _disk_size(disk), None) for name, disk in disks(ctx).items()]
    return maximum(values, 'LightsailDisk', 'lightsail:GetDisks')


def attached_disk_space(ctx):
    usage = sum(_disk_size(disk) for disk in disks(ctx).values()
                if disk.get('attachedTo'))
    return dict(usage=usage, source='lightsail:GetDisks', method='ACCOUNT_COUNT')


def active_certificates(ctx):
    usage = 0
    for summary in ctx.call(LIGHTSAIL, 'get_certificates', 'certificates'):
        detail = summary.get('certificateDetail') or {}
        status = detail.get('status')
        if status not in CERTIFICATE_STATES:
            raise NoData('Lightsail certificate has an unknown status')
        usage += status in ACTIVE_CERTIFICATE_STATES
    return dict(usage=usage, source='lightsail:GetCertificates',
                method='ACCOUNT_COUNT')


def _distribution_maximum(measure):
    def check(ctx):
        values = [(name, measure(distribution), None)
                  for name, distribution in distributions(ctx).items()]
        return maximum(values, 'LightsailDistribution', 'lightsail:GetDistributions')
    return check


def _forwarded(field, entry):
    """Count the allow list on one forwarded cookie, header or query string set."""
    def measure(distribution):
        settings = distribution.get('cacheBehaviorSettings') or {}
        forwarded = settings.get(field) or {}
        if not isinstance(forwarded, dict):
            raise NoData('Lightsail distribution has invalid cache settings')
        allowed = forwarded.get(entry) or []
        if not isinstance(allowed, list):
            raise NoData('Lightsail distribution has an invalid allow list')
        return len(allowed)
    return measure


def _service_maximum(measure):
    def check(ctx):
        values = [(name, measure(service), None)
                  for name, service in container_services(ctx).items()]
        return maximum(values, 'LightsailContainerService',
                       'lightsail:GetContainerServices')
    return check


def _per_service(method, key, source):
    def check(ctx):
        values = [(name, len(ctx.call(LIGHTSAIL, method, key, serviceName=name)), None)
                  for name in container_services(ctx)]
        return maximum(values, 'LightsailContainerService', source)
    return check


def _scale(service):
    scale = service.get('scale')
    if not isinstance(scale, int) or isinstance(scale, bool) or scale < 0:
        raise NoData('Lightsail container service has no scale')
    return scale


def _deployment_containers(service):
    deployment = service.get('currentDeployment') or {}
    containers = deployment.get('containers') or {}
    if not isinstance(containers, dict):
        raise NoData('Lightsail deployment has an invalid container map')
    return len(containers)


CHECKS = [
    ('L-4259AF9B', 'Instances', lambda ctx: count(ctx, 'get_instances', 'instances')),
    ('L-3B2B13A1', 'Databases',
     lambda ctx: count(ctx, 'get_relational_databases', 'relationalDatabases')),
    ('L-BB561519', 'Container services',
     lambda ctx: count(ctx, 'get_container_services', 'containerServices')),
    ('L-1DB37119', 'Distributions',
     lambda ctx: count(ctx, 'get_distributions', 'distributions')),
    ('L-C512E6B9', 'Load balancers',
     lambda ctx: count(ctx, 'get_load_balancers', 'loadBalancers')),
    ('L-CF67FCDA', 'Maximum buckets per account',
     lambda ctx: count(ctx, 'get_buckets', 'buckets')),
    ('L-D5FCDF87', 'Maximum certificates',
     lambda ctx: count(ctx, 'get_certificates', 'certificates')),
    ('L-D3506055', 'Maximum active certificates', active_certificates),
    ('L-6A41A279', 'Block storage disks per instance', disks_per_instance),
    ('L-8F295028', 'Maximum block storage disk space', largest_disk),
    ('L-9773709E', 'Total attached block storage disk space', attached_disk_space),
    ('L-C5DF431B', 'Container service nodes', _service_maximum(_scale)),
    ('L-FC916C10', 'Container service deployment containers',
     _service_maximum(_deployment_containers)),
    ('L-8C5BE2E1', 'Container service custom domains',
     _service_maximum(lambda service: sum(
         len(names) for names in (service.get('publicDomainNames') or {}).values()))),
    ('L-56E0BA80', 'Container service deployment versions',
     _per_service('get_container_service_deployments', 'deployments',
                  'lightsail:GetContainerServiceDeployments')),
    ('L-B35F6366', 'Container service stored container images',
     _per_service('get_container_images', 'containerImages',
                  'lightsail:GetContainerImages')),
    ('L-C27ADEB6', 'Custom domain names per distribution',
     _distribution_maximum(
         lambda distribution: len(distribution.get('alternativeDomainNames') or []))),
    ('L-9A462869', 'Directory and file overrides per distribution',
     _distribution_maximum(
         lambda distribution: len(distribution.get('cacheBehaviors') or []))),
    ('L-C3D6EA9E', 'Allowed cookies per cache behavior for a distribution',
     _distribution_maximum(_forwarded('forwardedCookies', 'cookiesAllowList'))),
    ('L-97957401', 'Allowed headers per cache behavior for a distribution',
     _distribution_maximum(_forwarded('forwardedHeaders', 'headersAllowList'))),
    ('L-A85C5367', 'Allowed query strings per cache behavior for a distribution',
     _distribution_maximum(_forwarded('forwardedQueryStrings',
                                      'queryStringsAllowList'))),
]


def get_current_quotastatus_lightsail(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'lightsail' for service, _ in context.quotas):
        return []
    return context.run('lightsail', CHECKS, skip)
