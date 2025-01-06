import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import List

import requests  # type: ignore


@dataclass
class PullRequest:
    number: int
    title: str
    user: str
    user_url: str
    url: str


class ChangelogGenerator:
    def __init__(
        self,
        username: str,
        repository: str,
        current_version: str,
        new_version: str,
    ):
        self.username = username
        self.repository = repository
        self.base_url = f"https://api.github.com/repos/{username}/{repository}"
        self.current_version = current_version
        self.new_version = new_version
        self.commits = self.get_commits_after_tag(current_version)
        self.prs = [self.get_pr_for_commit(commit) for commit in self.commits]

    def get_commits_after_tag(self, tag: str) -> List[str]:
        result = subprocess.run(
            ["git", "log", f"{tag}..HEAD", "--pretty=format:%H"],
            stdout=subprocess.PIPE,
            text=True,
        )
        return result.stdout.split()

    def get_pr_for_commit(self, commit_sha: str) -> PullRequest:
        url = f"{self.base_url}/commits/{commit_sha}/pulls"
        response = requests.get(url)
        response.raise_for_status()
        pr_data = response.json()[0]
        return PullRequest(
            number=pr_data["number"],
            title=pr_data["title"],
            user=pr_data["user"]["login"],
            user_url=pr_data["user"]["html_url"],
            url=pr_data["html_url"],
        )

    def generate_changelog(self) -> str:
        markdown = f"\n## [{self.new_version}] - {datetime.now().strftime('%Y-%m-%d')}\n"
        for pr in self.prs:
            markdown += (
                f"### {pr.title.capitalize()}\n"
                f"- Author - [{pr.user}]({pr.user_url})\n"
                f"- PR <{pr.url}>\n"
            )
        markdown += f"\n[{self.new_version}]: https://pypi.org/project/{self.repository}/{self.new_version}\n"
        return markdown


if __name__ == "__main__":
    generator = ChangelogGenerator(
        username="BeanieODM",
        repository="beanie",
        current_version="1.29.0",
        new_version="1.30.0",
    )

    changelog = generator.generate_changelog()
    print(changelog)
