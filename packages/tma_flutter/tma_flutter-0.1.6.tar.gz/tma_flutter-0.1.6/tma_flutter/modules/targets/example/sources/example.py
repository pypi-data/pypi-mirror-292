import typer, os, shutil
from typing_extensions import Annotated
from pathlib import Path
from tma_flutter.snippets.sources import flutter, template


app = typer.Typer()


@app.command(name="make")
def make_target(
    example_name: Annotated[str, typer.Argument()],
    dir_name: Annotated[str, typer.Argument()] = "examples",
):
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


def add_view_dependency(view_name: str):
    example_path = _get_example_path()
    os.chdir(example_path)
    flutter.add_dependency(
        target_name=view_name,
        target_path="../views",
    )
    os.chdir(example_path.parent)


def _get_example_path() -> Path:
    return Path(os.getcwd()).joinpath("examples")


if __name__ == "__main__":
    app()
