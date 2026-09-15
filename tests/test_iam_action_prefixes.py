"""The collector's IAM policy must name each service by its IAM prefix.

An SDK client name is not always the IAM prefix: Voice ID signs as `voiceid`,
Amazon Managed Prometheus as `aps`. A policy written against the client name
grants nothing, and the collector only finds out with an AccessDenied at run
time, so the prefixes are checked against botocore's signing names here.
"""
import re
from pathlib import Path

import boto3

POLICY = Path('deployment/main.tf')
ACTION = re.compile(r'"([a-z0-9\-]+):([A-Za-z]\w*)"')
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
