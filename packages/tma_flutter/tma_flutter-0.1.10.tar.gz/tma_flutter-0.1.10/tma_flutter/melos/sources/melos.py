import typer, os
from pathlib import Path
from typing_extensions import Annotated
from tma_flutter.snippets.sources import template, shell


app = typer.Typer()


@app.command(name="init")
def init_melos(project_name: Annotated[str, typer.Argument()]):
    current_path = Path(os.getcwd())
    template_path = Path(__file__).absolute().parent.parent.joinpath("templates")
    template.copy(
        copy_path=template_path,
        copy_file="pubspec.yaml.template",
        paste_path=current_path,
        paste_file="pubspec.yaml",
        template_variables={
            "project_snake": project_name,
        },
    )
    template.copy(
        copy_path=template_path,
        copy_file="melos.yaml.template",
        paste_path=current_path,
        paste_file="melos.yaml",
        template_variables={
            "project_snake": project_name,
        },
    )
    template.copy(
        copy_path=template_path,
        copy_file=".gitignore.template",
        paste_path=current_path,
        paste_file=".gitignore",
    )

    shell.run_script(["dart pub add", "dev:melos:6.1.0"])
    shell.run_script(["melos bootstrap"])
    shell.run_script(["melos test_all"])


if __name__ == "__main__":
    app()
