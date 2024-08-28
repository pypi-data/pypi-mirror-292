import inspect
import sys
from os.path import join, exists, basename, dirname

from thinking_modules.importing import _abs_dirname
from thinking_modules.model import ModuleName


def main_module():
    return sys.modules["__main__"]


#todo belongs to thinking-modules
def main_module_real_name() -> ModuleName:
    main = sys.modules["__main__"]
    try:
        main_file = main.__file__
    except AttributeError:
        raise NotImplementedError("main_module_real_name() doesn't cover shell sessions")
    assert main_file.endswith(".py")  # todo msg
    name_parts = [basename(main_file)[:-len(".py")]]
    parent_dir = dirname(main_file)
    while exists(join(parent_dir, "__init__.py")):
        name_parts = [basename(parent_dir)] + name_parts
        parent_dir = dirname(parent_dir)
    return ModuleName(name_parts)


def root_pkg(path: str = None) -> str:
    abs_path = _abs_dirname(path or main_module().__file__)
    shallowest_module = None
    while exists(join(abs_path, "__init__.py")):
        abs_path, slash, shallowest_module = abs_path.rpartition("/")
    assert shallowest_module is not None
    return shallowest_module

def caller_module_name(lvl=1):
    """
    :param lvl: 0 - refers to invocation of caller_module_name itself, will return name of this module;
    1 - who called this method?;
    -1 - main function running this interpreter
    :return: module name, possibly "__main__"
    """
    s = inspect.stack() # 0 -
    return s[lvl].frame.f_globals["__name__"]
