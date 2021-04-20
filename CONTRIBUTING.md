## Test each feature

Each feature must be tested in a separate unit test. Even if it looks like other tests are covering it now. This strategy guarantees that:
- All the features will be covered 
- Independency of other features and test changes.

## Use pre-commit

Please, use pre-commit. To set it up, run:

```shell
poetry install
pre-commit install
```

## Single commit

Please, squash your commits to a single one. The instructions can be found [here](https://www.internalpointers.com/post/squash-commits-into-one-git) or [here](https://medium.com/@slamflipstrom/a-beginners-guide-to-squashing-commits-with-git-rebase-8185cf6e62ec)
