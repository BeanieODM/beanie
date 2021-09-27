# Changelog

Beanie project changes

## [1.5.0] - 2021-09-27

### Update

- Custom encoders to be able to configure, 
how specific type should be presented in the database

### Implementation

- Author - [Nazar Vovk](https://github.com/Vovcharaa)
- PR - <https://github.com/roman-right/beanie/pull/91>

## [1.4.0] - 2021-09-13

### Added

- Document state management

### Implementation

- PR - <https://github.com/roman-right/beanie/pull/114>

## [1.3.0] - 2021-09-08

### Added

- Active record pattern

### Implementation

- Issue - <https://github.com/roman-right/beanie/issues/110>

## [1.2.8] - 2021-09-01

### Fix

- Delete's return annotation

### Implementation

- PR - <https://github.com/roman-right/beanie/pull/109>

## [1.2.7] - 2021-09-01

### Update

- Annotations for update and delete

### Implementation

- Author - [Anthony Shaw](https://github.com/tonybaloney)
- PR - <https://github.com/roman-right/beanie/pull/106>

## [1.2.6] - 2021-08-25

### Fixed

- MongoDB 5.0 in GH actions

### Implementation

- PR - <https://github.com/roman-right/beanie/pull/100>

## [1.2.5] - 2021-07-21

### Fixed

- Indexed fields work with aliases now

### Implementation

- Author - [Kira](https://github.com/KiraPC)
- Issue - <https://github.com/roman-right/beanie/issues/96>

## [1.2.4] - 2021-07-13

### Fixed

- Aggregation preset method outputs

### Implementation

- Issue - <https://github.com/roman-right/beanie/issues/91>

## [1.2.3] - 2021-07-08

### Fixed

- Pyright issues

### Added

- Doc publishing on merge to the main branch 

### Implementation

- Issue - <https://github.com/roman-right/beanie/issues/87>
- Issue - <https://github.com/roman-right/beanie/issues/70>

## [1.2.2] - 2021-07-06

### Fixed

- Bool types in search criteria

### Implementation

- Issue - <https://github.com/roman-right/beanie/issues/85>

## [1.2.1] - 2021-07-06

### Fixed

- Document, FindQuery, Aggregation typings

### Implementation

- Author - [Kira](https://github.com/KiraPC)
- Issue - <https://github.com/roman-right/beanie/issues/69>

## [1.2.0] - 2021-06-25

### Added

- Upsert

### Implementation

- Issue - <https://github.com/roman-right/beanie/issues/64>

## [1.1.6] - 2021-06-21

### Fix

- Pydantic dependency version ^1.5

### Implementation

- PR - <https://github.com/roman-right/beanie/pull/71>

## [1.1.5] - 2021-06-17

### Fix

- Convert document id to the right type in the `get()` method

### Implementation

- ISSUE - <https://github.com/roman-right/beanie/issues/65>

## [1.1.4] - 2021-06-15

### Changed

- Stricter flake8 and fixing resulting errors

### Implementation

- Author - [Joran van Apeldoorn](https://github.com/jorants)
- PR - <https://github.com/roman-right/beanie/pull/62>

## [1.1.3] - 2021-06-15

### Added

- MyPy to pre-commit

### Fixed

- Typing errors

### Implementation

- Author - [Joran van Apeldoorn](https://github.com/jorants)
- PR - <https://github.com/roman-right/beanie/pull/54>

## [1.1.2] - 2021-06-14

### Changed

- Skip migration test when transactions not available

### Implementation

- Author - [Joran van Apeldoorn](https://github.com/jorants)
- PR - <https://github.com/roman-right/beanie/pull/50>

## [1.1.1] - 2021-06-14

### Added

- Save method

### Implementation

- Author - [Joran van Apeldoorn](https://github.com/jorants)
- PR - <https://github.com/roman-right/beanie/pull/47>

## [1.1.0] - 2021-06-02

### Added

- Custom id types.

### Implementation

- Issue - <https://github.com/roman-right/beanie/issues/12>

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

- Document class was
  reworked. [Documentation](https://roman-right.github.io/beanie/api/document/)

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

[1.1.0]: https://pypi.org/project/beanie/1.1.0

[1.1.1]: https://pypi.org/project/beanie/1.1.1

[1.1.2]: https://pypi.org/project/beanie/1.1.2

[1.1.3]: https://pypi.org/project/beanie/1.1.3

[1.1.4]: https://pypi.org/project/beanie/1.1.4

[1.1.5]: https://pypi.org/project/beanie/1.1.5

[1.1.6]: https://pypi.org/project/beanie/1.1.6

[1.2.0]: https://pypi.org/project/beanie/1.2.0

[1.2.1]: https://pypi.org/project/beanie/1.2.1

[1.2.2]: https://pypi.org/project/beanie/1.2.2

[1.2.3]: https://pypi.org/project/beanie/1.2.3

[1.2.4]: https://pypi.org/project/beanie/1.2.4

[1.2.5]: https://pypi.org/project/beanie/1.2.5

[1.2.6]: https://pypi.org/project/beanie/1.2.6

[1.2.7]: https://pypi.org/project/beanie/1.2.7

[1.2.8]: https://pypi.org/project/beanie/1.2.8

[1.3.0]: https://pypi.org/project/beanie/1.3.0

[1.4.0]: https://pypi.org/project/beanie/1.4.0

[1.5.0]: https://pypi.org/project/beanie/1.5.0