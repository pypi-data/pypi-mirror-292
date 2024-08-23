import typer
from tma_flutter.modules.layers.sources import presentation, domain, core
from tma_flutter.melos.sources import melos


app = typer.Typer()
app.add_typer(presentation.app, name="presentation")
app.add_typer(domain.app, name="domain")
app.add_typer(core.app, name="core")
app.add_typer(melos.app, name="melos")


if __name__ == "__main__":
    app()
