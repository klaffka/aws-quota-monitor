"""Amazon Macie regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('macie2', method, key)),
                source=f'macie2:{method}', method='ACCOUNT_COUNT')


def jobs(ctx):
    """Return the full definition of every sensitive data discovery job."""
    for job in ctx.call('macie2', 'list_classification_jobs', 'items'):
        job_id = job.get('jobId')
        if job_id:
            yield job_id, ctx.call('macie2', 'describe_classification_job', jobId=job_id)


def buckets_per_job(ctx):
    values = []
    for job_id, detail in jobs(ctx):
        definitions = (detail.get('s3JobDefinition') or {}).get('bucketDefinitions') or ()
        values.append((job_id, sum(len(entry.get('buckets') or ()) for entry in definitions), None))
    return maximum(values, 'MacieClassificationJob',
                   'macie2:ListClassificationJobs+DescribeClassificationJob')


def identifiers_per_job(ctx):
    return maximum([(job_id, len(detail.get('customDataIdentifierIds') or ()), None)
                    for job_id, detail in jobs(ctx)], 'MacieClassificationJob',
                   'macie2:ListClassificationJobs+DescribeClassificationJob')


CHECKS = [
    ('L-14954719', 'S3 buckets per sensitive data discovery job', buckets_per_job),
    ('L-3572300B', 'Custom data identifiers per sensitive data discovery job', identifiers_per_job),
    ('L-7D690B48', 'Custom data identifiers per account',
     lambda ctx: resource_count(ctx, 'list_custom_data_identifiers', 'items')),
    ('L-E2FBEE6E', 'Findings rules',
     lambda ctx: resource_count(ctx, 'list_findings_filters', 'findingsFilterListItems')),
    ('L-2F634A96', 'Member accounts through AWS Organizations',
     lambda ctx: resource_count(ctx, 'list_members', 'members')),
    ('L-7AF7F5C8', 'Member accounts by invitation',
     lambda ctx: dict(usage=ctx.call('macie2', 'get_invitations_count').get('invitationsCount', 0),
                      source='macie2:GetInvitationsCount', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_macie(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'macie2' for service, _ in context.quotas):
        return []
    return context.run('macie2', CHECKS, skip)
