"""Every service name a check passes to ctx.call must be a real SDK client.

A wrong name (`cassandra` for Keyspaces, `elasticfilesystem` for EFS) raises
UnknownServiceError at runtime only, so the check reports an error every run
while its tests keep passing against a Mock.
"""
import ast
from pathlib import Path

import boto3
import pytest
from botocore import xform_name

# These services were retired from botocore. Their checks route through
# sdk_call, which reports the absence as UNSUPPORTED rather than an error.
RETIRED = {'evidently', 'iotanalytics', 'iotevents', 'qldb', 'robomaker'}
CHECKS = Path('src/modules/qmchecks')
# Subpackages hold call sites too; a flat glob left ec2, vpc and lambda_checks
# unguarded, which is how DescribeLaunchTemplates kept an OwnerId it rejects.
MODULES = tuple(sorted(path for path in CHECKS.rglob('*.py')
                       if path.name != '__init__.py'))


def module_id(path):
    return path.relative_to(CHECKS).with_suffix('').as_posix().replace('/', '.')


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


def _call_sites(path, attributes, arity=1, keywords=False):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    constants = _literals(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in attributes and len(node.args) >= arity:
            values = tuple(_value(argument, constants)
                           for argument in node.args[:arity])
            if not keywords:
                yield values
                continue
            # A ** unpacking hides the names, so the call cannot be judged here.
            # test_check_smoke.py validates the merged kwargs instead.
            named = None if any(kw.arg is None for kw in node.keywords) else {
                kw.arg for kw in node.keywords}
            yield values + (named,)


def _operation(session, service, method):
    """Return the operation model behind a snake_case client method."""
    model = session.client(service).meta.service_model
    for name in model.operation_names:
        if xform_name(name) == method:
            return model.operation_model(name)
    return None


def service_names(path):
    """Collect the literal service names a module passes to call or client."""
    return {service for (service,) in _call_sites(path, {'call', 'client'})
            if service}


@pytest.mark.parametrize('path', MODULES, ids=module_id)
def test_every_called_service_has_an_sdk_client(path):
    available = set(boto3.Session(region_name='eu-central-1').get_available_services())
    unknown = service_names(path) - available - RETIRED
    assert not unknown, f'{module_id(path)} calls clients botocore does not ship: {unknown}'


def test_retired_services_are_still_listed_as_retired():
    """If botocore restores one, drop it from RETIRED and from sdk_call."""
    available = set(boto3.Session(region_name='eu-central-1').get_available_services())
    assert not RETIRED & available


@pytest.mark.parametrize('path', MODULES, ids=module_id)
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
    assert not missing, f'{module_id(path)} calls operations the SDK has not: {missing}'


def _output_members(session, service, method):
    """Return the output members of one operation, or None if it has none."""
    model = session.client(service).meta.service_model
    for name in model.operation_names:
        if xform_name(name) == method:
            shape = model.operation_model(name).output_shape
            return set(shape.members) if shape is not None else set()
    return None


@pytest.mark.parametrize('path', MODULES, ids=module_id)
def test_every_paginated_key_exists_in_the_response(path):
    """A wrong key reports zero usage with an OK status: a silent undercount."""
    session = boto3.Session(region_name='eu-central-1')
    available = set(session.get_available_services())
    wrong = []
    for service, method, key in _call_sites(path, {'call'}, arity=3):
        if not service or not method or not key or service in RETIRED \
                or service not in available:
            continue
        members = _output_members(session, service, method)
        if members is not None and key not in members:
            wrong.append(f'{service}.{method}[{key}]')
    assert not wrong, f'{module_id(path)} reads response keys that do not exist: {wrong}'


@pytest.mark.parametrize('path', MODULES, ids=module_id)
def test_every_call_passes_parameters_the_operation_accepts(path):
    """A wrong or missing parameter name only fails once the call is made."""
    session = boto3.Session(region_name='eu-central-1')
    available = set(session.get_available_services())
    wrong = []
    for service, method, given in _call_sites(path, {'call'}, arity=2, keywords=True):
        if not service or not method or given is None or service in RETIRED \
                or service not in available:
            continue
        operation = _operation(session, service, method)
        if operation is None or operation.input_shape is None:
            continue
        # The third positional argument names the response key, never an input.
        unknown = given - set(operation.input_shape.members)
        missing = set(operation.input_shape.required_members) - given
        if unknown or missing:
            wrong.append(f'{service}.{method}: unknown={sorted(unknown)} '
                         f'missing={sorted(missing)}')
    assert not wrong, f'{module_id(path)} calls operations with wrong parameters: {wrong}'
