# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `tests/check-invariants.py`, a script enforcing the invariants every v2
  build stage checked by hand: `claude plugin validate .` exits clean, and
  every `skills/*/SKILL.md` frontmatter block parses as YAML with a `name`
  matching its directory and a `description`, catching the unquoted `": "`
  trap that silently drops a skill's frontmatter at load time. Wired into
  CI via `.github/workflows/ci.yml` (renamed from `gitleaks.yml`, which now
  also runs this check as a second job) on push and pull request. The em
  dash / en dash scan this issue originally specified is omitted: the rule
  it would enforce was already removed.

### Changed

- Context-link additions and removals now emit a Changelog line
  (`+link "<label>"` / `-link "<label>"`) and are reported by `catchup`,
  closing the one gap where a ledger change was invisible to it
  (`docs/ledger-format.md`, `skills/log/SKILL.md`, `skills/catchup/SKILL.md`).

### Documentation

- Documented that a local-marketplace install copies the repo at install
  time rather than referencing it live, and that `claude --plugin-dir .`
  remains the loop to use for development.

### Changed

- Removed the non-overridable "never an em dash or en dash" rule from the
  default voice (`docs/voice.md`, `docs/config-contract.md`,
  `templates/writing-style.md`, `skills/thread/SKILL.md`). Absolute dates
  remain the only non-overridable rule. `docs/ledger-format.md`'s three-split
  parser bound is unchanged; only its justification was reworded.

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
