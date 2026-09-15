"""AWS Systems Manager Incident Manager Contacts resource counts.

`Rotations per schedule` stays in the audit: Incident Manager has no schedule
resource of its own, so the parent the quota counts against cannot be named
from the API without guessing which one it means.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

CONTACTS = 'ssm-contacts'


def plans(ctx):
    """Yield (contact ARN, engagement plan) for every contact in the account."""
    for contact in ctx.call(CONTACTS, 'list_contacts', 'Contacts'):
        arn = contact.get('ContactArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('Incident Manager contact is missing its ARN')
        detail = ctx.call(CONTACTS, 'get_contact', ContactId=arn)
        if detail.get('ContactArn') != arn:
            raise NoData('Incident Manager contact detail has a different identity')
        yield arn, detail.get('Plan') or {}


def stages_per_plan(ctx):
    return maximum([(arn, len(plan.get('Stages') or ()), None) for arn, plan in plans(ctx)],
                   'IncidentManagerContact', 'ssm-contacts:ListContacts+GetContact')


def channels_per_stage(ctx):
    """A stage engages its targets, so the widest stage sets the usage."""
    values = []
    for arn, plan in plans(ctx):
        for index, stage in enumerate(plan.get('Stages') or ()):
            values.append((f'{arn}#{index}', len(stage.get('Targets') or ()), None))
    return maximum(values, 'IncidentManagerContactStage',
                   'ssm-contacts:ListContacts+GetContact')


def contacts_per_rotation(ctx):
    return maximum([(rotation.get('RotationArn'), len(rotation.get('ContactIds') or ()), None)
                    for rotation in ctx.call(CONTACTS, 'list_rotations', 'Rotations')],
                   'IncidentManagerRotation', 'ssm-contacts:ListRotations')


CHECKS = [
    ('L-7DD2017D', 'Contacts per account',
     lambda c: dict(usage=len(c.call(CONTACTS, 'list_contacts', 'Contacts')),
                    source='ssm-contacts:ListContacts', method='ACCOUNT_COUNT')),
    ('L-4EA3AB3A', 'Rotations per account',
     lambda c: dict(usage=len(c.call(CONTACTS, 'list_rotations', 'Rotations')),
                    source='ssm-contacts:ListRotations', method='ACCOUNT_COUNT')),
    ('L-5AE11799', 'Stages per plan', stages_per_plan),
    ('L-F338226A', 'Contact channels per stage', channels_per_stage),
    ('L-D438A616', 'Contacts per rotation', contacts_per_rotation),
]


def get_current_quotastatus_ssm_contacts(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == CONTACTS for service, _ in context.quotas):
        return []
    return context.run(CONTACTS, CHECKS, skip)
