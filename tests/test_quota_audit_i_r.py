import json
from pathlib import Path

from modules.qmcore.registry import custom_keys


def test_i_r_audit_lists_every_open_catalog_quota():
    catalog = json.loads(Path('tests/fixtures/service-quota-keys.json').read_text())
    registered = custom_keys()
    document = Path('docs/quota-audit-i-r.md').read_text()
    seen = set()
    for quota in catalog:
        service = quota.get('serviceCode', '')
        key = (service, quota.get('quotaCode'))
        if 'i' <= service[:1].lower() <= 'r' and key not in registered:
            seen.add(key)
            assert f'## `{service}`' in document
            assert f'`{quota["quotaCode"]}`' in document
    assert seen
