# Releasing AWS Quota Monitor

Releases use semantic versions in the form `MAJOR.MINOR.PATCH`. Increment:

- `MAJOR` for incompatible configuration, state, or behavior changes.
- `MINOR` for backward-compatible functionality and quota coverage.
- `PATCH` for backward-compatible fixes.

`VERSION` contains the next development or release version. Development versions may
use a SemVer prerelease suffix such as `0.2.0-dev.0`; published tags are stable versions
such as `v0.2.0`.

## Prepare a release

Keep user-visible changes under `CHANGELOG.md` → `[Unreleased]`. When the release is
ready, run:

```bash
python scripts/release.py prepare 0.1.0
python scripts/release.py check-tag v0.1.0
git diff -- VERSION CHANGELOG.md
```

The prepare command rejects invalid versions, duplicate changelog sections, and empty
release notes. It writes the current date, moves all Unreleased notes into the new
version section, and updates `VERSION`.

Commit the prepared metadata with the release changes. Let CI pass on that commit, then
create and push an annotated tag pointing to that exact commit:

```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

The tag starts `.github/workflows/release.yml`. The workflow calls the complete CI
workflow again against the tagged commit, validates that tag, `VERSION`, and changelog
agree, and only then creates the GitHub release. Release notes come from the matching
changelog section. Assets include the verified Lambda dependency layer and its SHA-256
checksum; GitHub also supplies source archives for the tagged commit.

The release workflow does not apply Terraform or invoke AWS APIs. Deployment remains a
separate, reviewed operation; see [deploying.md](deploying.md).

After a release, set `VERSION` to the next intended development version, for example
`0.2.0-dev.0`, and commit that change.
