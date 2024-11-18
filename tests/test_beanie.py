from pathlib import Path

import toml

from beanie import __version__


def parse_version_from_pyproject():
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    toml_data = toml.loads(pyproject.read_text())
    return toml_data["project"]["version"]


def test_version():
    assert __version__ == parse_version_from_pyproject()
