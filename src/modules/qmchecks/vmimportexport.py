"""VM Import/Export concurrent task quotas.

The two quotas cover different operation families, so each counts only the task
inventories that belong to it.
"""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

EC2 = 'ec2'
TASK_STATES = {'active', 'cancelling', 'cancelled', 'completed', 'deleting', 'deleted'}
# Only a task that is still moving occupies the concurrency quota.
RUNNING_STATES = {'active', 'cancelling'}


def _status(item, field, subject):
    status = item.get(field)
    if status not in TASK_STATES:
        raise NoData(f'VM Import/Export {subject} has an unknown status')
    return status


def image_and_snapshot_tasks(ctx):
    """ImportImage, ImportSnapshot and ExportImage share one concurrency quota."""
    usage = 0
    for task in ctx.call(EC2, 'describe_import_image_tasks', 'ImportImageTasks'):
        usage += _status(task, 'Status', 'import image task') in RUNNING_STATES
    for task in ctx.call(EC2, 'describe_import_snapshot_tasks', 'ImportSnapshotTasks'):
        detail = task.get('SnapshotTaskDetail')
        if not isinstance(detail, dict):
            raise NoData('VM Import/Export import snapshot task has no detail')
        usage += _status(detail, 'Status', 'import snapshot task') in RUNNING_STATES
    for task in ctx.call(EC2, 'describe_export_image_tasks', 'ExportImageTasks'):
        usage += _status(task, 'Status', 'export image task') in RUNNING_STATES
    return dict(usage=usage, source='ec2:DescribeImportImageTasks+'
                                    'DescribeImportSnapshotTasks+'
                                    'DescribeExportImageTasks',
                method='ACCOUNT_COUNT')


def instance_and_volume_tasks(ctx):
    """ImportInstance, ImportVolume and CreateInstanceExportTask share the other."""
    usage = 0
    for task in ctx.call(EC2, 'describe_conversion_tasks', 'ConversionTasks'):
        usage += _status(task, 'State', 'conversion task') in RUNNING_STATES
    for task in ctx.call(EC2, 'describe_export_tasks', 'ExportTasks'):
        usage += _status(task, 'State', 'export task') in RUNNING_STATES
    return dict(usage=usage,
                source='ec2:DescribeConversionTasks+DescribeExportTasks',
                method='ACCOUNT_COUNT')


CHECKS = [
    ('L-66ABAAD5',
     'Concurrent task limit for ImportImage, ImportSnapshot, and ExportImage',
     image_and_snapshot_tasks),
    ('L-0994E50B',
     'Concurrent task limit for ImportInstance, ImportVolume, and '
     'CreateInstanceExportTask',
     instance_and_volume_tasks),
]


def get_current_quotastatus_vmimportexport(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'vmimportexport' for service, _ in context.quotas):
        return []
    return context.run('vmimportexport', CHECKS, skip)
