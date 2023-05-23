# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Poetry "pyproject.toml" [PEP 621](https://peps.python.org/pep-0621/) compliant project metadata file.
- Markdown changelog and readme.
- Pre-commit tests ([Black](https://github.com/psf/black), [Flake8](https://github.com/PyCQA/flake8), etc.)
- GitHub actions to automate testing.

### Changed

- Refactored docs.

### Removed

- Python "setup.py" and "setup.cfg" packaging files.
- RST based changelog and readme.
- Support for Python < 3.8.

## [2.0.2] - 2017-03-13

### Fixed

- Requirements for Python > 3.4.

## [2.0.1] - 2017-02-27

### Added

- Support for Python 2.6.

### Removed

- "enum34" dependency requirement for Python > 3.4.

## [2.0] - 2016-09-26

### Added

- "force_set" method.
- Field machine.
- Support for Python 3.5.

### Changed

- Backward compatibility breaks:
  - Empty state is now disallowed.
  - Only full names are allowed, when using scalars, no shortcuts.
  - Removed support for unhashable types.

## [1.0] - 2014-09-04

### Added

- All basic features.

## [0.1.0] - 2014-08-08

### Added

- First release on PyPI.
- Utilities to create simple state machine.

[unreleased]: https://github.com/beregond/super_state_machine/compare/2.0.2...HEAD
[2.0.2]: https://github.com/beregond/super_state_machine/compare/2.0.1...2.0.2
[2.0.1]: https://github.com/beregond/super_state_machine/compare/2.0...2.0.1
[2.0]: https://github.com/beregond/super_state_machine/compare/1.0...2.0
[1.0]: https://github.com/beregond/super_state_machine/compare/0.1.0...1.0
[0.1.0]: https://github.com/beregond/super_state_machine/releases/tag/0.1.0
