"""Secrets Manager regional secret inventory."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def versions_per_secret(ctx):
    values = []
    for secret in ctx.call('secretsmanager', 'list_secrets', 'SecretList'):
        identifier = secret.get('ARN') or secret.get('Name')
        if identifier:
            versions = ctx.call('secretsmanager', 'list_secret_version_ids',
                                'Versions', SecretId=identifier)
            values.append((identifier, len(versions), None))
    return maximum(values, 'Secret', 'secretsmanager:ListSecrets+ListSecretVersionIds')


CHECKS = [
    ('L-2F66C23C', 'Secrets',
     lambda ctx: dict(usage=len(ctx.call('secretsmanager', 'list_secrets', 'SecretList')),
                      source='secretsmanager:ListSecrets', method='ACCOUNT_COUNT')),
    ('L-7823223D', 'Versions per secret', versions_per_secret),
]


def get_current_quotastatus_secretsmanager(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'secretsmanager' for service, _ in context.quotas):
        return []
    return context.run('secretsmanager', CHECKS, skip)
