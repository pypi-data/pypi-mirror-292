# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2024-07-29
### Changed
- Upgrade package dependencies to the latest versions.
- upgrade modelscope to modelscope[framework] to add dataset framework support.

## [0.1.3] - 2024-07-28
### Changed
- Change modelscope version to 1.15.0. for stability.

## [0.1.2] - 2024-07-27
### Changed
- Deleted the `transcribe.py` file.
- Refactored the `translate.py` to `translator.py`.
- Refactored server scripts in class and moved them to services folder.
- Moved the base stations scripts to base folder.

## [0.1.1] - 2024-07-26
### Added
- Added support for `server` extras.
- Defined extra dependencies for server-related functionalities.

### Changed
- Updated the version to 0.1.1 to include the new extras and improvements.

### Fixed
- Fixed the omission of the `extras_require` in the initial release.

## [0.1.0] - 2024-07-25
### Added
### Added
- Initial release of `openmmla-audio` with core functionalities.