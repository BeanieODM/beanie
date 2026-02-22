"""Generate a changelog entry for a new release.

Fetches PRs merged since the previous tag, uses gpt-4o-mini to produce
a clean one-line summary for each, and prepends the block to
``docs/changelog.md`` in the project's established format.

Usage::

    python scripts/generate_changelog.py \\
        --prev-tag 2.0.1 \\
        --new-version 26.2.0 \\
        --repo BeanieODM/beanie

Environment variables required:
    GH_TOKEN      GitHub personal access token (read:repo is enough)
    OPENAI_API_KEY  OpenAI API key
"""

import argparse
import os
import subprocess
from dataclasses import dataclass
from datetime import date
from typing import List, Set

import requests
from openai import OpenAI

CHANGELOG_PATH = "docs/changelog.md"
PYPI_URL = "https://pypi.org/project/beanie/{version}"

SYSTEM_PROMPT = (
    "You write changelog entries for an open-source Python library. "
    "Given a pull request title and optional description, produce a single "
    "short sentence (no trailing period) that clearly describes what the PR "
    "does from a user's perspective. "
    "Capitalise only the first word and proper nouns. "
    "Do not start with 'This PR', 'Added', 'Fixed' -- just describe the change. "
    "Examples: "
    "'Fix: preserve fetch_links across chained find() and find_one()', "
    "'Handle aggregation method on the whole collection', "
    "'Bump lazy-model'."
)


@dataclass
class PullRequest:
    """Metadata for a single merged pull request."""

    number: int
    title: str
    body: str
    author: str
    author_url: str
    url: str


def get_commits_since_tag(tag: str) -> List[str]:
    """Return list of commit SHAs merged after ``tag``."""
    result = subprocess.run(
        ["git", "log", f"{tag}..HEAD", "--pretty=format:%H"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    return [sha for sha in result.stdout.splitlines() if sha]


def get_pr_for_commit(
    commit_sha: str, base_url: str, headers: dict
) -> PullRequest | None:
    """Return the PR associated with ``commit_sha``, or None."""
    url = f"{base_url}/commits/{commit_sha}/pulls"
    response = requests.get(url, headers=headers, timeout=15)
    if response.status_code != 200 or not response.json():
        return None
    data = response.json()[0]
    return PullRequest(
        number=data["number"],
        title=data["title"],
        body=data.get("body") or "",
        author=data["user"]["login"],
        author_url=data["user"]["html_url"],
        url=data["html_url"],
    )


def collect_prs(
    commits: List[str], base_url: str, headers: dict
) -> List[PullRequest]:
    """Return deduplicated list of PRs for the given commits."""
    prs: List[PullRequest] = []
    seen: Set[int] = set()
    for sha in commits:
        pr = get_pr_for_commit(sha, base_url, headers)
        if pr and pr.number not in seen:
            seen.add(pr.number)
            prs.append(pr)
    prs.sort(key=lambda p: p.number, reverse=True)
    return prs


def summarise_pr(pr: PullRequest, client: OpenAI) -> str:
    """Use gpt-4o-mini to produce a clean one-line changelog summary."""
    user_content = f"Title: {pr.title}\n\nDescription:\n{pr.body[:1000]}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        max_tokens=80,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def build_changelog_block(
    prs: List[PullRequest], version: str, client: OpenAI
) -> str:
    """Build the full Markdown block for this release."""
    today = date.today().strftime("%Y-%m-%d")
    lines = [f"## [{version}] - {today}"]
    for pr in prs:
        summary = summarise_pr(pr, client)
        lines.append(f"### {summary}")
        lines.append(f"- Author - [{pr.author}]({pr.author_url})")
        lines.append(f"- PR <{pr.url}>")
    lines.append(f"\n[{version}]: {PYPI_URL.format(version=version)}")
    return "\n".join(lines)


def prepend_to_changelog(block: str) -> None:
    """Insert ``block`` after the ``# Changelog`` header in the changelog file."""
    content = open(CHANGELOG_PATH).read()
    # Find the first version section and insert before it
    insert_pos = content.index("\n## ")
    new_content = (
        content[:insert_pos] + "\n\n" + block + "\n" + content[insert_pos:]
    )
    open(CHANGELOG_PATH, "w").write(new_content)


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prev-tag", required=True, help="Previous git tag")
    parser.add_argument(
        "--new-version", required=True, help="New version string"
    )
    parser.add_argument(
        "--repo",
        default="BeanieODM/beanie",
        help="GitHub repo in owner/name format",
    )
    args = parser.parse_args()

    gh_token = os.environ["GH_TOKEN"]
    openai_key = os.environ["OPENAI_API_KEY"]

    headers = {
        "Authorization": f"Bearer {gh_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    base_url = f"https://api.github.com/repos/{args.repo}"
    client = OpenAI(api_key=openai_key)

    print(f"Collecting commits since {args.prev_tag}...")
    commits = get_commits_since_tag(args.prev_tag)
    print(f"Found {len(commits)} commits")

    prs = collect_prs(commits, base_url, headers)
    print(f"Found {len(prs)} unique PRs")

    if not prs:
        print("No PRs found, skipping changelog update")
        return

    print("Generating changelog block with gpt-4o-mini...")
    block = build_changelog_block(prs, args.new_version, client)
    print(block)

    prepend_to_changelog(block)
    print(f"Updated {CHANGELOG_PATH}")


if __name__ == "__main__":
    main()
