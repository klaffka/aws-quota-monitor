"""AWS CodeArtifact domain, repository and upstream inventories.

`Upstream repositories searched` bounds how far one package resolution walks
the upstream chain rather than how many a repository declares, so it is not an
inventory and stays open.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def domains(ctx):
    return ctx.call('codeartifact', 'list_domains', 'domains')


def repositories_per_domain(ctx):
    values = []
    for domain in domains(ctx):
        repos = ctx.call('codeartifact', 'list_repositories_in_domain', 'repositories',
                         domain=domain['name'])
        values.append((domain['name'], len(repos), None))
    return maximum(values, 'CodeArtifactDomain', 'codeartifact:ListRepositoriesInDomain')


def upstreams_per_repository(ctx):
    """A repository declaring no upstream counts as zero rather than dropping out."""
    values = []
    for domain in domains(ctx):
        domain_name = domain['name']
        for repository in ctx.call('codeartifact', 'list_repositories_in_domain',
                                   'repositories', domain=domain_name):
            name = repository.get('name')
            if not isinstance(name, str) or not name:
                raise NoData('CodeArtifact repository is missing its name')
            detail = ctx.call('codeartifact', 'describe_repository', domain=domain_name,
                              repository=name).get('repository') or {}
            upstreams = detail.get('upstreams') or []
            values.append((f'{domain_name}/{name}', len(upstreams), None))
    return maximum(values, 'CodeArtifactRepository', 'codeartifact:DescribeRepository')


CHECKS = [
    ('L-DD7208D3', 'Domains per AWS account',
     lambda ctx: dict(usage=len(domains(ctx)), source='codeartifact:ListDomains', method='ACCOUNT_COUNT')),
    ('L-86608C96', 'Repositories per domain', repositories_per_domain),
    ('L-D42B1EF2', 'Direct upstreams per repository', upstreams_per_repository),
]


def get_current_quotastatus_codeartifact(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'codeartifact' for service, _ in context.quotas): return []
    return context.run('codeartifact', CHECKS, skip)
