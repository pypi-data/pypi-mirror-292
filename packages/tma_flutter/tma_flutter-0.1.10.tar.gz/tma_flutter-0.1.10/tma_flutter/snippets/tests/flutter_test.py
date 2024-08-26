import yaml
from pathlib import Path
from tma_flutter.snippets.sources import flutter


def test_add_dependency():
    # given
    test_path = Path(__file__).absolute().parent
    pubspec_path = test_path.joinpath("mock_pubspec.yaml")
    mock_pubspec = {"mock": "mock"}
    with open(pubspec_path, "w") as f:
        yaml.dump(mock_pubspec, f)
    target_names = ["target1", "target2", "target3"]

    # when
    flutter.add_dependencies(target_names, pubspec_path)

    # then
    target_dict = {name: "any" for name in target_names}
    with open(pubspec_path, "r") as f:
        result = yaml.safe_load(f)
        assert result["dependencies"] == target_dict
    pubspec_path.unlink()
