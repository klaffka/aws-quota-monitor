"""Daily, account/region-specific catalog snapshots. Publish only complete snapshots."""
from uuid import uuid4
from boto3.dynamodb.conditions import Key
from modules.qmcore.aws import paginate

CATALOG_VERSION = 1


def _annotate(quota, level="ACCOUNT"):
    quota = dict(quota)
    quota.setdefault("QuotaAppliedAtLevel", level)
    context = quota.get("QuotaContext") or {}
    quota["catalogContextId"] = context.get("ContextId")
    quota["catalogKey"] = "#".join(str(value) for value in (
        quota.get("ServiceCode"), quota.get("QuotaCode"),
        quota.get("QuotaAppliedAtLevel"), context.get("ContextId", "ACCOUNT")))
    return quota


def fetch_catalog(client):
    quotas, errors = [], []
    services = paginate(client, 'list_services', 'Services')
    if not services:
        raise RuntimeError('Service Quotas returned no services')
    for service in services:
        code = service['ServiceCode']
        try:
            # ALL preserves resource-level entries where AWS exposes a context.
            items = paginate(client, 'list_service_quotas', 'Quotas',
                             ServiceCode=code, QuotaAppliedAtLevel='ALL')
            items = [_annotate(item) for item in items]
            quotas.extend(items)
            for quota in items:
                if quota.get('ErrorReason'):
                    errors.append(f"catalog:{code}/{quota['QuotaCode']}: {quota['ErrorReason']}")
        except Exception as exc:
            errors.append(f'catalog:{code}: {exc}')
    return quotas, errors


def account_catalog(quotas):
    """Select one account-level quota per service/code for existing collectors."""
    selected = {}
    for quota in quotas:
        key = (quota.get("ServiceCode"), quota.get("QuotaCode"))
        current = selected.get(key)
        if current is None or (quota.get("QuotaAppliedAtLevel") == "ACCOUNT" and
                               current.get("QuotaAppliedAtLevel") != "ACCOUNT"):
            selected[key] = quota
    return list(selected.values())


def get_catalog(ctx, db, force=False):
    pk = f'CATALOG#{ctx.account}#{ctx.region}'
    pointer = db.get_quota_entry(pk, 'LATEST')
    now = int(ctx.now.timestamp())
    if pointer and not force:
        try:
            fresh = (pointer.get('catalogVersion') == CATALOG_VERSION and
                     0 <= now - int(pointer['refreshedAt']) < 86400 and
                     isinstance(pointer['generation'], str) and bool(pointer['generation']))
            if fresh:
                kwargs = {'KeyConditionExpression': Key('PK').eq(pk) & Key('SK').begins_with(pointer['generation'] + '#'),
                          'ConsistentRead': True}
                items = []
                while True:
                    page = db.table.query(**kwargs)
                    items.extend(item['quota'] for item in page.get('Items', [])
                                 if isinstance(item.get('quota'), dict))
                    if not page.get('LastEvaluatedKey'):
                        break
                    kwargs['ExclusiveStartKey'] = page['LastEvaluatedKey']
                if len(items) == int(pointer['count']) and all(
                        q.get('ServiceCode') and q.get('QuotaCode') for q in items):
                    return items, []
        except (KeyError, TypeError, ValueError):
            # Treat malformed or legacy pointers as stale and rebuild safely.
            pass
    quotas, errors = fetch_catalog(ctx.client('service-quotas'))
    if not errors:
        generation = uuid4().hex
        with db.table.batch_writer() as writer:
            for q in quotas:
                writer.put_item(Item=db._to_dynamodb_compatible({
                    'PK': pk, 'SK': f"{generation}#{q['ServiceCode']}#{q['QuotaCode']}",
                    'quota': q, 'ttl': now + 3 * 86400}))
        db.put_quota_entry({'PK': pk, 'SK': 'LATEST', 'generation': generation,
                            'count': len(quotas), 'refreshedAt': now,
                            'catalogVersion': CATALOG_VERSION})
    return quotas, errors
