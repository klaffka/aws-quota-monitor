"""Amazon FSx file system, cache, capacity and backup quotas.

Storage capacity is reported in GiB, throughput in MBps and IOPS as a count,
which is what the catalog limits state: Windows SSD storage capacity is 524,288,
that is 512 TiB in GiB.
"""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

FSX = 'fsx'
FILE_SYSTEM_TYPES = {'WINDOWS', 'LUSTRE', 'ONTAP', 'OPENZFS'}
LUSTRE_DEPLOYMENT_TYPES = {'SCRATCH_1', 'SCRATCH_2', 'PERSISTENT_1', 'PERSISTENT_2'}
SCRATCH_TYPES = {'SCRATCH_1', 'SCRATCH_2'}
STORAGE_TYPES = {'SSD', 'HDD', 'INTELLIGENT_TIERING'}
CONFIGURATIONS = {'WINDOWS': 'WindowsConfiguration', 'LUSTRE': 'LustreConfiguration',
                  'ONTAP': 'OntapConfiguration', 'OPENZFS': 'OpenZFSConfiguration'}


def file_systems(ctx):
    found = []
    for file_system in ctx.call(FSX, 'describe_file_systems', 'FileSystems'):
        kind = file_system.get('FileSystemType')
        if kind not in FILE_SYSTEM_TYPES:
            raise NoData('FSx file system has an unknown type')
        if kind == 'LUSTRE':
            deployment = (file_system.get('LustreConfiguration') or {}).get(
                'DeploymentType')
            if deployment is not None and deployment not in LUSTRE_DEPLOYMENT_TYPES:
                raise NoData('FSx Lustre file system has an unknown deployment type')
        storage = file_system.get('StorageType')
        if storage is not None and storage not in STORAGE_TYPES:
            raise NoData('FSx file system has an unknown storage type')
        found.append(file_system)
    return found


def _matching(ctx, kind, deployment=None, storage=None):
    for file_system in file_systems(ctx):
        if file_system['FileSystemType'] != kind:
            continue
        if deployment is not None:
            configured = (file_system.get('LustreConfiguration') or {}).get(
                'DeploymentType')
            if configured not in deployment:
                continue
        if storage is not None and file_system.get('StorageType') != storage:
            continue
        yield file_system


def count_type(ctx, file_system_type, deployment_type=None):
    deployment = {deployment_type} if deployment_type else None
    usage = sum(1 for _ in _matching(ctx, file_system_type, deployment))
    return dict(usage=usage, source='fsx:DescribeFileSystems',
                method='ACCOUNT_COUNT')


def _capacity(field, kind, deployment=None, storage=None, largest=False):
    """Sum, or take the largest, of one capacity field across file systems."""
    def check(ctx):
        values = []
        for file_system in _matching(ctx, kind, deployment, storage):
            if field == 'StorageCapacity':
                value = file_system.get('StorageCapacity')
            else:
                configuration = file_system.get(CONFIGURATIONS[kind]) or {}
                value = configuration.get(field)
            if value is None:
                continue
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise NoData(f'FSx file system has an invalid {field}')
            values.append((file_system.get('FileSystemId'), value, None))
        if largest:
            return maximum(values, 'FSxFileSystem', 'fsx:DescribeFileSystems')
        return dict(usage=sum(value for _, value, _ in values),
                    source='fsx:DescribeFileSystems', method='ACCOUNT_COUNT')
    return check


def _nested_capacity(kind, configuration_field, nested_field, storage=None):
    """Read a capacity that lives one level inside the type's configuration."""
    def check(ctx):
        usage = 0
        for file_system in _matching(ctx, kind, storage=storage):
            configuration = file_system.get(CONFIGURATIONS[kind]) or {}
            nested = configuration.get(configuration_field) or {}
            value = nested.get(nested_field)
            if value is None:
                continue
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise NoData(f'FSx file system has an invalid {nested_field}')
            usage += value
        return dict(usage=usage, source='fsx:DescribeFileSystems',
                    method='ACCOUNT_COUNT')
    return check


def file_caches(ctx):
    found = []
    for cache in ctx.call(FSX, 'describe_file_caches', 'FileCaches'):
        if cache.get('FileCacheType') != 'LUSTRE':
            raise NoData('FSx file cache has an unknown type')
        found.append(cache)
    return found


def cache_storage_capacity(ctx):
    usage = 0
    for cache in file_caches(ctx):
        value = cache.get('StorageCapacity')
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise NoData('FSx file cache has no storage capacity')
        usage += value
    return dict(usage=usage, source='fsx:DescribeFileCaches',
                method='ACCOUNT_COUNT')


def backups_by_type(ctx):
    counts = Counter()
    for backup in ctx.call(FSX, 'describe_backups', 'Backups'):
        file_system = backup.get('FileSystem') or {}
        kind = file_system.get('FileSystemType')
        if kind not in FILE_SYSTEM_TYPES:
            raise NoData('FSx backup has an unknown file system type')
        counts[kind] += 1
    return counts


def _backups(kind):
    return lambda ctx: dict(usage=backups_by_type(ctx)[kind],
                            source='fsx:DescribeBackups', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-C28C1403', 'ONTAP file systems', lambda ctx: count_type(ctx, 'ONTAP')),
    ('L-5B89F9CE', 'Windows file systems', lambda ctx: count_type(ctx, 'WINDOWS')),
    ('L-59D0763F', 'OpenZFS file systems', lambda ctx: count_type(ctx, 'OPENZFS')),
    ('L-9AFA1F09', 'Lustre Persistent_1 file systems',
     lambda ctx: count_type(ctx, 'LUSTRE', 'PERSISTENT_1')),
    ('L-FD6F2F22', 'Lustre Persistent_2 file systems',
     lambda ctx: count_type(ctx, 'LUSTRE', 'PERSISTENT_2')),
    ('L-C48231E5', 'Lustre Scratch file systems',
     lambda ctx: dict(usage=sum(1 for _ in _matching(ctx, 'LUSTRE', SCRATCH_TYPES)),
                      source='fsx:DescribeFileSystems', method='ACCOUNT_COUNT')),
    ('L-60836D3E', 'Lustre Cache_1 caches',
     lambda ctx: dict(usage=len(file_caches(ctx)), source='fsx:DescribeFileCaches',
                      method='ACCOUNT_COUNT')),
    ('L-15D9FE87', 'Lustre Cache_1 storage capacity', cache_storage_capacity),
    ('L-C8640C82', 'Lustre Persistent_1 storage capacity',
     _capacity('StorageCapacity', 'LUSTRE', {'PERSISTENT_1'})),
    ('L-8F1B9C74', 'Lustre Persistent_2 storage capacity',
     _capacity('StorageCapacity', 'LUSTRE', {'PERSISTENT_2'})),
    ('L-AD2FC696', 'Lustre Scratch storage capacity',
     _capacity('StorageCapacity', 'LUSTRE', SCRATCH_TYPES)),
    ('L-736F3D6F', 'Lustre Persistent HDD storage capacity (per file system)',
     _capacity('StorageCapacity', 'LUSTRE', None, 'HDD', largest=True)),
    ('L-B7391FCE',
     'Lustre Persistent Intelligent-Tiering SSD read cache storage capacity',
     _nested_capacity('LUSTRE', 'DataReadCacheConfiguration', 'SizeGiB',
                      'INTELLIGENT_TIERING')),
    ('L-0CD18A5D', 'Lustre Persistent Intelligent-Tiering throughput capacity',
     _capacity('ThroughputCapacity', 'LUSTRE', None, 'INTELLIGENT_TIERING')),
    ('L-E2C89679', 'ONTAP SSD storage capacity',
     _capacity('StorageCapacity', 'ONTAP')),
    ('L-C5F860DD', 'ONTAP throughput capacity',
     _capacity('ThroughputCapacity', 'ONTAP')),
    ('L-57578687', 'ONTAP SSD IOPS',
     _nested_capacity('ONTAP', 'DiskIopsConfiguration', 'Iops')),
    ('L-88479C21', 'OpenZFS SSD storage capacity',
     _capacity('StorageCapacity', 'OPENZFS')),
    ('L-7D5FDD38', 'OpenZFS SSD storage capacity (per file system)',
     _capacity('StorageCapacity', 'OPENZFS', largest=True)),
    ('L-4EDE4065', 'OpenZFS throughput capacity',
     _capacity('ThroughputCapacity', 'OPENZFS')),
    ('L-E24B4DE4', 'OpenZFS disk IOPS',
     _nested_capacity('OPENZFS', 'DiskIopsConfiguration', 'Iops')),
    ('L-4E6C2FB3', 'OpenZFS provisioned SSD read cache storage capacity',
     _nested_capacity('OPENZFS', 'ReadCacheConfiguration', 'SizeGiB')),
    ('L-E43BDB2E', 'Windows SSD storage capacity',
     _capacity('StorageCapacity', 'WINDOWS', None, 'SSD')),
    ('L-84EAF187', 'Windows HDD storage capacity',
     _capacity('StorageCapacity', 'WINDOWS', None, 'HDD')),
    ('L-FD89CA8A', 'Windows throughput capacity',
     _capacity('ThroughputCapacity', 'WINDOWS')),
    ('L-901C77F5', 'Windows total SSD IOPS',
     _nested_capacity('WINDOWS', 'DiskIopsConfiguration', 'Iops')),
    ('L-CD5E0524', 'Lustre backups', _backups('LUSTRE')),
    ('L-C431DBA3', 'ONTAP backups', _backups('ONTAP')),
    ('L-DD0F7417', 'OpenZFS backups', _backups('OPENZFS')),
    ('L-E94C1C19', 'Windows backups', _backups('WINDOWS')),
]


def get_current_quotastatus_fsx(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'fsx' for service, _ in context.quotas):
        return []
    return context.run('fsx', CHECKS, skip)
