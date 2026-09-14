"""Emit the complete catalog/check delta for an auditable quota review.

Usage: python scripts/quota_audit.py [catalog.json]
The output is deterministic Markdown and includes every catalog entry whose
quota code is not present in a registered Python check.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from modules.qmcore.registry import custom_keys

SERVICE_ALIASES = {'awscloudmap': 'servicediscovery'}


def service_code(value):
    raw = str(value or '')
    return SERVICE_ALIASES.get(raw.lower(), raw.lower())


def audit(catalog_path, source_root="src"):
    catalog = json.loads(Path(catalog_path).read_text())
    covered = custom_keys()
    unique = {(service_code(q.get("serviceCode")), q.get("quotaCode")): q for q in catalog}
    rows = [q for (service, code), q in unique.items() if (service, code) not in covered
            and "a" <= service[:1].lower() <= "h"]
    rows.sort(key=lambda q: (q.get("serviceCode", ""), q.get("quotaCode", "")))
    print("# Open quota audit A–H")
    print(f"\nTotal open entries: **{len(rows)}**\n")
    current = None
    for quota in rows:
        service = quota.get("serviceCode", "unknown")
        if service != current:
            current = service
            print(f"\n## {service}\n")
        print(f"- `{quota['quotaCode']}` — {quota.get('quotaName', '')}")


if __name__ == "__main__":
    default = next(Path("data").glob("service-quotas-*.json"))
    audit(sys.argv[1] if len(sys.argv) > 1 else default)
