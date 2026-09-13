## Change

Describe the behavior that changes and why.

## Validation

- [ ] `ruff check src tests scripts`
- [ ] `python -m pytest -q`
- [ ] `bash deployment/build_layer.sh && python scripts/verify_package.py`
- [ ] `terraform -chdir=deployment fmt -check -recursive`
- [ ] `terraform -chdir=deployment validate`
- [ ] User-visible changes are documented under `CHANGELOG.md` → `Unreleased`
