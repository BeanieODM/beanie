import subprocess
import sys
from pathlib import Path

import requests  # type: ignore

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
import tomli_w
from gh import GitHubHandler


class SemVer:
    def __init__(self, version: str):
        self.version = version
        self.major, self.minor, self.patch = map(int, self.version.split("."))

    def increment_minor(self):
        return SemVer(f"{self.major}.{self.minor + 1}.0")

    def __str__(self):
        return self.version

    def __eq__(self, other):
        return self.version == other.version

    def __gt__(self, other):
        return (
            (self.major > other.major)
            or (self.major == other.major and self.minor > other.minor)
            or (
                self.major == other.major
                and self.minor == other.minor
                and self.patch > other.patch
            )
        )


class VersionHandler:
    PACKAGE_NAME = "beanie"
    ROOT_PATH = Path(__file__).parent.parent.parent.parent

    def __init__(self):
        self.pyproject = self.ROOT_PATH / "pyproject.toml"
        self.init_py = self.ROOT_PATH / "beanie" / "__init__.py"
        self.changelog = self.ROOT_PATH / "docs" / "changelog.md"

        self.current_version = self.parse_version_from_pyproject(
            self.pyproject
        )
        self.pypi_version = self.get_version_from_pypi()

        if self.current_version < self.pypi_version:
            raise ValueError("Current version is less than pypi version")

        if self.current_version == self.pypi_version:
            self.current_version = self.current_version.increment_minor()
            self.update_files()
        else:
            self.flit_publish()

    @staticmethod
    def parse_version_from_pyproject(pyproject: Path) -> SemVer:
        with pyproject.open("rb") as f:
            toml_data = tomllib.load(f)
        return SemVer(toml_data["project"]["version"])

    def get_version_from_pypi(self) -> SemVer:
        response = requests.get(
            f"https://pypi.org/pypi/{self.PACKAGE_NAME}/json"
        )
        if response.status_code == 200:
            return SemVer(response.json()["info"]["version"])
        raise ValueError("Can't get version from pypi")

    def update_files(self):
        self.update_pyproject_version()
        self.update_file_versions([self.init_py])
        self.update_changelog()

    def update_pyproject_version(self):
        with self.pyproject.open("rb") as f:
            pyproject = tomllib.load(f)
        pyproject["project"]["version"] = str(self.current_version)
        with self.pyproject.open("wb") as f:
            tomli_w.dump(pyproject, f)

    def update_file_versions(self, files_to_update):
        for file_path in files_to_update:
            content = file_path.read_text()
            content = content.replace(
                str(self.pypi_version), str(self.current_version)
            )
            file_path.write_text(content)

    def update_changelog(self):
        handler = GitHubHandler(
            "BeanieODM",
            "beanie",
            str(self.pypi_version),
            str(self.current_version),
        )
        changelog_content = handler.build_markdown_for_many_prs()

        changelog_lines = self.changelog.read_text().splitlines()
        new_changelog_lines = []
        inserted = False

        for line in changelog_lines:
            new_changelog_lines.append(line)
            if line.strip() == "# Changelog" and not inserted:
                new_changelog_lines.append(changelog_content)
                inserted = True

        self.changelog.write_text("\n".join(new_changelog_lines))
        handler.commit_changes()

    def flit_publish(self):
        subprocess.run(["flit", "publish"], check=True)


if __name__ == "__main__":
    VersionHandler()
