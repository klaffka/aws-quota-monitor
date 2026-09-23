"""Drive every check against a synthetic, shape-accurate AWS response.

The Mock-based tests in this suite fabricate their own responses, so a check
that reads a key the API never returns, or sends a parameter it rejects, still
passes them. This harness replaces ``ctx.call`` with one that consults the live
botocore service model: the operation must exist, the parameters must satisfy
botocore's own validator, the response key must be a member of the output
shape, and the payload handed back is generated from that shape.

It is not a test module; ``test_check_smoke.py`` parametrizes over it.
"""
from datetime import datetime, UTC
from importlib import import_module

import boto3
from botocore import xform_name
from botocore.exceptions import UnknownServiceError
from botocore.validate import validate_parameters

from modules.qmcore.aws import CheckContext
from modules.qmcore.registry import _CHECK_MODULES

ACCOUNT = '123456789012'
REGION = 'eu-central-1'
MOMENT = datetime(2026, 9, 15, tzinfo=UTC)
# Deep shapes recurse; eight levels reaches the prefix lists nested inside a
# security group rule, which is the deepest structure any check walks.
MAX_DEPTH = 8
# Identifiers that travel back into a request often carry a minimum length the
# response shape does not state, so a generated string is long by default.
DEFAULT_LENGTH = 36


def _string(shape):
    """Return a value that satisfies the shape's enum and length constraints."""
    if shape.metadata.get('enum'):
        return shape.metadata['enum'][0]
    length = max(int(shape.metadata.get('min') or 0), DEFAULT_LENGTH)
    return 'x' * min(length, int(shape.metadata.get('max') or length))


def synth(shape, depth=0, populated=True):
    """Build a response fragment botocore's own validator accepts.

    ``populated=False`` models a fresh account: every inventory comes back
    empty, while scalar responses such as account settings stay well formed,
    because AWS returns those whether or not anything has been created.
    """
    if shape is None or depth > MAX_DEPTH:
        return None
    kind = shape.type_name
    if kind == 'structure':
        # Fill every member, not only the required ones: checks read optional
        # identifiers such as VpcId or ImageId, and an absent key is a KeyError
        # the harness would report as a defect in the check.
        return {name: value for name in shape.members
                if (value := synth(shape.members[name], depth + 1, populated)) is not None}
    if kind == 'list':
        if not populated:
            return []
        item = synth(shape.member, depth + 1, populated)
        return [item] if item is not None else []
    if kind == 'map':
        if not populated:
            return {}
        value = synth(shape.value, depth + 1, populated)
        return {_string(shape.key): value} if value is not None else {}
    if kind == 'string':
        return _string(shape)
    if kind in {'integer', 'long'}:
        return max(int(shape.metadata.get('min') or 0), 1)
    if kind in {'float', 'double'}:
        return float(max(int(shape.metadata.get('min') or 0), 1))
    if kind == 'boolean':
        return False
    if kind == 'timestamp':
        return MOMENT
    if kind == 'blob':
        return b'x'
    return None


class UnknownOperation(AssertionError):
    """The client ships no operation by that name."""


class WrongResponseKey(AssertionError):
    """The key read is not a member of the operation's output shape."""


class ShapeCall:
    """A ``ctx.call`` that answers from the service model instead of the network."""

    def __init__(self, session, populated=True):
        self.session = session
        self.populated = populated
        self.sites = []
        self._models = {}

    def _model(self, service):
        if service not in self._models:
            self._models[service] = self.session.client(service).meta.service_model
        return self._models[service]

    def __call__(self, service, method, key=None, **kwargs):
        self.sites.append((service, method, key))
        try:
            model = self._model(service)
        except UnknownServiceError:
            # sdk_call turns this into UNSUPPORTED, exactly as in production.
            raise
        name = next((n for n in model.operation_names if xform_name(n) == method), None)
        if name is None:
            raise UnknownOperation(f'{service} has no operation {method}')
        operation = model.operation_model(name)
        if operation.input_shape is not None:
            validate_parameters(kwargs, operation.input_shape)
        elif kwargs:
            raise UnknownOperation(f'{service}.{method} takes no parameters: {sorted(kwargs)}')
        output = operation.output_shape
        if key is None:
            return synth(output, populated=self.populated) or {}
        if output is None or key not in output.members:
            members = sorted(output.members) if output is not None else []
            raise WrongResponseKey(f'{service}.{method} returns no {key}; it returns {members}')
        return synth(output.members[key], populated=self.populated) or []


def entries():
    """Yield (module name, service, checks) for every registered check module."""
    for module_name, service in _CHECK_MODULES:
        module = import_module(module_name)
        checks = getattr(module, 'ALL_CHECKS', getattr(module, 'CHECKS', ()))
        if isinstance(checks, dict):
            for check_service, items in checks.items():
                yield module_name, check_service, list(items)
        elif checks and service:
            yield module_name, service, list(checks)


def entry_points():
    """Yield (module name, entry point, quota keys) for the modules `entries`
    cannot see, because they build their checks when the collector calls them.

    ``account_services`` is absent on purpose: it matches the catalog by quota
    name rather than by code, so a synthetic catalog would decide what it
    measures. tests/test_account_services.py covers it against a real client.
    """
    covered = {module for module, _service, _checks in entries()}
    for module_name, _service in _CHECK_MODULES:
        if module_name in covered:
            continue
        module = import_module(module_name)
        keys = getattr(module, 'CUSTOM_KEYS', None)
        if not keys:
            continue
        entry = next((getattr(module, name) for name in dir(module)
                      if name.startswith('get_current_quotastatus_')), None)
        if entry is not None:
            yield module_name, entry, sorted(keys)


def run_entry(entry, keys, populated=True):
    """Run a module through its collector entry point and return (measurements,
    recorded call sites), the same pair `run` returns.

    Returning the sites is what lets the IAM guard see these modules at all: an
    entry point builds its checks when called, so the AST walk cannot reach them
    and discarding the sites left every call they make unguarded.
    """
    session = boto3.Session(region_name=REGION)
    quotas = [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100, 'Unit': 'Count'}
              for service, code in keys]
    ctx = CheckContext(session, quotas, account=ACCOUNT, now=MOMENT)
    call = ShapeCall(session, populated=populated)
    ctx.call = call
    return entry(ctx=ctx), call.sites


def run(service, checks, populated=True):
    """Run one module's checks and return (measurements, recorded call sites)."""
    session = boto3.Session(region_name=REGION)
    quotas = [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100, 'Unit': 'Count'}
              for code, _name, _fn in checks]
    ctx = CheckContext(session, quotas, account=ACCOUNT, now=MOMENT)
    call = ShapeCall(session, populated=populated)
    ctx.call = call
    return ctx.run(service, checks), call.sites
