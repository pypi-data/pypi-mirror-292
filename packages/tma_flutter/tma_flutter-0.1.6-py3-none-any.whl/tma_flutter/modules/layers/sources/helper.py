import os
from pathlib import Path
from tma_flutter.modules.targets.interface.sources import interface
from tma_flutter.modules.targets.test.sources import test
from tma_flutter.modules.targets.view.sources import view
from tma_flutter.modules.targets.example.sources import example
from tma_flutter.modules.targets.feature.sources import feature


def make_domain_module(
    module_name: str,
    layer_name: str,
):
    current_path = Path(os.getcwd())
    module_path = current_path.joinpath(layer_name).joinpath(module_name)
    Path(module_path).mkdir(parents=True, exist_ok=True)
    os.chdir(module_path)

    feature_name = feature.name(module_name)
    test_name = test.name(module_name)
    interface_name = interface.name(module_name)

    feature.make_target(feature_name)
    test.make_target(test_name)
    interface.make_target(interface_name)

    feature.copy_template(
        feature_name=feature_name,
        interface_name=interface_name,
    )
    test.copy_template(
        feature_name=feature_name,
    )
    interface.copy_template(
        interface_name=interface_name,
    )

    feature.add_dependency(
        interface_name=interface_name,
    )
    test.add_dependency(
        feature_name=feature_name,
        interface_name=interface_name,
    )


def make_presentation_module(module_name: str):
    current_path = Path(os.getcwd())
    module_path = current_path.joinpath("presentation").joinpath(module_name)
    Path(module_path).mkdir(parents=True, exist_ok=True)
    os.chdir(module_path)

    example_name = example.name(module_name)
    view_name = view.name(module_name)
    feature_name = feature.name(module_name)
    test_name = test.name(module_name)
    interface_name = interface.name(module_name)

    example.make_target(example_name)
    view.make_target(view_name)
    feature.make_target(feature_name)
    test.make_target(test_name)
    interface.make_target(interface_name)

    example.copy_template(
        example_name=example_name,
        view_name=view_name,
    )
    view.copy_template(
        view_name=view_name,
        feature_name=feature_name,
    )
    feature.copy_template(
        feature_name=feature_name,
        interface_name=interface_name,
    )
    test.copy_template(
        feature_name=feature_name,
    )
    interface.copy_template(
        interface_name=interface_name,
    )

    example.add_view_dependency(
        view_name=view_name,
    )
    view.add_dependency(
        feature_name=feature_name,
    )
    feature.add_dependency(
        interface_name=interface_name,
    )
    test.add_dependency(
        feature_name=feature_name,
        interface_name=interface_name,
    )
