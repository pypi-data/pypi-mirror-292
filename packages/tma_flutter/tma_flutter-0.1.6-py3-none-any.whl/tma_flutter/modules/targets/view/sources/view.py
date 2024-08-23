import typer, os
from typing_extensions import Annotated
from tma_flutter.snippets.sources import flutter
from tma_flutter.snippets.sources import template
from pathlib import Path


app = typer.Typer()


@app.command(name="make")
def make_target(
    view_name: Annotated[str, typer.Argument()],
    dir_name: Annotated[str, typer.Argument()] = "views",
):
    flutter.create_package(
        package_name=view_name,
        dir_name=dir_name,
    )


def name(module_name: str) -> str:
    return module_name + "_" + "view"


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
    view_path = _get_view_path()
    os.chdir(view_path)
    flutter.add_dependency(
        target_name=feature_name,
        target_path="../features",
    )
    os.chdir(view_path.parent)


def _get_view_path() -> Path:
    return Path(os.getcwd()).joinpath("views")


if __name__ == "__main__":
    app()
