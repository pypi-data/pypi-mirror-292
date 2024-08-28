import sys
from enum import Enum, auto
from importlib import import_module
from os.path import basename
from types import ModuleType
from typing import NamedTuple, Optional, Self


class ModuleKind(Enum):
    MODULE = auto()
    """Represents non-package module"""

    PACKAGE = auto()
    """Represent __init__.py file of a package"""

    PACKAGE_MAIN = auto()
    """Represents __main__.py file of a package"""

    SHELL = auto()
    """Represents interactive shell session or running with 'python -c ...'"""


type ModulePointer = str | ModuleName | ModuleType

type ModuleNamePointer = ModulePointer | list[str] | object


class Module(NamedTuple):
    module_: ModuleType
    file_path: Optional[str]
    name: 'ModuleName'
    kind: ModuleKind

    @property
    def is_package(self) -> bool:
        return self.kind in { ModuleKind.PACKAGE, ModuleKind.PACKAGE_MAIN }

    @property
    def is_shell(self) -> bool:
        return self.kind == ModuleKind.SHELL

    @property
    def is_module(self) -> bool:
        return self.kind == ModuleKind.MODULE

    @classmethod
    def find(cls, pointer: ModulePointer, *, evaluate_if_missing: bool = True) -> ModuleType:
        """
        Turn the pointer to the module (of typing.ModuleType type).

        Pointer may be a ModuleName or str (being an unparsed version of module name) or module itself (in which case
        this method is passthrough).

        If module hasn't been imported yet (is not present in sys.modules), behaviour depends on evaluate_if_missing.
        If that argument is True, the module will be imported; if False, KeyError will be raised.

        :raise KeyError: if module hasn't been ever imported and evaulate_if_missing is False.
        :return: raw python module
        """
        if isinstance(pointer, ModuleType):
            return pointer
        name = ModuleName.resolve(pointer).qualified
        if evaluate_if_missing:
            return import_module(name)
        return sys.modules[name]

    @classmethod
    def resolve(cls, pointer: ModulePointer, *, evaluate_if_missing: bool = True) -> Self:
        """
        Find the module (with Module.find(...); both arguments are forwarded there) and describe it to obtain an instance
        of Module.

        :raise KeyError: in the same case as Module.find(...)
        :return: descriptor of the module
        """
        mod = cls.find(pointer, evaluate_if_missing=evaluate_if_missing)
        try:
            f = mod.__file__
        except AttributeError:
            return cls(mod, None, ModuleName.resolve("__main__"), ModuleKind.SHELL)
        filename = basename(f)
        if filename == "__init__.py":
            kind = ModuleKind.PACKAGE
        elif filename == "__main__.py":
            kind = ModuleKind.PACKAGE_MAIN
        else:
            kind = ModuleKind.MODULE
        return Module(mod, f, ModuleName.resolve(mod), kind)

class ModuleName(NamedTuple):
    parts: list[str]

    @property
    def qualified(self) -> str:
        """
        :return: Full, dot-separated name represented by this instance.
        """
        return ".".join(self.parts)

    @property
    def simple(self) -> str:
        """
        :return: Part after the last dot in qualified name. Name (w/o extension) of the file holding the module or
                directory holding the package.
        """
        return self.parts[-1]

    @property
    def root_package(self) -> Optional[str]:
        """
        :return: Part before the first dot in qualified name, or None in case of a module lying outside of package.
        """
        if len(self.parts) > 1 or (len(self.parts) > 0 and Module.resolve(self.qualified).is_package):
            return self.parts[0]
        return None

    @property
    def parent(self) -> Optional[Self]:
        """
        :return: ModuleName of the package in which the module/package named with this instance resides in, or None in
                case of root packages and non-packaged modules.
        """
        if len(self.parts) == 1:
            return None
        return ModuleName(self.parts[:-1])

    @property
    def has_been_evaluated(self) -> bool:
        """
        :return: Has the import of module with that name happened? Mind you that pkg.__main__ is represented as name pkg.
        """
        return self.qualified in sys.modules

    @classmethod
    def resolve(cls, something: ModuleNamePointer) -> Self:
        """
        - If argument is already a ModuleName, then this method is pass-through.
        - If argument is str assumes that it's a raw module/package name.
        - If argument is list of str, assumes that it's previous case split over dot.
        - If argument is a module (of type typing.ModuleType), parses its name. In case of packages, both __init__.py
          and __main__.py will evaluate to the package name itself.
        - In any other case will retrieve module in which the object has been defined and parse it.
        """
        if isinstance(something, ModuleName):
            return something
        name = None
        parts = None
        if isinstance(something, str):
            parts = something.split(".")
        elif isinstance(something, ModuleType):
            name = something.__name__
        elif isinstance(something, list):
            assert all(isinstance(x, str) for x in something)  # todo msg
            parts = something
        else:
            name = something.__module__
        if parts is None:
            parts = name.split(".")
        if parts[-1] == "__main__":
            parts = parts[:-1]
        return ModuleName(parts)
