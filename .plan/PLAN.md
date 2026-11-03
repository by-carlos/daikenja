# Replace the ledger with DECISIONS.md, open.md and git history — plan & protocol

This plan replaces Daikenja's append-only project ledger (one file with IDs,
supersession chains, a Changelog and checkpoints, specified by the 799-line
`docs/ledger-format.md`) with a record of what is true now: `DECISIONS.md` at
each registered repository's root, `.daikenja/open.md` in the project's home
repository, and git as the history. It comes from by-carlos/daikenja#292.
This file is the **single source of truth** for durable decisions: the
architecture, the frozen decisions, the stage index, and the operating
protocol every stage session follows. Decisions live here and are *referenced,
never copied* — a decision that exists in one place cannot diverge.

## Architecture (what we're building)

```
Today                                       After this plan
─────                                       ───────────────
.daikenja/ledger.md   (or an absolute       <repo>/DECISIONS.md        every registered repository;
  `ledger:` pointer for pathless projects)    decisions still in force, shared
  IDs, end-of-line markers, chains,           plan-staged-rollout format
  Changelog, checkpoints                      (<!-- decisions-format: 1 -->)
docs/ledger-format.md (799 lines)           <home>/.daikenja/open.md   home repo = first entry of `paths`
daikenja.yaml: `ledger:`, `paths: []`,        open items + "Context links" + "Sources"
  `last_checkpoint` = UTC timestamp           (<!-- daikenja-open-format: 1 -->)
                                            docs/decisions-format.md   byte-identical copy of upstream spec
                                            docs/open-format.md        Daikenja's own: open.md grammar and
                                                                       the version rule for both files
                                            daikenja.yaml: no `ledger:`, no `paths: []`;
                                              `last_checkpoint` = map repo path -> commit SHA
History: git log <sha>..HEAD -- DECISIONS.md .daikenja/open.md, per repository
         (project-catchup reads it; the Slack bot never does)
Every project lives in a git repository; pathless projects are removed.
```

Components touched: format specs (`docs/`), the config contract
(`docs/config-*.md`, `templates/daikenja.yaml`), 15+ skills, the Slack bot
(`bot/`), the user guide (`docs/guide/`, `README.md`), fixtures and invariant
checks (`tests/`). "Ledger" stays the user-facing name for the pair of files
(D-7).

## Requirements

Captured first, before any decision, and played back to the user in plain
language for confirmation. The brief's Outcome, Day to day, Constraints and
Done sections are generated from here.

- **Outcome:** A project's ledger stops being an append-only log and becomes a
  record of what is true now: `DECISIONS.md` at each repository root, in the
  format plan-staged-rollout shares, and `.daikenja/open.md` in the home
  repository, with git holding the history. Every project lives in a git
  repository, so pathless projects go. Skills and the Slack bot read the new
  files; `project-log` writes them in one approved batch; existing ledgers
  migrate with the user's approval and a dated backup.
- **Day to day:** The maintainer drives stages from a Windows desktop, one fresh
  session per stage (`/stage-run` or `/plan-run-local`). Daikenja users run the
  skills in Claude Code sessions inside their repos. The Slack bot keeps running
  headless and read-only (Read, Glob, Grep only): it reads the files, never git.
- **Constraints, ranked:**
  1. Repo rules: never push to `main`, never move `release`, never bump
     `.claude-plugin/plugin.json`; public-repo scrub (no employer terms,
     hostnames, personal paths); fixtures synthetic (invented projects and
     people, `example.com` links); `skills/` ships to users (no contributor
     instructions there), `bot/` stays lean with no new dependency, `.claude/` is
     contributor-only.
  2. The `DECISIONS.md` spec is copied byte-identical — it is the contract
     between the two plugins.
  3. The three design calls settled at launch (D-2, D-3, D-4).
  4. Every on-disk change carries its `docs/upgrading.md` and `CHANGELOG.md`
     `## [Unreleased]` entries in the same commit.
  5. `tests/check-skill-size.py` keeps passing — skills shrink, not grow.
- **Out of scope:** Status reports that also read a staged-rollout plan's
  progress file and open issues; the single entry point that routes work by
  size; persona and writing-style files (including Tensei); the Sources rework
  of by-carlos/daikenja#293 — that issue only gets a note of what changed for
  the ledger's Sources section, posted after the maintainer's yes. No dated
  follow-ups.
- **Done, as checks:**
  1. `python3 tests/check-invariants.py` passes.
  2. `python -m pytest bot/tests` passes.
  3. `cmp docs/decisions-format.md <upstream plan-staged-rollout skills/staged-rollout/references/decisions-format.md>` reports identical.
  4. `docs/ledger-format.md` no longer exists, and `docs/decisions-format.md` and `docs/open-format.md` are each under 200 lines (`wc -l`).
  5. `git grep -nE "pathless|paths: \[\]|daikenja/ledgers" -- . ":!.plan" ":!docs/ledger-migration.md" ":!tests/fixtures/ledger-migration.md" ":!tests/fixtures/setup-user-upgrade.md"` hits only `CHANGELOG.md`, `docs/upgrading.md` history and the D-21 legacy-handling sentences.
  6. A synthetic ledger fixture, plus a pathless one, migrates to `DECISIONS.md` and `open.md` with a dated backup beside the old ledger.
  7. Hand-walked fixtures show: catchup reports changes since a SHA and treats an unresolvable SHA as a first run, saying so; catchup lists uncommitted changes to the two files; a multi-repository project's reading skills read every repo's `DECISIONS.md`; a newer format version makes reading skills warn once and `project-log` refuse.
  8. `SF` walks each of #292's seven "When this closes" items and records each as met.

## Frozen decisions

Change these in THIS file only — never restate them in stage files or the
ledger. If a stage changes a decision, amend it here as the last step of that
stage (Operating protocol, finish step 3). Each decision carries its triage
group: **Decided** (reversible and low impact — settled with its reason, not
asked), **Needs you** (taste, irreversible, cost, security or anything
external — asked in the one bootstrap batch, and the answer recorded) or
**Default for now** (a working default, flagged to revisit). A **Needs you**
decision still waiting for its answer names the stages that wait on it;
only those stages are blocked.

`.plan/BRIEF.md` is the one-page brief generated from this file (stamp line
first, never edited by hand). Whoever edits this file regenerates it in the
same commit; feedback on the brief is applied here, never to the brief.

- **D-1 — Plan branch and names** *(Decided)*. Plan branch
  `feat/292-replace-ledger-decisions-md-open` (the maintainer's instruction and
  their integration-branch convention), stage branches
  `feat/292-replace-ledger-decisions-md-open-s<N>`, worktrees `../daikenja-s<N>`.
  Known gap: the plugin's `renumber_stages.py` only recognises started stages on
  branches named `plan-<slug>-s<N>`, so before inserting a stage, check which
  stages have started by hand (`git branch -a --list
  "feat/292-replace-ledger-decisions-md-open-s*"`).
- **D-2 — Body markers** *(Needs you — answered)*. Only `Blocked by:` survives,
  as a plain-text prefix on `.daikenja/open.md` item lines naming the other item
  in words, because `project-gaps` annotates it. `Contradicts` is dropped:
  `DECISIONS.md` is current-only, so a contradiction is resolved when the entry
  is written. `Imposed` is dropped as a marker and moves into an entry's "why"
  clause ("imposed by the architecture board"). `DECISIONS.md` carries no
  markers.
- **D-3 — `last_checkpoint` is a commit SHA per registered repository** *(Needs
  you — answered)*. Under the project entry, a map from repository path to SHA.
  `project-catchup` diffs `git log <sha>..HEAD -- DECISIONS.md
  .daikenja/open.md` per repository. When the SHA no longer resolves, the run is
  a first run and says so. Replaces today's UTC timestamp in `daikenja.yaml`, so
  it needs an upgrade note.
- **D-4 — Format version lines** *(Needs you — answered)*. `DECISIONS.md` uses
  the shared spec's `<!-- decisions-format: 1 -->`; `open.md` gets
  `<!-- daikenja-open-format: 1 -->`. A newer version than the plugin knows:
  reading skills still read the file and warn once; `project-log` refuses to
  write and asks for a plugin update. This rule lives in Daikenja's own docs
  (`docs/open-format.md`), never in the shared spec copy.
- **D-5 — Spec files** *(Decided)*. `docs/decisions-format.md` is the verbatim
  copy of plan-staged-rollout's
  `skills/staged-rollout/references/decisions-format.md` (byte-identical to
  upstream `main` on 3 Nov 2026; blocker plan-staged-rollout#226 closed).
  `docs/open-format.md` is Daikenja's own: the `open.md` grammar and the version
  rule for both files. `docs/ledger-format.md` is deleted in the last steps of S9, once
  nothing cites it. Skills cite them as `${CLAUDE_PLUGIN_ROOT}/docs/...`.
- **D-6 — Who commits** *(Needs you — answered)*. `project-log` writes the files
  and never commits. `project-catchup` also lists uncommitted changes to the two
  files, from `git status`, as "not committed yet", so nothing is invisible.
  Reason: no skill commits on whatever branch the user is on; one notice line is
  the nudge.
- **D-7 — "Ledger" stays the user-facing word** *(Needs you — answered)*,
  redefined as `DECISIONS.md` plus `open.md`. Skill trigger phrases, bot prompts
  and their tests, and `docs/guide/ledger.md` stay valid.
- **D-8 — Home repository is the first entry of `paths`** *(Decided)*. Reuses
  the existing "first path is the project root" rule; no new key.
  `setup-project` asks which repository is home and writes it first.
- **D-9 — The `ledger:` key goes** *(Decided)*. Files sit at fixed paths:
  `<repo>/DECISIONS.md`, `<home>/.daikenja/open.md`.
- **D-10 — Closing an open item deletes its line** *(Decided)*. No IDs; git
  keeps the history.
- **D-11 — Migration drops superseded entries and keeps a dated backup**
  *(Decided)*. In-force decisions become `DECISIONS.md` entries, superseded ones
  are dropped, open items move to `open.md`; the old ledger is kept as
  `ledger.<YYYY-MM-DD>.bak.md` beside it; the user approves the result before
  anything is written.
- **D-12 — This repo's decision record** *(Decided)*. No ADR folder or
  `DECISIONS.md` exists in by-carlos/daikenja, so the plan's lasting decisions
  go to a new root `DECISIONS.md` at close (SF). That file is the adopted
  decisions document for this repository.
- **D-13 — One plan, not a programme** *(Decided)*. The format swap is one
  outcome that cannot merge in pieces.
- **D-14 — Changelog entries and shared write territory** *(Needs you —
  answered)*. `CHANGELOG.md` `## [Unreleased]` is written by S1 and S8, each
  with its `docs/upgrading.md` note in the same commit, and by S9, which writes
  the entry set for every other stage from their ledger notes — so the
  parallel wave never collides there. Fixtures whose `Depends on:` lines cite
  several skills are written by parallel stages on purpose: small,
  order-independent overlaps; the second merger syncs and re-runs its
  acceptance. `tests/README.md` is edited only by a stage that adds or removes
  a fixture.
- **D-15 — Release notes say pathless projects are gone** *(Decided)*. The
  README advertises them today; the changelog entry and README say so plainly.
  The README sentence says "projects without a folder", so it does not trip the
  Done check 5 grep.
- **D-16 — Every stage keeps the invariants green** *(Decided)*. Each stage runs
  `python3 tests/check-invariants.py` before its PR and updates the fixtures and
  `Depends-on` lines that cite what it changed.
- **D-17 — The bot stays read-only and dependency-free** *(Decided)*. It reads
  current files only, never git history; no new entry in `bot/requirements.txt`.
- **D-18 — The #293 note is posted only after the maintainer's yes**
  *(Decided)*. SF drafts the note of what changed for the ledger's Sources
  section; posting is outward-facing.
- **D-19 — Plan review is pragmatic** *(Needs you — answered)*. Lenses:
  Simplicity, Architect, Security, Operator. A finding needs a concrete
  consequence for what the plan does; Security reports only abuse paths with a
  plausible actor and path, never checklist hygiene.
- **D-20 — Migration procedure lives in `docs/ledger-migration.md`** *(Default
  for now — revisit at S8 if `setup-project` would break
  `check-skill-size.py`)*. `setup-project` runs it per project; `setup-user`'s
  upgrade branch hands off to it.
- **D-21 — Legacy config keys** *(Default for now — revisit after the first real
  upgrade)*. Readers ignore a leftover `ledger:` with a one-line notice pointing
  at `setup-user`; a `paths: []` project is reported as "needs migration" and
  skipped. An old-format ledger at the legacy location (`.daikenja/ledger.md`
  in the home repository, no `ledger:` key needed) with no `.daikenja/open.md`
  beside it also means "needs migration", whether or not a `DECISIONS.md`
  exists: readers say so in one line pointing at `setup-user`, and
  `project-log` refuses to scaffold or write either file over it. *(Amended in
  S1: keyed on the missing `open.md` rather than a missing `DECISIONS.md`, so a
  `DECISIONS.md` another tool wrote does not hide an unmigrated ledger.)*
  *(Amended in S2: the migration's own batch, handed to `project-log` by
  `docs/ledger-migration.md`, is exempt from that refusal -- it is the run the
  refusal points at. `setup-project`'s seed and every other run are not.)*
- **D-22 — Pathless migration target folder** *(Default for now — revisit at S8
  if users have no registered root)*. `setup-project` asks for the folder and
  suggests a sibling of an already-registered root, named after the project key.
  The suggested folder is never inside an existing repository without asking:
  S8 runs `git -C <target> rev-parse --show-toplevel`, and if the target is
  inside a repository it names that repository and asks. The default is a new
  folder outside any repository, with `git init`. The approval line states that
  the content moves from a private folder into a repository.
- **Git strategy:** branch-per-stage (fixed — the only supported model).
  `.plan/` is **tracked** on the plan branch and the plan branch has an
  **upstream** — both are load-bearing, not housekeeping (preflight step 0.0).
  `main` → `feat/292-replace-ledger-decisions-md-open` (the plan branch; `.plan/`
  lives here) → one branch per stage
  `feat/292-replace-ledger-decisions-md-open-s<N>` (flat names — git refs can't
  nest a branch under an existing branch), each landing as a **squash-merged**
  PR into `feat/292-replace-ledger-decisions-md-open`; final PR
  `feat/292-replace-ledger-decisions-md-open` → `main` at closeout is a **normal
  (non-squash) merge** so each stage keeps its own commit on `main`. Commits on
  a stage branch are compulsory
  and incremental (logical units as the stage progresses, not one commit at
  the end). The agent creates and pushes stage and plan branches without
  asking, and **opens** the stage PR as a compulsory part of finishing a
  stage — never merging without your OK, never pushing to `main`. The one
  carve-out is the plan-level `merge: auto` flag (Stage index, plan flags
  line): it gives that OK in advance for **stage PRs only**, so the session
  squash-merges its own stage PR once checks are green; the plan→main PR is
  manual in every mode. A stage
  cannot be marked `done` until its PR is merged into the plan branch; the
  `done` edit itself is committed on the plan branch *after* the merge
  (Operating protocol, finish step 5), never on the stage branch.
- **Worktree strategy:** worktree-per-stage (fixed — the only supported
  model). *The clone holds the plan; worktrees hold the work.* The main clone
  stays parked on `feat/292-replace-ledger-decisions-md-open` for the life of
  the plan — that is the only branch ever checked out there, which is what keeps
  `.plan/` readable and the
  `done` write committable at any moment without disturbing an in-flight
  stage. Each stage branch is checked out **only** in its own sibling
  worktree, `../daikenja-s<N>` (`-redo-<K>` for a redo), created from
  the plan branch tip. Provisioning prefers the harness's native worktree
  mechanism, but only when it honors this convention's exact branch and path
  names, and falls back to `git worktree add` otherwise; it never degrades
  to checking a stage branch out in the clone (Operating protocol, step 4).
  Teardown is part of finishing: a clean, fully-pushed worktree is removed
  with its merged branch, and anything else is left alone and reported
  (finish step 5).
- **Final review stage:** the last stage (`SF`) is a standing plan review and
  stays last. It catalogs loose ends — each becomes an issue, a later plan (the
  programme), or an explicit "accepted, won't fix" — and NEVER implements and
  never adds a stage, except a **fix**: one that names the requirement, failing
  Done check or regression it repairs (never a feature), with the user present
  and saying yes, at most 3 per plan (a fourth is a hard stop in every mode).
  Unattended, `SF` stops and asks instead of adding a fix.

## Plan review

Run by bootstrap before the scaffold is committed — lenses, digest and
outcomes are defined in the `staged-rollout` skill's
`references/plan-review.md`.

- **Date:** 2026-11-03 · **Lenses:** Simplicity (always); Architect — the
  ledger file format and the `daikenja.yaml` schema change across skills, bot
  and docs; Security — catchup passes a config-stored SHA to `git`, migration
  rewrites user files (run pragmatic, per D-19); Operator — the Slack bot runs
  unattended and its reading changes. No lens called the plan unsound.
- F1 S8/S1 — migration moved files only, stranding config keys and the card →
  **changed** S8 edits the config entry and moves the card in the same
  approval; S1's upgrade note defers those removals to the migration.
- F2 S6/S8 — setup and migration wrote the files directly, bypassing
  `project-log` → **changed** both write through `project-log` (#292 makes it
  the one writer); S6 depends on S2.
- F3 S5/S7 — the bot prompts name no ledger paths, so the section-name handoff
  was empty → **changed** handoff dropped; S7 kept for F7's work.
- F4 S10 — a serial tail of small edits → **changed** folded into S9's last
  steps; S10 removed.
- F5 every stage — eleven `CHANGELOG.md` entries collide in wave 2 →
  **changed** `tests/README.md` edited only where a fixture is added or
  removed; S9 writes the changelog entries except S1's and S8's (maintainer's
  answer, D-14).
- F6 D-21 — an unmigrated ledger at the default location went undetected and
  `project-log` could fork it → **changed** D-21 amended; S1 and S2 implement.
- F7 S5/S7 — the headless bot discards "needs migration"/"newer format"
  notices and posts a normal verdict → **changed** S5 emits a fixed token; S7
  logs it and posts one fixed line.
- F8 D-22/S8 — a pathless ledger could migrate into an existing repo's working
  tree and get committed → **changed** D-22 amended: `rev-parse` check, ask,
  default outside any repo.
- F9 Done check 5 and stage greps — they matched `.plan/` and the migration
  text → **changed** exclusions added; D-15 wording adjusted.
- F10 S8 — migration would cite `ledger-format.md`, which S9 deletes →
  **changed** `docs/ledger-migration.md` is self-contained.
- F11 S6 — deleting `templates/ledger.md` early broke link check (j) →
  **changed** moved to S9's tail with the other de-links.
- F12 S9/S8 — plugin and bot update separately with no documented order →
  **changed** operator sequence in `slack-bot.md` and the upgrade note.
- F13 S3 — an existing scalar `last_checkpoint` had no defined handling →
  **changed** treated as a first run with a stated reason.
- F14 (Security, outside its lens) S2/S6/S8 — an existing `DECISIONS.md`
  (e.g. from plan-staged-rollout) could be overwritten → **changed**
  `project-log` adopts it and adds entries; fixture cases in S6 and S8.

## Stage index & dependencies

| Stage | File | Depends | mode | exec | model | effort | gate | estimate |
|---|---|---|---|---|---|---|---|---|
| S0 Format specs and file templates | `stage-0-format-specs.md` | — | direct | inline | opus | high | auto | 1–2h |
| S1 Config, resolution and reading contracts | `stage-1-config-contracts.md` | S0 | direct | inline | opus | high | auto | 1.5–3h |
| S2 project-log writes both files | `stage-2-project-log.md` | S0, S1 | direct | inline | opus | high | auto | 2–3.5h |
| S3 Catchup and decisions read git history | `stage-3-catchup-decisions.md` | S0, S1 | direct | inline | opus | high | auto | 1.5–3h |
| S4 Gaps, summary, list and sources skills | `stage-4-gaps-summary-list-sources.md` | S0, S1 | direct | inline | opus | medium | auto | 1.5–3h |
| S5 Judgement, thread, meeting-review and other readers | `stage-5-other-readers.md` | S0, S1 | direct | inline | opus | medium | auto | 1.5–3h |
| S6 setup-project registers git-backed projects only | `stage-6-setup-project.md` | S2 | direct | inline | opus | high | auto | 1.5–3h |
| S7 Slack bot reports unreadable project data | `stage-7-bot.md` | S5 | direct | inline | opus | medium | auto | 1–2h |
| S8 Migration from the old ledger | `stage-8-migration.md` | S6 | direct | inline | opus | high | auto | 2–4h |
| S9 User guide, README and retiring ledger-format.md | `stage-9-user-docs.md` | S2, S3, S4, S5, S6, S7, S8 | direct | inline | opus | medium | auto | 2–3.5h |
| S10 Fix: align the migration batch exemption | `stage-10-fix-migration-exemption.md` | S9 | direct | inline | opus | medium | auto | 0.5–1h |
| SF Plan review | `stage-f-review.md` | S9, S10 | direct | inline | opus | high | auto | 0.5–1h |

Plan flags: `merge: auto` · `plan-dir: delete`

Plan estimate: summed 16.5–32h · elapsed 11–21h

This table is the **single authoritative home** for every stage's `depends` /
`mode` / `exec` / `model` / `effort` / `gate` / `estimate`, and the **plan
flags** line under it is the home of the plan-level `merge` and `plan-dir`
flags. The **plan estimate** line is computed from the `estimate` column by
the `staged-rollout` skill's `scripts/estimates.py plan`, never added up by
hand, and recomputed whenever a row's estimate or `depends` changes. Stage
files never restate them (a copy is what drifts), and the tooling reads them
from here: `/stage-run`'s weight check reads `model`/`effort` from this index,
the runnable-set logic (below) reads `depends` from it, an unattended runner
reads `gate` and `merge`, and `/plan-close` reads `plan-dir`. A stage that
isn't in this table is invisible to all of them — so adding a new stage
(including one the final review spawns) means passing the scope referee
(*Adding a stage*, below), then adding its row here first, in
running order, then running the `staged-rollout` skill's
`scripts/renumber_stages.py --slug 292-replace-ledger-decisions-md-open`, which
renumbers only the unstarted
stages (index, file names, ledger, `depends`, `BLOCKED.md`, `S<N>` references);
regenerate `.plan/BRIEF.md` in the same commit. **Known gap (D-1):** the script
only recognises started stages on branches named `plan-<slug>-s<N>`, which this
plan's branches are not, so check by hand which stages have started
(`git branch -a --list "feat/292-replace-ledger-decisions-md-open-s*"`) before
running it.

The two plan flags are this plan's **declared defaults**: the answers a
session applies when there is nobody to ask (`--unattended`). An interactive
session still asks, taking the declared value as its recommendation. See the
`staged-rollout` skill, *Unattended mode*, for the full classification of
which questions have a default and which are hard stops in every mode.

Flag values: `mode` = `direct` \| `brainstorm`; `exec` = `inline` \|
`subagent(<model>)`; `model`/`effort` = launch hints (checked, not faked);
`gate` = `auto` \| `human` \| `local` \| `live` (may the stage be launched with
nobody watching? `human` means never — a person's judgment or presence is part
of the stage itself; `local` means never *by a driver that could be running
anywhere but the local machine* — the stage needs a resource only that
machine has: local hardware, a LAN-only host, a secret not committed anywhere
reachable, or a locally-installed toolchain; `live` means never by a driver
either — the stage deploys or changes a running system, so a person chooses
when it fires. Same refusal, different reason — an unattended runner stops in
front of any of the three exactly the same way. Runners fire a stage only when
its `gate` is `auto` or absent — and the local runner, `/plan-run-local`, also
`local`, since it runs on the local machine; any other value, unknown ones
included, is refused and named. Every stage that is not `live` is a build stage, and the
files it may touch are its `## Artifacts` list. Two `live` stages never run at
once: `/stage-run` preflight refuses to start a `live` stage while another
`live` stage's row is `todo` with a stage branch that has commits (preflight
step 0.5's live-sibling signature), and the session-start hook only notes it);
`estimate` = a range in hours such as `1–2h`, or `—` for none (a rough guess
at the stage's own session time, leaving out waits and blockers; the method
is the skill's `references/estimates.md`);
`merge` = `manual` \| `auto` (does the session merge its own stage PR into the plan
branch once checks are green, or offer it for your OK?); `plan-dir` =
`delete` \| `keep` (at closeout, is `.plan/` removed as the last commit on the
plan branch, or left in place because the plan doubles as documentation?).
Defaults stay cheap where cheap is safe, and preserve the fully-manual flow — `direct`,
`inline`, a model sized to finish the stage, `gate: auto`, `merge: manual`,
`plan-dir: delete`; a missing `gate` column, a missing plan-flags line, or a
missing entry on it means those defaults. Escalate only where a stage has
genuine open design questions (`brainstorm`, which also makes it
`gate: human`), needs a resource only the local machine has (`gate: local`),
deploys or changes a running system (`gate: live`), or has heavy iteration
churn (`subagent`). `merge` governs stage PRs only —
the plan→main PR at closeout is manual in every mode.

**Stage IDs** are plain numbers (`S0`, `S1`, `S2`, …) plus `SF` for the final
review. Numbering follows running order: stages that can run side by side get
consecutive numbers, and a stage never has a lower number than anything it
`depends` on. A suffixed ID (`S12b`) is never created — not at scaffold time
and not when a stage is inserted — but an existing one is still read, because
a started stage keeps its ID and plans already in flight keep running.

### Runnable set & waves (derived, never stored)

The `Depends` column is a full dependency graph, so everything about execution
order is **derived from it** — waves and parallelism are never written down as
their own column. A stored copy is what drifts; the graph is the truth.

- **Runnable set:** every stage whose `LEDGER.md` status is `todo` and whose
  `depends` are all `done` or `skipped` — a skip is a settled outcome, not an
  unmet dependency, so it must not deadlock a dependent — plus any `doing`
  stage (resumable). This is a
  *set*, not a single stage. When it holds more than one, those stages have no
  dependency on each other and can be run **concurrently, one per fresh
  session**.
- **Waves:** wave 0 is every stage with no `depends`; wave *k* is every stage
  whose deepest prerequisite sits in wave *k−1*. The number of waves is the
  fewest rounds the plan can take, and the **critical path** — the longest
  chain of `depends` edges — is the floor on elapsed time that no amount of
  parallelism removes.
- **`depends` means "cannot safely start until", not "written after".** List
  only genuine prerequisites. Chaining `S0 → S1 → S2 → S3` when the real graph
  is `S0 → {S1, S2, S3}` costs three rounds instead of two and hides the cost,
  because the index still looks correct.
- **Concurrency is an operator action.** Nothing here launches sessions:
  running a wave in parallel means opening one session per stage yourself —
  or leaving it to an unattended runner outside any session, which launches
  only `gate: auto` stages (or stages with no `gate` column; the local runner
  also `local` ones) and stops in front of any other value — `human`, `live`,
  and `local` for a cloud runner. What
  the protocol owes you is that doing so is safe — see *Concurrent stages*
  below.

### Concurrent stages (when the set fans out)

Running two stages at once changes nothing about the git model: still one
branch per stage, one PR per branch, one stage per session. It adds one
structural fact and four rules about timing.

- **Separate working trees are what make concurrency physical.** Each stage
  runs in its own worktree, so two sessions never contend for `HEAD` and
  neither can see the other's uncommitted work. The rules below are about
  what happens when their *branches* meet at the plan branch.
- **A sibling's stage branch is expected state, not drift.** Two stage
  branches cut from the same plan-branch tip is exactly what a fan-out looks
  like. Preflight step 0.5 classifies by whose stage the mismatch belongs to:
  drift on the stage *this* session is about to run still stops it, while
  another stage's in-flight branch is reported and stepped over.
- **The plan branch is the serialization point.** Parallel stage PRs merge
  **one at a time, first come first served** — there is no queue to manage.
  Whoever merges second re-syncs first (finish step 4): merge the plan branch
  *into* the stage branch, resolve there, and re-run the acceptance checks. A
  PR GitHub calls "mergeable" only means no textual conflict — not that this
  stage still passes after the sibling's change landed.
- **Shared write territory is a `depends` edge.** Two stages with no logical
  relationship can still write the same files, and `Depends` is the only place
  that can express it — so express it there and let the wave structure narrow
  accordingly. There is deliberately **no** separate "territory" field: a
  second place to record the same constraint is a second thing to drift. If
  the overlap is small and genuinely order-independent, leaving both stages in
  one wave is a legitimate choice, and the re-sync-and-re-verify rule above is
  the net that catches it.
- **The `done` ledger write can race.** It is a direct commit on the plan
  branch (finish step 5), so two sessions finishing minutes apart collide
  there. Finish step 5 says how: edit after the fast-forward, replay on
  rejection, never force-push the plan branch.

### Adding a stage — the scope referee

A plan may grow; it should not quietly become a different plan. Every stage
added after the scaffold commit — by a stage session, by the final review's
`Fix:` stages, or by hand mid-plan — passes the **scope referee** first.
Nothing else triggers it: amending a decision, rewording a stage or skipping
one never does, so most sessions never meet it.

1. **Ask the referee before writing the new row.** Dispatch a fresh subagent
   (Sonnet-class) with exactly these inputs and nothing from this session's
   conversation — its value is that it has no stake in the work so far:
   - `## Requirements` › **Outcome** and **Out of scope**, verbatim;
   - the stage being added: its name, and one line on why it is needed;
   - every `Added by` line already in `LEDGER.md`'s notes blocks.

   With no subagent tool, judge it in this session against the same inputs
   only, and say so. The referee returns one verdict and one line of reason:
   - **grows** — the stage serves the Outcome. Add it.
   - **losing shape** — it serves the Outcome, but together with the earlier
     additions it reads as unplanned growth: several additions chasing one
     problem, or additions with no common thread. Add it, and tell the user
     in one line, naming the pattern and suggesting a re-plan of the
     remaining stages. Nothing waits for an answer.
   - **different plan** — it no longer serves the Outcome, or crosses Out of
     scope: a review that starts implementing, a proof of concept turning
     into the production build, a change in what is being built. **Stop
     before writing anything**, show the Outcome, the stage and the reason,
     and offer three choices: **carry on** (add it as asked); **re-plan**
     (amend `## Requirements` to the new direction with the user, then add
     and renumber); or **close this plan** as a milestone (remaining stages
     `skipped` with the reason, `SF`, closeout) and bootstrap a new plan for
     the new direction. The user decides.
2. **Record it** as the first line of the new stage's notes block in
   `LEDGER.md`: `Added by <S<N> | hand> — <why> — referee: <verdict>`, plus
   ` → <choice>` after a **different plan** answer. A recorded line settles
   that stage: it is never refereed again, including on a redo.
3. **Unattended, no stage is added.** The work goes in this stage's notes
   block as a follow-up (*Scope discipline*, step 6), where the final review
   finds it; the referee runs when a person later adds it.

## Operating protocol (every stage session)

0. **Preflight & sync (required):** run this before reading any status or
   touching any branch. The ledger is canonical but may only be trusted
   *after* it passes — git state inherited from a previous session, a remote
   merge, or a crash is verified here, never assumed.
   0. **Verify the plan is real git, not a loose directory.** Two checks,
      both hard gates — the whole protocol rests on them:
      - **`.plan/` is tracked:** `git ls-files --error-unmatch .plan/PLAN.md`.
        If it fails, `.plan/` is untracked or ignored — stop. An untracked
        plan produces no committable content, so stages that only amend
        `PLAN.md`/`LEDGER.md` can never open a PR, which makes every
        downstream dependency gate unsatisfiable; and the entire decision
        record dies with the working directory. Fix by removing the ignore
        rule (`git check-ignore -v .plan/PLAN.md` names it) and committing
        `.plan/` on the plan branch before running any stage.
      - **The plan branch has an upstream:**
        `git rev-parse --abbrev-ref feat/292-replace-ledger-decisions-md-open@{upstream}`.
        If it fails, the
        branch is local-only — the fetch and fast-forward below would succeed
        while doing nothing, forever. Push it (`git push -u origin
        feat/292-replace-ledger-decisions-md-open`) and continue; pushing a
        feature branch needs no
        approval.
   1. **Fetch:** `git fetch origin`.
   2. **Sync the plan branch:** fast-forward local
      `feat/292-replace-ledger-decisions-md-open` to
      `origin/feat/292-replace-ledger-decisions-md-open` —
      `git merge --ff-only origin/feat/292-replace-ledger-decisions-md-open` when
      it is checked out,
      `git fetch origin feat/292-replace-ledger-decisions-md-open:feat/292-replace-ledger-decisions-md-open`
      otherwise.
      This holds under both remote squash-merge and merge-commit: either way
      the remote plan branch only moves forward. If it won't fast-forward, the
      branch has diverged — stop and report. Then **check the branch is not
      ahead**, whichever command ran: `git rev-list --count
      origin/feat/292-replace-ledger-decisions-md-open..feat/292-replace-ledger-decisions-md-open`.
      The check is needed because
      `git merge --ff-only` (unlike the fetch form, which refuses)
      prints `Already up to date.` and exits 0 when the local branch holds
      commits the remote lacks. If the count is non-zero,
      stop and report that many unpushed commits on
      `feat/292-replace-ledger-decisions-md-open`, with the two
      ways out: push the plan branch, or discard the commits. Never push or
      reset on its own — unpushed commits flow into every stage worktree cut
      from this branch and into the remote squash merge, and publishing or
      destroying them is the user's call.
   3. **Verify the trees:** a clean working tree is required in *this* tree
      **and** in the main clone. The clone matters even when the stage runs
      elsewhere: the `done` write (finish step 5) is a commit there, so a
      dirty clone blocks the stage from ever closing. If either is dirty,
      stop and list exactly what is uncommitted — never auto-stash.
   4. **Verify position (the two-tree rule):** the clone is parked on
      `feat/292-replace-ledger-decisions-md-open`; stage branches live only in
      sibling worktrees. Establish
      which tree this session is in — inside a worktree `git rev-parse
      --git-dir` and `--git-common-dir` differ; in the clone they match —
      then check:
      - **The clone's HEAD must be `feat/292-replace-ledger-decisions-md-open`.**
        A stage branch checked
        out there is drift: stop and report. The fix is to check the plan
        branch back out in the clone and give that stage its own worktree —
        never run the stage in the clone.
      - **A fresh stage starts in the clone**, which is where step 4 creates
        its worktree.
      - **A resumed stage must run inside that stage's worktree.** If the
        worktree exists but this session is in the clone, print its path and
        enter it (step 4's provisioning rule) — do not check the branch out.
      - Detached HEAD anywhere, or a worktree whose HEAD is not its own stage
        branch → stop and report.
   5. **Reconcile ledger vs reality:** cross-check the `LEDGER.md` status
      table against actual branch and PR state (`gh pr list --base
      feat/292-replace-ledger-decisions-md-open --state all`, `git branch -a
      --no-merged feat/292-replace-ledger-decisions-md-open`).
      Classify each mismatch by *whose* stage it belongs to — the stage this
      session is about to run, or another one:
      - **Self-healing:** a `doing` row whose stage PR is already merged
        means the merge happened remotely — complete the finish protocol's
        post-merge bookkeeping (finish step 5) by recording that row `done`
        on the plan branch. If that row is the stage *this* session was
        launched to run, the stage is finished: skip to finish step 6 (the
        announcement) — it is neither a resume nor a redo, in any mode.
      - **Drift — report and stop:** a `done` row with an open or unmerged
        stage PR; an open stage PR based on `main` instead of
        `feat/292-replace-ledger-decisions-md-open`; and **this session's own
        stage** showing a `todo` row
        while its stage branch already exists with commits (a crashed
        earlier attempt at the very stage you are starting — resume it or
        discard it, don't run over it).
      - **Report and continue:** *another* stage's `todo` row with an
        existing stage branch that has commits. Under concurrent execution
        that is the ordinary signature of a **live sibling** — a session
        working that stage right now, whose `doing` flip and evidence are
        still on its own unmerged branch and therefore invisible from here.
        Halting would stop every parallel session, so list each one in the
        preflight report (stage id, branch, whether it has an open PR) and
        carry on. Detection is re-aimed, not weakened: the same signature
        with no session behind it is a crashed stage, it reappears in every
        later preflight report, the final review stage sees it, and closeout
        still refuses to run while any stage PR is open or unmerged.

      Then reconcile **worktrees** by the same rule, from `git worktree list
      --porcelain` — but only worktrees whose branch matches
      `feat/292-replace-ledger-decisions-md-open-s*`. An operator's unrelated
      worktree (any other branch)
      is none of this plan's business: it is ignored entirely, never
      classified into any bucket below and never offered for removal. A
      worktree belonging to *this* session's stage that this session did not
      create is the crashed-attempt case — stop, resume or discard it, don't
      run over it. A worktree for *another* `todo`/`doing` stage is the
      ordinary live sibling — list it and carry on. A worktree whose stage
      branch is already merged or gone is an **orphan** from an interrupted
      teardown — report its path and offer removal; never remove it unasked,
      and never assume it is empty.

      Finally, read `.plan/BLOCKED.md` if it exists. A `### S<N>` section there
      records a stage a previous session or an unattended runner marked
      `blocked` while its `LEDGER.md` row still reads `todo` or `doing` — so
      the row alone will not tell you. List each one in the preflight report,
      and where the section belongs to **this session's own stage**, state what
      it was waiting on before starting, so the stage is not walked straight
      back into the same gate. Relaunching by hand is itself the operator's
      answer, so this does not stop the session; deleting the section is theirs
      to do, not yours (*Recording a block*, below).
   6. **Check the brief is current:** if `.plan/BRIEF.md` exists, compare
      its line-1 stamp (`Generated from PLAN.md @ <hash> — do not edit`)
      with the first 12 hex characters of `git hash-object .plan/PLAN.md`,
      both read in the clone on the freshly synced plan branch. A match needs
      nothing. A mismatch means the brief is stale — two sibling stages that
      each amended `PLAN.md` and regenerated leave a merged file matching
      neither — so regenerate it before anything reads it: rebuild each
      section from the `PLAN.md` section its italic *From `PLAN.md` › …* line
      names, keeping the headings and their order, write the new stamp, and
      carry nothing over that `PLAN.md` no longer holds. Commit it directly
      on the plan branch (`chore(plan): regenerate brief`) and push, with the
      `done` write's race handling (finish step 5): edit after the
      fast-forward, replay on a rejected push, never force-push. The file is
      the brief; an artifact render of it, if one was published, is not
      republished here. No `.plan/BRIEF.md` — a plan scaffolded before briefs
      existed — means this step does nothing.
   7. **Report, don't repair:** on anything preflight can't fast-forward or
      reconcile, stop with an accurate report of the state and what would fix
      it — no auto-stash, no reset, no branch deletion, no `git worktree
      remove --force`, and no automatic `git worktree prune`.
1. **Read only:** this file + the target stage file + the `LEDGER.md` status
   table + the notes blocks of the stages this one `depends` on + any docs the
   stage file names + the **decisions in force** covering this stage's files
   (below). Do NOT scan the rest of the repo. (Exception: the final
   review stage reads the *entire* ledger.)

   **Decisions in force.** The repository's decisions document is the one
   the Frozen decisions above record as adopted (bootstrap records it as a
   **Decided** item — an existing current-decisions document, or
   `DECISIONS.md`); with none recorded, it is `DECISIONS.md` at the
   repository root. If it exists, match each path in the stage file's
   `## Artifacts` section against each area's `Paths:` line — an area covers
   an artifact when either path lies under the other (a trailing `/` is a
   subtree, `*` and `**` are globs, `.` is the whole repository) — and read
   too every `DECISIONS.md` in an artifact's parent folders and any file an
   area's `Moved:` line names. Show the covering areas' entries, verbatim
   under their area headings, before implementing. They bind the stage as
   frozen decisions do: work that would contradict one is settled only by a
   frozen decision here that says so — otherwise it is a question for the
   user, and unattended it is a block (*Recording a block*). An adopted
   document with no `Paths:` lines cannot be matched: name it in one line so
   the stage reads what applies. No decisions document, or no `## Artifacts`
   section, means nothing to show and nothing else changes.
2. **Weight check:** compare the session's model against the stage's `model`
   flag (your system prompt states your model), checked mechanically against
   the `staged-rollout` skill's **Model weight tiers** rubric — not a guess
   about your own weight; state the `effort` actually set, read from
   `CLAUDE_EFFORT`, next to the stage's `effort` flag (`med` = `medium`), and
   say it could not be read if that variable is absent rather than assuming
   it matched — an unreadable effort is not a mismatch and neither asks nor
   blocks. If the session is lighter than recommended, or the effort set
   differs from the flag (higher or lower — both are misaligned), **stop**
   before doing anything: name the mismatch and the model and effort to
   relaunch with. There is no continue option; nothing is written and the
   row stays `todo`. A heavier model alone is not a mismatch. Attended, end
   the stop with one plain line the operator can act on in place — *"switch
   the model and effort in this session's model menu to \<model> /
   \<effort>, then type **go** (or just **.**)"* — and treat a **go** or
   **.** as the next message as a fresh start of this same stage, re-reading
   the model and `CLAUDE_EFFORT`: it re-checks, it never overrides. If the
   disclosed model doesn't recognizably match a tier in the rubric, don't
   guess — state the exact model ID/name and ask the user which tier applies.
   **Unattended?** If this session was launched with nobody to answer it (an
   unattended runner, or `/stage-run`'s `--unattended` argument), check the
   stage's `gate` first: a stage whose `gate` is anything but `auto` — `human`,
   `local`, `live`, or a value not in that list — is never
   started unattended; report that and stop here. The one exception is
   `local` in a session `/plan-run-local` launched (`/stage-run`'s
   `--runner local`): that driver runs on the local machine, so it starts. For a stage that starts, every offer or
   question in this step and the ones below either has a **declared default**
   on the plan flags line or is a **hard stop** — there is no third option
   and nothing waits for an answer (see the `staged-rollout` skill,
   *Unattended mode*, for the full classification). Nothing in this step has a
   declared default, so a lighter-than-recommended model, a readable effort
   that differs from the flag, or an unrecognised tier marks the row `blocked` with the mismatch as the runbook, commits it
   per *Recording a block* below — this step runs before step 4, so that is a
   direct commit on the plan branch — and stops.
3. **Dependency gate:** for every `depends` stage, confirm it is `done` or
   `skipped` in `LEDGER.md` **AND its stage branch/PR is merged into the plan
   branch** (`git fetch` first — the merge may be remote and not yet local).
   Both must hold, for a `skipped` dependency exactly as for a `done` one: a
   skip still commits its ledger row and opens a PR (nothing here exempts it
   from the git strategy above), and a dependent branched before that PR is
   merged would silently miss the decision. A `done`/`skipped` ledger row
   alone is not enough: a stage branched off the plan branch before a
   prerequisite's PR is merged will silently lack that prerequisite's work. If
   either isn't true, stop and say so. This gate is always satisfiable:
   **every** stage has repo artifacts, because `.plan/` is tracked and every
   stage edits the ledger — a documentation- or decision-only stage, and a
   skipped one, still commits its `PLAN.md`/`LEDGER.md` changes and still
   opens a PR. A depends-stage with no PR means preflight step 0.0 was
   skipped, not that the stage was exempt.
4. **Branch & worktree:** the stage runs in its own sibling worktree and the
   clone stays on the plan branch (frozen decision above). Create branch and
   worktree together from the plan branch, which preflight step 2 already
   brought up to date — or use them as-is if the human already made them:
   - **Prefer the harness's native mechanism** where there is one (Claude
     Code's `EnterWorktree`, or the `superpowers:using-git-worktrees` skill
     when installed) — but only if it honors this protocol's naming
     convention (branch `feat/292-replace-ledger-decisions-md-open-s<N>`, path
     `../daikenja-s<N>`).
     A mechanism that picks its own path or branch name breaks the ledger's
     path references, the teardown command, and the next session's resume
     lookup — none of them can find a worktree under any name but this one.
     If it can't be pointed at this exact name and path, don't use it.
   - **Otherwise:** `git worktree add ../daikenja-s<N> -b
     feat/292-replace-ledger-decisions-md-open-s<N>
     feat/292-replace-ledger-decisions-md-open`, then work there by absolute
     path for the rest of the stage.
   - **If the harness refuses to work outside its starting directory:** stop,
     print the worktree path, and tell the operator to relaunch this stage
     with that path as the working directory. **Never** fall back to checking
     the stage branch out in the clone — that closes the ledger window and
     breaks every concurrent session.
   - **A fresh worktree holds only tracked files.** Untracked local setup the
     stage needs — `.env`, local config, build caches, dependency directories
     — is not there. Copy what it needs and record in the ledger notes what
     you copied, because the next session starts from the same blank slate.
   **Redo:** re-running a `done` stage cuts a fresh
   `feat/292-replace-ledger-decisions-md-open-s<N>-redo-<K>` branch in its
   **own** worktree (`../daikenja-s<N>-redo-<K>`) from the current plan branch
   tip — never reuse a merged stage branch or its worktree.
5. **Honor `mode` / `exec`:**
   - `mode: direct` → state a one-line plan, then implement.
   - `mode: brainstorm` → run a design pass scoped to THIS stage first,
     treating frozen decisions as settled; land outcomes as frozen decisions
     here, not in a second spec.
   - `exec: inline` → implement in this session.
   - `exec: subagent(<model>)` → act as orchestrator and dispatch the
     implementation to a subagent so the churn stays out of this context.
6. **Scope discipline:** do only this stage. Work belonging to another stage →
   note it in the ledger notes and leave it untouched. It may become a new
   stage, through the scope referee (*Adding a stage*, above).
   **Acceptance is the stop line.** Once this stage's Acceptance checks pass,
   the stage is finished. More of the same work — a proof of concept
   hardened into the production build, one more feature in the same files —
   is a new stage however natural the next step looks, and it is handled
   exactly as above: a note, then the scope referee when attended, a
   follow-up note when unattended. Work that crosses `## Requirements` ›
   **Outcome** or **Out of scope** is handled the same way before Acceptance
   passes too.
7. **Finish protocol (required):**
   1. Run the stage's **Acceptance** checks; paste the real output into the
      stage's notes block in `LEDGER.md`. Then add this session's
      **`Actuals:` line** to the same block: run the skill's
      `scripts/effortlog.py usage` and paste its `line` as is. Every session
      that worked on the stage adds one, including one that stops `doing` or
      `blocked` (with its handoff note or runbook). Then add the
      **`Artifacts check:` line**, from the stage worktree: run the skill's
      `scripts/artifacts_check.py --stage-file .plan/<this stage's file>
      --base origin/feat/292-replace-ledger-decisions-md-open` and paste its line
      as is — `match`,
      `undeclared` (no paths in `## Artifacts`) or `outside: <paths>`. It is a
      record, never a gate: nothing stops on it, and the final review judges
      each `outside` line.
   2. Update the stage's table row: absolute date, verified yes/no, one-line
      result — but the status stays `doing` here. `done` is recorded only
      after the PR merges (step 5 below), so a `done` row is always visible
      from a synced plan branch. Detail goes in the notes block, never the
      table. A stage stopping `blocked` instead of finishing never reaches
      step 5 at all — *Recording a block* below says where its row and runbook
      are committed, and it still opens its PR at step 4.
   3. If a decision changed or was added, amend **Frozen decisions in this
      file** — nowhere else — and, when `.plan/BRIEF.md` exists, regenerate
      it in the same commit (as preflight step 0.6 does).
   4. Commit on the stage branch throughout the stage at logical units
      (conventional messages) — not one commit at the end. Everything in this
      step — commits, push, the PR, any sibling re-sync merge — happens
      **inside the stage worktree**, never in the clone. There is no such
      thing as a stage with nothing to commit: steps 1–3 above always change
      tracked files under `.plan/`, so a stage whose Artifacts are "no host or
      secret changes" still lands its ledger evidence and any frozen-decision
      amendment as a commit. Push the branch
      and **open the PR** into `feat/292-replace-ledger-decisions-md-open`
      (compulsory, not offered),
      pinning the base explicitly — `gh pr create --base
      feat/292-replace-ledger-decisions-md-open` — never
      relying on the default, which falls back to the repo's default branch
      (`main`). Then **offer** to merge it once reviewed — never merge on
      your own. Stage PRs are **squash-merged** (one commit per stage on the
      plan branch), and the merged stage branch is deleted. The stage cannot
      be marked `done` until this PR is merged.
      **Under `merge: auto`** (plan flags line): the OK is given in advance
      for stage PRs, so once the sibling re-sync check below has run and
      every required check on the PR is green, squash-merge it yourself
      (`gh pr merge --squash --delete-branch`) and continue straight to step
      5. Never force or retry past a refusal — a red or missing check, or a
      protection rule on the plan branch, means the merge did not happen this
      session: leave the row `doing`, report the refusal and why, and end;
      the next preflight (step 0.5) finishes the bookkeeping once someone
      merges it. `merge` never applies to the plan→main PR, and it never
      reaches a stage that is stopping `blocked` — that PR is opened and left
      for a person (*Recording a block* below).
      **Merge order with a sibling in flight:** parallel stage PRs merge one
      at a time, first come first served — the plan branch is the
      serialization point, so there is no queue to coordinate. Before
      offering the merge, `git fetch origin` and check whether
      `origin/feat/292-replace-ledger-decisions-md-open` has moved past this
      stage branch's merge base. If
      it has, a sibling merged while this stage was in flight: merge the plan
      branch *into* the stage branch (`git merge
      origin/feat/292-replace-ledger-decisions-md-open`),
      resolve any conflict there, push, and **re-run the Acceptance checks**,
      replacing the evidence in the ledger notes with the output from the
      merged result. GitHub reporting the PR as mergeable is not enough — it
      means no textual conflict, not that this stage still passes after the
      sibling's change. Never rebase or force-push a stage branch: resolving
      with a merge commit on the stage branch costs the plan branch nothing,
      because the squash merge discards it. If yet another sibling lands in
      the window between the re-sync and the merge, repeat the check — it is
      cheap, and a stale re-verify is worth less than none.
   5. **After the merge:** return to the main clone — it is already on
      `feat/292-replace-ledger-decisions-md-open`, so there is no checkout to
      do — and fast-forward it
      (`git fetch origin` + `git merge --ff-only
      origin/feat/292-replace-ledger-decisions-md-open`), then
      flip the stage's row to `done` as a direct commit on the plan branch
      and push. The `done` edit lives on the plan branch, after the merge —
      never on the stage branch. If the merge doesn't happen this session,
      leave the row `doing` and end anyway; the next session's preflight
      (step 0.5) completes this bookkeeping when it finds the merged PR.
      **If a sibling stage is running, this write races.** Both sessions
      commit directly on the plan branch, so: make the edit *after* the
      fast-forward (never before), touch only your own row, and push
      immediately. If the clone is dirty on arrival and the change isn't
      yours — a sibling's session is mid-edit in this same clone — wait and
      retry rather than committing on top of it or folding it into your own
      commit; that is the one case the push-race handling below doesn't cover,
      because it happens before either side has pushed. If the push is
      rejected as non-fast-forward, the sibling won the race by seconds —
      fetch and replay your single ledger commit on top (`git pull --rebase
      origin feat/292-replace-ledger-decisions-md-open`), then push again.
      **Never
      force-push the plan branch**: last-writer-wins would erase the
      sibling's `done` row. If the replay conflicts, both rows are wanted —
      the two edits touch adjacent lines of the same table, so resolve by
      keeping **both**.

      **Then tear the worktree down, from the clone.** If the stage worktree
      is clean and fully pushed, remove it and delete the merged stage branch:
      `git worktree remove ../daikenja-s<N>`, then `git branch -D
      feat/292-replace-ledger-decisions-md-open-s<N>`. Use `-D`, not `-d` — the
      stage PR was squash-merged,
      so git's own merge-tracking never sees this branch as merged into
      `feat/292-replace-ledger-decisions-md-open` and `-d` refuses with "not
      fully merged" even though the
      squash commit already carries the work safely onto the plan branch,
      which is exactly what makes `-D` safe here. If the worktree holds
      anything uncommitted, unpushed, or stashed, **leave it** and report its
      path and what is in it — a worktree is a real directory and its
      contents are not
      recoverable from git. Never `--force`, never `prune` to tidy up; an
      orphan left behind is reported by every later preflight and gates
      closeout, which is the safe failure. **The two thresholds differ on
      purpose:** a stage leaves anything it is unsure about, and closeout
      sweeps up whichever of those turn out to be merged with nothing
      unpushed. Erring towards leaving costs a line in a report; erring
      towards removing costs a directory git cannot give back. If the merge did not happen this
      session, the worktree stays — teardown belongs with the `done` write.

      End the session in the clone, on the plan branch.
   6. Announce: this stage is **finished**, then the **complete runnable
      set** — *every* `todo` stage whose `depends` are now all `done` or
      `skipped`, not just the first (see *Runnable set & waves* above). For
      each one, give
      the exact prompt/command to run it, its recommended `model`/`effort`
      and its `gate` from the stage index — a `gate: human` stage needs a
      person at the keyboard, a `gate: local` stage needs a machine that
      has what it needs, and a `gate: live` stage changes a running system (no
      two at once), so an unattended runner reading this stops in front
      of each. If the set holds more than one stage, say so
      plainly: they are independent and can be launched **concurrently, one
      per fresh session**. If it is empty, say which it is — every stage
      `done`/`skipped` (ready for closeout) or stalled on `blocked` rows and
      unmet dependencies. Then stop.

### Recording a block (wherever it happens)

A `blocked` record is only worth writing if the next reader — a person, or an
unattended runner — can find it **without waiting for a merge**. Where the
session commits it depends on one thing and nothing else: whether this stage's
branch exists yet.

- **Before the stage branch exists** — preflight, the weight check (step 2),
  the `gate: human` backstop, the dependency gate (step 3). This session is in
  the clone, on the plan branch, and no stage branch can be holding unmerged
  edits to this stage's row. Set the row `blocked` in `LEDGER.md`, write the
  runbook in its notes block, and commit that **directly on the plan branch,
  then push** — the same write as the `done` edit of finish step 5, with the
  same race handling: edit after the fast-forward, touch only your own row,
  replay on a rejected push, never force-push.
- **After the stage branch exists** — any block from step 4 onwards, including
  a mid-stage question the frozen decisions don't settle. The row and its notes
  may already carry this stage's own committed evidence on the stage branch, so
  the plan branch must not be edited into conflict with it. Two writes, in this
  order:
  1. **In the worktree, on the stage branch:** set the row `blocked`, write the
     full runbook in the stage's notes block, commit, push, and **open the
     stage PR** into `feat/292-replace-ledger-decisions-md-open` (compulsory at
     finish step 4 in every case)
     so the runbook is reviewable there. Never merge it — a blocked stage is
     not a finished one, and `merge: auto` does not reach it.
  2. **In the clone, on the plan branch:** append a `### S<N>` section to
     `.plan/BLOCKED.md` — **never** the ledger row — carrying one line on what
     is being waited for, the stage branch name, and the stage PR's URL. Commit
     and push it. Point at the PR for the detail rather than restating the
     runbook: a copy is what drifts.

  Leave the plan branch's ledger row reading `doing`. It becomes `blocked`
  there only once the stage PR is merged, and that is a person's call.

**The discovered case — `needs-local`.** `gate: local` (Stage index &
dependencies, above) covers a local-resource need known at authoring time. A
stage can also discover this *mid-run*, with nothing declared up front — a
credential that turns out to live only on this machine, a host only reachable
from a LAN this session isn't on, a locally-installed toolchain the session
doesn't have. Record it exactly like any other block above — same two cases
by whether the stage branch exists yet, same commit points — but write the
one-line reason as the literal token `needs-local`: in the row's `Result`
cell for the before-the-branch case, or as the first line of the
`.plan/BLOCKED.md` section's body for the after-the-branch case. That literal
token is what lets an unattended runner's report say "re-run this stage
locally" instead of a bare failure the next reader has to diagnose from
scratch. The full runbook — what exactly is missing and how to get it — still
goes in the notes block or the stage PR, same as any other block; `needs-local`
is a machine-readable tag, not a substitute for it.

**Not every unattended stop is a block.** A stage that did its work and stopped
only because `merge: manual` withheld the merge — or because a required check
was red — is not `blocked`: it leaves the row `doing` with its PR open, exactly
as finish step 4 says, and writes nothing here. This record is for a question
or a gate the stage cannot get past at all.

**Why the sibling file and not the row.** `.plan/BLOCKED.md` is the one file no
stage branch ever edits, so a write to it on the plan branch cannot contend
with the stage branch's own ledger edits. Writing the block into `LEDGER.md` on
the plan branch instead would diverge from the stage branch's unmerged commit
and leave that stage's own PR unmergeable — the runbook would be naming a merge
its own write had just made impossible.

**Both readers see it.** Preflight step 0.5 reads `.plan/BLOCKED.md` alongside
the ledger, and an unattended runner treats any stage id with a `### S<N>`
section there as `blocked` and never retries it, whatever the `LEDGER.md` row
still reads. Nothing clears a section automatically: delete that stage's
section by hand once the stage is resolved — its PR merged, or its row `done`.
