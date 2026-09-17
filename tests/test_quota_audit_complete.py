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


def test_audit_documents_list_nothing_that_is_already_measured():
    """The completeness assertion above only pushes one way: it fails when an
    open quota is missing from the documents, never when a documented one has
    since been measured. Those entries stayed listed as work to do, and the
    documents are the candidate pool a coverage session mines, so 1,373 of the
    7,735 entries had become false leads before this caught them."""
    registered = custom_keys()
    documented = {}
    for path in sorted(Path("docs").glob("quota-audit-*.md")):
        for pair in _documented_pairs(path):
            documented.setdefault(pair, path.name)
    measured = {f"{path}: {service}:{code}"
                for (service, code), path in documented.items()
                if (service, code) in registered}
    assert not measured, f"measured quotas still listed as open: {sorted(measured)[:10]}"
