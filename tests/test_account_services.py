from datetime import datetime, timezone
from unittest.mock import Mock

from modules.qmchecks.account_services import (
    _account_quota_entries,
    _iam_entries,
    get_current_quotastatus_account_services,
)
from modules.qmcore.aws import CheckContext


NOW = datetime(2026, 3, 1, tzinfo=timezone.utc)


def context(quotas):
    session = Mock(region_name="eu-central-1")
    ctx = CheckContext(session, account="123456789012", now=NOW, quotas=quotas)
    ctx.call = Mock()
    return ctx


def test_rds_account_attributes_preserve_usage_and_applied_limit():
    ctx = context([{
        "ServiceCode": "rds", "QuotaCode": "L-7B6409FD",
        "QuotaName": "DB instances", "Value": 80, "Unit": "None",
    }])
    ctx.call.return_value = {"AccountQuotas": [{
        "AccountQuotaName": "DBInstances", "Used": 12, "Max": 80,
    }]}
    entries = _account_quota_entries(ctx, "rds", "AccountQuotas")
    assert len(entries) == 1
    assert entries[0]["usageValue"] == 12
    assert entries[0]["limitValue"] == 80
    assert entries[0]["qualityStatus"] == "OK"


def test_dms_and_rds_permissions_are_isolated():
    ctx = context([{
        "ServiceCode": "rds", "QuotaCode": "rds-code", "QuotaName": "DB instances", "Value": 40,
    }, {
        "ServiceCode": "dms", "QuotaCode": "dms-code", "QuotaName": "Replication instances", "Value": 20,
    }])
    ctx.call.side_effect = [RuntimeError("AccessDenied"), {"AccountQuotas": [{
        "AccountQuotaName": "ReplicationInstances", "Used": 2, "Max": 20,
    }]}]
    entries = get_current_quotastatus_account_services(ctx)
    by_service = {entry["serviceCode"]: entry for entry in entries}
    assert by_service["rds"]["qualityStatus"] == "ERROR"
    assert by_service["dms"]["qualityStatus"] == "OK"


def test_iam_summary_pairs_usage_and_quota_keys():
    ctx = context([])
    ctx.call.return_value = {"SummaryMap": {
        "Users": 8, "UsersQuota": 10,
        "Roles": 3, "RolesQuota": 5,
        "AccountMFAEnabled": 1,
    }}
    entries = _iam_entries(ctx)
    assert {(e["quotaCode"], e["usageValue"], e["limitValue"]) for e in entries} == {
        ("IAM-UsersQuota", 8, 10), ("IAM-RolesQuota", 3, 5)
    }
    assert all(e["maxResourceMeta"]["global"] for e in entries)


def test_iam_failure_is_explicit():
    ctx = context([])
    ctx.call.side_effect = RuntimeError("Throttling")
    entries = get_current_quotastatus_account_services(ctx)
    result = [entry for entry in entries if entry["serviceCode"] == "iam"][0]
    assert result["qualityStatus"] == "ERROR"
    assert result["utilizationPct"] is None
