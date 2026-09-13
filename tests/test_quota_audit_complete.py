import json
import re
from pathlib import Path

from modules.qmcore.registry import custom_keys
from scripts.quota_audit import service_code


def _documented_pairs(path):
    pairs = set()
    service = None
    for line in Path(path).read_text().splitlines():
        match = re.match(r"^##+ `?([^` (]+)`?(?: \(|$)", line)
        if match:
            service = match.group(1)
            continue
        match = re.match(r"^(?:\||-)\s*`(L-[A-Z0-9]+)`", line)
        if match and service:
            pairs.add((service, match.group(1)))
    return pairs


def test_audit_documents_cover_every_open_catalog_quota():
    catalog = json.loads(Path("tests/fixtures/service-quota-keys.json").read_text())
    registered = custom_keys()
    registered_codes = {code for _, code in registered}
    open_pairs = {
        (service_code(q.get("serviceCode")), q.get("quotaCode"))
        for q in catalog
        if q.get("quotaCode") not in registered_codes
    }
    documented = set()
    for path in Path("docs").glob("quota-audit-*.md"):
        documented |= _documented_pairs(path)
    missing = open_pairs - documented
    assert not missing, f"undocumented open quotas: {sorted(missing)[:10]}"
