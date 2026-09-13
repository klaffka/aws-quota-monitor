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
