"""The collector's IAM policy must name each service by its IAM prefix.

An SDK client name is not always the IAM prefix: Voice ID signs as `voiceid`,
Amazon Managed Prometheus as `aps`. A policy written against the client name
grants nothing, and the collector only finds out with an AccessDenied at run
time, so the prefixes are checked against botocore's signing names here.
"""
import ast
import json
import re

import boto3

from tests.iam_policy import ACTION, POLICY, granted_actions, is_granted

# Services whose documented IAM prefix is not the signing name botocore
# reports. CloudWatch signs its requests as `monitoring` but authorises them
# as `cloudwatch`; `sso` is IAM Identity Center's prefix, while the SDK's `sso`
# client is the sign-in portal that signs as `awsssoportal`.
DOCUMENTED_EXCEPTIONS = {'cloudwatch', 'sso'}


def policy_prefixes():
    return {match.group(1) for match in ACTION.finditer(
        POLICY.read_text(encoding='utf-8'))}


def test_every_policy_prefix_matches_the_services_signing_name():
    session = boto3.Session(region_name='eu-central-1')
    available = set(session.get_available_services())
    wrong = {}
    for prefix in sorted(policy_prefixes()):
        if prefix not in available or prefix in DOCUMENTED_EXCEPTIONS:
            continue
        metadata = session.client(prefix).meta.service_model.metadata
        signing = metadata.get('signingName') or metadata.get('endpointPrefix')
        if signing and signing != prefix:
            wrong[prefix] = signing
    assert not wrong, f'policy prefixes that are SDK client names: {wrong}'


def test_no_statement_grants_the_same_action_twice():
    actions, duplicates, inside = set(), [], False
    for line in POLICY.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if stripped.startswith('Action = ['):
            actions, inside = set(), True
        elif inside and stripped.startswith(']'):
            inside = False
        elif inside:
            match = ACTION.search(line)
            if match:
                if match.group(0) in actions:
                    duplicates.append(match.group(0))
                actions.add(match.group(0))
    assert not duplicates, f'actions granted twice in one statement: {duplicates[:8]}'


# API Gateway authorises by HTTP verb rather than by operation, and S3's IAM
# action names differ from its API operation names.
VERB_AUTHORISED = {'apigateway', 'apigatewayv2'}
# CloudWatch signs as `monitoring` but authorises as `cloudwatch`, and the IoT
# data plane signs as `iotdata` while authorising under the control plane's
# `iot` prefix.
PREFIX_ALIASES = {'monitoring': 'cloudwatch', 'iotdata': 'iot'}
S3_ALIASES = {
    'ListBuckets': 'ListAllMyBuckets',
    'GetBucketReplication': 'GetReplicationConfiguration',
    'GetBucketLifecycleConfiguration': 'GetLifecycleConfiguration',
    'GetBucketNotificationConfiguration': 'GetBucketNotification',
}


def _parameters(function):
    arguments = function.args
    return [argument.arg for argument in
            (*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs)]


def _argument_source(node, parameters, constants, value_of):
    """Where one ctx.call argument comes from: a literal, or a parameter."""
    value = value_of(node, constants)
    if value is not None:
        return ('const', value)
    if isinstance(node, ast.Name) and node.id in parameters:
        return ('param', node.id)
    return None


def _indirect_call_sites(path):
    """Yield (service, operation) for a ctx.call that reads either half from the
    enclosing helper's parameter.

    Roughly one call site in seven routes through such a helper -- omics'
    `resource_count(ctx, method, key)` is the shape -- and the plain AST walk
    sees the parameter name instead of an operation. Every caller inside the
    module binds that parameter to a literal, so the pair resolves there.

    Both halves must come from one call node. Crossing every service literal in
    a module with every operation literal invents grants no check asks for: it
    reports `sso:ListApplications` for misc_counts, which holds `sso` as a
    catalog key and `list_applications` for servicecatalog-appregistry.
    """
    from tests.test_check_client_names import _literals, _value

    tree = ast.parse(path.read_text(encoding='utf-8'))
    constants = _literals(tree)
    templates, signatures = {}, {}
    for function in ast.walk(tree):
        if not isinstance(function, ast.FunctionDef):
            continue
        parameters = _parameters(function)
        signatures[function.name] = parameters
        for node in ast.walk(function):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == 'call' and len(node.args) >= 2):
                continue
            service = _argument_source(node.args[0], parameters, constants, _value)
            operation = _argument_source(node.args[1], parameters, constants, _value)
            if service and operation and 'param' in (service[0], operation[0]):
                templates.setdefault(function.name, set()).add((service, operation))
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in templates):
            continue
        bound = dict(zip(signatures[node.func.id], node.args))
        bound.update({keyword.arg: keyword.value
                      for keyword in node.keywords if keyword.arg})

        def resolve(source):
            if source[0] == 'const':
                return source[1]
            argument = bound.get(source[1])
            return _value(argument, constants) if argument is not None else None

        for service, operation in templates[node.func.id]:
            names = (resolve(service), resolve(operation))
            if all(names):
                yield names


def test_every_operation_a_check_calls_is_granted_somewhere():
    """A new check without its IAM action fails with AccessDenied in production."""
    import boto3
    from botocore import xform_name

    from tests.test_check_client_names import MODULES, RETIRED, _call_sites, module_id

    session = boto3.Session(region_name='eu-central-1')
    available = set(session.get_available_services())
    granted = granted_actions()
    models, ungranted = {}, []
    for path in MODULES:
        sites = [*_call_sites(path, {'call'}, arity=2), *_indirect_call_sites(path)]
        for service, method in sites:
            if not service or not method or service in RETIRED \
                    or service not in available or service in VERB_AUTHORISED:
                continue
            if service not in models:
                models[service] = session.client(service).meta.service_model
            model = models[service]
            operation = next((name for name in model.operation_names
                              if xform_name(name) == method), None)
            if operation is None:
                continue
            # The client name is not the IAM prefix: qconnect signs as wisdom.
            prefix = model.metadata.get('signingName') or model.metadata.get('endpointPrefix')
            prefix = PREFIX_ALIASES.get(prefix, prefix)
            if not is_granted(granted, prefix, S3_ALIASES.get(operation, operation)):
                ungranted.append(f'{module_id(path)}: {prefix}:{operation}')
    assert not ungranted, f'operations called without an IAM grant: {ungranted}'


def test_every_operation_a_check_actually_makes_is_granted():
    """The AST guard above only sees a call whose service and operation are
    literal at the ctx.call node. Most modules route through a helper that takes
    the operation as a parameter, so roughly half the call sites are invisible
    to it and a missing grant surfaces as AccessDenied in production.

    The smoke harness records every call a check really makes, so the policy is
    checked against that instead of against what the source happens to spell out.
    """
    import boto3
    from botocore import xform_name

    from tests.shape_harness import entries, entry_points, run, run_entry
    from tests.test_check_client_names import RETIRED

    session = boto3.Session(region_name='eu-central-1')
    available = set(session.get_available_services())
    granted = granted_actions()
    called = set()
    for _module, service, checks in entries():
        _results, sites = run(service, checks)
        called.update(sites)
    for _module, entry, keys in entry_points():
        _results, sites = run_entry(entry, keys)
        called.update(sites)
    models, ungranted = {}, set()
    for service, method, _key in called:
        if service in RETIRED or service not in available or service in VERB_AUTHORISED:
            continue
        if service not in models:
            models[service] = session.client(service).meta.service_model
        model = models[service]
        operation = next((name for name in model.operation_names
                          if xform_name(name) == method), None)
        if operation is None:
            continue
        # The prefix matters: a grant written for the wrong one authorises
        # nothing, which is how MWAA Serverless ran under `airflow:`.
        prefix = model.metadata.get('signingName') or model.metadata.get('endpointPrefix')
        prefix = PREFIX_ALIASES.get(prefix, prefix)
        if not is_granted(granted, prefix, S3_ALIASES.get(operation, operation)):
            ungranted.add(f'{prefix}:{operation}')
    assert not ungranted, f'operations called without an IAM grant: {sorted(ungranted)}'


# AWS caps the *sum* of a role's inline policies at 10,240 characters, so
# splitting a policy in two buys nothing. The grants grew from 883 characters
# to over forty thousand without any gate noticing: `terraform validate` does
# not check policy sizes and CI never applies. This is that gate.
INLINE_POLICY_LIMIT = 10240
# Stands in for a Terraform reference the size cannot be known for until apply.
# Longer than a real report-bucket ARN, so the estimate stays an upper bound.
PLACEHOLDER_ARN = ('arn:aws:servicename:eu-central-1:123456789012:'
                   'resource-type/a-long-resource-name')


def _policy_bodies():
    """Yield (resource name, the HCL object each policy passes to jsonencode)."""
    text = POLICY.read_text(encoding='utf-8')
    for match in re.finditer(r'resource "aws_iam_role_policy" "(\w+)" \{', text):
        start = text.index('jsonencode({', match.end()) + len('jsonencode(')
        depth, position = 0, start
        while True:
            if text[position] == '{':
                depth += 1
            elif text[position] == '}':
                depth -= 1
                if depth == 0:
                    break
            position += 1
        yield match.group(1), text[start:position + 1]


def _as_document(body):
    """Read one jsonencode body as the JSON document AWS will store."""
    body = re.sub(r'#[^\n]*', '', body)
    body = re.sub(r'"\$\{[^}]*\}[^"]*"', f'"{PLACEHOLDER_ARN}"', body)
    body = re.sub(r'(?<![":\w])[a-z]\w*(?:\.\w+)+', f'"{PLACEHOLDER_ARN}"', body)
    body = re.sub(r'([{,]\s*|^\s*|\n\s*)([A-Za-z]\w*)\s*=', r'\1"\2":', body)
    body = re.sub(r'("(?:[^"\\]|\\.)*")\s*=', r'\1:', body)
    # HCL separates attributes by newline; JSON wants commas.
    lines = [line.rstrip() for line in body.split('\n') if line.strip()]
    joined = []
    for position, line in enumerate(lines):
        following = lines[position + 1].lstrip() if position + 1 < len(lines) else ''
        if line.endswith(('"', ']', '}')) and following \
                and not following.startswith((']', '}', ',')):
            line += ','
        joined.append(line)
    return json.loads(re.sub(r',(\s*[}\]])', r'\1', '\n'.join(joined)))


def test_the_inline_policies_fit_in_one_role():
    sizes = {name: len(json.dumps(_as_document(body), separators=(',', ':')))
             for name, body in _policy_bodies()}
    assert sizes, 'no inline role policies found; the resource shape changed'
    total = sum(sizes.values())
    largest = max(sizes, key=sizes.get)
    assert total <= INLINE_POLICY_LIMIT, (
        f'inline policies total {total} characters against a {INLINE_POLICY_LIMIT} '
        f'limit; {largest} alone is {sizes[largest]}. Collapse a service\'s read '
        f'verbs to one wildcard rather than listing every operation.')
