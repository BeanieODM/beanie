# Development

Hopefully you have landed here because you would like to help out with the development of Beanie. Whether through adding new features, fixing bugs, or extending documentation, your help is really appreciated! Please read this page carefully. If you have any questions, drop by on [the discord.](https://discord.com/invite/ZTTnM7rMaz)

## Setting up the development environment

We assume you are familiar with the general forking and pull request workflow for submitting to open-source projects. If not, don't worry, there are plenty of good guides available, maybe check out [this one.](https://www.atlassian.com/git/tutorials/comparing-workflows/forking-workflow).

Beanie uses [poetry](https://python-poetry.org/) to manage dependencies and packaging.
If you are not familiar with poetry, it might be usefully to read up on it before working on Beanie, but here is a quick guide to get you started.

Ensure poetry is installed globally:
```shell
pip install --user poetry 
```

To install all required dependencies in a virtual informant, run the following command in the root of the Beanie project
```shell
poetry install
```

To add a dependency you can use 
```shell
poetry add <package name>
```
which takes an optional `-D` flag for development only dependencies.

To run commands like `pytest` or `black` you have to run them using the virtual environment which contains the dependencies and Beanie. You can do this in two ways, you may run `poetry shell` to activate the environment for the current shell, or you can run them in a one-off fashion as such `poetry run pytest`.

### Database connection

To run tests, and use Beanie in general, you will need an accessible MongoDB database. 


## Testing

Beanie uses pytest for unit testing. To ensure the stability of Beanie, each added feature must be tested in a separate unit test. Even if it looks like other tests are covering it now. This strategy guarantees that:

- All the features will be covered and stay covered. 
- Independence from other features and test cases.



## Use pre-commit

Please, use pre-commit. To set it up, run:

```shell
poetry install
pre-commit install
```

## Single commit

Please, squash your commits to a single one. The instructions can be found [here](https://www.internalpointers.com/post/squash-commits-into-one-git) or [here](https://medium.com/@slamflipstrom/a-beginners-guide-to-squashing-commits-with-git-rebase-8185cf6e62ec)
