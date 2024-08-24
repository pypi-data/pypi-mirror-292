import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def copy(
    copy_path: Path,
    copy_file: str,
    paste_path: Path,
    paste_file: str,
    template_variables: dict = {},
):
    env = Environment(loader=FileSystemLoader(copy_path))
    template = env.get_template(copy_file)
    template_str = template.render(template_variables)
    paste_path.mkdir(parents=True, exist_ok=True)
    with open(paste_path.joinpath(paste_file), "w") as f:
        f.write(template_str)


def prepare_copy(
    lib_path: Path,
    test_path: Path,
):
    shutil.rmtree(lib_path)
    shutil.rmtree(test_path)


def pascal_case(name: str) -> str:
    return "".join(x for x in name.title() if x != "_")
