#!/usr/bin/env bash
# Scan only version-controlled/eligible source, never local state or AWS exports.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
scan_dir=$(mktemp -d)
cache_dir="${RUNNER_TEMP:-${TMPDIR:-/tmp}}/aws-quota-monitor-trivy-cache"
mkdir -p "$cache_dir"
trap 'rm -rf "$scan_dir"' EXIT
git ls-files -z --cached --others --exclude-standard |
  tar --null -T - -cf - | tar -xf - -C "$scan_dir"
scanner='aquasec/trivy:0.74.0@sha256:62b1e65e8869bc4b4c6aa4fa2b21595256c7c2f6018a9d9ad61caf87187c1969'
# JSON is summarized without matched secret values or source snippets.
if ! report=$(docker run --rm -v "$scan_dir:/source:ro" -v "$cache_dir:/root/.cache/trivy" "$scanner" --quiet fs \
  --scanners vuln,secret,misconfig --severity HIGH,CRITICAL \
  --format json --ignorefile /source/.trivyignore.yaml /source); then
  printf 'Security scanner could not complete.\n' >&2
  exit 1
fi
printf '%s' "$report" | python3 scripts/security_summary.py
