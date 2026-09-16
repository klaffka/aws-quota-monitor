"""The reporting registry and the collector must list the same check modules.

``registry.py`` decides which quota codes count as implemented, while
``quota-collector/main.py`` decides which checks actually run. A module in only
one of them either reports coverage that is never measured or measures quotas
that no report counts.
"""
import ast
from pathlib import Path

from modules.qmcore.registry import _CHECK_MODULES

COLLECTOR = Path('src/functions/quota-collector/main.py')
PREFIX = 'get_current_quotastatus_'


def collector_modules():
    """Map each invoked collector entry point to the module it comes from."""
    tree = ast.parse(COLLECTOR.read_text(encoding='utf-8'))
    imported = {alias.asname or alias.name: node.module
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom)
                and (node.module or '').startswith('modules.qmchecks')
                for alias in node.names if alias.name.startswith(PREFIX)}
    # Most entry points are called directly; ec2, vpc and lambda are referenced
    # through a tuple of collectors, so any load of the name counts.
    used = {node.id for node in ast.walk(tree)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
            and node.id.startswith(PREFIX)}
    return {module for name, module in imported.items() if name in used}, set(imported) - used


def test_every_registered_module_is_invoked_by_the_collector():
    invoked, _ = collector_modules()
    missing = sorted({module for module, _ in _CHECK_MODULES} - invoked)
    assert not missing, f'registered but never collected: {missing}'


def test_every_invoked_module_is_registered_for_reporting():
    invoked, _ = collector_modules()
    missing = sorted(invoked - {module for module, _ in _CHECK_MODULES})
    assert not missing, f'collected but not registered: {missing}'


def test_no_collector_entry_point_is_imported_without_being_used():
    _, unused = collector_modules()
    assert not sorted(unused), f'imported but never invoked: {sorted(unused)}'
