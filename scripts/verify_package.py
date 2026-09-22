"""Offline check of the deployable ZIP and isolated dependency layer."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    layer = ROOT / 'deployment/lambda_layer.zip'
    if not layer.is_file():
        raise SystemExit('Build deployment/lambda_layer.zip first')
    with tempfile.TemporaryDirectory() as temp:
        temp = Path(temp)
        source_zip = temp / 'function.zip'
        with zipfile.ZipFile(source_zip, 'w') as archive:
            for file in sorted((ROOT / 'src').rglob('*.py')):
                if '__pycache__' not in file.parts:
                    archive.write(file, file.relative_to(ROOT / 'src'))
        with zipfile.ZipFile(layer) as archive:
            assert not any(name.endswith(('.so', '.dylib')) for name in archive.namelist()), 'Review native architecture before release'
            archive.extractall(temp / 'layer')
        program = '''
import importlib, pathlib, sys
sys.path[:0] = sys.argv[1:]
for module in ('functions.quota-collector.main', 'functions.reporting.main', 'qm-quotalist.main', 'qmreport.report'):
    importlib.import_module(module)
import boto3, botocore
assert 'layer' in boto3.__file__ and 'layer' in botocore.__file__
print('Package imports passed using only the built layer and function ZIP')
'''
        subprocess.run([sys.executable, '-S', '-c', program, str(source_zip), str(temp/'layer/python')],
                       check=True, cwd=temp, env={**os.environ, 'AWS_EC2_METADATA_DISABLED': 'true'})


if __name__ == '__main__':
    main()
