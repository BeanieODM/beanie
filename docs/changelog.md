# Changelog
Beanie project changes

## [0.4.3] - 2021-04-25
### Fixed
- PydanticObjectId openapi generation

## [0.4.2] - 2021-04-20
### Added
- Python ^3.6.1 support.

### Fixed
- Documents init order in migrations

## [0.4.1] - 2021-04-19
### Added
- Projections support to reduce database load. [Issue](https://github.com/roman-right/beanie/issues/16). **Thanks [Nicholas Smith](https://github.com/nzsmith1)**

## [0.4.0] - 2021-04-18
### Added
- [ODM Documentation](https://roman-right.github.io/beanie/documentation/odm/)

### Changed
- [Documentation](https://roman-right.github.io/beanie/)

## [0.4.0b1] - 2021-04-14
### Added
- Migrations. [Documentation](https://roman-right.github.io/beanie/quickstart/migrations/).
- `inspect_collection` Document method
- `count_documents` Document method

### Changed
- Session can be provided to the most of the Document methods

### Removed
- Internal `DocumentMeta` class.

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
[0.3.4]: https://pypi.org/project/beanie/0.3.4
[0.4.0b1]: https://pypi.org/project/beanie/0.4.0b1
[0.4.0]: https://pypi.org/project/beanie/0.4.0
[0.4.1]: https://pypi.org/project/beanie/0.4.1
[0.4.2]: https://pypi.org/project/beanie/0.4.2
[0.4.3]: https://pypi.org/project/beanie/0.4.3