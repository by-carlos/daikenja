---
name: project-catchup
description: Reports what changed in a project's Daikenja ledger since the user last checked, read from git history of each repository's DECISIONS.md and the home repository's open.md, then advances each repository's checkpoint on approval. The only skill that writes last_checkpoint in daikenja.yaml; it never touches ledger content. Accepts an optional project key -- `/daikenja:project-catchup <key>` reads that project from anywhere.
metadata:
  owner: Carlos
  version: 3
  writes: ~/.claude/daikenja/daikenja.yaml (last_checkpoint only)
disable-model-invocation: true
---

# Catchup

Reports what changed since the user's last checkpoint, then moves the
checkpoint. The ledger keeps no changelog: git is the history, so the delta is
the commits that touched `DECISIONS.md` and `.daikenja/open.md` since the
commit the user last saw, per repository. The one read skill that writes
anything, and it writes exactly one config key, never the ledger.

## Step 0: read the contracts

Read these before doing anything. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/reading.md` § Step A0, § Step A, § Step B, §
  Step C and § Notices, shared wording -- the shared resolve-and-parse
  mechanism Steps 1 and 3 below follow, plus the exact notice text they reuse
  without restating it (a config marked absent or a project left unregistered
  has no literal wording inline in Step A -- only in § Notices, shared
  wording).
- `${CLAUDE_PLUGIN_ROOT}/docs/decisions-format.md` § Shape, § Current only and
  § Splitting -- what an entry is, why a replaced entry shows up in history as
  an edit or a deletion rather than a marker, and the `Moved:` files that are
  part of the same record.
- `${CLAUDE_PLUGIN_ROOT}/docs/open-format.md` § Version line, § Section: Open
  items, § Closing an item, § Section: Context links, § Section: Sources and §
  Reading rules for skills -- each section's grammar for naming a changed line,
  and why a deleted open item means it was closed.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-schema.md` § Field notes --
  `last_checkpoint`'s format: a map from repository path to commit SHA.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-writers.md` -- who writes what. This doc
  has no subsections to narrow to -- the whole file is that one topic.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. Read in full and not narrowed to a section: Step 4 explicitly
  follows only § Entries are named topic-first, location in parentheses, but the
  contract's own scope says a skill "implements it; it never redefines it" --
  every rule in the file (tone scaling, the clean-result line, itemised
  findings) governs this skill's replies whether or not Step 4 names it.

## Step 1: resolve config, project and ledger

Follow `reading.md` § Step A0, § Step A and § Step B.

**The user may name a project** -- `/daikenja:project-catchup <key>`, or the key in
prose. `reading.md` § Step A0 is the whole rule: a named key resolves that
project from anywhere on disk and never falls back to the current directory.
Do not restate the resolution here.

**The repositories to diff** are the project's paths, in `paths` order, each
one that exists on disk. An unregistered project has one: the repository
holding the current directory (`git -C <dir> rev-parse --show-toplevel`). A
registered path that is not a git repository is reported in one line and
gets no history -- every project lives in git, so this is a broken
registration, and `/daikenja:project-list` is where it is fixed.

## Step 2: read and check each checkpoint

Read the matched project's `last_checkpoint` and decide, per repository,
whether there is a baseline to diff against. Every case without one is a
**first run for that repository**, and the report says which case and why --
a silent first run reads exactly like "nothing changed before".

- **No `last_checkpoint`, or no entry for this repository's path** (matched
  exactly as written in `paths`): `No checkpoint for <repo> yet.`
- **A scalar value** -- one string instead of a map, the UTC timestamp written
  before this layout: a first run for **every** repository, said once:

  ```
  The checkpoint for <project> predates the new ledger (it is the timestamp
  <value>), so this is a first run for every repository. Approving below
  replaces it with one commit per repository.
  ```

- **A map value that fails validation** (below): a first run, and the value is
  never passed to git: `The checkpoint for <repo> is not a commit SHA, so it
  was not used.` Do not echo a value longer than 40 characters.
- **A valid SHA that does not resolve** in that repository -- a rewritten
  history, a fresh clone, a branch that was never pulled: `The checkpoint for
  <repo> (<sha>) is not in its history any more, so this is a first run
  there.`

**Validate before git sees it.** A SHA comes from a file anyone can edit, so it
is data until proven otherwise:

1. It must match `^[0-9a-fA-F]{7,40}$` -- hexadecimal, 7 to 40 characters,
   nothing else. A space, a semicolon, a quote, a `-` prefix, a `..` range or
   a ref name all fail.
2. Only a value that passed is used, and only as a revision argument after the
   end-of-options marker, never interpolated into a shell string:

   ```
   git -C "<repo>" rev-parse --verify --quiet --end-of-options "<sha>^{commit}"
   ```

   Exit 0 means it resolves; anything else is the unresolvable case above.

## Step 3: compute the delta

Run every command per repository, with the validated SHA placed exactly as in
Step 2. The pathspec is `DECISIONS.md` and, in the home repository,
`.daikenja/open.md`, plus every `DECISIONS.md` a `Moved:` line names.

**With a baseline.** List the commits, then take the net change:

```
git -C "<repo>" log --format="%h %ad %an %s" --date=short --end-of-options "<sha>..HEAD" -- DECISIONS.md .daikenja/open.md
git -C "<repo>" diff --end-of-options "<sha>" HEAD -- DECISIONS.md .daikenja/open.md
```

Read the diff against each file's grammar, per `reading.md` § Step C, and name
every change by what the line says now:

- **`DECISIONS.md`.** An added bullet is a new decision; a removed bullet
  paired with an added one in the same area, saying the same thing differently,
  is an edited decision -- report the new wording; a removed bullet with no
  pair is a decision no longer in force, reported in one line with its old
  rule. An added or renamed area heading, or a changed `Paths:` line, is
  reported as such.
- **`open.md`.** An added item is new; a removed item was closed, per §
  Closing an item; an item whose owner or text changed is reported with its
  current line. Context links and sources are added, removed or retargeted by
  label; a source whose field lines changed names the fields.

A change that does not parse against its section's grammar is reported as a
line, never skipped. The commit list supplies who changed what and when; a
change is reported once, by its net effect, however many commits touched it.

**First run.** There is no baseline, so the delta is the whole current content
of the files, read per `reading.md` § Step C: every decision in force and every
open item, context link and source.

**Not committed yet.** For both cases, ask git for uncommitted changes:

```
git -C "<repo>" status --porcelain -- DECISIONS.md .daikenja/open.md
```

Any line it prints is a file with edits that no commit holds -- `project-log`
writes and never commits. Read those edits with `git -C "<repo>" diff HEAD --
<file>` (an untracked file is new in full) and report them under their own
heading, so nothing in the ledger is invisible. They are not part of what the
checkpoint moves past: the checkpoint is a commit, so they show up again, as
committed changes, once they are committed.

**No changes anywhere.** No commits since any baseline, no uncommitted edits,
and no first run: say so and stop before proposing a checkpoint move.

```
No changes to the ledger since the last checkpoint.
```

## Step 4: report the delta

Group by repository (the last segment of its path), then by file and section.
One line per entry, current state, topic first, per `response-format.md`. The
repository and section headings already say where each entry lives, so the
parentheses carry the change -- and, for a decision, its area. Give the commit range first, and the first-run reason
from Step 2 where one applies:

```
Ledger: C:/GitHub/atlas/DECISIONS.md, C:/GitHub/atlas/.daikenja/open.md

atlas -- 3 changes since 4f9c2e1 (2 commits, latest 2026-08-14 by Priya):

Decisions
- Ramp the Harbor rollout 5% / 25% / 100% over three days (new, Rollout)
- Replicas are sized for peak plus 30%, not peak alone (edited, Infrastructure)

Open items
- Confirm the 30-day replica cost with finance -- @sam (closed)
- Decide who is on call during the cutover window -- @unassigned (new)

Context links
- Runbook -- https://example.com/atlas/runbook (new)

Not committed yet
- open.md: Book the cutover room for Saturday -- @priya (new)
```

Call out unowned new open items -- they are what `project-gaps` would also
flag, and the user is seeing them for the first time.

**A long delta is shown whole.** A bulk write or a first run can hold dozens of
changes. Grouping consecutive entries that took the same change is fine
(`Decisions -- 12 new in the API area, seeded from the architecture wiki`), as
long as every entry is still accounted for. Say how many changes each
repository holds before its list, so a long report is expected rather than
alarming.

## Step 5: propose and write the checkpoint

Propose, per repository, its current commit -- the full SHA from `git -C
"<repo>" rev-parse HEAD`, which passes Step 2's validation by construction:

```
Advance the checkpoint for <project>?
- atlas: 4f9c2e1 -> 7d0e9b2
- atlas-infra: (none) -> 1c44a90
```

On a scalar checkpoint the proposal says it replaces the timestamp with this
map. A repository whose stored SHA already is its current commit is left out.
A repository with no commits yet, or not a git repository, gets no entry and
is named as skipped. Wait for approval. Silence is not approval.

- **Approved.** Edit `~/.claude/daikenja/daikenja.yaml`, the matched project's
  `last_checkpoint` key only, surgically -- not a rewrite. Each repository's
  path is written exactly as it appears in `paths`; entries for repositories
  not proposed are left as they are. If the project is unregistered, there is
  nowhere to write it: say so and name `/daikenja:setup-project` as the way to
  register it, then stop without writing.
- **Declined.** Leave the checkpoint untouched and say so. The next run
  reports the same delta again, which is correct -- nothing was missed.

Never write anything else in `daikenja.yaml`. The single-writer rule governs
the ledger; this carve-out is `last_checkpoint` alone, per
`config-writers.md` § Who writes what.

## Failure cases

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | Treat as a first run against the files under the current directory. Note that no checkpoint can be written until `/daikenja:setup-user` has configured Daikenja and `/daikenja:setup-project` has registered this project. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. |
| The user named a project key that is not in `daikenja.yaml` | **Stop.** Name the key and list the registered ones. Never fall back to the current directory -- an answer about the wrong project reads exactly like a right one. |
| The project has no repository, or still has a `ledger:` key, or its ledger was never migrated | One line each, per `reading.md` § Step A and § Step B. No repository or an unmigrated ledger stops the run; a leftover `ledger:` is ignored. |
| No ledger files in any repository | Report per `reading.md` § Step B and stop. Name `/daikenja:project-log`. |
| A file carries a newer format version | Warn once per run, per `open-format.md` § Version line, and report the delta anyway. |
| A checkpoint fails validation, or does not resolve, or is a scalar timestamp | A first run for that repository (every repository, for a scalar), with the reason stated, per Step 2. The invalid value never reaches git. |
| A registered path is not a git repository, or `git` is not installed | One line naming the path or the missing tool; no history for that repository, and no checkpoint proposed for it. Continue with the others. |
| A registered path does not exist on disk | Skip it silently, per `config-resolution.md` § Reading several repositories. |
| Project unregistered | Show the delta for the current repository (a first run), but say the checkpoint cannot be saved until the project is registered. |
