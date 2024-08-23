# Publishing a New Version of Beanie

This guide provides step-by-step instructions on how to prepare and publish a new version of Beanie. Before starting, ensure that you have the necessary permissions to update the repository.

## 1. Prepare a New Version PR

To publish a new version of Beanie, you need to create a pull request (PR) with the following updates:

### 1.1 Update the Version in `pyproject.toml`

1. Open the [`pyproject.toml`](https://github.com/BeanieODM/beanie/blob/main/pyproject.toml) file.
2. Update the `version` field to the new version number.

### 1.2 Update the Version in the `__init__.py` File

1. Open the [`__init__.py`](https://github.com/BeanieODM/beanie/blob/main/beanie/__init__.py) file.
2. Update the `__version__` variable to the new version number.

### 1.3 Update the Changelog

To update the changelog, follow these steps:

#### 1.3.1 Set the Version in the Changelog Script

1. Open the [`scripts/generate_changelog.py`](https://github.com/BeanieODM/beanie/blob/main/scripts/generate_changelog.py) file.
2. Set the `current_version` to the current version and `new_version` to the new version in the script.

#### 1.3.2 Run the Changelog Script

1. Run the following command to generate the updated changelog:

   ```bash
   python scripts/generate_changelog.py
   ```

2. The script will generate the changelog for the new version.

#### 1.3.3 Update the Changelog File

1. Open the [`changelog.md`](https://github.com/BeanieODM/beanie/blob/main/docs/changelog.md) file.
2. Copy the generated changelog and paste it at the top of the `changelog.md` file.

### 1.4 Create and Submit the PR

Once you have made the necessary updates, create a PR with a descriptive title and summary of the changes. Ensure that all checks pass before merging the PR.

## 2. Publishing the Version

After the PR has been merged, respective GH action will publish it to the PyPI.

## 3. Create a Git Tag and GitHub Release

After the version has been published:

1. Pull the latest changes from the `master` branch:
   ```bash
   git pull origin master
   ```

2. Create a new Git tag with the version number:
   ```bash
   git tag -a v1.xx.y -m "Release v1.xx.y"
   ```

3. Push the tag to the remote repository:
   ```bash
   git push origin v1.xx.y
   ```

4. Create a new release on GitHub using the GitHub interface.