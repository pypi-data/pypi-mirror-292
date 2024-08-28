from typing import Callable

from thinking_modules.importing import import_package_recursively
from thinking_modules.model import ModuleName

from thinking_tests.decorators import KNOWN_CASES
from thinking_tests.protocol import ThinkingCase
from thinking_tests.runner.protocol import BackendResultType
from thinking_tests.runner.run import execute
from thinking_tests.utils import root_pkg, caller_module_name, main_module_real_name


def default_sorter(cases: list[ThinkingCase]) -> list[ThinkingCase]:
    return sorted(cases, key=lambda x: x.coordinates)


def run_all(predicate: Callable[[ThinkingCase], bool] = None,
            *,
            root_package: str = "",
            sorter: Callable[[list[ThinkingCase]], list[ThinkingCase]] = None) -> BackendResultType:
    """
    Run all discovered tests matching the predicate with the global runner.

    Will import root_pkg recursively, unless it is None. By default, root_pkg is figured out based on __main__ module
    placement.

    Order can be tweaked by providing sorting function - by default cases are sorted by coordinates.

    :param predicate: filter for cases; by default accepts all cases; use this to skip tests on whatever condition
                    you fancy
    :param root_package: package to be scanned (recursively, by importing it and all its subpackages and modules) when
                    looking for test cases; use None to disable package scan; by default will scan root package of __main__
    :param sorter: sorting function of cases; by default will sort by coordinates
    :return: test suite result (type depending on global test runner)
    """
    predicate = predicate or (lambda x: True)
    sorter = sorter or default_sorter
    if root_package is not None:
        import_package_recursively(root_package or root_pkg())
    return execute(sorter([x for x in KNOWN_CASES if predicate(x)]))


def run_current_module(predicate: Callable[[ThinkingCase], bool] = None,
                       *,
                       sorter: Callable[[list[ThinkingCase]], list[ThinkingCase]] = None) -> BackendResultType:
    """
    Run all cases present in module calling this function. See run_all(...) for arguments and result description. Does
    not scan anything but the caller module. If other modules are already imported/scanned, will filter out any case
    that is not declared in the caller module by looking at its coordinates.
    """
    predicate = predicate or (lambda x: True)
    sorter = sorter or default_sorter
    caller_module = caller_module_name(2) # 1 is this module, we're looking for caller of this method
    def final_predicate(x: ThinkingCase) -> bool:
        return x.coordinates.module_name == caller_module and predicate(x)
    return run_all(final_predicate, root_package=None, sorter=sorter)


def run_current_package(predicate: Callable[[ThinkingCase], bool] = None,
                        *,
                        sorter: Callable[[list[ThinkingCase]], list[ThinkingCase]] = None) -> BackendResultType:
    """
    Scan the package in which calling module lies, as well as its subpackages. If called from pkg.__main__ or pkg.__init__,
    takes pkg as that package. Run all tests found within
    """
    predicate = predicate or (lambda x: True)
    sorter = sorter or default_sorter
    name = caller_module_name(2) # 1 is this module, we're looking for caller of this method
    caller_module = main_module_real_name() if name == "__main__" else ModuleName.resolve(name)
    pkg_name = caller_module.parent
    def final_predicate(x: ThinkingCase) -> bool:
        return ModuleName.resolve(x.coordinates.module_name).parent == pkg_name and predicate(x)
    return run_all(final_predicate, root_package=pkg_name.qualified, sorter=sorter)
