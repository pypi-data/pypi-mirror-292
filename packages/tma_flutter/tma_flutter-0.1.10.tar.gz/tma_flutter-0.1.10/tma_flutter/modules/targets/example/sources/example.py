import os
from pathlib import Path
from tma_flutter.snippets.sources import flutter, template


def make_target(example_name: str):
    dir_name = "examples"
    flutter.create_app(
        app_name=example_name,
        dir_name=dir_name,
    )


def name(module_name: str) -> str:
    return module_name + "_" + "example"


def copy_template(
    example_name: str,
    view_name: str,
):
    example_path = _get_example_path()
    lib_path = example_path.joinpath("lib")
    test_path = example_path.joinpath("test")
    template.prepare_copy(lib_path, test_path)

    template_path = Path(__file__).absolute().parent.parent.joinpath("templates")
    template.copy(
        copy_path=template_path.joinpath("lib"),
        copy_file="main.dart",
        paste_path=lib_path,
        paste_file="main.dart",
        template_variables={
            "example_snake": example_name,
            "example_pascal": template.pascal_case(example_name),
        },
    )
    template.copy(
        copy_path=template_path.joinpath("lib"),
        copy_file="example.dart",
        paste_path=lib_path,
        paste_file=f"{example_name}.dart",
        template_variables={
            "example_pascal": template.pascal_case(example_name),
            "view_snake": view_name,
            "view_pascal": template.pascal_case(view_name),
        },
    )


def add_dependency(view_name: str):
    flutter.add_dependencies(
        dependency_names=[view_name],
        pubspec_path=_get_example_path(),
    )


def _get_example_path() -> Path:
    return Path(os.getcwd()).joinpath("examples")
