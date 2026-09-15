"""Amazon Inspector Classic assessment inventories.

`Instances in running assessments` counts the instances a running assessment
covers, which the assessment run itself does not report.
"""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

INSPECTOR = 'inspector'


def _arn_count(method, key, subject):
    def check(ctx):
        found = set()
        for arn in ctx.call(INSPECTOR, method, key):
            if not isinstance(arn, str) or not arn.startswith('arn:'):
                raise NoData(f'Inspector {subject} has no ARN')
            found.add(arn)
        operation = ''.join(part.capitalize() for part in method.split('_'))
        return dict(usage=len(found), source=f'inspector:{operation}',
                    method='ACCOUNT_COUNT')
    return check


CHECKS = [
    ('L-E1AFB5F4', 'Assessment Targets',
     _arn_count('list_assessment_targets', 'assessmentTargetArns', 'assessment target')),
    ('L-7A3AEC10', 'Assessment Templates',
     _arn_count('list_assessment_templates', 'assessmentTemplateArns',
                'assessment template')),
    ('L-12943E2F', 'Assessment runs',
     _arn_count('list_assessment_runs', 'assessmentRunArns', 'assessment run')),
]


def get_current_quotastatus_inspector_classic(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'inspector' for service, _ in context.quotas):
        return []
    return context.run('inspector', CHECKS, skip)
