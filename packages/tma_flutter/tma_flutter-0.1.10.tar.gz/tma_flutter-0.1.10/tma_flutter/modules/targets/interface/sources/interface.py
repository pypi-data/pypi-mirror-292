import os
from pathlib import Path
from typing import List
from tma_flutter.snippets.sources import flutter, template


def make_target(interface_name: str):
    dir_name = "interfaces"
    flutter.create_package(
        package_name=interface_name,
        dir_name=dir_name,
    )


def name(module_name: str) -> str:
    return module_name + "_" + "interface"


def copy_template(interface_name: str):
    interface_path = _get_interface_path()
    lib_path = interface_path.joinpath("lib")
    test_path = interface_path.joinpath("test")
    template.prepare_copy(lib_path, test_path)

    template_path = Path(__file__).absolute().parent.parent.joinpath("templates")
    template.copy(
        copy_path=template_path.joinpath("lib"),
        copy_file="interface.dart",
        paste_path=lib_path,
        paste_file=f"{interface_name}.dart",
    )


def add_dependency(dependency_names: List[str]):
    flutter.add_dependencies(
        dependency_names=dependency_names,
        pubspec_path=_get_interface_path(),
    )


def _get_interface_path() -> Path:
    return Path(os.getcwd()).joinpath("interfaces")
