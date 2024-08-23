import typer
from typing_extensions import Annotated
from tma_flutter.modules.layers.sources import helper


app = typer.Typer()


@app.command(name="make")
def make_module(module_name: Annotated[str, typer.Argument()]):
    helper.make_domain_module(
        module_name=module_name,
        layer_name="core",
    )


if __name__ == "__main__":
    app()
