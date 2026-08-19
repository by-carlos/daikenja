# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- `docs/config-contract.md` § Finding the current project no longer says that a
  read skill stops when no `projects:` entry matches. It continues, because an
  unregistered project can still have a ledger on disk and a ledger on disk wins
  over the config. That behaviour landed with #47 and updated
  `docs/reading.md` § Step A; the contradicting sentence in the contract was
  left behind, so the two documents disagreed on the branch a reader is most
  likely to check first. The corrected step states the rule and defers the
  branch to `docs/reading.md`, which stays the single home for the shared read
  recipe. No skill behaviour changes -- `project-catchup`'s failure table and
  `project-summary` Step 4 already implement the continue path (#75).

### Changed

- `docs/voice.md` § Assume the reader is not a native English speaker split its
  last bullet, "International (US) English. Neutral, no regional slang or
  idiom.", into two Fixed rules: neutral English with no regional slang or
  idiom, and holding to one spelling variant consistently within a message
  (never "organize" next to "colour"). Which variant to use is a new
  `## Defaults` rule, § Spelling variant, whose shipped default flips from US
  to Commonwealth/British spelling, on the reasoning that a non-native reader
  was more likely taught Commonwealth spelling than US -- the same premise the
  surrounding Fixed block already rests on. Unlike the other Defaults rules
  audited in #28, this one is replaceable outright rather than narrowing-only,
  since a user writing to a US audience has an equally legitimate claim on US
  spelling. `templates/writing-style.md` now prompts the user to name their
  variant (#66).

### Added

- The writing skills -- `compose`, `doc-review`, `preflight`,
  `remember-persona`, `self-review` and `thread` -- can now be run on
  claude.ai. `scripts/build-claude-ai-skills.py` builds one upload zip per
  skill into `dist/`, carrying the documents and templates each one
  reads and resolving their paths for a surface that has no
  `${CLAUDE_PLUGIN_ROOT}`. Settings come from the `daikenja` folder in Google
  Drive, so nothing needs uploading or keeping in sync. The `project-*` skills
  and `meeting-review` stay Claude Code only by design -- they need the ledger,
  and Claude Code remains the source of truth (#42).
- `remember-persona` appends its entry to the Drive `personas.md` on claude.ai,
  by the replace-and-verify sequence the config contract already defined.
  Verified on 19 August 2026: the template survived byte for byte, the entry
  landed below it with its recorded date, and the superseded copy was trashed
  leaving one file in the folder. The local path is not a fallback there -- the
  filesystem a skill can reach is discarded with the session, so writing to it
  would report a success and lose the prose (#42).
- `docs/future-work.md` records what claude.ai cannot do, measured on
  19 August 2026: no reviewer dispatch, no ledger, no `setup-user`, no syncing
  between surfaces, a separate connector approval per call, and skills that
  need to be named rather than triggered by description on a long pasted
  draft (#42).
- `CONTRIBUTING.md` and `SECURITY.md`, both written for a public repository:
  how to file an issue and open a pull request, the conventions that are easy
  to trip over (voice, ledger format, templates, fixtures), and a private
  disclosure route through GitHub security advisories with an explicit scope
  statement for a plugin that has no server (#15).
- A "This repo is public" section in `.claude/reference/github-issues.md`
  covering the scrub rule and the rendered-body-plus-explicit-OK gate before
  filing, and naming the two things the scrub deliberately does not cover --
  Daikenja's own config paths and the synthetic test fixtures (#15).
- Two hard rules in `docs/voice.md` § Fixed that were written down nowhere:
  **no profanity or slurs** in anything Daikenja generates, with quoted
  material in a pasted draft or a log line still copied across untouched, and
  **no shouting** -- no capitals for emphasis and no stacked exclamation marks,
  since those read as anger whatever the writer intended (#28).

### Changed

- `docs/voice.md` now carries a **substitution floor**: a replacement only
  counts when it is at least as natural as what it replaced, so an idiom with
  no better plain form stays. The idiom rule read as a blanket ban, which is
  what turned "I do not want to kick it off without a heads up" into the
  stiffer "without telling you first". `a heads up`, `a rabbit hole` and
  `catch up` are named as examples that stay, and `docs/reviewer-personas.md`
  binds the non-native readability check to the same floor so `preflight` does
  not flag them (#40).
- `docs/voice.md` is now split into a **`## Fixed`** tier that no user
  `writing-style.md` can switch off and a **`## Defaults`** tier that a user's
  file may narrow or replace, with every rule audited into one of them. Fixed
  takes absolute dates and the whole "assume the reader is not a native English
  speaker" block, which encodes the product premise rather than a taste
  preference and was overridable until now. Defaults keeps the substitution
  floor, the ~300-word length threshold and humor; the floor and humor are
  marked narrowing-only, so a user can tighten them but cannot loosen either
  past a Fixed rule. `docs/config-contract.md`, `templates/writing-style.md`,
  `docs/rewrite-rules.md`, `docs/README.md`, `compose` and `preflight` all
  restate the layering in terms of the two tiers; `compose` had also been
  claiming two non-overridable rules since #23 removed the second one (#28).
- `preflight` now states how the reviewers actually ran, on every report, in a
  mandatory `Reviewed:` line. It previously raised a notice only when dispatch
  was unavailable, which asked it to notice an absence -- across four runs the
  notice appeared twice, and one of the silent runs claimed a fix was
  "confirmed cycle 2" when no reviewer had read the revision. Cycle 2 now
  re-reads in the sequential mode and never confirms. `README.md` and
  `.claude-plugin/plugin.json` drop the flat "Claude Code only" claim for the
  split between the two halves (#42).

## [0.4.0] - 2026-08-17

### Added

- A plausibility check in `project-log` Step 3 before it offers to scaffold a
  ledger: refuses outright in the user's home directory or `~/.claude`, and
  requires a path-naming confirmation, separate from the Step 5 write
  approval, anywhere else that is neither a VCS root nor already has a
  `.daikenja/`. Closes the gap where `/daikenja:meeting-review`, run from a
  directory that is not a project, ended in an ordinary-looking approval to
  scaffold a ledger nobody meant to create (#47).
- `docs/reading.md` § Step B now requires every read skill to name the
  resolved ledger path in a `Ledger: <path>` line before its answer, success
  or failure, so `project-catchup`, `project-summary`, `project-decisions` and
  `project-gaps` all state their scope without four copies of the rule (#47).
- `profile.writing_style` and `profile.personas` may now name a **Google Drive
  file**, written `drive:<file name>`, as well as a relative or an absolute
  path. The prose is read and written through the Google Drive connector under
  the user's own account, which makes a persona file or a writing style
  reachable from a machine other than the one that wrote it -- the grant spans
  surfaces, so a file created in Claude Code is readable from claude.ai. The
  two keys resolve independently, so personal notes on colleagues can stay
  local while a writing style is shared. Local files remain the default: a
  user who never mentions Drive sees no change, and `/daikenja:setup-user`
  offers the option once and completes without a Google account. Drive is the
  only remote store; a pointer is a path or it is `drive:`. The rule lives in
  `docs/config-contract.md` § Resolving `writing_style` and `personas`, and
  the five skills that touch these keys defer to it. The ledger does not move
  -- it stays in the project, and `docs/ledger-format.md` is untouched (#41).
- Everything Daikenja stores in Drive lives in **one `daikenja` folder**,
  created by `/daikenja:setup-user`, mirroring `~/.claude/daikenja/` on the
  user's machine. Nothing is left loose at the top level of a Drive (#41).
- A Drive pointer names the **file**, never a URL, an ID or a path, and
  resolves by searching that folder for the exact name. The folder is fixed, so
  it stays out of the pointer: `drive:personas.md` is the whole value. Every
  write mints a new file ID, so a stored ID would be stale the first time the
  user's prose changed. Two files sharing the name does not resolve, and
  neither does a missing or duplicated folder: those states mean an earlier
  write was interrupted, and choosing between the copies is the user's call
  (#41).
- `/daikenja:setup-user` is the only skill that creates the `daikenja` folder or
  a Drive file, and now has to be: the connector shows Claude only the files it
  created itself, so a document already in the user's Drive cannot be pointed at
  however it is shared. It creates the folder if it is absent, stops rather than
  choosing when two carry that name, proposes a file name, refuses to create a
  second file under a name already in use, writes the shipped template, confirms
  the file reads back, and only then writes the pointer (#41).
- `/daikenja:remember-persona` now says how a Drive write works: download,
  splice the entry into the downloaded bytes, create a new file under the same
  name in the same folder, confirm it reads back, and only then trash the old
  one. A replacement created outside the folder would hold everything and stop
  resolving, which is worse than a failed write. The connector
  has no content-update tool, so a write is a replacement. **Never trash
  first** -- a create that fails after a successful trash destroys prose that
  cannot be recovered. What is written is always the downloaded bytes plus the
  one entry, never a regenerated file (#41).
- Reads always use the connector's `download_file_content`, never
  `read_file_content`. Measured 17 August 2026 against the same 171-byte
  Markdown file: the former returned it byte-exact, the latter returned a lossy
  rendering with Markdown syntax backslash-escaped (`\#`, `\- \[ \]`,
  `\[link\]`) and hard-break spaces added. Splicing an entry into that text and
  writing it back would permanently corrupt hand-written prose (#41).
- Drive writes disable conversion to Google's own document types. Measured
  17 August 2026: a 203-byte Markdown upload without that flag was stored as a
  Google Doc and read back at 205 bytes with trailing hard-break spaces added;
  with the flag it read back byte-identical (#41).
- Resolving a Drive pointer passes an explicit page size and reads every page.
  Measured 17 August 2026: the search tool's default page size is one, so a
  name carried by two files returned only the older one, and the duplicate
  appeared only once the page size was set. Left as-is, the duplicate check
  would have missed exactly the case it exists to catch and resolved to the
  stale copy (#41).

### Changed

- `/daikenja:remember-persona` no longer hard-stops on a first run before
  `/daikenja:setup-user` has created `~/.claude/daikenja/personas.md`. When it
  has an entry to write and the file is missing, it now scaffolds it from
  `templates/personas.md` itself and reports the scaffold alongside the entry,
  mirroring how `/daikenja:project-log` scaffolds a missing ledger.
  `setup-user`'s own create-if-absent rule is unchanged, and it still never
  writes persona content (#35).
- The plugin description in `.claude-plugin/plugin.json` no longer says that
  everything Daikenja reads lives under `~/.claude/daikenja/`. The
  configuration file still does; the persona and writing-style prose it points
  at may now live in Google Drive. The Claude Code and Cowork restrictions are
  unchanged (#41).
- **A configured pointer that fails is no longer treated as an unconfigured
  one.** `docs/config-contract.md` § Failure behavior now separates the two:
  a key the user never set still degrades with one notice, but a `drive:`
  pointer that cannot be resolved -- connector absent, no file or several files
  under that name, or a download that comes back empty -- stops the skill and
  names the file. None of those can be told apart from prose the user never
  wrote, so continuing would mean drafting in the default voice while the user
  believed their own style had been applied. An empty download counts as a
  failure deliberately: treating it as an empty file costs a persona write that
  replaces the user's prose with a file holding one entry, and treating it as a
  failure costs one run. Local paths keep the older behavior, because a missing
  local file is a fact that can be established (#41).

## [0.3.0] - 2026-08-17

### Added

- `/daikenja:remember-persona`, the single owner of content writes to
  `~/.claude/daikenja/personas.md`. It records what the user says about a
  person they write to, appending a section for a new person without asking
  and reporting it afterwards, and proposing rather than silently applying any
  change to prose the user wrote by hand. It records only what the user
  actually stated -- never a trait inferred from a draft, a thread or a role --
  and it never creates the file, which stays `setup-user`'s job
  (`skills/remember-persona/SKILL.md`).
- `docs/reviewer-personas.md`, the fixed roster of nine reviewer archetypes
  `preflight` dispatches, the two checks it always runs in its own context
  (the AI-tell check and non-native English readability), and the critique
  contract every finding comes back in. Archetypes are reading behaviours
  rather than people, which is what lets a named recipient layer on top of one
  instead of competing with it. The roster changes only by pull request.
- `docs/future-work.md`, recording what the shipped design does not do -- no
  group-level personas, no user-defined archetypes, no persona onboarding by
  sampling past messages, and the two-cycle ceiling on the review loop.
  Written as limitations of current behaviour, not as a roadmap.
- Three `preflight` fixtures covering the cases the review loop can be
  falsified on: a draft whose missing facts appear nowhere in the file, a
  draft with two real recipients no single fix serves, and two drafts that
  are complete on the facts (`tests/fixtures/preflight-content-gap.md`,
  `tests/fixtures/preflight-recipient-conflict.md`,
  `tests/fixtures/preflight-clean-draft.md`).
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

- **Pull requests now require maintainer approval.** Every tracked path is owned
  by `@by-carlos`, allowing contributions while ensuring the maintainer's review
  is required before changes merge.
- **Required CI jobs now use the shared names `gitleaks` and `validate`.** The
  existing plugin and skill invariant checks are unchanged; only their public
  GitHub job context is normalized.
- **The five project-scoped skills now carry a `project-` prefix**: `log` ->
  `project-log`, `summary` -> `project-summary`, `catchup` -> `project-catchup`,
  `decisions` -> `project-decisions`, `gaps` -> `project-gaps`. The other eight
  skills already carried their scope in their names and are unchanged. This is a
  rename and documentation sweep only -- no skill's behaviour, failure branches
  or output shape changed. Landing now, ahead of the repo going public, costs one
  sweep instead of breaking other users' muscle memory later
  (`skills/project-log/SKILL.md`, `skills/project-summary/SKILL.md`,
  `skills/project-catchup/SKILL.md`, `skills/project-decisions/SKILL.md`,
  `skills/project-gaps/SKILL.md`, and every skill and doc that names one).
  `docs/ledger-format.md`'s `<writer>` field now documents `project-log` as the
  current writer name, noting that ledgers written before 0.3.0 name it `log`
  instead; the field grammar itself is unchanged. `templates/ledger.md` reflects
  the new name for ledgers scaffolded from now on -- existing ledgers keep
  whatever wording they already have, since templates are copied once and never
  edited afterwards. `tests/fixtures/sample-ledger.md` gained one Changelog line
  written by `project-log` alongside its existing `log` lines, so the fixture
  exercises reading both the pre- and post-rename writer name.
- `/daikenja:preflight` is now a bounded review loop instead of a one-shot
  verdict. It runs the six substance checks, dispatches reviewer personas as
  isolated subagents, applies the wording fixes they raise, re-checks once,
  and returns a revised draft plus the facts only the user can supply. The
  loop may change wording and never content: every proposed fix is tested
  against the draft in the main context, and one that needs a fact the draft
  does not contain is reclassified as a question rather than written in. The
  rewrite step is never delegated. Reviewer selection caps at four archetypes
  plus two named recipients, the busy reader is always dispatched, and a
  conflict between two real recipients is reported rather than resolved. With
  subagents unavailable the reviewers run in sequence after one notice
  (`skills/preflight/SKILL.md`).
- `preflight` now says so in one line when it can tell it is not running on
  Opus, before it does anything else. Its adjudication step is what stops the
  loop inventing content, and that judgment is the part most sensitive to
  model strength. The notice never blocks, and it stays silent both on Opus
  and when the model cannot tell. Reviewer personas still all inherit the
  session's model, which is recorded as a limitation in `docs/future-work.md`
  (`skills/preflight/SKILL.md`).
- `preflight`'s no-subagent fallback is documented as an **unsupported path**.
  It still runs, so the skill degrades rather than failing, but it says the
  findings are weaker and it is recorded as a limitation -- sequential
  reviewers read each other and cannot preserve the isolation that makes a
  second opinion worth having (`skills/preflight/SKILL.md`,
  `docs/future-work.md`).
- `preflight`'s cycle 2 re-dispatch is no longer skippable on cost. An
  acceptance run talked itself out of re-dispatching because "re-spawning five
  agents adds cost, not signal", which is the unchecked self-assessment cycle 2
  exists to prevent -- the reviewer raised the finding and is the one who says
  whether the fix landed (`skills/preflight/SKILL.md`).
- Neither `preflight` nor `remember-persona` will record a persona described in
  material that says it is synthetic. Running the acceptance fixtures used to
  offer to write invented people into the user's real `personas.md`
  (`skills/preflight/SKILL.md`, `skills/remember-persona/SKILL.md`).
- `remember-persona` now matches the format the personas file already uses
  rather than imposing the template's, appends after the last entry instead of
  at the end of the file so trailing sections stay last, and no longer repeats
  what the file says about anyone other than the person being recorded. All
  three were found by watching it do the right thing while the skill text said
  otherwise (`skills/remember-persona/SKILL.md`).
- `compose` now routes a recipient the user describes inline to
  `remember-persona` when that person has no entry yet, and reports the write
  in its `Comment` block. Only what the user stated is passed on
  (`skills/compose/SKILL.md`).
- Context-link additions and removals now emit a Changelog line
  (`+link "<label>"` / `-link "<label>"`) and are reported by `project-catchup`,
  closing the one gap where a ledger change was invisible to it
  (`docs/ledger-format.md`, `skills/project-log/SKILL.md`,
  `skills/project-catchup/SKILL.md`).
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

- Removed the non-overridable "never an em dash or en dash" rule from the
  default voice (`docs/voice.md`, `docs/config-contract.md`,
  `templates/writing-style.md`, `skills/thread/SKILL.md`). Absolute dates
  remain the only non-overridable rule. `docs/ledger-format.md`'s three-split
  parser bound is unchanged; only its justification was reworded.

### Documentation

- Documented that a local-marketplace install copies the repo at install
  time rather than referencing it live, and that `claude --plugin-dir .`
  remains the loop to use for development.
- `docs/README.md` now indexes all six contracts in `docs/`. It previously
  listed two, omitted `reading.md` and `substance-checks.md` entirely, and
  still carried a "Still to land" section for `voice.md`, which already
  ships.
- `docs/rewrite-rules.md` states that its no-invention rule outranks every
  rule in `docs/voice.md`, including the one marked non-overridable: a voice
  rule satisfiable only by adding a fact the source lacks is reported as
  unhonorable, not silently broken. `docs/voice.md` scopes "non-overridable"
  to mean only that no `writing-style.md` can disable the rule -- it does not
  rank the rule against other contracts. Neither file's behaviour changes;
  this writes down precedence that was previously resolved only by inference.

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

[Unreleased]: https://github.com/by-carlos/daikenja/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/by-carlos/daikenja/releases/tag/v0.4.0
[0.3.0]: https://github.com/by-carlos/daikenja/releases/tag/v0.3.0
[0.2.0]: https://github.com/by-carlos/daikenja/releases/tag/v0.2.0
