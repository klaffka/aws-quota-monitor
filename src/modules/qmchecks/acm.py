"""AWS Certificate Manager regional certificate inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-F141DD1D', 'ACM certificates',
     lambda ctx: dict(usage=len(ctx.call('acm', 'list_certificates', 'CertificateSummaryList')),
                      source='acm:ListCertificates', method='ACCOUNT_COUNT')),
    ('L-D2CB7DE9', 'Imported certificates',
     lambda ctx: dict(usage=sum(certificate.get('Type') == 'IMPORTED'
                                for certificate in ctx.call('acm', 'list_certificates',
                                                            'CertificateSummaryList')),
                      source='acm:ListCertificates(Type=IMPORTED)', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_acm(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'acm' for service, _ in context.quotas):
        return []
    return context.run('acm', CHECKS, skip)
