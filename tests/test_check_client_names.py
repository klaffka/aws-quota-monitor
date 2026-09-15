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


def _literals(tree):
    """Map module-level string constants, which name most services."""
    constants = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    constants[target.id] = node.value.value
    return constants


def _value(node, constants):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return constants.get(node.id)
    return None


def _call_sites(path, attributes, arity=1):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    constants = _literals(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in attributes and len(node.args) >= arity:
            yield tuple(_value(argument, constants)
                        for argument in node.args[:arity])


def service_names(path):
    """Collect the literal service names a module passes to call or client."""
    return {service for (service,) in _call_sites(path, {'call', 'client'})
            if service}


@pytest.mark.parametrize('path', sorted(CHECKS.glob('*.py')), ids=lambda p: p.stem)
def test_every_called_service_has_an_sdk_client(path):
    available = set(boto3.Session(region_name='eu-central-1').get_available_services())
    unknown = service_names(path) - available - RETIRED
    assert not unknown, f'{path.name} calls clients botocore does not ship: {unknown}'


def test_retired_services_are_still_listed_as_retired():
    """If botocore restores one, drop it from RETIRED and from sdk_call."""
    available = set(boto3.Session(region_name='eu-central-1').get_available_services())
    assert not RETIRED & available


@pytest.mark.parametrize('path', sorted(CHECKS.glob('*.py')), ids=lambda p: p.stem)
def test_every_called_method_exists_on_its_client(path):
    """A renamed or never-existing operation only fails at runtime otherwise."""
    session = boto3.Session(region_name='eu-central-1')
    available = set(session.get_available_services())
    missing = []
    for service, method in _call_sites(path, {'call'}, arity=2):
        if not service or not method or service in RETIRED or service not in available:
            continue
        if not hasattr(session.client(service), method):
            missing.append(f'{service}.{method}')
    assert not missing, f'{path.name} calls operations the SDK has not: {missing}'
