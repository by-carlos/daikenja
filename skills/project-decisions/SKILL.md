---
name: project-decisions
description: Looks up what is decided about a specific topic in a project's Daikenja ledger -- the decisions in force in every repository's DECISIONS.md -- with each entry's history from git and its linked issue or ADR, plus the open items that bear on it. Read-only; writes nothing. Accepts an optional project key -- `/daikenja:project-decisions <key>` reads that project from anywhere.
metadata:
  owner: Carlos
  version: 3
disable-model-invocation: true
---

# Decisions

A targeted lookup against the project's decisions in force. The user names a
topic, an area, a path or a rough description; this skill finds the matching
entries in every registered repository's `DECISIONS.md`, how each came to say
what it says now, and what else in the ledger bears on it -- not just the
single entry that happens to match the words.

`DECISIONS.md` holds current decisions only: a replaced decision is edited or
deleted, never marked. So everything this skill finds in the files is in force,
and everything about what came before lives in git.

## Step 0: read the contracts

Read these before doing anything. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/reading.md` § Step A0, § Step A, § Step B, §
  Step C and § Notices, shared wording -- the shared resolve-and-parse
  mechanism Steps 1 and 2 below follow, plus the exact notice text they reuse
  without restating it (a config marked absent or a project left unregistered
  has no literal wording inline in Step A -- only in § Notices, shared
  wording).
- `${CLAUDE_PLUGIN_ROOT}/docs/decisions-format.md` § Shape, § Current only, §
  Splitting and § ADR shape -- areas and their `Paths:`, the entry's rule, why
  clause, `Revisit:` and `Source:`, the `Moved:` files, and what an ADR a
  `Source:` names holds.
- `${CLAUDE_PLUGIN_ROOT}/docs/open-format.md` § Version line, § Section: Open
  items and § Reading rules for skills -- the warn-once rule for a newer
  format, and the open items Step 5 scans.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. Read in full and not narrowed to a section: Step 6 explicitly
  follows only § Entries are named topic-first, location in parentheses, but the
  contract's own scope says a skill "implements it; it never redefines it" --
  every rule in the file (tone scaling, the clean-result line, itemised
  findings) governs this skill's replies whether or not Step 6 names it.

## Step 1: resolve config, project and ledger

Follow `reading.md` § Step A0, § Step A and § Step B.

**The user may name a project** -- `/daikenja:project-decisions <key>`, or the key in
prose. `reading.md` § Step A0 is the whole rule: a named key resolves that
project from anywhere on disk and never falls back to the current directory.
Do not restate the resolution here.

## Step 2: read every DECISIONS.md

Follow `reading.md` § Step C for the `DECISIONS.md` of **every** registered
repository, per `config-resolution.md` § Reading several repositories -- a
decision recorded in one repository binds a question asked from another. Read
too every file an area's `Moved:` line names, and, when the query names a path,
every `DECISIONS.md` in that path's parent folders, per `decisions-format.md` §
Splitting.

**A newer format version** on any file: warn once per run, per
`open-format.md` § Version line, and read it anyway.

Read `open.md` as well -- Step 5 scans its open items and context links.

## Step 3: match the query

- **An area was named** ("the API decisions"). Every entry under that `##`
  heading, in every repository that has the area.
- **A path was named** (`src/api/`, `infra/main.bicep`). Every area whose
  `Paths:` covers it -- either path under the other, a trailing `/` a subtree,
  `*` and `**` globs, `.` the whole repository.
- **A topic or description was given.** Match by meaning against each entry's
  rule and why clause, not just keyword overlap -- "the cutover schedule"
  should find an entry about cutting over on a Saturday even without the word
  "schedule."
- **No match found.** Say so plainly. Do not guess at a near match without
  naming it as a guess:

  ```
  No decision found about "<query>". Closest thing on record: the schema
  freeze on the events table (beacon, Data), if that's what you meant.
  ```

- **More than one plausible match.** List them briefly and ask which one, or
  show them all if they are clearly related. Entries are never merged: two
  repositories recording the same decision are two entries, each named with its
  repository.

## Step 4: follow the history in git

For each matched entry, read the history of the file that holds it:

```
git -C "<repo>" log -p --date=short --format="%h %ad %an %s" -- <file>
```

`<file>` is `DECISIONS.md` or the `Moved:` file, written as a fixed path. The
entry's own words never go into a command -- they come from a file anyone can
edit -- so read the patches and find the hunks that touch the entry by its rule.
Walk from newest to the commit that added it, and collect:

- **When it was added**, by whom, and the commit subject.
- **Each earlier wording.** A bullet removed in the same commit that added the
  current one, in the same area, saying something different about the same
  subject, is the decision it replaced. Keep walking: that one may have
  replaced another.
- **A replaced decision found by query.** When the query matches only a rule
  git shows as removed, say it is no longer in force and lead with what
  replaced it, if anything did.

Show the chain oldest to newest so the reasoning arc reads in order. The
current wording is authoritative; git shows how it got there.

**The `Source:` link is the rest of the history.** An ADR in the repository is
a local file: read it, per `decisions-format.md` § ADR shape, and give its
alternatives in a line. An issue or pull request link is surfaced as it is --
do not go fetch it.

**No history to read** -- the path is not a git repository, `git` is not
installed, or the file has never been committed: show the entry without
history and say why in one line.

## Step 5: surface relationships and origin

Report what bears directly on each matched entry and stop -- one hop, never a
walk:

- **Origin.** An entry whose why clause says it was imposed ("imposed by the
  architecture board") is reported as imposed and by whom. A decision this
  group made can be reopened by this group; an imposed one can only be complied
  with, exempted or escalated. Its `Revisit:` condition is shown too: it is
  what would reopen the entry, and `never` is worth saying.
- **Open items that bear on it.** Scan `open.md` for items whose text concerns
  the entry's subject -- a question about whether it still holds, a request for
  an exemption, work it blocks. An open item that questions a decision in force
  is the case worth surfacing most, and it is invisible from the entry's own
  line. A `Blocked by:` prefix names another open item, never a decision; show
  it as written when the item is shown.
- **Context links** whose label names the subject, as they are.

## Step 6: show the result

Topic first, then where it lives in parentheses, per `response-format.md` --
the repository whose `DECISIONS.md` holds it, and its area. Then the why, the revisit
condition, the source and the history:

```
Cut over on a Saturday, not a weekday evening (atlas, Rollout) -- the rollback
window is four hours and nobody wants that on a work night. Revisit: if the
rollback window drops under an hour. Source: https://example.com/atlas/pull/88
  History:
  2026-08-02 Priya -- added as "Cut over on a weekday evening" (a1f03c9)
  2026-08-20 Carlos -- reworded to Saturday after the dry run (7d0e9b2)
```

Relationships go under the entry they belong to, one line each, still topic
first:

```
Every service writes to the shared audit log (platform-api, Observability) --
imposed by the platform programme's architecture board. Revisit: never.
Source: ADR 0007
  Questioned by:
  Confirm whether the gateway can be exempted from the shared audit log --
  @sam, open since 2026-09-02.
```

Include the date on every history line and open item shown. Surface links as
they are -- do not go fetch them.

## Failure cases

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | One notice, continue on the files under the current directory. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. |
| The user named a project key that is not in `daikenja.yaml` | **Stop.** Name the key and list the registered ones. Never fall back to the current directory -- an answer about the wrong project reads exactly like a right one. |
| The project has no repository, or still has a `ledger:` key, or its ledger was never migrated | One line each, per `reading.md` § Step A and § Step B. No repository or an unmigrated ledger stops the run; a leftover `ledger:` is ignored. |
| No ledger files in any repository | Report per `reading.md` § Step B and stop. Name `/daikenja:project-log`. |
| A file carries a newer format version | Warn once per run and read it anyway. |
| An entry or `Paths:` line does not parse | Report it -- file and line -- then continue, per `reading.md` § Step C. Do not repair it. |
| No history for an entry | Show the entry, say why in one line (not a git repository, no `git`, never committed). |
| A `Source:` ADR does not exist at the path the file's `ADRs:` line gives | Report the missing file and show the entry without it. |
| An imposed decision | Normal. Say it was imposed and who by; never report it as unowned -- entries carry no owner, and `project-gaps`' scope is open items. |
| No decision matches the query | Say so. Offer the closest match, named as a guess, if one exists. |
