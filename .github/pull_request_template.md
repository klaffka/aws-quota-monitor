## Change

Describe the behavior that changes and why.

## Validation

Listed in the order CI runs them, so working down this list reproduces
`.github/workflows/ci.yml` locally.

- [ ] `docker run --rm -v "${PWD}:/repo" --workdir /repo rhysd/actionlint:1.7.12 -color`
- [ ] `python -m pip check`
- [ ] `python scripts/release.py check`
- [ ] `ruff check src tests scripts`
- [ ] `python -m compileall -q src tests scripts`
- [ ] `python -m pytest -q`
- [ ] `python scripts/quota_coverage.py tests/fixtures/quota-catalog-union.json --baseline tests/fixtures/coverage-baseline.json`
- [ ] `bash deployment/build_layer.sh && python scripts/verify_package.py`
- [ ] `terraform -chdir=deployment init -backend=false -lockfile=readonly`, then:
- [ ] `terraform -chdir=deployment fmt -check -recursive`
- [ ] `terraform -chdir=deployment validate`
- [ ] User-visible changes are documented under `CHANGELOG.md` → `Unreleased`
