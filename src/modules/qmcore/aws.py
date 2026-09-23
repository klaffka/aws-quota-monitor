"""AWS context and all-or-error paginated inventories, cached within one run."""
import os
import json
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, UnknownServiceError
from modules.qmcore.model import measurement, utcnow

CONFIG = Config(retries={'mode': 'adaptive', 'max_attempts': 8},
                connect_timeout=5, read_timeout=30)


class Unsupported(ValueError):
    pass


class NoData(ValueError):
    pass


# Answers that say a service is not set up, not offered to this account, or
# retired. They carry no usage, but the check did not fail either. Matching is
# on the error code and a fragment of AWS's message, and optionally the
# operation, because AccessDenied also reports a missing IAM grant: anything
# not listed here stays an ERROR.
NOT_SET_UP = (
    # (error code, operation or None, message fragment, status)
    ('AccessDeniedException', None, 'No default admin could be found', 'NO_DATA'),
    ('AccessDeniedException', None, ('Service role not found. Consult setup procedures in '
     'License Manager'), 'NO_DATA'),
    ('AccessDeniedException', None, 'Macie is not enabled', 'NO_DATA'),
    ('AccessDeniedException', None, 'Please complete AWS Audit Manager setup', 'NO_DATA'),
    ('UninitializedAccountException', None, 'Account not initialized', 'NO_DATA'),
    ('UnsupportedUserEditionException', None, 'is not subscribed for QuickSight', 'NO_DATA'),
    ('ValidationException', 'ListRotations', 'Account not found for the request', 'NO_DATA'),
    ('OptInRequiredException', None, '', 'NO_DATA'),
    ('TagOptionNotMigratedException', None, '', 'NO_DATA'),
    ('InvalidOperationException', None, 'is not the management account of the Organization',
     'NO_DATA'),
    # Automation rules belong to the Security Hub administrator account.
    ('AccessDeniedException', 'ListAutomationRules', 'is not authorized to perform this operation',
     'NO_DATA'),
    ('403', None, 'Telco Network Builder is deprecated', 'UNSUPPORTED'),
    ('UnauthorizedException', None, 'no longer available to new customers', 'UNSUPPORTED'),
    ('AccessDeniedException', 'GetDevEndpoints', 'operation is currently disabled', 'UNSUPPORTED'),
    ('AccessDeniedException', None, 'Account is not authorized to use this feature', 'UNSUPPORTED'),
    ('InvalidParameterValueException', 'DescribeFleetAdvisorCollectors', 'Access Denied to API',
     'UNSUPPORTED'),
    # Organization-wide answers only reach the management account.
    ('AccessDeniedException', 'ListRoots', "You don't have permissions to access this resource",
     'NO_DATA'),
    ('UnauthorizedException', 'ListCentralizationRulesForOrganization', 'Unauthorized', 'NO_DATA'),
    # The IAM Identity Center instance lives in another Region or account.
    ('AccessDeniedException', 'ListPermissionSets', ('because the resource does not exist in this '
     'Region'), 'NO_DATA'),
)

# These services answer the listing of a feature closed to the account with an
# AccessDeniedException that carries no message at all, even for an
# administrator; a missing IAM grant always names the principal and action. A
# later call that fails after the listing succeeded is not a closed feature.
CLOSED_FEATURES = {'iotfleetwise', 'rekognition'}


def not_set_up(exc, service=None):
    """The status for a ClientError that NOT_SET_UP or CLOSED_FEATURES explains, else None."""
    error = exc.response.get('Error', {})
    code, message = error.get('Code'), error.get('Message') or ''
    if (code == 'AccessDeniedException' and not message.strip() and service in CLOSED_FEATURES
            and exc.operation_name.startswith('List')):
        return 'UNSUPPORTED'
    for known, operation, fragment, status in NOT_SET_UP:
        if code == known and operation in {None, exc.operation_name} and fragment in message:
            return status
    return None


def session_from_env():
    return boto3.Session(profile_name=os.getenv('QM_AWS_PROFILE') or os.getenv('AWS_PROFILE'),
                         region_name=os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION'))


def sdk_call(ctx, service, method, key=None, **kwargs):
    """Call an API, reporting a service this SDK no longer ships as unsupported.

    The call is still attempted, so a check starts working again by itself once
    botocore restores the client.
    """
    try:
        return ctx.call(service, method, key, **kwargs)
    except UnknownServiceError:
        raise Unsupported(f'This SDK ships no {service} client, so no inventory '
                          'can be read') from None


def paginate(client, method, key, **kwargs):
    # Some newer EC2 operations have NextToken but no SDK paginator yet.
    if client.can_paginate(method):
        return [item for page in client.get_paginator(method).paginate(**kwargs)
                for item in page.get(key, [])]
    result, seen = [], set()
    while True:
        page = getattr(client, method)(**kwargs)
        result.extend(page.get(key, []))
        token = (page.get('NextToken') or page.get('nextToken') or page.get('NextMarker')
                 or page.get('Marker') or page.get('NextPageToken')
                 or page.get('nextPageToken') or page.get('position'))
        if not token:
            return result
        if token in seen:
            raise RuntimeError(f'Repeated pagination token: {method}')
        seen.add(token)
        if 'nextToken' in page:
            kwargs['nextToken'] = token
        elif 'NextToken' in page:
            kwargs['NextToken'] = token
        elif 'NextMarker' in page:
            kwargs['NextMarker'] = token
        elif 'Marker' in page:
            kwargs['Marker'] = token
        elif 'NextPageToken' in page:
            # Service Catalog returns NextPageToken but takes it back as PageToken.
            kwargs['PageToken'] = token
        elif 'nextPageToken' in page:
            # Lightsail returns nextPageToken but takes it back as pageToken.
            kwargs['pageToken'] = token
        else:
            # API Gateway v1 uses the lower-case ``position`` cursor.
            kwargs['position'] = token


class CheckContext:
    def __init__(self, session, quotas=(), account=None, now=None):
        self.session = session
        self.account = account or session.client('sts', config=CONFIG).get_caller_identity()['Account']
        self.region = session.region_name
        if not self.region:
            raise ValueError('Configure AWS_REGION or AWS_DEFAULT_REGION')
        self.now = now or utcnow()
        self.quotas = {(q['ServiceCode'], q['QuotaCode']): q for q in quotas}
        self.cache = {}
        self.clients = {}

    def client(self, service):
        if service not in self.clients:
            self.clients[service] = self.session.client(service, config=CONFIG)
        return self.clients[service]

    def call(self, service, method, key=None, **kwargs):
        # default=str keeps datetimes usable as arguments; several APIs take a
        # time window and the key only has to be stable, not round-trippable.
        cache_key = (service, method, key,
                     json.dumps(kwargs, sort_keys=True, default=str))
        if cache_key not in self.cache:
            try:
                client = self.client(service)
                self.cache[cache_key] = (paginate(client, method, key, **kwargs) if key
                                         else getattr(client, method)(**kwargs))
            except Exception as exc:
                self.cache[cache_key] = exc
        value = self.cache[cache_key]
        if isinstance(value, Exception):
            raise value
        return value

    def run(self, service, checks, skip=()):
        results = []
        for code, name, fn in checks:
            if (service, code) in skip:
                continue
            quota = self.quotas.get((service, code), {})
            limit = quota.get('Value')
            try:
                kwargs = fn(self)
                if not quota:
                    quota = self.call('service-quotas', 'get_service_quota',
                                      ServiceCode=service, QuotaCode=code)['Quota']
                    limit = quota.get('Value')
                if quota.get('ErrorReason'):
                    raise RuntimeError(f"Service Quotas error: {quota['ErrorReason']}")
                # Checks can provide a documented, API-native limit/unit (Lambda bytes).
                kwargs.setdefault('limit', limit)
                kwargs.setdefault('unit', quota.get('Unit') if quota.get('Unit') not in {None, 'None'} else 'Count')
                result = measurement(self.account, self.region, service, code, name,
                                     now=self.now, **kwargs)
            except (Unsupported, NoData) as exc:
                result = measurement(self.account, self.region, service, code, name, limit,
                                     now=self.now, status='UNSUPPORTED' if isinstance(exc, Unsupported) else 'NO_DATA',
                                     reason=str(exc), unit=quota.get('Unit', 'Count'))
            except ClientError as exc:
                unavailable = exc.response['Error']['Code'] in {'NoSuchResourceException', 'NoSuchResource'}
                status = 'UNSUPPORTED' if unavailable else not_set_up(exc, service) or 'ERROR'
                result = measurement(self.account, self.region, service, code, name, limit,
                                     now=self.now, status=status,
                                     reason=str(exc), unit=quota.get('Unit', 'Count'))
            except Exception as exc:
                result = measurement(self.account, self.region, service, code, name, limit,
                                     now=self.now, status='ERROR', reason=f'{type(exc).__name__}: {exc}',
                                     unit=quota.get('Unit', 'Count'))
            results.append(result)
        return results


def maximum(values, resource_type, source='resource_check'):
    # values: (resource ID, usage, metadata); full inventory must already be available.
    rid, usage, meta = max(values, key=lambda value: value[1], default=(None, 0, None))
    return dict(usage=usage, resource_type=resource_type, resource_id=rid,
                meta=meta, source=source, method='PER_RESOURCE_MAX')
