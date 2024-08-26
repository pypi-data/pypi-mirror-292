import typer
from typing import List, Optional
from typing_extensions import Annotated
from tma_flutter.modules.layers.sources import helper


app = typer.Typer()


@app.command(name="make")
def make_module(
    module_name: Annotated[str, typer.Argument()],
    dependency_names: Annotated[Optional[List[str]], typer.Option("-dp")] = None,
):
    helper.make_domain_module(
        module_name,
        dependency_names,
    )


if __name__ == "__main__":
    app()
