import yaml
from pathlib import Path
from typing import List
from tma_flutter.snippets.sources import shell
import yaml.loader


def create_package(package_name: str, dir_name: str):
    commands = [
        "flutter create",
        f"--project-name {package_name} {dir_name}",
        "--template=package",
    ]
    shell.run_script(commands)


def create_app(app_name: str, dir_name: str):
    commands = [
        "flutter create",
        f"--project-name {app_name} {dir_name}",
        f"--org com.{app_name}",
        "--template=app",
    ]
    shell.run_script(commands)


def add_dependencies(
    dependency_names: List[str],
    pubspec_path: Path,
):
    if not dependency_names:
        return

    pubspec_path = pubspec_path.joinpath("pubspec.yaml")

    dependencies = "dependencies"
    with open(pubspec_path, "r") as f:
        pubspec = yaml.safe_load(f)
        if dependencies not in pubspec:
            pubspec[dependencies] = dict()
        dependency_dict = {name: "any" for name in dependency_names}
        pubspec[dependencies].update(dependency_dict)

    with open(pubspec_path, "w") as f:
        yaml.dump(pubspec, f, default_flow_style=False, sort_keys=False)
