"""Every service name a check passes to ctx.call must be a real SDK client.

A wrong name (`cassandra` for Keyspaces, `elasticfilesystem` for EFS) raises
UnknownServiceError at runtime only, so the check reports an error every run
while its tests keep passing against a Mock.
"""
import ast
from pathlib import Path

import boto3
import pytest

# These services were retired from botocore. Their checks route through
# sdk_call, which reports the absence as UNSUPPORTED rather than an error.
RETIRED = {'evidently', 'iotanalytics', 'iotevents', 'qldb', 'robomaker'}
CHECKS = Path('src/modules/qmchecks')


def service_names(path):
    """Collect the literal service names a module passes to call or client."""
    tree = ast.parse(path.read_text(encoding='utf-8'))
    constants = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    constants[target.id] = node.value.value
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in {'call', 'client'} and node.args:
            first = node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                found.add(first.value)
            elif isinstance(first, ast.Name) and first.id in constants:
                found.add(constants[first.id])
    return found


@pytest.mark.parametrize('path', sorted(CHECKS.glob('*.py')), ids=lambda p: p.stem)
def test_every_called_service_has_an_sdk_client(path):
    available = set(boto3.Session(region_name='eu-central-1').get_available_services())
    unknown = service_names(path) - available - RETIRED
    assert not unknown, f'{path.name} calls clients botocore does not ship: {unknown}'


def test_retired_services_are_still_listed_as_retired():
    """If botocore restores one, drop it from RETIRED and from sdk_call."""
    available = set(boto3.Session(region_name='eu-central-1').get_available_services())
    assert not RETIRED & available
