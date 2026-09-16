"""AWS Private CA Connector for SCEP resource quotas."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


SERVICE = 'pca-connector-scep'
CONNECTOR_STATES = {'CREATING', 'ACTIVE', 'DELETING', 'FAILED'}


def _validate_arn(arn, ctx, prefix, subject):
    parts = arn.split(':', 5) if isinstance(arn, str) else []
    if (len(parts) != 6 or parts[0] != 'arn' or parts[2] != SERVICE
            or parts[3] != ctx.region or parts[4] != ctx.account
            or not parts[5].startswith(prefix)
            or len(parts[5]) <= len(prefix)):
        raise NoData(f'PCA Connector SCEP {subject} has an inconsistent ARN')


def connectors(ctx):
    result = {}
    for item in ctx.call(SERVICE, 'list_connectors', 'Connectors'):
        if not isinstance(item, dict):
            raise NoData('PCA Connector SCEP inventory contains an invalid connector')
        arn = item.get('Arn')
        _validate_arn(arn, ctx, 'connector/', 'connector')
        if item.get('Status') not in CONNECTOR_STATES:
            raise NoData('PCA Connector SCEP connector has an unknown state')
        if arn in result:
            if result[arn] != item:
                raise NoData('PCA Connector SCEP connector changed during pagination')
            continue
        result[arn] = item
    return result


def connector_count(ctx):
    return dict(usage=len(connectors(ctx)), source=f'{SERVICE}:ListConnectors',
                method='ACCOUNT_COUNT')


def challenges_per_connector(ctx):
    values = []
    for connector_arn, connector in connectors(ctx).items():
        if connector['Status'] != 'ACTIVE':
            raise NoData('PCA Connector SCEP connector child inventory is unresolved')
        challenges = {}
        items = ctx.call(SERVICE, 'list_challenge_metadata', 'Challenges',
                         ConnectorArn=connector_arn)
        parent = connector_arn.split(':', 5)[5]
        for item in items:
            if not isinstance(item, dict):
                raise NoData('PCA Connector SCEP inventory contains an invalid challenge')
            arn = item.get('Arn')
            _validate_arn(arn, ctx, f'{parent}/challenge/', 'challenge')
            if item.get('ConnectorArn') != connector_arn:
                raise NoData('PCA Connector SCEP challenge has an inconsistent parent')
            if arn in challenges:
                if challenges[arn] != item:
                    raise NoData('PCA Connector SCEP challenge changed during pagination')
                continue
            challenges[arn] = item
        values.append((connector_arn, len(challenges), None))
    return maximum(values, 'PcaConnectorScepConnector',
                   f'{SERVICE}:ListConnectors+ListChallengeMetadata')


CHECKS = [
    ('L-CB21FAEA', 'Number of connectors', connector_count),
    ('L-D42FC980', 'Number of challenges per connector', challenges_per_connector),
]


def get_current_quotastatus_pca_connector_scep(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == SERVICE for service, _ in context.quotas):
        return []
    return context.run(SERVICE, CHECKS, skip)
