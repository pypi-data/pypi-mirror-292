<!-- SPDX-FileCopyrightText: 2024 German Aerospace Center <fame@dlr.de>

SPDX-License-Identifier: CC0-1.0 -->

# Changelog
## [2.3.1](https://gitlab.com/fame-framework/fame-io/-/tags/v2.3.1) - 2024-08-26
### Fixed
- Fix ignored default values of `convert_results` for `merge-times` arguments #211 (@dlr-cjs, dlr_fn)

## [2.3.0](https://gitlab.com/fame-framework/fame-io/-/tags/v2.3.0) - 2024-08-12
### Added
- New attribute type `string_set` #175 (@dlr_fn @dlr-cjs)
- Add warning if a timeseries file has additional, non-empty columns #155 (@LeonardWilleke)
- Ensure `CHANGELOG.md` is updated in automated testing pipeline #207 (@dlr_fn)

### Fixed
- ConvertFameResults: Fix bug on `merge-times` when `--memory-saving` is active #201 (@dlr_fn @dlr-cjs)

## [2.2.0](https://gitlab.com/fame-framework/fame-io/-/tags/v2.2.0) - 2024-05-28
### Changed
- New command line option `-enc --encoding` to change encoding when reading yaml-files #170 (@dlr-cjs)
- Improve error message when timeseries is not found and is number string #178 (@dlr-cjs)

### Added
- Add writing of FAME-Io and FAME-Protobuf versions to created input protobuf #192 (@dlr-cjs)
- Add deprecation warning for section `GeneralProperties.Output` in scenario #203 (@dlr-cjs)

## [2.1.1](https://gitlab.com/fame-framework/fame-io/-/tags/v2.1.1) - 2024-05-28
### Fixed
- ConvertFameResults: Fix crash on complex column conversion if Agent has no simple columns #204 (@dlr_fn @dlr-cjs)

## [2.1.0](https://gitlab.com/fame-framework/fame-io/-/tags/v2.1.0) - 2024-05-11
### Changed
- Change format of auto-created timeseries from constant values #196 (@dlr-cjs)
- Change default log level to "WARNING" #191 (@dlr_fn @dlr-cjs)
- Adapt link-formatting in Changelog !155 (@dlr-cjs)

### Added
- Read java package names from Schema and write to input.pb #198 (@dlr-cjs)

### Fixed
- Fix docstrings in CLI `handle_args()` #190 (@dlr-cjs @dlr_fn)
- Fix potential duplicates in logging #191 (@dlr_fn @dlr-cjs)

## [2.0.1](https://gitlab.com/fame-framework/fame-io/-/tags/v2.0.1) - 2024-04-05
### Fixed
- Fix potential missing columns when memory-saving-mode `-m` is enabled #194 (@dlr_fn @dlr-cjs)

### Remove
- Remove convert results option `-cc MERGE` #194 (@dlr_fn @dlr-cjs)

## [2.0.0](https://gitlab.com/fame-framework/fame-io/-/tags/v2.0.0) - 2024-04-03
### Changed
- **Breaking**: Removed support for `python==3.8` #163 (@dlr-cjs @dlr_fn)
- **Breaking**: Signature of `run` functions in `make_config.py` and `convert_results.py` changed: the input file is now read from the configuration dictionary #163 (@dlr-cjs @dlr_fn)
- **Breaking**: Created protobuf files now have a header section -> minimum required FAME-Core version is now 1.6.0 #183 (@dlr-cjs @dlr_fn)
- Raise error for NaN float values in scenario and time series #165 (@dlr-cjs @dlr_fn)
- Enhance Schema to include metadata and output fields #156 (@dlr-cjs @litotes18 @dlr_fn)
- Enhance Contracts to include metadata #158 (@dlr-cjs @litotes18 @dlr_fn)
- Enhance Agents to include metadata #159 (@dlr-cjs @litotes18 @dlr_fn)
- Improve general handling of CLI arguments #163 (@dlr_fn @dlr-cjs)
- Ensure `fameio` logger is used consistently !126 (@dlr-cjs @dlr_fn)
- Enhanced error message if mandatory attribute is not defined by logging `full_name` #177 (@dlr_fn)
- Switch to pyproject.toml #173 (@dlr-cjs)
- Restrict supported pandas versions #171 (@dlr-cjs)
- Enable to specify defaults for MERGE_TIME parameters #179 (@dlr-cjs)
- Conserve order of keys in YAML files #186 (@dlr-cjs @dlr_fn)
- Update to `fameprotobuf==1.4.0` #189 (@dlr-cjs @dlr_fn)
- Update `CHANGELOG.md` to conform with Common Changelog format #172 (@dlr-cjs @dlr_fn)

### Added
- Write Schema and Metadata of Contracts and Agents to protobuf file #160 (@dlr-cjs @litotes18 @dlr_fn)
- Add option to recover input data `--input-recovery`/`--no-input-recovery` #163 (@litotes18 @dlr_fn @dlr-cjs)
- Add pipeline tests for all major Python versions >= 3.8 #173 (@dlr-cjs)
- Read all input from protobuf file #162 (@dlr-cjs @litotes18 @dlr_fn)
- Write all input from protobuf to disk #163 (@litotes18 @dlr_fn @dlr-cjs)
- Add header section to input protobuf enabling recovering of inputs from protobuf #183 (@dlr-cjs @dlr_fn)
- Add pipeline tests for all major Python versions >= 3.8, < 3.12 #173 (@dlr-cjs)
- Enable comments in timeseries using '#' #184 (@dlr-cjs)
- Raise Warning if Agent has no Contracts attributed #187 (@dlr_fn)
- Add JOSS Paper in folder paper/ #139 (@dlr-cjs @litotes18 @dlr_fn)
- Add `CONTRIBUTING.md` #102 (@dlr-cjs @dlr_fn)
- Add `Citation.cff` #166 (@dlr-cjs)

### Removed
- Remove deprecated protobuf test !127 (@dlr-cjs @dlr_fn)

### Fixed
- Fix deprecated arguments in pandas groupby !129 (@maurerle)
- Fix breaking tests in Pytest 8.0 #176 (@dlr-cjs)
- Fix PyTests for Python 3.12 #182 (@dlr_fn)

## [1.8.1](https://gitlab.com/fame-framework/fame-io/-/tags/v1.8.1) - 2023-05-04
### Fixed
- Fix fail of `ConvertFameResults` when `merge-times` was not specified

## [1.8.0](https://gitlab.com/fame-framework/fame-io/-/tags/v1.8) - 2023-04-14
### Changed
- Update repository to be compliant to `REUSE` standard
- Accept custom `date_format` (default: `"%Y-%m-%d_%H:%M:%S"`) for `FameTime.convert_fame_time_step_to_datetime()`
- Parse command-line arguments case-insensitive for arguments with predefined options
- Handle potentially missing cli arguments in `cli.update_default_config` for `makeFameRunConfig` and `convertFameResults` in a robust way.

### Added
- **Breaking**: Add option to define conversion of time steps to given format (default=`UTC`) by `-t/--time {UTC, INT, FAME}` for `convertFameResults`
- Add option to merge time steps in results with `convertFameResults`
- Add pre-commit hooks enforcing high coding standards and reducing CI runner minutes during development

## [1.7.0](https://gitlab.com/fame-framework/fame-io/-/tags/v1.7) - 2023-02-20
### Added
- Support dictionaries in Schema for field `Products` in elements of `AgentTypes`
- Support dictionaries in Schema for field `Values` in elements of `Attributes`

### Changed
- Use `Pathlib` for path handling
- Improve error message when no valid `YAML` file is specified for `makeFameRunConfig`

### Remove
- **Breaking**: `Products` in Schema no longer support single non-list values

## [1.6.3](https://gitlab.com/fame-framework/fame-io/-/tags/v1.6.3) - 2022-11-04
### Added
- Allow parsing `Help` for `Attributes` in `schema`

## [1.6.1](https://gitlab.com/fame-framework/fame-io/-/tags/v1.6.1) - 2022-11-02
### Changed
- Use existing logger if already set up to avoid duplicates when `fameio` is used as dependency in third party workflows

## [1.6.0](https://gitlab.com/fame-framework/fame-io/-/tags/v1.6) - 2022-07-08
### Added
- Add option to enable memory saving mode using the flag `-m` or `--memory-saving`
- Add options to deal with complex indexed output columns using the flag `-cc` or `--complex-column` with
  options `IGNORE`, `MERGE` or `SPLIT`

### Changed
- **Breaking**: Update requirement to `python>=3.8`
- **Breaking**: Update requirement to `fameprotobuf==v1.2`
- Enable parsing of protobuf output files > 2 GB
- Reduce memory profile for `convertFameResults`
- Extract `source` scripts relevant for `convertFameResults` to be hosted in subpackage `results`

## [1.5.4](https://gitlab.com/fame-framework/fame-io/-/tags/v1.5.4) - 2022-06-01
### Changed
- Limit `protobuf` dependency to `>=3.19,<4.0`

## [1.5.3](https://gitlab.com/fame-framework/fame-io/-/tags/v1.5.3) - 2022-03-18
### Changed
- Harmonize interface with `famegui`
- Return `None` on failure of `resolve_series_file_path` instead of raising a `FileNotFoundError`

## [1.5.2](https://gitlab.com/fame-framework/fame-io/-/tags/v1.5.2) - 2022-03-10
### Changed
- Allow interfacing of `famegui` with `scenario` (e.g. serialization, error handling)
- Move `scenario` validation to `validator.py`
- Extract `path_resolver.py`
- Increase test coverage by incorporating [AMIRIS examples](https://gitlab.com/dlr-ve/esy/amiris/examples)

## [1.5.1](https://gitlab.com/fame-framework/fame-io/-/tags/v1.5.1) - 2022-01-10
### Added
- Provide documentation on installation using `pipx`
- Add optional argument `-se`/`--singleexport` for exporting individual files for each agent
- Add compatibility hook for `famegui` integration

### Changed
- Refactor `scenario.py`
- Ensure code formatting using `black`

## [1.5.0](https://gitlab.com/fame-framework/fame-io/-/tags/v1.5) - 2021-06-30
### Added
- Support specifying an output folder in command line interface of `convert_results.py`

### Changed
- Update to latest protobuf package
- Refactor code

## [1.4.0](https://gitlab.com/fame-framework/fame-io/-/tags/v1.4) - 2021-06-10
### Added
- Enable "Default" values for Attributes - these are used in case a mandatory attribute is not specified in the Scenario
- Allow "List" Attributes with multiple values
- Add new AttributeTypes "Long", "String" and "TimeStamp"
- Add compact definition of multiple contracts: enable lists for senders and receivers

### Changed
- **Breaking**: Update requirement to `fameprotobuf==1.1.4`
- Refactor `make_config.py`: split into several classes and packages, improved exception handling
- Switch to pytest and improved test coverage
- Make keywords in Schema and Scenario case-insensitive
- Improve validations for Schema and Scenario

### Fixed
- Fixed minor bugs

## [1.3.0](https://gitlab.com/fame-framework/fame-io/-/tags/v1.3) - 2021-04-13
### Added
- Enable `Attributes` in agents (formerly known as `Fields`) to be structured in complex tree-like data dictionaries
- Allow contracts to support `Attributes` of type `int`, `float`, `enum` or `dict`
- Add coverage report badge
- Add `CHANGELOG.md`

### Changed
- **Breaking**: Use new format `DataStorage` for input and output protobuf files allowing `FAME-Core` input and output to be written to the same file (requires `FAME-Core > 1.0`)
- **Breaking**: Update requirement to `fameprotobuf==1.1.2`
- Enable automatic detection of `TimeStamps` by string format and conversion to int64
- Raise proper error when file can not be loaded triggered by `!include` command
- Raise critical error when trying to convert empty protobuf output file
- Check if `product` in `contract` is valid according to `schema.yaml`

## [1.2.4](https://gitlab.com/fame-framework/fame-io/-/tags/v1.2.4) - 2021-02-26
### Changed
- Move `is_compatible` function to class `AttributeType`

## [1.2.3](https://gitlab.com/fame-framework/fame-io/-/tags/v1.2.3) - 2021-02-24
### Fixed
- Fix file prefix `IGNORE_` (used when loading a set of contract files with the !include argument) is now working consistently

## [1.2.2](https://gitlab.com/fame-framework/fame-io/-/tags/v1.2.2) - 2021-02-18
### Changed
- **Breaking**: Rename `fieldtype` to `attributetype` in `schema.yaml`
- Derive protobuf imports from `fameprotobuf` package
- Improve handling of cases for keys in `scenario.yaml`
- Improve handling of time stamp strings

## [1.2.1](https://gitlab.com/fame-framework/fame-io/-/tags/v1.2.1) - 2021-02-10
### Changed
- Improve key handling for contracts which are now case-insensitive

## [1.2.0](https://gitlab.com/fame-framework/fame-io/-/tags/v1.2) - 2021-02-04
### Added
- Add `!include` command to yaml loading to allow integrating additional yaml files

### Changed
- **Breaking**: Rename package to `fameio`
- Improve executables
- Restructure logging
- Improve documentation

### Fixed
- Fix bugs

## [1.1.0](https://gitlab.com/fame-framework/fame-io/-/tags/v1.1) - 2020-12-09
### Added
- Package to PyPI
- Provide executables for calling `makeFameRunConfig` and `convertFameResults`

### Changed
- Improve documentation

## [1.0.0](https://gitlab.com/fame-framework/fame-io/-/tags/v1.0) - 2020-11-17
_Initial release of `famepy`_
