# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `/daikenja:remember-persona`, the single owner of content writes to
  `~/.claude/daikenja/personas.md`. It records what the user says about a
  person they write to, appending a section for a new person without asking
  and reporting it afterwards, and proposing rather than silently applying any
  change to prose the user wrote by hand. It records only what the user
  actually stated -- never a trait inferred from a draft, a thread or a role --
  and it never creates the file, which stays `setup-user`'s job
  (`skills/remember-persona/SKILL.md`).
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
- `compose`'s rewrite rules moved out of the skill into a shared
  `docs/rewrite-rules.md`, so `preflight` can apply the same contract. No
  behaviour change to `compose` (`skills/compose/SKILL.md`,
  `docs/rewrite-rules.md`).
- `docs/config-contract.md`'s who-writes-what table now splits `personas.md`
  into creation, which stays `setup-user`'s and is unchanged, and content,
  which belongs to `remember-persona`. It previously stated that Daikenja
  never edits the file. `skills/setup-user/SKILL.md` carries the matching
  boundary note, `templates/personas.md` now tells new users that Daikenja may
  append entries and how to spot them, and `README.md`'s "Where your data
  lives" table no longer credits `personas.md` to the user alone.

### Documentation

- Documented that a local-marketplace install copies the repo at install
  time rather than referencing it live, and that `claude --plugin-dir .`
  remains the loop to use for development.
- `docs/README.md` now indexes all six contracts in `docs/`. It previously
  listed two, omitted `reading.md` and `substance-checks.md` entirely, and
  still carried a "Still to land" section for `voice.md`, which already
  ships.

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
