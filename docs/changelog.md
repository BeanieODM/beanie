# Changelog
Beanie project changes

## [0.3.4] - 2021-04-09
### Changed
- `Indexed(...)` field supports index types. [Documentation](https://roman-right.github.io/beanie/#indexes). **Thanks [Joran van Apeldoorn](https://github.com/jorants)**

## [0.3.3] - 2021-04-09
### Added
- Simple indexes via type hints. [Documentation](https://roman-right.github.io/beanie/#indexes). **Thanks [Joran van Apeldoorn](https://github.com/jorants)**

## [0.3.2] - 2021-03-25
### Added
- `init_beanie` supports also lists of strings with model paths as the` document_models` parameter. [Documentation](https://roman-right.github.io/beanie/#init). **Thanks [Mohamed Nesredin](https://github.com/Mohamed-Kaizen)**

## [0.3.1] - 2021-03-21
### Added
- `skip`, `limit` and `sort` parameters in the `find_many` and `find_all` methods. [Documentation](https://roman-right.github.io/beanie/#find-many-documents)

## [0.3.0] - 2021-03-19
### Added
- `Collection` - internal class of the `Document` to set up additional properties. [Documentation](https://roman-right.github.io/beanie/#collection-setup).
- Indexes support. [Documentation](https://roman-right.github.io/beanie/#indexes).

### Changed
- **Breaking change:** `init_beanie` is async function now.

### Deprecated
- Internal `DocumentMeta` class. Will be removed in **0.4.0**.

[0.3.0]: https://pypi.org/project/beanie/0.3.0
[0.3.1]: https://pypi.org/project/beanie/0.3.1
[0.3.2]: https://pypi.org/project/beanie/0.3.2
[0.3.3]: https://pypi.org/project/beanie/0.3.3
[0.3.4]: https://pypi.org/project/beanie/0.3.3