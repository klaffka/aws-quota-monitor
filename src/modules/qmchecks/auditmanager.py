"""AWS Audit Manager regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


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


def accounts_in_scope(ctx):
    assessments = {}
    for item in ctx.call('auditmanager', 'list_assessments', 'assessmentMetadata'):
        if not isinstance(item, dict):
            raise NoData('Audit Manager assessment inventory contains an invalid item')
        assessment_id = item.get('id')
        if not isinstance(assessment_id, str) or not assessment_id:
            raise NoData('Audit Manager assessment is missing its ID')
        if assessment_id in assessments and assessments[assessment_id] != item:
            raise NoData('Audit Manager assessment inventory changed during pagination')
        assessments[assessment_id] = item

    accounts = set()
    for assessment_id in sorted(assessments):
        response = ctx.call('auditmanager', 'get_assessment', assessmentId=assessment_id)
        assessment = response.get('assessment') if isinstance(response, dict) else None
        metadata = assessment.get('metadata') if isinstance(assessment, dict) else None
        scope = metadata.get('scope') if isinstance(metadata, dict) else None
        if not isinstance(metadata, dict) or metadata.get('id') != assessment_id:
            raise NoData('Audit Manager assessment detail is inconsistent')
        scoped_accounts = scope.get('awsAccounts') if isinstance(scope, dict) else None
        if (not isinstance(scoped_accounts, list)
                or any(not isinstance(account, dict) for account in scoped_accounts)):
            raise NoData('Audit Manager assessment has an invalid account scope')
        for account in scoped_accounts:
            account_id = account.get('id')
            if not isinstance(account_id, str) or not account_id:
                raise NoData('Audit Manager account scope contains an invalid account')
            accounts.add(account_id)
    return dict(usage=len(accounts),
                source='auditmanager:ListAssessments+GetAssessment',
                method='ACCOUNT_COUNT')


CHECKS = [
    ('L-8935A6F1', 'Custom frameworks',
     lambda ctx: dict(usage=len(custom_frameworks(ctx)), source='auditmanager:ListAssessmentFrameworks', method='ACCOUNT_COUNT')),
    ('L-0255B75F', 'Custom controls',
     lambda ctx: dict(usage=len(custom_controls(ctx)), source='auditmanager:ListControls', method='ACCOUNT_COUNT')),
    ('L-92B50F18', 'Running assessments',
     lambda ctx: dict(usage=len(ctx.call('auditmanager', 'list_assessments', 'assessmentMetadata', status='ACTIVE')),
                      source='auditmanager:ListAssessments', method='ACCOUNT_COUNT')),
    ('L-724DD74D', 'Controls per framework', controls_per_framework),
    ('L-BEA222D4', 'Accounts in scope across all assessments', accounts_in_scope),
]


def get_current_quotastatus_auditmanager(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'auditmanager' for service, _ in context.quotas):
        return []
    return context.run('auditmanager', CHECKS, skip)
