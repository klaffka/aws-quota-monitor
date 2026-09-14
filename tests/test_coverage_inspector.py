import json

from scripts.coverage_inspector import coverage_percentages, latest_snapshots, load_items, render_table


def test_latest_snapshots_filters_non_coverage_and_selects_per_scope(tmp_path):
    path = tmp_path / "items.json"
    path.write_text(json.dumps({"Items": [
        {"PK": "QUOTA#account#region", "SK": "TS#1"},
        {"PK": "COVERAGE#account#region", "SK": "TS#2026-01-01", "ok": 1},
        {"PK": "COVERAGE#account#region", "SK": "TS#2026-01-02", "ok": 2},
        {"PK": "COVERAGE#other#r2", "SK": "TS#2026-01-01", "ok": 3},
    ]}), encoding="utf-8")

    snapshots = latest_snapshots(load_items(str(path)))

    assert [item["ok"] for item in snapshots] == [2, 3]


def test_json_lines_and_table_output(tmp_path):
    path = tmp_path / "items.jsonl"
    path.write_text(
        '{"PK":"COVERAGE#a#r","SK":"TS#1","totalCatalog":4,"measured":3,"ok":2,"unsupported":1,"noData":0,"errors":0}\n',
        encoding="utf-8",
    )
    items = latest_snapshots(load_items(str(path)))
    output = render_table(items)
    assert "Catalog" in output
    assert "a#r" in output
    assert "4" in output
    assert "75.0%" in output


def test_coverage_percentages_are_display_only_and_handle_empty_catalog():
    assert coverage_percentages({"totalCatalog": 4, "measured": 3, "ok": 2}) == {
        "measured": "75.0%", "ok": "50.0%"
    }
    assert coverage_percentages({"totalCatalog": 0, "measured": 0, "ok": 0}) == {
        "measured": "-", "ok": "-"
    }


def test_table_keeps_percentages_independent_for_mixed_snapshots():
    snapshots = latest_snapshots([
        {"PK": "COVERAGE#a#eu", "SK": "TS#2", "totalCatalog": 10,
         "measured": 8, "ok": 7, "unsupported": 1, "noData": 1, "errors": 0},
        {"PK": "COVERAGE#b#us", "SK": "TS#2", "totalCatalog": 4,
         "measured": 1, "ok": 1, "unsupported": 2, "noData": 1, "errors": 0},
    ])

    output = render_table(snapshots)

    assert "80.0%" in output and "70.0%" in output
    assert "25.0%" in output, "the second scope must not reuse the first denominator"
