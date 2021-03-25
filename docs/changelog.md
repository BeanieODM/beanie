# Changelog
Beanie project changes

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