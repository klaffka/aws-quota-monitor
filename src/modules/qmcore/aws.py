"""AWS context and all-or-error paginated inventories, cached within one run."""
import os
import json
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from modules.qmcore.model import measurement, utcnow

CONFIG = Config(retries={'mode': 'adaptive', 'max_attempts': 8},
                connect_timeout=5, read_timeout=30)


class Unsupported(ValueError):
    pass


class NoData(ValueError):
    pass


def session_from_env():
    return boto3.Session(profile_name=os.getenv('QM_AWS_PROFILE') or os.getenv('AWS_PROFILE'),
                         region_name=os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION'))


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
                 or page.get('Marker') or page.get('position'))
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
        cache_key = (service, method, key, json.dumps(kwargs, sort_keys=True))
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
                result = measurement(self.account, self.region, service, code, name, limit,
                                     now=self.now, status='UNSUPPORTED' if unavailable else 'ERROR',
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
