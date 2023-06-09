pydoc-markdown
cd docs/build

remote_repo="https://x-access-token:${GITHUB_TOKEN}@${GITHUB_DOMAIN:-"github.com"}/${GITHUB_REPOSITORY}.git"
git remote rm origin
git remote add origin "${remote_repo}"
mkdocs gh-deploy --force