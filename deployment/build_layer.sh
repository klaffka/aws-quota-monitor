#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
BUILD_PYTHON="${QM_BUILD_PYTHON:-python3}"
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT
"$BUILD_PYTHON" -m pip install --disable-pip-version-check --no-compile \
  --only-binary=:all: --platform manylinux2014_x86_64 --implementation cp \
  --python-version 3.14 --abi cp314 --no-deps \
  -r ../requirements.txt --target "$BUILD_DIR/python"
"$BUILD_PYTHON" - "$BUILD_DIR" <<'PY'
import csv
import io
import pathlib
import sys
import zipfile

root = pathlib.Path(sys.argv[1])
# Fixed timestamps and stable ordering make the same wheels produce the same ZIP.
with zipfile.ZipFile('lambda_layer.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(root.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
            if path.relative_to(root).parts[:2] == ('python', 'bin'):
                continue  # Optional CLIs have host-specific interpreter paths.
            if path.parent.name == 'yaml' and path.name.startswith('_yaml.') and path.suffix in {'.so', '.dylib'}:
                continue  # PyYAML's optional accelerator; SafeLoader has a pure-Python fallback.
            content = path.read_bytes()
            if path.name == 'RECORD':
                rows = csv.reader(io.StringIO(content.decode('utf-8')))
                output = io.StringIO(newline='')
                csv.writer(output).writerows(row for row in rows if not row[0].startswith('../../bin/'))
                content = output.getvalue().encode('utf-8')
            info = zipfile.ZipInfo(path.relative_to(root).as_posix(), (2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, content)
PY
