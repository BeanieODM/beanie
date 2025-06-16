import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from beanie import __version__


def parse_version_from_pyproject():
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    with pyproject.open("rb") as f:
        toml_data = tomllib.load(f)
    return toml_data["project"]["version"]


def test_version():
    assert __version__ == parse_version_from_pyproject()
