import os
from tma_flutter.snippets.sources import flutter
from tma_flutter.snippets.sources import template
from pathlib import Path


def make_target(view_name: str):
    dir_name = "views"
    flutter.create_package(
        package_name=view_name,
        dir_name=dir_name,
    )


def name(module_name: str) -> str:
    return module_name


def copy_template(
    view_name: str,
    feature_name: str,
):
    view_path = _get_view_path()
    lib_path = view_path.joinpath("lib")
    test_path = view_path.joinpath("test")
    template.prepare_copy(lib_path, test_path)

    template_path = Path(__file__).absolute().parent.parent.joinpath("templates")
    template.copy(
        copy_path=template_path.joinpath("lib"),
        copy_file="view.dart",
        paste_path=lib_path,
        paste_file=f"{view_name}.dart",
        template_variables={
            "view_pascal": template.pascal_case(view_name),
            "feature_snake": feature_name,
        },
    )


def add_dependency(feature_name: str):
    flutter.add_dependencies(
        dependency_names=[feature_name],
        pubspec_path=_get_view_path(),
    )


def _get_view_path() -> Path:
    return Path(os.getcwd()).joinpath("views")
