poetry run pydoc-markdown
cd docs/build

remote_repo="https://x-access-token:${GITHUB_TOKEN}@${GITHUB_DOMAIN:-"github.com"}/${GITHUB_REPOSITORY}.git"
echo "${remote_repo}"
git remote rm origin
git remote add origin "${remote_repo}"

poetry run mkdocs gh-deploy