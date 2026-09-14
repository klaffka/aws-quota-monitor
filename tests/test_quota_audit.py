from pathlib import Path

from scripts.quota_audit import audit


def test_quota_audit_deduplicates_catalog_and_limits_to_a_h(tmp_path, capsys):
    catalog = tmp_path / 'catalog.json'
    catalog.write_text('[{"serviceCode":"alpha","quotaCode":"L-OPEN","quotaName":"Count"},'
                       '{"serviceCode":"alpha","quotaCode":"L-OPEN","quotaName":"Count"},'
                       '{"serviceCode":"zulu","quotaCode":"L-ZULU","quotaName":"Count"}]')
    audit(catalog, source_root=tmp_path)
    output = capsys.readouterr().out
    assert 'Total open entries: **1**' in output
    assert '`L-OPEN`' in output
    assert 'L-ZULU' not in output
