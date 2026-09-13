"""CloudWatch anomaly detector inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-58896C49', 'CloudWatch Anomaly Detection models',
     lambda c: dict(usage=len(c.call('cloudwatch', 'describe_anomaly_detectors',
                                     'AnomalyDetectors')),
                    source='cloudwatch:DescribeAnomalyDetectors', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_cloudwatchpredictions(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'cloudwatchpredictions' for service, _ in context.quotas):
        return []
    return context.run('cloudwatchpredictions', CHECKS, skip)
