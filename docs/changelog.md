# Changelog

Beanie project changes

## [1.0.6] - 2021-06-01

### Fixed

- Typo in the module name.

### Implementation

- Author - [Joran van Apeldoorn](https://github.com/jorants)
- PR - <https://github.com/roman-right/beanie/pull/44>

## [1.0.5] - 2021-05-25

### Fixed

- Typing.

### Implementation

- PR - <https://github.com/roman-right/beanie/pull/40>

## [1.0.4] - 2021-05-18

### Fixed

- `aggregation_model` -> `projection_model`

### Implementation

- PR - <https://github.com/roman-right/beanie/pull/39>

## [1.0.3] - 2021-05-16

### Added

- Index kwargs in the Indexed field

### Implementation

- Author - [Michael duPont](https://github.com/flyinactor91)
- PR - <https://github.com/roman-right/beanie/pull/32>

## [1.0.2] - 2021-05-16

### Fixed

- Deprecated import

### Implementation

- Author - [Oliver Andrich](https://github.com/oliverandrich)
- PR - <https://github.com/roman-right/beanie/pull/33>

## [1.0.1] - 2021-05-14

### Fixed

- `Document` self annotation

### Implementation

- Issue - <https://github.com/roman-right/beanie/issues/29>

## [1.0.0] - 2021-05-10

### Added

- QueryBuilder

### Changed

- Document class was reworked. [Documentation](https://roman-right.github.io/beanie/api/document/)

### Implementation

- PR - <https://github.com/roman-right/beanie/pull/27>

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

- Projections support to reduce database load

### Implementation

- Author - [Nicholas Smith](https://github.com/nzsmith1)
- Issue - <https://github.com/roman-right/beanie/issues/16>

## [0.4.0] - 2021-04-18

### Added

- [ODM Documentation](https://roman-right.github.io/beanie/documentation/odm/)

### Changed

- [Documentation](https://roman-right.github.io/beanie/)

## [0.4.0b1] - 2021-04-14

### Added

- Migrations
- `inspect_collection` Document method
- `count_documents` Document method

### Changed

- Session can be provided to the most of the Document methods

### Removed

- Internal `DocumentMeta` class.

## [0.3.4] - 2021-04-09

### Changed

- `Indexed(...)` field supports index types.

### Implementation

- Author - [Joran van Apeldoorn](https://github.com/jorants)

## [0.3.3] - 2021-04-09

### Added

- Simple indexes via type hints.

### Implementation

- Author - [Joran van Apeldoorn](https://github.com/jorants)

## [0.3.2] - 2021-03-25

### Added

- `init_beanie` supports also lists of strings with model paths as
  the` document_models` parameter.

### Implementation

- Author - [Mohamed Nesredin](https://github.com/Mohamed-Kaizen)

## [0.3.1] - 2021-03-21

### Added

- `skip`, `limit` and `sort` parameters in the `find_many` and `find_all`
  methods. [Documentation](https://roman-right.github.io/beanie/#find-many-documents)

## [0.3.0] - 2021-03-19

### Added

- `Collection` - internal class of the `Document` to set up additional
  properties.
- Indexes support.

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

[1.0.0]: https://pypi.org/project/beanie/1.0.0

[1.0.1]: https://pypi.org/project/beanie/1.0.1

[1.0.2]: https://pypi.org/project/beanie/1.0.2

[1.0.3]: https://pypi.org/project/beanie/1.0.3

[1.0.4]: https://pypi.org/project/beanie/1.0.4

[1.0.5]: https://pypi.org/project/beanie/1.0.5

[1.0.6]: https://pypi.org/project/beanie/1.0.6