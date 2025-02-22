# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2024-03-07
### Added
- Python 3.8+ support
- Tests
- "release" and "tests" pipelines

### Changed
- Use the standard "urllib" library instead of "requests"
- Removed Plex Home Theater notifications due to deprication
- README.md

## [2.1.4] - 2020-05-12

### Changed
- Use persistent auth-token instead of username/password to
  authenticate with plex
- Your plex password is no longer stored in plaintext on disk
- Updated README with instructions for Auth-Token
- Changed README to be better readable

## [2.1.3] - 2020-03-12

### Added
- compatibility to Python 3.x
- depedency handling for external module "requests"
- .gitignore file

### Changed
- reodered and simplified default settings
- modernized codebase to be much more pythonic
- refactored "request" section of code
- use system's default python version

## [2.1.2] - 2019-10-23
First GitHub release.

### Added
- Readme and Changelog files.

### Fixed
- Fix for [NOTIFYPLEX: Skipping Plex Update because download failed](https://forum.nzbget.net/viewtopic.php?f=8&t=1393) error.

## [2.1.1] - 2019-10-23
Semantically unchanged release of latest NotifyPlex file I was able to find.

### Fixed
- File formatting following [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
