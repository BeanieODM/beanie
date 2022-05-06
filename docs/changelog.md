# Changelog

Beanie project

## [1.11.0] - 2022-05-06

### Features

- Multi-model mode
- Views

## [1.10.9] - 2022-05-06

### Improvement

- pymongo_kwargs for insert many

## [1.10.8] - 2022-04-13

### Fix

- Match step after limit step

### Implementation

- ISSUE <https://github.com/roman-right/beanie/issues/241>

## [1.10.7] - 2022-04-12

### Fix

- Empty update fails on revision id turned on

### Implementation

- ISSUE <https://github.com/roman-right/beanie/issues/239>

## [1.10.6] - 2022-04-12

### Improvement

- Single syntax for find by id

### Implementation

- PR <https://github.com/roman-right/beanie/pull/238>

## [1.10.5] - 2022-04-11

### Improvement

- Avoid creating redundant query object

### Implementation

- Author - [amos402](https://github.com/amos402)
- PR <https://github.com/roman-right/beanie/pull/235>

## [1.10.4] - 2022-03-24

### Improvement

- Allow custom MigrationNode for build

### Implementation

- Author - [amos402](https://github.com/amos402)
- PR <https://github.com/roman-right/beanie/pull/234>

## [1.10.3] - 2022-02-29

### Improvement

- Delete action

### Implementation

- ISSUE <https://github.com/roman-right/beanie/issues/225>

## [1.10.2] - 2022-02-28

### Improvement

- Bulk writer for upsert

### Implementation

- ISSUE <https://github.com/roman-right/beanie/issues/224>

## [1.10.1] - 2022-02-24

### Improvement

- Skip actions

### Implementation

- Author - [Paul Renvoisé](https://github.com/paul-finary)
- PR <https://github.com/roman-right/beanie/pull/218>

## [1.10.0] - 2022-02-24

### Improvement

- Timeseries collections support
- Pymongo kwargs for find, aggregate, update and delete operations

### Implementation

- PR <https://github.com/roman-right/beanie/pull/214>

## [1.9.2] - 2022-02-22

### Improvement

- First or None for find queries

### Implementation

- ISSUE - <https://github.com/roman-right/beanie/issues/207>

## [1.9.1] - 2022-02-11

### Improvement

- Add support for py.typed file

### Implementation

- Author - [Nicholas Smith](https://github.com/nzsmith1)
- PR - <https://github.com/roman-right/beanie/pull/201>

## [1.9.0] - 2022-02-11

### Breaking Change

- Property allow_index_dropping to be default False. Indexes will not be deleted by default

### Implementation

- Author - [Nicholas Smith](https://github.com/nzsmith1)
- PR - <https://github.com/roman-right/beanie/pull/196>

## [1.8.13] - 2022-02-10

### Improvement

- Add state_management_replace_objects setting

### Implementation

- Author - [Paul Renvoisé](https://github.com/paul-finary)
- PR - <https://github.com/roman-right/beanie/pull/197>

## [1.8.12] - 2022-01-06

### Improvement

- Add exclude_hidden to dict() to be able to keep hidden fields hidden when the exclude parameter set

### Implementation

- Author - [Yallxe](https://github.com/yallxe)
- PR - <https://github.com/roman-right/beanie/pull/178>


## [1.8.11] - 2021-12-30

### Improvement

- Only safe pydantic version are allowed. https://github.com/samuelcolvin/pydantic/security/advisories/GHSA-5jqp-qgf6-3pvh

## [1.8.10] - 2021-12-29

### Fix

- Revision didn't swap previous revision id and the current one on getting objects from db

## [1.8.9] - 2021-12-23

### Improvement

- Deep search of updates for the `save_changes()` method

### Kudos

- Thanks, [Tigran Khazhakyan](https://github.com/tigrankh) for the deep search algo here

## [1.8.8] - 2021-12-17

### Added

- Search by linked documents fields (for pre-fetching search only)

## [1.8.7] - 2021-12-12

### Fixed

- Binary encoder issue

## [1.8.6] - 2021-12-14

### Improved

- Encoder

## [1.8.5] - 2021-12-09

### Added

- `Optional[Link[Sample]]` is allowed field type syntax now


## [1.8.4] - 2021-12-12

### Fixed

- DateTime bson type

## [1.8.3] - 2021-12-07

### Added

- Subclasses inherit event-based actions

## [1.8.2] - 2021-12-04

### Fixed

- Encoder priority

## [1.8.1] - 2021-11-30

### Added

- Key-based call of subfields in the query builders

## [1.8.0] - 2021-11-30

### Added

- Relations

### Implementation

- PR <https://github.com/roman-right/beanie/pull/149>

## [1.7.2] - 2021-11-03

### Fixed

- `revision_id` is hidden in the api schema

### Implementation

- ISSUE <https://github.com/roman-right/beanie/issues/136>

## [1.7.1] - 2021-11-02

### Fixed

- `revision_id` is hidden in the outputs

### Implementation

- ISSUE <https://github.com/roman-right/beanie/issues/136>

## [1.7.0] - 2021-10-12

### Added

- Cache
- Bulk write
- `exists` - find query's method

### Implementation

- PR - <https://github.com/roman-right/beanie/pull/123>
- PR - <https://github.com/roman-right/beanie/pull/122>
- PR - <https://github.com/roman-right/beanie/pull/129>

## [1.6.1] - 2021-10-06

### Update

- Customization support. It is possible to change query builder classes, 
used in the classes, which are inherited from the Document class

### Implementation

- PR - <https://github.com/roman-right/beanie/pull/125>

## [1.6.0] - 2021-09-30

### Update

- Validate on save

### Implementation

- PR - <https://github.com/roman-right/beanie/pull/118>

## [1.5.1] - 2021-09-27

### Update

- Simplification for init_beanie function

### Implementation

- PR - <https://github.com/roman-right/beanie/pull/104>

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

[1.5.1]: https://pypi.org/project/beanie/1.5.1

[1.6.0]: https://pypi.org/project/beanie/1.6.0

[1.6.1]: https://pypi.org/project/beanie/1.6.1

[1.7.0]: https://pypi.org/project/beanie/1.7.0

[1.7.1]: https://pypi.org/project/beanie/1.7.1

[1.7.2]: https://pypi.org/project/beanie/1.7.2

[1.8.0]: https://pypi.org/project/beanie/1.8.0

[1.8.1]: https://pypi.org/project/beanie/1.8.1

[1.8.2]: https://pypi.org/project/beanie/1.8.2

[1.8.3]: https://pypi.org/project/beanie/1.8.3

[1.8.4]: https://pypi.org/project/beanie/1.8.4

[1.8.5]: https://pypi.org/project/beanie/1.8.5

[1.8.6]: https://pypi.org/project/beanie/1.8.6

[1.8.7]: https://pypi.org/project/beanie/1.8.7

[1.8.8]: https://pypi.org/project/beanie/1.8.8

[1.8.9]: https://pypi.org/project/beanie/1.8.9

[1.8.10]: https://pypi.org/project/beanie/1.8.10

[1.8.11]: https://pypi.org/project/beanie/1.8.11

[1.8.12]: https://pypi.org/project/beanie/1.8.12

[1.8.13]: https://pypi.org/project/beanie/1.8.13

[1.9.0]: https://pypi.org/project/beanie/1.9.0

[1.9.1]: https://pypi.org/project/beanie/1.9.1

[1.9.2]: https://pypi.org/project/beanie/1.9.2

[1.10.0]: https://pypi.org/project/beanie/1.10.0

[1.10.1]: https://pypi.org/project/beanie/1.10.1

[1.10.2]: https://pypi.org/project/beanie/1.10.2

[1.10.3]: https://pypi.org/project/beanie/1.10.3

[1.10.4]: https://pypi.org/project/beanie/1.10.4

[1.10.5]: https://pypi.org/project/beanie/1.10.5

[1.10.6]: https://pypi.org/project/beanie/1.10.6

[1.10.7]: https://pypi.org/project/beanie/1.10.7

[1.10.8]: https://pypi.org/project/beanie/1.10.8

[1.11.0]: https://pypi.org/project/beanie/1.11.0

[1.10.9]: https://pypi.org/project/beanie/1.10.9