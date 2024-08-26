import os
from pathlib import Path
from tma_flutter.snippets.sources import flutter, template


def make_target(feature_name: str):
    dir_name = "features"
    flutter.create_package(
        package_name=feature_name,
        dir_name=dir_name,
    )


def presentation_name(module_name: str) -> str:
    return module_name + "_" + "feature"


def domain_name(module_name: str) -> str:
    return module_name


def copy_template(
    feature_name: str,
    interface_name: str,
):
    feature_path = _get_feature_path()
    lib_path = feature_path.joinpath("lib")
    test_path = feature_path.joinpath("test")
    template.prepare_copy(lib_path, test_path)

    template_path = Path(__file__).absolute().parent.parent.joinpath("templates")
    template.copy(
        copy_path=template_path.joinpath("lib"),
        copy_file="feature.dart",
        paste_path=lib_path,
        paste_file=f"{feature_name}.dart",
        template_variables={
            "interface_snake": interface_name,
        },
    )


def add_dependency(interface_name: str):
    flutter.add_dependencies(
        dependency_names=[interface_name],
        pubspec_path=_get_feature_path(),
    )


def _get_feature_path() -> Path:
    return Path(os.getcwd()).joinpath("features")
