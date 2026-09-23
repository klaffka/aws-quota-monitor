"""Account-level quota APIs that return both usage and limit directly.

RDS and DMS expose ``DescribeAccountAttributes``. IAM exposes the equivalent
``GetAccountSummary`` API. Keeping these checks here avoids guessing usage from
resource listings and makes permission failures visible per quota.
"""
import re

from modules.qmcore.model import measurement, number


def _key(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def _catalog_by_name(ctx, service):
    return {_key(q.get("QuotaName")): q for (svc, _), q in ctx.quotas.items()
            if svc == service and q.get("QuotaName")}


def _account_quota_entries(ctx, service, response_key, skip=()):
    catalog = _catalog_by_name(ctx, service)
    response = ctx.call(service, "describe_account_attributes")
    entries = []
    for item in response.get(response_key, []):
        name = item.get("AccountQuotaName")
        quota = catalog.get(_key(name))
        if not quota:
            # AWS occasionally spells the same quota differently between APIs.
            quota = next((q for q in catalog.values()
                          if _key(q.get("QuotaName", "")) in _key(name)
                          or _key(name) in _key(q.get("QuotaName", ""))), None)
        if not quota:
            continue
        if (service, quota['QuotaCode']) in skip:
            continue
        limit, usage = number(item.get("Max")), number(item.get("Used"))
        entries.append(measurement(
            ctx.account, ctx.region, service, quota["QuotaCode"], quota["QuotaName"],
            limit, usage, now=ctx.now, unit=quota.get("Unit") or "Count",
            source=f"{service}:DescribeAccountAttributes", method="ACCOUNT_QUOTA_API",
            meta={"apiQuotaName": name}))
    return entries


def _iam_entries(ctx):
    summary = ctx.call("iam", "get_account_summary").get("SummaryMap", {})
    entries = []
    # IAM is account-global and does not appear in ListServiceQuotas in many
    # regions. Pair e.g. Users with UsersQuota and emit a stable synthetic code.
    for quota_key, limit in summary.items():
        if not quota_key.endswith("Quota") or number(limit) is None:
            continue
        usage_key = quota_key[:-5]
        usage = number(summary.get(usage_key))
        if usage is None:
            continue
        entries.append(measurement(
            ctx.account, ctx.region, "iam", f"IAM-{quota_key}", quota_key[:-5],
            limit, usage, now=ctx.now, unit="Count", source="iam:GetAccountSummary",
            method="ACCOUNT_QUOTA_API", meta={"usageKey": usage_key, "global": True}))
    return entries


def get_current_quotastatus_account_services(ctx, skip=()):
    entries = []
    # Each API is isolated so RDS permissions do not hide DMS or IAM values.
    for service, key in (("rds", "AccountQuotas"), ("dms", "AccountQuotas")):
        try:
            entries.extend(_account_quota_entries(ctx, service, key, skip))
        except Exception as exc:
            for (svc, code), quota in ctx.quotas.items():
                if svc == service and (svc, code) not in skip:
                    entries.append(measurement(
                        ctx.account, ctx.region, service, code, quota.get("QuotaName", code),
                        quota.get("Value"), None, now=ctx.now, status="ERROR",
                        reason=f"{type(exc).__name__}: {exc}", unit=quota.get("Unit") or "Count",
                        source=f"{service}:DescribeAccountAttributes", method="ACCOUNT_QUOTA_API"))
    try:
        entries.extend(_iam_entries(ctx))
    except Exception as exc:
        entries.append(measurement(ctx.account, ctx.region, "iam", "IAM-ACCOUNT-SUMMARY",
                                   "IAM account summary", None, None, now=ctx.now,
                                   status="ERROR", reason=f"{type(exc).__name__}: {exc}",
                                   unit="Count", source="iam:GetAccountSummary",
                                   method="ACCOUNT_QUOTA_API"))
    return entries
