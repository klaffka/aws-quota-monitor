"""Lambda configuration quotas. Sizes use bytes with explicit unit conversion."""
from botocore.exceptions import ClientError
from modules.qmcore.aws import CheckContext, maximum, Unsupported, session_from_env


def functions(ctx):
    return ctx.call('lambda', 'list_functions', 'Functions', FunctionVersion='ALL')


def storage(ctx):
    settings = ctx.call('lambda', 'get_account_settings')
    return dict(usage=settings['AccountUsage']['TotalCodeSize'],
                limit=settings['AccountLimit']['TotalCodeSize'], unit='Bytes',
                source='lambda:GetAccountSettings', method='ACCOUNT_TOTAL')


def sized(ctx, code, fn, source):
    result = maximum([(f['FunctionArn'], fn(f), None) for f in functions(ctx)], 'FunctionVersion', source)
    quota = ctx.quotas.get(('lambda', code)) or ctx.call('service-quotas', 'get_service_quota',
                   ServiceCode='lambda', QuotaCode=code)['Quota']
    scale = {'Bytes': 1, 'Kilobytes': 1024, 'Megabytes': 1024**2, 'Gigabytes': 1024**3}.get(quota.get('Unit'))
    if scale is None:
        raise Unsupported('Lambda size quota unit is not explicit; refusing magnitude heuristic')
    result.update(limit=quota['Value'] * scale, unit='Bytes')
    return result


def environment_size(function):
    env = function.get('Environment', {})
    if env.get('Error'):
        raise RuntimeError(f"Environment inventory unavailable: {env['Error']}")
    return sum(len(k.encode('utf-8')) + len(v.encode('utf-8'))
               for k, v in env.get('Variables', {}).items())


def policy_size(ctx, function):
    try:
        policy = ctx.call('lambda', 'get_policy', FunctionName=function['FunctionArn'])['Policy']
        return len(policy.encode('utf-8'))
    except ClientError as exc:
        if exc.response['Error']['Code'] == 'ResourceNotFoundException':
            # Distinguish no policy from a function/qualifier deleted mid-inventory.
            ctx.call('lambda', 'get_function_configuration', FunctionName=function['FunctionArn'])
            return 0
        raise



def policies(ctx):
    resources = list(functions(ctx))
    # Aliases can have independent resource-based policies too.
    latest = {f['FunctionName']: f for f in resources if f.get('Version') == '$LATEST'}
    for name in latest:
        for alias in ctx.call('lambda', 'list_aliases', 'Aliases', FunctionName=name):
            resources.append({'FunctionArn': alias['AliasArn']})
    result = maximum([(f['FunctionArn'], policy_size(ctx, f), None) for f in resources],
                     'FunctionVersionOrAlias', 'lambda:GetPolicy')
    quota = ctx.quotas.get(('lambda', 'L-07A00131')) or ctx.call('service-quotas', 'get_service_quota',
                   ServiceCode='lambda', QuotaCode='L-07A00131')['Quota']
    scale = {'Bytes': 1, 'Kilobytes': 1024}.get(quota.get('Unit'))
    if scale is None:
        raise Unsupported('Lambda policy size quota unit is not explicit')
    result.update(limit=quota['Value'] * scale, unit='Bytes')
    return result


def kafka_default_mode(ctx):
    """Count Kafka mappings in on-demand (default) poller mode.

    Lambda exposes ``ProvisionedPollerConfig`` only for provisioned mode. An
    absent or empty config is the documented on-demand mode. The quota covers
    both Amazon MSK and self-managed Apache Kafka mappings, represented by
    their respective event-source configuration fields.
    """
    mappings = ctx.call('lambda', 'list_event_source_mappings', 'EventSourceMappings')
    count = sum(
        (mapping.get('AmazonManagedKafkaEventSourceConfig') is not None or
         mapping.get('SelfManagedKafkaEventSourceConfig') is not None) and
        not mapping.get('ProvisionedPollerConfig')
        for mapping in mappings
    )
    return dict(usage=count, source='lambda:ListEventSourceMappings', method='REGION_TOTAL')


def direct_upload_package_size(ctx):
    """Keep the direct-upload quota explicitly unsupported.

    Lambda exposes the compressed ``CodeSize`` and ``PackageType`` for a
    function, but it does not retain the provenance of a ZIP upload.  A ZIP
    uploaded with ``CreateFunction(Zip=...)`` and the same ZIP supplied via
    ``S3Bucket`` both appear as ``PackageType=Zip`` (and ``GetFunction`` only
    reports the repository as Lambda-managed storage).  Counting every ZIP
    would therefore include S3 uploads, while counting only packages below
    50 MB would still include both kinds.  Neither result is a valid
    measurement of the *direct upload* quota.

    The quota is a request-time limit, not an account usage counter.  Keep it
    visible in coverage until Lambda exposes upload provenance or a usage
    metric for this quota.
    """
    raise Unsupported(
        'Lambda API exposes ZIP size and package type, but not direct-vs-S3 '
        'upload provenance; direct-upload usage cannot be measured safely'
    )


def unsupported(reason):
    raise Unsupported(reason)


CHECKS = [
    ('L-2ACBD22F', 'Function and layer storage', storage),
    ('L-75F48B05', 'Deployment package size (direct upload)', direct_upload_package_size),
    ('L-01237738', 'Function layers', lambda c: maximum(
        [(f['FunctionArn'], len(f.get('Layers', [])), None) for f in functions(c)], 'FunctionVersion', 'lambda:ListFunctions')),
    ('L-6581F036', 'Environment variable size', lambda c: sized(c, 'L-6581F036', environment_size, 'lambda:ListFunctions')),
    ('L-07A00131', 'Function resource-based policy', policies),
    ('L-C952DDE4', 'Kafka Event Source Mappings in default mode on Lambda Managed Instances', kafka_default_mode),
]


def get_current_quotastatus_lambda(session=None, *, ctx=None, skip=()):
    return (ctx or CheckContext(session or session_from_env())).run('lambda', CHECKS, skip)
