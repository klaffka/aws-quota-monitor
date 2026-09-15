import ast
from pathlib import Path

from modules.qmcore.registry import custom_keys


def test_check_lists_have_unique_service_quota_pairs():
    pairs = []
    root = Path(__file__).parents[1] / 'src' / 'modules' / 'qmchecks'
    for path in root.rglob('*.py'):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == 'CHECKS'
                            for target in node.targets)
                    and isinstance(node.value, (ast.List, ast.Tuple))):
                continue
            for item in node.value.elts:
                if (isinstance(item, (ast.List, ast.Tuple)) and len(item.elts) >= 2
                        and all(isinstance(value, ast.Constant) for value in item.elts[:2])):
                    pairs.append((item.elts[0].value, item.elts[1].value, path))
    keys = [(service, code) for service, code, _ in pairs]
    assert len(keys) == len(set(keys)), [item for item in pairs if keys.count(item[:2]) > 1]


def test_registry_includes_checks_from_composite_collectors():
    keys = custom_keys()
    assert ('cleanrooms', 'L-F60C2030') in keys
    assert ('medialive', 'L-D1AFAF75') in keys
    assert ('servicediscovery', 'L-0FE3F50E') in keys
    assert ('appstream2', 'L-8A6F32DC') in keys


# Modules that are deliberately not collected. Each entry needs a reason: an
# unregistered module either reports quotas nobody measures or is dead code.
NOT_COLLECTED = {
    'general.utilization_report': 'manual exporter, driven by hand and not by the collector',
    'robomaker': 'botocore ships no robomaker client; the checks stay for its return',
    'sagemaker': 'compatibility wrapper; the collector registers sagemaker_resources',
    'twinmaker': 'reached through the iottwinmaker entry point, not registered directly',
}


def test_the_registry_lists_every_module_once():
    """A duplicated entry imports a module twice and double-counts its coverage."""
    from modules.qmcore.registry import _CHECK_MODULES

    assert len(_CHECK_MODULES) == len(set(_CHECK_MODULES)), [
        entry for entry in _CHECK_MODULES if _CHECK_MODULES.count(entry) > 1]


def test_every_check_module_is_registered_imported_or_documented():
    """An unreferenced module is dead code or a silently uncollected check."""
    from modules.qmcore.registry import _CHECK_MODULES

    root = Path(__file__).parents[1] / 'src' / 'modules' / 'qmchecks'
    registered = {module.removeprefix('modules.qmchecks.') for module, _ in _CHECK_MODULES}
    imported = set()
    for path in root.rglob('*.py'):
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node, ast.ImportFrom) and (node.module or '').startswith('modules.qmchecks'):
                tail = node.module.removeprefix('modules.qmchecks').lstrip('.')
                imported |= {f'{tail}.{alias.name}' if tail else alias.name for alias in node.names}
                imported.add(tail)
    unreferenced = set()
    for path in root.rglob('*.py'):
        if path.name == '__init__.py':
            continue
        name = path.relative_to(root).with_suffix('').as_posix().replace('/', '.')
        leaf = name.rsplit('.', 1)[-1]
        if not ({name, leaf} & (registered | imported | set(NOT_COLLECTED))):
            unreferenced.add(name)
    assert not unreferenced, sorted(unreferenced)
