# Changelog

Beanie project

## [1.29.0] - 2025-01-06
### Fix serialization of link/backlink and openapi schema generation
- Author - [staticxterm](https://github.com/staticxterm)
- PR <https://github.com/BeanieODM/beanie/pull/1080>
### Fix: `owner` model missing in `init_beanie` in inheritance documentation's inserts example
- Author - [ksayer](https://github.com/ksayer)
- PR <https://github.com/BeanieODM/beanie/pull/1090>
### Make `diacritic_sensitive` parameter optional to support $text operator on cosmos db
- Author - [mykolaskrynnyk](https://github.com/mykolaskrynnyk)
- PR <https://github.com/BeanieODM/beanie/pull/1089>
### Add tests with case of {id} in fastapi path
- Author - [dantetemplar](https://github.com/dantetemplar)
- PR <https://github.com/BeanieODM/beanie/pull/1100>
### Use strings to specify mongodb versions in ci
- Author - [Viicos](https://github.com/Viicos)
- PR <https://github.com/BeanieODM/beanie/pull/1094>
### fix: pydantic 2.10.x breaking change
- Author - [mdaffad](https://github.com/mdaffad)
- PR <https://github.com/BeanieODM/beanie/pull/1095>
### Bulk writer improving & bulk_writer method for document and possibility to bypass mongo document validation + comment parameter
- Author - [CAPITAINMARVEL](https://github.com/CAPITAINMARVEL)
- PR <https://github.com/BeanieODM/beanie/pull/1079>
### Add coverage configuration to pyproject.toml
- Author - [staticxterm](https://github.com/staticxterm)
- PR <https://github.com/BeanieODM/beanie/pull/1091>

[1.29.0]: https://pypi.org/project/beanie/1.29.0

## [1.28.0] - 2024-12-05
### Fix kwargs/args untyped
- Author - [CAPITAINMARVEL](https://github.com/CAPITAINMARVEL)
- PR <https://github.com/BeanieODM/beanie/pull/1049>
### Update pre-commit
- Author - [07pepa](https://github.com/07pepa)
- PR <https://github.com/BeanieODM/beanie/pull/1046>
### Drop support for python 3.7
- Author - [07pepa](https://github.com/07pepa)
- PR <https://github.com/BeanieODM/beanie/pull/1044>
### Add missing type hint to `find_many_in_all` method
- Author - [vasuman](https://github.com/vasuman)
- PR <https://github.com/BeanieODM/beanie/pull/1068>
### Add documentdb compatibility to fetch_links
- Author - [whitfin](https://github.com/whitfin)
- PR <https://github.com/BeanieODM/beanie/pull/1042>
### Fix issues caused by #1044
- Author - [07pepa](https://github.com/07pepa)
- PR <https://github.com/BeanieODM/beanie/pull/1053>
### Feat(skip_index): possibility added to skip index actions
- Author - [jorma16](https://github.com/jorma16)
- PR <https://github.com/BeanieODM/beanie/pull/942>
### Fix pydanticobjectid fields being parsed into str
- Author - [07pepa](https://github.com/07pepa)
- PR <https://github.com/BeanieODM/beanie/pull/1060>
### Modify tests to not raise deprecation warnings
- Author - [07pepa](https://github.com/07pepa)
- PR <https://github.com/BeanieODM/beanie/pull/1047>
### Add python 3.13 and jit into testing
- Author - [07pepa](https://github.com/07pepa)
- PR <https://github.com/BeanieODM/beanie/pull/1051>
### Handle limit and session in .count() method
- Author - [CAPITAINMARVEL](https://github.com/CAPITAINMARVEL)
- PR <https://github.com/BeanieODM/beanie/pull/1040>

[1.28.0]: https://pypi.org/project/beanie/1.28.0

## [1.27.0] - 2024-10-06
### Add tests on all major mongo version
- Author - [07pepa](https://github.com/07pepa)
- PR <https://github.com/BeanieODM/beanie/pull/1034>
### Fix return type from document update
- Author - [CAPITAINMARVEL](https://github.com/CAPITAINMARVEL)
- PR <https://github.com/BeanieODM/beanie/pull/1030>
### Fix expression type hint not allowing some type https://github.com/beanieodm/beanie/issues/1020
- Author - [CAPITAINMARVEL](https://github.com/CAPITAINMARVEL)
- PR <https://github.com/BeanieODM/beanie/pull/1023>
### Fix type hint using pymongo client session instead of motor client session
- Author - [CAPITAINMARVEL](https://github.com/CAPITAINMARVEL)
- PR <https://github.com/BeanieODM/beanie/pull/1022>
### Fix logical operator typing #1000
- Author - [janas-adam](https://github.com/janas-adam)
- PR <https://github.com/BeanieODM/beanie/pull/1021>
### Use session in document insert
- Author - [andraghetti](https://github.com/andraghetti)
- PR <https://github.com/BeanieODM/beanie/pull/1018>
### Use sequence instead of list in init_beanie
- Author - [07pepa](https://github.com/07pepa)
- PR <https://github.com/BeanieODM/beanie/pull/1015>
### Replace deprecated datetime.utcnow with datetime.now
- Author - [adeelsohailahmed](https://github.com/adeelsohailahmed)
- PR <https://github.com/BeanieODM/beanie/pull/1014>
### Fix uniondoc type hint missing in init_beanie and on findinterface
- Author - [CAPITAINMARVEL](https://github.com/CAPITAINMARVEL)
- PR <https://github.com/BeanieODM/beanie/pull/1007>
### Add test to ensure dict with enum keys are encoded properly
- Author - [adeelsohailahmed](https://github.com/adeelsohailahmed)
- PR <https://github.com/BeanieODM/beanie/pull/1001>
### Project publishing instruction + changelog generation script
- Author - [roman-right](https://github.com/roman-right)
- PR <https://github.com/BeanieODM/beanie/pull/998>
### Revert project publishing gh action
- Author - [roman-right](https://github.com/roman-right)
- PR <https://github.com/BeanieODM/beanie/pull/996>
### Extend motor option to beanie
- Author - [Dudesons](https://github.com/Dudesons)
- PR <https://github.com/BeanieODM/beanie/pull/995>
### Fix regex storing
- Author - [07pepa](https://github.com/07pepa)
- PR <https://github.com/BeanieODM/beanie/pull/989>
### Remove links to ko-fi from the project
- Author - [roman-right](https://github.com/roman-right)
- PR <https://github.com/BeanieODM/beanie/pull/986>
### Fix typo in source code comment in inheritance.md
- Author - [fnogatz](https://github.com/fnogatz)
- PR <https://github.com/BeanieODM/beanie/pull/984>
### Fix gh action to grant permissions and use tags
- Author - [roman-right](https://github.com/roman-right)
- PR <https://github.com/BeanieODM/beanie/pull/972>
### Fix: example of find by id and link to finding-documents
- Author - [fredowashere](https://github.com/fredowashere)
- PR <https://github.com/BeanieODM/beanie/pull/970>
### Fix incorrect type serialization when dumping to python
- Author - [07pepa](https://github.com/07pepa)
- PR <https://github.com/BeanieODM/beanie/pull/968>
### Use ruff format instead of black
- Author - [roman-right](https://github.com/roman-right)
- PR <https://github.com/BeanieODM/beanie/pull/962>
### Gh action: set new version and publish on push
- Author - [roman-right](https://github.com/roman-right)
- PR <https://github.com/BeanieODM/beanie/pull/961>
### Feature / fix: allow settings to be inherited and extended (fixes #644)
- Author - [dotKokott](https://github.com/dotKokott)
- PR <https://github.com/BeanieODM/beanie/pull/960>
### Fix: issue #951
- Author - [IterableTrucks](https://github.com/IterableTrucks)
- PR <https://github.com/BeanieODM/beanie/pull/952>
### Allow unordered parameter on bulkwriter
- Author - [thiagosalvatore](https://github.com/thiagosalvatore)
- PR <https://github.com/BeanieODM/beanie/pull/948>
### Fix: set default value in findinterface._inheritance_inited to avoid …
- Author - [Robert-Nogueira](https://github.com/Robert-Nogueira)
- PR <https://github.com/BeanieODM/beanie/pull/935>
### Fix example in multi-model.md
- Author - [gianpaj](https://github.com/gianpaj)
- PR <https://github.com/BeanieODM/beanie/pull/932>
### Add missing type signature to `basefindcomparisonoperator` constructor
- Author - [aaronted009](https://github.com/aaronted009)
- PR <https://github.com/BeanieODM/beanie/pull/925>
### Removed calls to function causing deprecation warning where possible
- Author - [07pepa](https://github.com/07pepa)
- PR <https://github.com/BeanieODM/beanie/pull/917>
### Update migrations.md
- Author - [marwan-alloreview](https://github.com/marwan-alloreview)
- PR <https://github.com/BeanieODM/beanie/pull/915>

[1.27.0]: https://pypi.org/project/beanie/1.27.0

## [1.26.0] - 2024-05-01
        
### Feature: soft delete
- Author - [Ali Moradi](https://github.com/alm0ra)
- PR <https://github.com/roman-right/beanie/pull/901>
            
### Update deprecated call of general_plain_validator_function (#676)
- Author - [dslemusp](https://github.com/dslemusp)
- PR <https://github.com/roman-right/beanie/pull/897>
            
### Annotate decorators that wrap `document` methods (#679)
- Author - [Maxim](https://github.com/bedlamzd)
- PR <https://github.com/roman-right/beanie/pull/886>
            
### Update relations docs to indicate that backlinks are virtual.
- Author - [Josh Borrow](https://github.com/JBorrow)
- PR <https://github.com/roman-right/beanie/pull/904>
            
### Docs: fix typo (#869)
- Author - [Valentin Oliver Loftsson](https://github.com/valentinoli)
- PR <https://github.com/roman-right/beanie/pull/899>
            
### Add possibility of leveraging enum in find query
- Author - [Danil](https://github.com/damikhai)
- PR <https://github.com/roman-right/beanie/pull/868>
            
### Handle typeerror in validator of pydanticobjectid
- Author - [Christian Grotheer](https://github.com/grthr)
- PR <https://github.com/roman-right/beanie/pull/861>
            
[1.26.0]: https://pypi.org/project/beanie/1.26.0

## [1.25.0] - 2024-01-24
        
### Encode Date Objects
- Author - [George Sakkis](https://github.com/gsakkis)
- PR <https://github.com/roman-right/beanie/pull/816>
            
### Fix: Findinterface Type-Hints Break On View Models
- Author - [Guy Tsitsiashvili](https://github.com/GuyGooL5)
- PR <https://github.com/roman-right/beanie/pull/819>
            
### Fix: Count With Text Queries And Links
- Author - [Benjamin Earle](https://github.com/MrEarle)
- PR <https://github.com/roman-right/beanie/pull/826>
            
### Update Migration Command To Enable/Disable Transactions
- Author - [Mahmoud Mabrouk](https://github.com/mmabrouk)
- PR <https://github.com/roman-right/beanie/pull/828>
            
### Sync Method
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/831>
            
### Limit Nesting Level Of Linked Documents

*WARNING: This is a breaking change. Please, read [the docs](https://beanie-odm.dev/tutorial/defining-a-document/#nested-documents-depth) before updating.*

- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/834>
            
[1.25.0]: https://pypi.org/project/beanie/1.25.0

## [1.24.0] - 2023-12-24
        
### Exclude revision_id From The get_changes Method
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/759>
            
### Add Support For Custom Bucket Fields In Time Series
- Author - [Lucas Hardt](https://github.com/Luc1412)
- PR <https://github.com/roman-right/beanie/pull/760>
            
### Add Bson Maxkey And Minkey
- Author - [Noah Witt](https://github.com/noah-witt)
- PR <https://github.com/roman-right/beanie/pull/768>
            
### Update Model During Save Validation
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/776>
            
### Fix init_beanie document_models Type Hint
- Author - [Capi Etheriel](https://github.com/barraponto)
- PR <https://github.com/roman-right/beanie/pull/784>
            
### Fix Encoding Keys In `Mapping` Branch Of `Encoder`
- Author - [Rubikoid](https://github.com/Rubikoid)
- PR <https://github.com/roman-right/beanie/pull/785>
            
### Improve Write Performances
- Author - [Thibault Djaballah](https://github.com/tdjaballah)
- PR <https://github.com/roman-right/beanie/pull/786>
            
### Doc Update: Queue
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/794>
            
### Tests For Indexed Fields
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/795>
            
### Rework Revision
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/797>
            
### Add Missing Type Signature To `Document` Constructor
- Author - [None](https://github.com/johnthagen)
- PR <https://github.com/roman-right/beanie/pull/813>
            
[1.24.0]: https://pypi.org/project/beanie/1.24.0

## [1.23.6] - 2023-11-12
        
### Fix Multiprocessing Mode
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/782>
            
[1.23.6]: https://pypi.org/project/beanie/1.23.6

## [1.23.5] - 2023-11-12
        
### Multiprocessing Mode For Init
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/781>
            
[1.23.5]: https://pypi.org/project/beanie/1.23.5

## [1.23.4] - 2023-11-12
        
### Args For `get_model_dump`
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/780>
            
[1.23.4]: https://pypi.org/project/beanie/1.23.4

## [1.23.3] - 2023-11-08
        
### Fix Id Notation
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/772>
            
[1.23.3]: https://pypi.org/project/beanie/1.23.3

## [1.23.2] - 2023-11-08
        
### Fix Aggregations With Text Queries
- Author - [Benjamin Earle](https://github.com/MrEarle)
- PR <https://github.com/roman-right/beanie/pull/752>
            
### Handle Annotated Indexes
- Author - [Benjamin Earle](https://github.com/MrEarle)
- PR <https://github.com/roman-right/beanie/pull/762>
            
### Fix Docstring
- Author - [Andrew Grinevich](https://github.com/Derfirm)
- PR <https://github.com/roman-right/beanie/pull/766>
            
### Build Aggregation Pipeline From Find Query Without Fetch
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/770>
            
[1.23.2]: https://pypi.org/project/beanie/1.23.2

## [1.23.1] - 2023-10-23
        
### Fix: Issue #631
- Author - [IterableTrucks](https://github.com/IterableTrucks)
- PR <https://github.com/roman-right/beanie/pull/734>
            
### Replace Custom 'Hidden=True' Field Attribute With Builtin 'Exclude=True'
- Author - [George Sakkis](https://github.com/gsakkis)
- PR <https://github.com/roman-right/beanie/pull/741>
            
### Add Support For Indexed Custom Pydantic Fields
- Author - [Adam Asay](https://github.com/aasay)
- PR <https://github.com/roman-right/beanie/pull/754>
            
[1.23.1]: https://pypi.org/project/beanie/1.23.0

## [1.23.0] - 2023-10-15
        
### Refactor Encoder
- Author - [George Sakkis](https://github.com/gsakkis)
- PR <https://github.com/roman-right/beanie/pull/584>
            
### Preserve Sort/Skip/Limit For Aggregations
- Author - [George Sakkis](https://github.com/gsakkis)
- PR <https://github.com/roman-right/beanie/pull/711>
            
### Update Pre-Commit Hooks
- Author - [SADIK KUZU](https://github.com/sadikkuzu)
- PR <https://github.com/roman-right/beanie/pull/712>
            
### Fixed Link Validation
- Author - [Evgeniy Goncharuck](https://github.com/iterlace)
- PR <https://github.com/roman-right/beanie/pull/714>
            
### Fix: pydantic_core._pydantic_core.Url object is not iterable
- Author - [Tomohiro Hiratsuka](https://github.com/tomohirohiratsuka)
- PR <https://github.com/roman-right/beanie/pull/730>
            
### Simplify And Fix DecimalAnnotation
- Author - [George Sakkis](https://github.com/gsakkis)
- PR <https://github.com/roman-right/beanie/pull/738>
            
- Issues:
                    
    - [[BUG] Validation Error on parsing retrieved document's BSON Decimal128 field](https://github.com/roman-right/beanie/issues/691)
                        
### Simplify BsonBinary
- Author - [George Sakkis](https://github.com/gsakkis)
- PR <https://github.com/roman-right/beanie/pull/739>
            
### Minor Fixes
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/745>
            
### Replace Encoder With get_dict In The replace_one Method
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/747>
            
[1.23.0]: https://pypi.org/project/beanie/1.23.0

## [1.22.6] - 2023-09-16
        
### Update Precommit Hooks & CI
- Author - [George Sakkis](https://github.com/gsakkis)
- PR <https://github.com/roman-right/beanie/pull/673>
            
[1.22.6]: https://pypi.org/project/beanie/1.22.6

## [1.22.5] - 2023-09-13
        
### Fix: Unify Methods for Retrieving Field's Extra Parameters During Backlink Processing
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/703>
            
- Issues: 
    - [[BUG] Optional[Backlink]](https://github.com/roman-right/beanie/issues/702)
                        
[1.22.5]: https://pypi.org/project/beanie/1.22.5

## [1.22.4] - 2023-09-13
        
### Fix Numpy Array Incompatability
- Author - [Alex Lau](https://github.com/riven314)
- PR <https://github.com/roman-right/beanie/pull/658>
            
[1.22.4]: https://pypi.org/project/beanie/1.22.4

## [1.22.3] - 2023-09-13
        
### Refactor: Simplify UpdateMany And UpdateOne __await__ Method
- Author - [Muzaffer Cikay](https://github.com/cikay)
- PR <https://github.com/roman-right/beanie/pull/687>
            
[1.22.3]: https://pypi.org/project/beanie/1.22.3

## [1.22.2] - 2023-09-13
        
### Fix get_field_type & Generalize extract_id_class
- Author - [George Sakkis](https://github.com/gsakkis)
- PR <https://github.com/roman-right/beanie/pull/657>
            
[1.22.2]: https://pypi.org/project/beanie/1.22.2

## [1.22.1] - 2023-09-13
        
### Fix | list_collection_names Requires Unnecessary Privileges
- Author - [Marina](https://github.com/marinashe)
- PR <https://github.com/roman-right/beanie/pull/681>
- Issues:
  - [[BUG] Can't use a View if the user doesn't have full read privileges to all collections](https://github.com/roman-right/beanie/issues/680)
            
[1.22.1]: https://pypi.org/project/beanie/1.22.1

## [1.22.0] - 2023-09-13
        
### Fix | August 2023
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/669>
- Issues:
                    
  - [[BUG] Issue with `List[Link[Type]]` when `fetch_all_links` is called](https://github.com/roman-right/beanie/issues/576) 
  - [Loosen type requirement for `insert_many()`?](https://github.com/roman-right/beanie/issues/591) 
  - [[BUG] Updating documents with a frozen BaseModel as field raises TypeError](https://github.com/roman-right/beanie/issues/599) 
  - [[BUG] Not operator cant be on top level](https://github.com/roman-right/beanie/issues/600)
  - [[BUG] `Text` query doesn't work with `fetch_links=True`](https://github.com/roman-right/beanie/issues/606)
  - [[BUG] List type fields in updated model record do not get update.](https://github.com/roman-right/beanie/issues/629)
  - [[BUG] Undefined behavior when chaining update methods](https://github.com/roman-right/beanie/issues/646)
  - [[BUG] Revision Id is in Responsemodel](https://github.com/roman-right/beanie/issues/648)
  - [[BUG] Custom types like bson.Binary require `__get_pydantic_core_schema__`](https://github.com/roman-right/beanie/issues/651)
  - [[BUG] `validate_on_save` doesn't work with `Document.save()`](https://github.com/roman-right/beanie/issues/664)
  - [[BUG] Beanie persists `root` field](https://github.com/roman-right/beanie/issues/668)
  - [Beanie 1.21 still triggers many deprecation warnings with Pydantic v2](https://github.com/roman-right/beanie/issues/676)
  - [[BUG] TypeError: expected 1 argument, got 0 when beanie.Document has method wrapped in pydantic.validate_call](https://github.com/roman-right/beanie/issues/695)
                        
[1.22.0]: https://pypi.org/project/beanie/1.22.0

## [1.21.0] - 2023-08-03
        
### Pydantic bump | final
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/636>
            
[1.21.0]: https://pypi.org/project/beanie/1.21.0

## [1.21.0b1] - 2023-07-21
        
### Bump pydantic | beta 1
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/624>
            
[1.21.0b1]: https://pypi.org/project/beanie/1.21.0b1

## [1.21.0b0] - 2023-07-19
        
### Bump pydantic | beta 0
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/620>
            
[1.21.0b0]: https://pypi.org/project/beanie/1.21.0b0

## [1.20.0] - 2023-06-30
        
### Docs: queue battery
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/603>
            
[1.20.0]: https://pypi.org/project/beanie/1.20.0

## [1.20.0b1] - 2023-06-09
        
### Feature: custom init classmethod
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/590>
            
[1.20.0b1]: https://pypi.org/project/beanie/1.20.0b1

## [1.20.0b0] - 2023-06-09
        
### Feature: optional batteries
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/575>
            
[1.20.0b0]: https://pypi.org/project/beanie/1.20.0b0

## [1.19.2] - 2023-05-25
        
### Fix: issues opened before 2023.05
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/571>
            
[1.19.2]: https://pypi.org/project/beanie/1.19.2

## [1.19.1] - 2023-05-22
        
### Fix: update forward refs during nested links check
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/566>
            
### Fix: session in iterative transactions
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/567>
            
[1.19.1]: https://pypi.org/project/beanie/1.19.1

## [1.19.0] - 2023-05-05
        
### Feat/back refs
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/557>
            
### Feat: add box operator
- Author - [Anton Kriese](https://github.com/akriese)
- PR <https://github.com/roman-right/beanie/pull/552>
            
### Fix table of contents not showing all classes
- Author - [Kai Schniedergers](https://github.com/kschniedergers)
- PR <https://github.com/roman-right/beanie/pull/546>
            
### Return bulkwriteresult response from motor
- Author - [divyam234](https://github.com/divyam234)
- PR <https://github.com/roman-right/beanie/pull/542>
            
### Fix typing in 'document.get(...)'
- Author - [Yallxe](https://github.com/yallxe)
- PR <https://github.com/roman-right/beanie/pull/526>
            
### Init view's cache
- Author - [Antonio Eugenio Burriel](https://github.com/aeburriel)
- PR <https://github.com/roman-right/beanie/pull/521>
            
### Kwargs arguments for elemmatch operator
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/517>
            
[1.19.0]: https://pypi.org/project/beanie/1.19.0

## [1.18.1] - 2023-05-04
        
### Keep nulls config
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/555>
            
[1.18.1]: https://pypi.org/project/beanie/1.18.1

## [1.18.0] - 2023-03-31
        
### Prevent the models returned from find_all to be modified in the middle of modifying
- Author - [Harris Tsim](https://github.com/harris)
- PR <https://github.com/roman-right/beanie/pull/502>
            
### Allow change class_id and use name settings in uniondoc
- Author - [설원준(Wonjoon Seol)/Dispatch squad](https://github.com/wonjoonSeol-WS)
- PR <https://github.com/roman-right/beanie/pull/466>
            
### Fix: make `revision_id` not show in schema
- Author - [Ivan GJ](https://github.com/ivan-gj)
- PR <https://github.com/roman-right/beanie/pull/478>
            
### Fix: added re.pattern support to common encoder suite
- Author - [Ilia](https://github.com/Abashinos)
- PR <https://github.com/roman-right/beanie/pull/511>
            
### Fix other issues
- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/518>
            
[1.18.0]: https://pypi.org/project/beanie/1.18.0

## [1.18.0b1] - 2023-02-09

### Fix

- Don't create state on init for docs with custom id types

### Implementation

- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/486>

[1.18.0b1]: https://pypi.org/project/beanie/1.18.0b1

## [1.18.0b0] - 2023-01-30

### Feature

- feat: convert updates to be atomic operations

### Implementation

- Author - [Roman Right](https://github.com/roman-right)
- PR <https://github.com/roman-right/beanie/pull/481>

[1.18.0b0]: https://pypi.org/project/beanie/1.18.0b0

## [1.17.0] - 2023-01-19

### Feature

- Add links to views

### Implementation

- Author - [Sebastian Battle](https://github.com/sabattle)
- PR <https://github.com/roman-right/beanie/pull/472>

[1.17.0]: https://pypi.org/project/beanie/1.17.0

## [1.16.8] - 2022-01-05

### Fix

- Already inserted Links will throw DuplicateKeyError on insert of wrapping doc

### Implementation

- Author - [noaHson86](https://github.com/noaHson86)
- PR <https://github.com/roman-right/beanie/pull/469>

## [1.16.7] - 2023-01-03

### Fix

- sort many args

### Implementation

- PR <https://github.com/roman-right/beanie/pull/468>

## [1.16.6] - 2022-12-27

### Feature

- Previous saved state

### Implementation

- Author - [Paul Renvoisé](https://github.com/paul-finary)
- PR <https://github.com/roman-right/beanie/pull/305>

## [1.16.5] - 2022-12-27

### Deprecation

- Raises exception if `Collection` inner class was used as it is not supported more

### Backported to

- [1.15.5]
- [1.14.1]

### Implementation

- PR <https://github.com/roman-right/beanie/pull/460>

## [1.16.4] - 2022-12-20

### Fix

- [[BUG] Initiating self-referencing documents with nested links breaks due to uncaught request loop](https://github.com/roman-right/beanie/issues/449)
- Nested lookups for direct links

### Implementation

- PR <https://github.com/roman-right/beanie/pull/455>

## [1.16.3] - 2022-12-19

### Fix

- [[BUG] revision_id field saved in MongoDB using save()/replace() on an existing document even if use_revision is False](https://github.com/roman-right/beanie/issues/420)

### Implementation

- PR <https://github.com/roman-right/beanie/pull/452>

## [1.16.2] - 2022-12-19

### Fix

- [[BUG] find_one projection link](https://github.com/roman-right/beanie/issues/383)
- [[BUG]: Link fields interference/contamination](https://github.com/roman-right/beanie/issues/433)
- [[BUG]: ElemMatch on Document property of Type List[Link] fails with IndexError in relations.py convert_ids()](https://github.com/roman-right/beanie/issues/439)

### Implementation

- PR <https://github.com/roman-right/beanie/pull/448>

## [1.16.1] - 2022-12-17

### Feature

- Remove yarl dependency

### Implementation

- PR <https://github.com/roman-right/beanie/pull/448>

## [1.16.0] - 2022-12-17

### Feature

- Support for fetching deep-nested Links

### Implementation

- Author - [Courtney Sanders](https://github.com/csanders-rga)
- PR <https://github.com/roman-right/beanie/pull/419>

## [1.16.0b3] - 2022-11-28

### Feature

- Lazy parsing for find many

### Implementation

- PR <https://github.com/roman-right/beanie/pull/436>

## [1.15.4] - 2022-11-18

### Fix

- Wrong inheritance behavior with non-rooted documents

### Implementation

- ISSUE <https://github.com/roman-right/beanie/issues/422>

## [1.15.3] - 2022-11-10

### Fix

- Deepcopy dict before encode it to save the original

### Implementation

- ISSUE <https://github.com/roman-right/beanie/issues/412>

## [1.15.2] - 2022-11-09

### Fix

- Use Settings inner class in migrations internals
- Fix inheritance: mark root docs with `_inheritance_inited = True`

### Implementation

- PR <https://github.com/roman-right/beanie/pull/409>

## [1.15.1] - 2022-11-07

### Fix

- Pass pymongo kwargs to the bulk writer

### Implementation

- PR <https://github.com/roman-right/beanie/pull/406>

## [1.15.0] - 2022-11-05

### Feature

- The sync version was moved to a separate project

### Breaking change

- There is no sync version here more. Please use [Bunnet](https://github.com/roman-right/bunnet) instead

### Implementation

- PR <https://github.com/roman-right/beanie/pull/395>

## [1.14.0] - 2022-11-04

### Feature

- Multi-model behavior for inherited documents

### Breaking change

- The inner class `Collection` is not supported more. Please, use `Settings` instead.

### Implementation

- Author - [Vitaliy Ivanov](https://github.com/Vitalium)
- PR <https://github.com/roman-right/beanie/pull/395>

## [1.13.1] - 2022-10-26

### Fix

- Remove redundant async things from sync interface

### Implementation

- ISSUE <https://github.com/roman-right/beanie/issues/390>

## [1.13.0] - 2022-10-22

### Improvement

- Sync interface

### Implementation

- PR <https://github.com/roman-right/beanie/pull/386>

## [1.12.1] - 2022-10-17

### Improvement

- Clone interface for query objects

### Implementation

- PR <https://github.com/roman-right/beanie/pull/378>

## [1.12.0] - 2022-10-06

### Improvement

- Optional list of links field

### Implementation

- Author - [Alex Deng](https://github.com/rga-alex-deng)
- PR <https://github.com/roman-right/beanie/pull/358>

## [1.11.12] - 2022-09-28

### Improvement

- Change before_event, after_event signature to be more pythonic

### Implementation

- DISCUSSION <https://github.com/roman-right/beanie/discussions/354>

## [1.11.11] - 2022-09-26

### Fix

- Remove prints

### Implementation

- ISSUE <https://github.com/roman-right/beanie/issues/355/>

## [1.11.10] - 2022-09-20

### Improvement

- Adding Update Action

### Implementation

- Author - [schwannden](https://github.com/schwannden)
- PR <https://github.com/roman-right/beanie/pull/291/>

## [1.11.9] - 2022-08-19

### Fix

- Move set state and swap revision to init to avoid problems with subdocs
- Issue <https://github.com/roman-right/beanie/issues/294>
- Issue <https://github.com/roman-right/beanie/issues/310>

## [1.11.8] - 2022-08-17

### Improvement

- Skip sync parameter for instance updates

## [1.11.7] - 2022-08-02

### Improvement

- Decimal128 encoding

### Implementation

- Author - [Teslim Olunlade](https://github.com/ogtega)
- PR <https://github.com/roman-right/beanie/pull/321>

## [1.11.6] - 2022-06-24

### Fix

- Roll back projections fix, as it was valid

## [1.11.5] - 2022-06-24

### Fix

- Projection fix for aggregations

## [1.11.4] - 2022-06-13

### Improvement

- Link as FastAPI output

## [1.11.3] - 2022-06-10

### Improvement

- Motor3 support

### Implementation

- ISSUE <https://github.com/roman-right/beanie/issues/262>

## [1.11.2] - 2022-06-06

### Fix

- Dnt inherit excludes

### Implementation

- PR <https://github.com/roman-right/beanie/pull/279>

## [1.11.1] - 2022-05-31

### Features

- Allow extra
- Distinct

### Implementation

- Author - [Robert Rosca](https://github.com/RobertRosca)
- PR <https://github.com/roman-right/beanie/pull/263>
- Author - [Никита](https://github.com/gruianichita)
- PR <https://github.com/roman-right/beanie/pull/268>

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

[1.10.9]: https://pypi.org/project/beanie/1.10.9

[1.11.0]: https://pypi.org/project/beanie/1.11.0

[1.11.1]: https://pypi.org/project/beanie/1.11.1

[1.11.2]: https://pypi.org/project/beanie/1.11.2

[1.11.3]: https://pypi.org/project/beanie/1.11.3

[1.11.4]: https://pypi.org/project/beanie/1.11.4

[1.11.5]: https://pypi.org/project/beanie/1.11.5

[1.11.6]: https://pypi.org/project/beanie/1.11.6

[1.11.7]: https://pypi.org/project/beanie/1.11.7

[1.11.8]: https://pypi.org/project/beanie/1.11.8

[1.11.9]: https://pypi.org/project/beanie/1.11.9

[1.11.10]: https://pypi.org/project/beanie/1.11.10

[1.11.11]: https://pypi.org/project/beanie/1.11.11

[1.11.12]: https://pypi.org/project/beanie/1.11.12

[1.12.0]: https://pypi.org/project/beanie/1.12.0

[1.12.1]: https://pypi.org/project/beanie/1.12.1

[1.13.0]: https://pypi.org/project/beanie/1.13.0

[1.13.1]: https://pypi.org/project/beanie/1.13.1

[1.14.0]: https://pypi.org/project/beanie/1.14.0

[1.15.0]: https://pypi.org/project/beanie/1.15.0

[1.15.1]: https://pypi.org/project/beanie/1.15.1

[1.15.2]: https://pypi.org/project/beanie/1.15.2

[1.15.3]: https://pypi.org/project/beanie/1.15.3

[1.15.4]: https://pypi.org/project/beanie/1.15.4

[1.16.0b3]: https://pypi.org/project/beanie/1.16.0b3

[1.16.0]: https://pypi.org/project/beanie/1.16.0

[1.16.1]: https://pypi.org/project/beanie/1.16.1

[1.16.2]: https://pypi.org/project/beanie/1.16.2

[1.16.3]: https://pypi.org/project/beanie/1.16.3

[1.16.4]: https://pypi.org/project/beanie/1.16.4

[1.16.5]: https://pypi.org/project/beanie/1.16.5

[1.14.1]: https://pypi.org/project/beanie/1.14.1

[1.15.5]: https://pypi.org/project/beanie/1.15.5

[1.16.6]: https://pypi.org/project/beanie/1.16.6

[1.16.7]: https://pypi.org/project/beanie/1.16.7

[1.16.8]: https://pypi.org/project/beanie/1.16.8
