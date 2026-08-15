# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-08-15

Initial public release.

### Added

- Twelve skills: `thread`, `compose`, and `preflight` for writing a reply;
  `log` for writing a project's decision ledger; `catchup`, `summary`,
  `decisions`, and `gaps` for reading it; `meeting-review`, `doc-review`, and
  `self-review` for reviewing things; and `setup-user` for one-time,
  re-runnable setup.
- `docs/` contracts the skills implement: `voice.md` and `config-contract.md`
  for generated writing, `ledger-format.md` for the ledger's parsing contract,
  plus `reading.md` and `substance-checks.md`.
- `templates/` blank starting points (`daikenja.yaml`, `ledger.md`,
  `personas.md`, `writing-style.md`) copied out to a user's machine on setup.
- `tests/fixtures/` synthetic inputs the skills are exercised against by hand.

[Unreleased]: https://github.com/by-carlos/daikenja/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/by-carlos/daikenja/releases/tag/v0.2.0
