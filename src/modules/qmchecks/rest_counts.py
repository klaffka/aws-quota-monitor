"""Additional direct resource-count checks discovered from the quota catalog."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env

CUSTOM_KEYS = {('application-signals', 'L-3FECAFD0'), ('aps', 'L-8873DB23'),
               ('voiceid', 'L-CF9F1A9B')}


def count(service, method, key):
    return lambda c: dict(usage=len(c.call(service, method, key)),
                          source=f'{service}:{method}', method='ACCOUNT_COUNT')


def voice_id_parent_max(ctx, method, key, code_kwargs=None):
    values = []
    for domain in ctx.call('voice-id', 'list_domains', 'Domains'):
        did = domain.get('DomainId')
        if did:
            kwargs = {'DomainId': did}
            if code_kwargs:
                kwargs.update(code_kwargs)
            values.append((did, len(ctx.call('voice-id', method, key, **kwargs)), None))
    return maximum(values, 'VoiceIdDomain', f'voice-id:{method}')


def get_current_quotastatus_rest_counts(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    entries = []
    if any(service == 'application-signals' for service, _ in context.quotas):
        entries.extend(context.run('application-signals', [
            ('L-3FECAFD0', 'Number of SLOs per Region',
             count('application-signals', 'list_service_level_objectives', 'SloSummaries')),
        ], skip))
    if any(service == 'aps' for service, _ in context.quotas):
        entries.extend(context.run('aps', [
            ('L-8873DB23', 'Workspaces per region per account',
             count('amp', 'list_workspaces', 'workspaces')),
        ], skip))
    if any(service == 'voiceid' for service, _ in context.quotas):
        entries.extend(context.run('voiceid', [
            ('L-CF9F1A9B', 'Domains per region', count('voice-id', 'list_domains', 'Domains')),
            ('L-3790424B', 'Watchlists per domain', lambda c: voice_id_parent_max(c, 'list_watchlists', 'WatchlistSummaries')),
            ('L-65FE7850', 'Speakers per domain', lambda c: voice_id_parent_max(c, 'list_speakers', 'SpeakerSummaries')),
            ('L-38B73369', 'Active fraudster registration jobs per domain', lambda c: voice_id_parent_max(c, 'list_fraudster_registration_jobs', 'JobSummaries', {'JobStatus': 'IN_PROGRESS'})),
            ('L-55441DAB', 'Active speaker enrollment jobs per domain', lambda c: voice_id_parent_max(c, 'list_speaker_enrollment_jobs', 'JobSummaries', {'JobStatus': 'IN_PROGRESS'})),
        ], skip))
    return entries
