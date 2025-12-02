# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial implementation of TextUtils library
- CaseConverter: Convert between camelCase, snake_case, kebab-case, PascalCase, and SCREAMING_SNAKE_CASE
- TextCleaner: Clean and normalize text with whitespace removal, HTML tag stripping, unicode normalization
- StringValidator: Validate emails, URLs, phone numbers, IP addresses, credit cards, passwords, and palindromes
- TextFormatter: Format text with truncation, padding, number/currency formatting, and list formatting
- Comprehensive test suite with pytest
- Type hints throughout the codebase
- Complete documentation with README and examples

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- N/A (initial release)

## [0.1.0] - 2024-12-29

### Added
- Initial release of TextUtils library
- Core functionality for text manipulation
- Basic test coverage
- Package structure with proper imports

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html):

- **Major**: Breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, backward compatible

## Contributing

When making changes, please update this changelog following the format above.

1. Add new entries under `[Unreleased]` section
2. Use the appropriate subsection (Added, Changed, Deprecated, Removed, Fixed, Security)
3. Group related changes together
4. Use clear, concise descriptions
5. Reference issue/PR numbers when applicable

## Format

Each version section should follow this format:

```
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature description

### Changed
- Changed feature description

### Deprecated
- Deprecated feature description

### Removed
- Removed feature description

### Fixed
- Bug fix description

### Security
- Security fix description
```

When releasing a new version:

1. Move `[Unreleased]` changes to a new version section
2. Update the version in `pyproject.toml` and `__init__.py`
3. Create a new `[Unreleased]` section for future changes
