"""Amazon GuardDuty regional detector resource-count quotas."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def detectors(ctx):
    return ctx.call('guardduty', 'list_detectors', 'detectorIds')


def detector_count(ctx):
    return dict(usage=len(detectors(ctx)), source='guardduty:ListDetectors', method='ACCOUNT_COUNT')


def sets_per_detector(ctx, method, key, source):
    values = []
    for detector in detectors(ctx):
        values.append((detector, len(ctx.call('guardduty', method, key, DetectorId=detector)), None))
    return maximum(values, 'GuardDutyDetector', source)


CHECKS = [
    ('L-FA6D6E3D', 'Detectors', detector_count),
    ('L-AFBA2260', 'Trusted IP sets',
     lambda ctx: sets_per_detector(ctx, 'list_ip_sets', 'IpSets', 'guardduty:ListIPSets')),
    ('L-2C0E14B9', 'Threat intel sets',
     lambda ctx: sets_per_detector(ctx, 'list_threat_intel_sets', 'ThreatIntelSets',
                                   'guardduty:ListThreatIntelSets')),
    ('L-9ABF7A23', 'Filters',
     lambda ctx: sets_per_detector(ctx, 'list_filters', 'FilterNames', 'guardduty:ListFilters')),
]


def get_current_quotastatus_guardduty(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'guardduty' for service, _ in context.quotas):
        return []
    return context.run('guardduty', CHECKS, skip)
