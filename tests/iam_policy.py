"""What the deployed IAM policy authorises.

The policy collapses a service's read verbs to `List*`, `Describe*` and, where
that cannot reach stored data, `Get*`, because AWS caps the sum of a role's
inline policies at 10,240 characters and spelling out every operation ran to
four times that. A test therefore cannot ask whether an action appears in
`deployment/main.tf` verbatim; it has to ask whether the policy grants it.
"""
import re
from fnmatch import fnmatchcase
from pathlib import Path

POLICY = Path(__file__).parents[1] / 'deployment/main.tf'
ACTION = re.compile(r'"([a-z0-9\-]+):([A-Za-z][\w*]*)"')


def granted_actions():
    """Every (prefix, pattern) pair the policy grants; a pattern may be a wildcard."""
    return {match.groups() for match in ACTION.finditer(
        POLICY.read_text(encoding='utf-8'))}


def is_granted(granted, prefix, operation):
    """Whether one operation is authorised, wildcards included."""
    return any(other == prefix and fnmatchcase(operation, pattern)
               for other, pattern in granted)


def grants(action):
    """Whether the policy authorises `prefix:Operation`."""
    prefix, operation = action.strip('"').split(':', 1)
    return is_granted(granted_actions(), prefix, operation)


def granted_prefixes():
    """Every service prefix the policy names."""
    return {prefix for prefix, _ in granted_actions()}
