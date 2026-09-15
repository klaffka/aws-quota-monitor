"""AWS IAM Access Analyzer regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def analyzers(ctx):
    return ctx.call('accessanalyzer', 'list_analyzers', 'analyzers')


def analyzer_count(ctx, analyzer_type):
    return dict(usage=sum(a.get('type') == analyzer_type for a in analyzers(ctx)),
                source='accessanalyzer:ListAnalyzers', method='ACCOUNT_COUNT')


def archive_rules_per_analyzer(ctx):
    values = []
    for analyzer in analyzers(ctx):
        # ListArchiveRules is addressed by analyzer name; the ARN is rejected.
        name, arn = analyzer.get('name'), analyzer.get('arn')
        if not name:
            raise NoData('Access Analyzer analyzer is missing its name')
        rules = ctx.call('accessanalyzer', 'list_archive_rules', 'archiveRules',
                         analyzerName=name)
        values.append((arn or name, len(rules), None))
    return maximum(values, 'AccessAnalyzer', 'accessanalyzer:ListArchiveRules')


CHECKS = [
    ('L-2F63646F', 'Account level analyzer', lambda ctx: analyzer_count(ctx, 'ACCOUNT')),
    ('L-6F85FE0C', 'Organization level analyzer', lambda ctx: analyzer_count(ctx, 'ORGANIZATION')),
    ('L-1E51937C', 'Archive rules per analyzer', archive_rules_per_analyzer),
]


def get_current_quotastatus_access_analyzer(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'access-analyzer' for service, _ in context.quotas):
        return []
    return context.run('access-analyzer', CHECKS, skip)
