"""AWS Audit Manager regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def custom_frameworks(ctx):
    return ctx.call('auditmanager', 'list_assessment_frameworks', 'frameworkMetadataList',
                    frameworkType='CUSTOM')


def custom_controls(ctx):
    return ctx.call('auditmanager', 'list_controls', 'controlMetadataList', controlType='CUSTOM')


def controls_per_framework(ctx):
    values = []
    for framework in custom_frameworks(ctx):
        framework_id = framework.get('id')
        details = ctx.call('auditmanager', 'get_assessment_framework', frameworkId=framework_id)['framework']
        count = sum(len(control_set.get('controls', [])) for control_set in details.get('controlSets', []))
        values.append((framework_id, count, None))
    return maximum(values, 'AuditManagerFramework', 'auditmanager:GetAssessmentFramework')


CHECKS = [
    ('L-8935A6F1', 'Custom frameworks',
     lambda ctx: dict(usage=len(custom_frameworks(ctx)), source='auditmanager:ListAssessmentFrameworks', method='ACCOUNT_COUNT')),
    ('L-0255B75F', 'Custom controls',
     lambda ctx: dict(usage=len(custom_controls(ctx)), source='auditmanager:ListControls', method='ACCOUNT_COUNT')),
    ('L-92B50F18', 'Running assessments',
     lambda ctx: dict(usage=len(ctx.call('auditmanager', 'list_assessments', 'assessmentMetadata', status='ACTIVE')),
                      source='auditmanager:ListAssessments', method='ACCOUNT_COUNT')),
    ('L-724DD74D', 'Controls per framework', controls_per_framework),
]


def get_current_quotastatus_auditmanager(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'auditmanager' for service, _ in context.quotas):
        return []
    return context.run('auditmanager', CHECKS, skip)
