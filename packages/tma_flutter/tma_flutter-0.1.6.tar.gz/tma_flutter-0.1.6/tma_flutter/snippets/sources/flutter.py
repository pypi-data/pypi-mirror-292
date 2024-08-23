from tma_flutter.snippets.sources import shell


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


def add_dependency(
    target_name: str,
    target_path: str,
):
    target_path = f'''"path":"{target_path}"'''
    target_path = "{" + target_path + "}"
    target_path = target_name + ":" + target_path
    target_path = "'" + target_path + "'"

    shell.run_script(
        [
            "dart pub add",
            target_path,
        ]
    )
