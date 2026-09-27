"""Collection and reporting use a single registry of modules."""
from inspect import signature
from modules.qmcore.registry import _CHECK_MODULES, collectors


def test_every_registered_module_has_one_callable_collector():
    resolved = list(collectors())
    assert len(resolved) == len(_CHECK_MODULES)
    assert {name for name, _ in resolved} == {name for name, _ in _CHECK_MODULES}
    assert len({name for name, _ in resolved}) == len(resolved)
    for _name, collector in resolved:
        signature(collector).bind(ctx=object(), skip=set())
