import os
from pathlib import Path
from tma_flutter.snippets.sources import flutter, template


def make_target(test_name: str):
    dir_name = "tests"
    flutter.create_package(
        package_name=test_name,
        dir_name=dir_name,
    )


def name(module_name: str) -> str:
    return module_name + "_" + "test"


def copy_template(feature_name: str):
    test_path = _get_test_path()
    lib_path = test_path.joinpath("lib")
    test_path = test_path.joinpath("test")
    template.prepare_copy(lib_path, test_path)

    template_path = Path(__file__).absolute().parent.parent.joinpath("templates")
    template.copy(
        copy_path=template_path.joinpath("lib"),
        copy_file="feature_testing.dart",
        paste_path=lib_path,
        paste_file=f"{feature_name}_testing.dart",
    )

    template.copy(
        copy_path=template_path.joinpath("test"),
        copy_file="feature_test.dart",
        paste_path=test_path,
        paste_file=f"{feature_name}_test.dart",
        template_variables={
            "feature_snake": feature_name,
        },
    )


def add_dependency_presentation(
    view_name: str,
    interface_name: str,
):
    flutter.add_dependencies(
        dependency_names=[view_name, interface_name],
        pubspec_path=_get_test_path(),
    )


def add_dependency_domain(
    feature_name: str,
    interface_name: str,
):
    flutter.add_dependencies(
        dependency_names=[feature_name, interface_name],
        pubspec_path=_get_test_path(),
    )


def _get_test_path() -> Path:
    return Path(os.getcwd()).joinpath("tests")
