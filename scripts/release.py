#!/usr/bin/env python3
"""Prepare and validate semantic releases from VERSION and CHANGELOG.md."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
import sys


SEMVER = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
HEADING = re.compile(r"^## \[([^]]+)](?: - (\d{4}-\d{2}-\d{2}))?$", re.MULTILINE)
PLACEHOLDER = "<!-- Add release notes here. -->"


class ReleaseError(ValueError):
    """A release invariant was violated."""


def validate_version(version: str, *, stable: bool = False) -> str:
    """Return a normalized semantic version or raise a readable error."""
    version = version.strip()
    match = SEMVER.fullmatch(version)
    if not match:
        raise ReleaseError(f"Invalid semantic version: {version!r}")
    if stable and (match.group(4) or match.group(5)):
        raise ReleaseError("Published releases must use MAJOR.MINOR.PATCH without suffixes")
    return version


def read_version(root: Path) -> str:
    path = root / "VERSION"
    if not path.is_file():
        raise ReleaseError(f"Missing {path}")
    return validate_version(path.read_text(encoding="utf-8"))


def changelog_sections(text: str) -> dict[str, tuple[str | None, str]]:
    """Return changelog sections keyed by their bracketed heading."""
    headings = list(HEADING.finditer(text))
    sections: dict[str, tuple[str | None, str]] = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        name = heading.group(1)
        if name in sections:
            raise ReleaseError(f"CHANGELOG.md contains duplicate [{name}] sections")
        sections[name] = (heading.group(2), text[heading.end() : end].strip())
    return sections


def meaningful_notes(body: str) -> bool:
    cleaned = body.replace(PLACEHOLDER, "").strip()
    return any(line.lstrip().startswith("- ") for line in cleaned.splitlines())


def check_repository(root: Path) -> str:
    """Validate development-time version and changelog invariants."""
    version = read_version(root)
    changelog = root / "CHANGELOG.md"
    if not changelog.is_file():
        raise ReleaseError(f"Missing {changelog}")
    sections = changelog_sections(changelog.read_text(encoding="utf-8"))
    if "Unreleased" not in sections:
        raise ReleaseError("CHANGELOG.md must contain an [Unreleased] section")
    if sections["Unreleased"][0] is not None:
        raise ReleaseError("CHANGELOG.md [Unreleased] must not have a date")
    for name, (release_date, body) in sections.items():
        if name == "Unreleased":
            continue
        validate_version(name, stable=True)
        if release_date is None:
            raise ReleaseError(f"CHANGELOG.md [{name}] must include a release date")
        try:
            date.fromisoformat(release_date)
        except ValueError as error:
            raise ReleaseError(f"CHANGELOG.md [{name}] has an invalid release date") from error
        if not meaningful_notes(body):
            raise ReleaseError(f"CHANGELOG.md [{name}] has no release notes")
    return version


def check_tag(root: Path, tag: str) -> str:
    """Validate a stable release tag against VERSION and its changelog entry."""
    check_repository(root)
    version = validate_version(read_version(root), stable=True)
    expected = f"v{version}"
    if tag != expected:
        raise ReleaseError(f"Tag {tag!r} does not match VERSION; expected {expected!r}")
    sections = changelog_sections((root / "CHANGELOG.md").read_text(encoding="utf-8"))
    if version not in sections:
        raise ReleaseError(f"CHANGELOG.md has no [{version}] release section")
    release_date, body = sections[version]
    if release_date is None:
        raise ReleaseError(f"CHANGELOG.md [{version}] must include a release date")
    if not meaningful_notes(body):
        raise ReleaseError(f"CHANGELOG.md [{version}] has no release notes")
    return version


def release_notes(root: Path, version: str) -> str:
    """Extract one version section as a standalone release note document."""
    version = validate_version(version, stable=True)
    sections = changelog_sections((root / "CHANGELOG.md").read_text(encoding="utf-8"))
    if version not in sections:
        raise ReleaseError(f"CHANGELOG.md has no [{version}] release section")
    release_date, body = sections[version]
    if release_date is None or not meaningful_notes(body):
        raise ReleaseError(f"CHANGELOG.md [{version}] is incomplete")
    return f"## {version} ({release_date})\n\n{body}\n"


def prepare_release(root: Path, version: str, release_date: date) -> None:
    """Move Unreleased notes into a dated release section and update VERSION."""
    version = validate_version(version, stable=True)
    changelog_path = root / "CHANGELOG.md"
    text = changelog_path.read_text(encoding="utf-8")
    sections = changelog_sections(text)
    if version in sections:
        raise ReleaseError(f"CHANGELOG.md already contains [{version}]")
    if "Unreleased" not in sections:
        raise ReleaseError("CHANGELOG.md must contain an [Unreleased] section")
    _, body = sections["Unreleased"]
    if not meaningful_notes(body):
        raise ReleaseError("Add at least one bullet to [Unreleased] before preparing a release")

    heading = re.search(r"^## \[Unreleased]$", text, re.MULTILINE)
    assert heading is not None
    next_heading = HEADING.search(text, heading.end())
    section_end = next_heading.start() if next_heading else len(text)
    replacement = (
        "## [Unreleased]\n\n"
        f"{PLACEHOLDER}\n\n"
        f"## [{version}] - {release_date.isoformat()}\n\n"
        f"{body}\n\n"
    )
    updated = text[: heading.start()] + replacement + text[section_end:].lstrip("\n")
    changelog_path.write_text(updated.rstrip() + "\n", encoding="utf-8")
    (root / "VERSION").write_text(version + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="validate VERSION and changelog structure")
    tagged = commands.add_parser("check-tag", help="validate a release tag")
    tagged.add_argument("tag")
    prepare = commands.add_parser("prepare", help="move Unreleased notes into a release")
    prepare.add_argument("version")
    prepare.add_argument("--date", type=date.fromisoformat, default=date.today())
    notes = commands.add_parser("notes", help="extract notes for one release")
    notes.add_argument("version")
    notes.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "check":
            version = check_repository(root)
            print(f"Version metadata is valid: {version}")
        elif args.command == "check-tag":
            version = check_tag(root, args.tag)
            print(f"Release tag is valid: v{version}")
        elif args.command == "prepare":
            prepare_release(root, args.version, args.date)
            print(f"Prepared release v{args.version}")
        elif args.command == "notes":
            notes = release_notes(root, args.version)
            if args.output:
                args.output.write_text(notes, encoding="utf-8")
            else:
                print(notes, end="")
    except (OSError, ReleaseError) as error:
        print(f"release: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
