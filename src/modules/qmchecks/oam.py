"""AWS CloudWatch Observability Access Manager resource counts and sink links."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def links_per_sink(ctx):
    """A sink nothing is attached to still holds the quota, so it counts zero."""
    values = []
    for sink in ctx.call('oam', 'list_sinks', 'Items'):
        arn = sink.get('Arn')
        if not isinstance(arn, str) or not arn:
            raise NoData('Observability Access Manager sink is missing its ARN')
        links = ctx.call('oam', 'list_attached_links', 'Items', SinkIdentifier=arn)
        values.append((arn, len(links), None))
    return maximum(values, 'ObservabilitySink', 'oam:ListAttachedLinks')

CHECKS = [
    ('L-92C40D6D', 'Number of links',
     lambda c: dict(usage=len(c.call('oam', 'list_links', 'Items')),
                    source='oam:ListLinks', method='ACCOUNT_COUNT')),
    ('L-AA726EB1', 'Number of sinks',
     lambda c: dict(usage=len(c.call('oam', 'list_sinks', 'Items')),
                    source='oam:ListSinks', method='ACCOUNT_COUNT')),
    ('L-303A1B23', 'Links per sink', links_per_sink),
]


def get_current_quotastatus_oam(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'oam' for service, _ in context.quotas):
        return []
    return context.run('oam', CHECKS, skip)
