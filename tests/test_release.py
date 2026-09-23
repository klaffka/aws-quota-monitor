import re
from datetime import date
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("release_script", ROOT / "scripts/release.py")
release = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(release)


def write_metadata(root, version="0.1.0-dev.0", notes="### Added\n\n- A change."):
    (root / "VERSION").write_text(version + "\n", encoding="utf-8")
    (root / "CHANGELOG.md").write_text(
        f"# Changelog\n\n## [Unreleased]\n\n{notes}\n", encoding="utf-8"
    )


@pytest.mark.parametrize(
    "version",
    ["1.0.0", "0.1.0-dev.1", "2.3.4+build.7", "2.3.4-rc.1+build.7"],
)
def test_validate_version_accepts_semver(version):
    assert release.validate_version(version) == version


@pytest.mark.parametrize("version", ["v1.0.0", "1.0", "01.0.0", "1.0.0-"])
def test_validate_version_rejects_invalid_values(version):
    with pytest.raises(release.ReleaseError):
        release.validate_version(version)


def test_prepare_release_updates_version_and_moves_notes(tmp_path):
    write_metadata(tmp_path)

    release.prepare_release(tmp_path, "0.1.0", date(2026, 9, 13))

    assert (tmp_path / "VERSION").read_text(encoding="utf-8") == "0.1.0\n"
    changelog = (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [Unreleased]\n\n<!-- Add release notes here. -->" in changelog
    assert "## [0.1.0] - 2026-09-13\n\n### Added\n\n- A change." in changelog
    assert release.check_tag(tmp_path, "v0.1.0") == "0.1.0"
    assert release.release_notes(tmp_path, "0.1.0") == (
        "## 0.1.0 (2026-09-13)\n\n### Added\n\n- A change.\n"
    )


def test_check_tag_rejects_a_mismatched_tag(tmp_path):
    write_metadata(tmp_path, version="1.2.3")
    with pytest.raises(release.ReleaseError, match=re.escape("expected 'v1.2.3'")):
        release.check_tag(tmp_path, "v1.2.4")


def test_prepare_release_requires_real_notes(tmp_path):
    write_metadata(tmp_path, notes=release.PLACEHOLDER)
    with pytest.raises(release.ReleaseError, match="at least one bullet"):
        release.prepare_release(tmp_path, "0.1.0", date(2026, 9, 13))


def test_check_rejects_duplicate_changelog_sections(tmp_path):
    write_metadata(tmp_path)
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        changelog.read_text(encoding="utf-8") + "\n## [Unreleased]\n\n- Again.\n",
        encoding="utf-8",
    )
    with pytest.raises(release.ReleaseError, match=r"duplicate \[Unreleased]"):
        release.check_repository(tmp_path)


def test_check_rejects_invalid_release_dates(tmp_path):
    write_metadata(tmp_path)
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        changelog.read_text(encoding="utf-8")
        + "\n## [0.0.1] - 2026-99-99\n\n### Fixed\n\n- A fix.\n",
        encoding="utf-8",
    )
    with pytest.raises(release.ReleaseError, match="invalid release date"):
        release.check_repository(tmp_path)
