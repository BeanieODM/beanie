# Development

Hopefully, you have landed here because you would like to help out with the development of Beanie. Whether through adding new features, fixing bugs, or extending documentation, your help is really appreciated! Please read this page carefully. If you have any questions, drop by on [the Discord](https://discord.com/invite/29mMrEBvr4).

Also, please read the [Code of Conduct](code-of-conduct.md).

## Setting up the development environment

We assume you are familiar with the general forking and pull request workflow for submitting to open-source projects. If not, don't worry, there are plenty of good guides available. Maybe check out [this one](https://www.atlassian.com/git/tutorials/comparing-workflows/forking-workflow).

All the dependencies and build configs are set in the `pyproject.toml` file. There are three main dependency sections there:

- dependencies: for the dependencies required to run Beanie
- test: for the dependencies required to run tests
- doc: for the dependencies required to build the documentation

And there are other extra dependency sections for Beanie batteries. For example, the `queue` section contains dependencies that extend features of Beanie with a queue.

To install all required dependencies, including test dependencies, you need to have uv installed.
Please find installation instruction for your platform [here](https://docs.astral.sh/uv/getting-started/installation/).

After uv installation, run the following command in the root directory of the Beanie project:

```shell
uv sync --group test
```

To install dependencies required for building the documentation, run:

```shell
uv sync --group doc
```

To install everything run:

```shell
uv sync --all-extras --dev
```

### Database connection

To run tests and use Beanie in general, you will need an accessible MongoDB database. To use migrations, you will need a connection to a Replica Set or Mongos instance. All tests assume that the database is hosted locally on port `27017` and do not require authentication.

## Testing

Beanie uses [pytest](https://docs.pytest.org) for unit testing. To ensure the stability of Beanie, each added feature must be tested in a separate unit test, even if it looks like other tests are covering it now. This strategy guarantees that:

- All the features will be covered and stay covered.
- There is independence from other features and test cases.

To run the test suite, make sure that you have MongoDB running and run `uv run pytest`.

## Submitting new code

You can submit your changes through a pull request on GitHub. Please take into account the following sections.

### Use pre-commit

To ensure code consistency, Beanie uses Black and Ruff through pre-commit. To set it up, run:

```shell
uv run pre-commit install
```

This will add the pre-commit command to your git's pre-commit hooks and make sure you never forget to run these.

### Single commit

To make the pull request reviewing easier and keep the version tree clean, your pull request should consist of a single commit. It is natural that your branch might contain multiple commits, so you will need to squash these into a single commit. Instructions can be found [here](https://www.internalpointers.com/post/squash-commits-into-one-git) or [here](https://medium.com/@slamflipstrom/a-beginners-guide-to-squashing-commits-with-git-rebase-8185cf6e62ec).

### Add documentation

Please write clear documentation for any new functionality you add. Docstrings will be converted to the API documentation, but more human-friendly documentation might also be needed! See the section below.

## Working on the documentation

The documentation is generated using `pydoc-markdown`. To see a preview of any edits you make, you can run:

```shell
uv run pydoc-markdown --server
```

and visit the printed address (usually `localhost:8000`) in your browser. Beware, the auto-recompiling might not work for everyone.
This will automatically generate the API documentation from the source. All other documentation should be written by hand. The documentation is compiled using `mkdocs` behind the scenes. To change the table of contents or other options, check out `pydoc-markdown.yml`.