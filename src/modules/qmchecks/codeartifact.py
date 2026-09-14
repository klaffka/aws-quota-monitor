"""AWS CodeArtifact domain and repository inventories."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def domains(ctx):
    return ctx.call('codeartifact', 'list_domains', 'domains')


def repositories_per_domain(ctx):
    values = []
    for domain in domains(ctx):
        repos = ctx.call('codeartifact', 'list_repositories', 'repositories', domain=domain['name'])
        values.append((domain['name'], len(repos), None))
    return maximum(values, 'CodeArtifactDomain', 'codeartifact:ListRepositories')


CHECKS = [
    ('L-DD7208D3', 'Domains per AWS account',
     lambda ctx: dict(usage=len(domains(ctx)), source='codeartifact:ListDomains', method='ACCOUNT_COUNT')),
    ('L-86608C96', 'Repositories per domain', repositories_per_domain),
]


def get_current_quotastatus_codeartifact(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'codeartifact' for service, _ in context.quotas): return []
    return context.run('codeartifact', CHECKS, skip)
