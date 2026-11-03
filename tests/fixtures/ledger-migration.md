# Ledger migration -- old ledgers and the configs that point at them

<!--
Fixture: synthetic old single-file ledgers, the daikenja.yaml entries that
point at them, and what `setup-project` Step 2a must leave on disk after
following docs/ledger-migration.md for each. Everything here is invented --
invented projects, invented people, `example.com` links.

There is no test runner. Walk the migration by hand against each input, in a
scratch folder, and compare the files it leaves against the expected result.
Today's date in every walk is 2026-11-03. Paths are written Windows-style as
the user would see them; a walk on another OS maps them one to one.

The walks also answer `project-log`'s questions; the answers are given with
each walk so the expected files are exact.
-->

Depends on: setup-project "Step 2a: migrate an old ledger", ledger-migration.md "Which projects need migration", ledger-migration.md "Reading the old ledger", ledger-migration.md "What moves where", ledger-migration.md "A project with no folder", ledger-migration.md "The proposal", ledger-migration.md "Writing, in order"

## Input A -- atlas, an old ledger at the default location

`daikenja.yaml`:

```yaml
projects:
  atlas:
    path: C:/GitHub/atlas
    last_checkpoint: 2026-08-20T09:12Z
```

`C:/GitHub/atlas` is a git repository. It holds `.daikenja/project.md` (the
card, already at its new place) and `.daikenja/ledger.md`, and no `open.md`:

```markdown
# Atlas migration ledger

## Decisions

- 2026-08-20 -- D-007 -- @rimuru -- Supersedes D-005. Cut over on a Sunday morning, not a Saturday -- the data team's Saturday batch overlaps the window. [runbook](https://example.com/atlas/runbook)
- 2026-08-14 -- D-006 -- @unassigned -- Imposed. Published by the platform programme's architecture board. Every service writes to the shared audit log.
- 2026-08-14 -- D-005 -- @rimuru -- Supersedes D-002. Cut over on a Saturday, not a weekday evening. -> superseded by D-007
- 2026-08-12 -- D-004 -- @unassigned -- Keep the legacy read replica online for 30 days after cutover. -> superseded D-008
- 2026-08-11 -- D-003 -- @shion -- Freeze schema changes from 2026-08-20 until cutover completes.
  Two teams have pending migrations. Both agreed to hold.
- 2026-08-08 -- D-002 -- @rimuru -- Cut over on a weekday evening. [thread](https://example.com/t/4417) -> superseded by D-005
- 2026-08-05 -- D-001 -- @shion -- Atlas replaces the legacy store. No dual-write period.

## Open items

- [ ] 2026-08-19 -- O-006 -- @benimaru -- Blocked by O-005. Contradicts D-006. Confirm whether the gateway can be exempted from the shared audit log.
- [ ] 2026-08-18 -- @gobta -- Book the cutover war room.
- [ ] 2026-08-16 -- O-005 -- @unassigned -- Find out who signs off audit-log exemptions.
- [ ] 2026-08-13 -- O-004 -- @gobta -- Blocked by O-002. Confirm the 30-day replica cost with finance. [budget sheet](https://example.com/atlas/budget)
- [ ] 2026-08-11 -- O-003 -- @shion -- Write the rollback runbook and dry-run it once.
  The dry run needs a full-size dataset.
- [x] 2026-08-09 -- O-002 -- @rimuru -- Get the legacy store's row counts from ops. -> resolved 2026-08-10
- [x] 2026-08-07 -- O-001 -- @rimuru -- Pick the cutover day. -> resolved 2026-08-14, see D-005

## Context links

- Runbook -- https://example.com/atlas/runbook
- Legacy store schema -- ./docs/legacy-schema.md

## Sources

- S-001 -- Platform standards page -- https://example.com/wiki/standards
  modified: 2026-08-10T09:12Z
  read: 2026-08-11
  covers: the mandatory controls and which services they bind.

## Changelog

- 2026-08-20T09:10Z -- project-log -- +D-007, superseded D-005
- 2026-08-19T10:02Z -- project-log -- +O-006
- 2026-08-14T16:40Z -- project-log -- +D-005, +D-006, superseded D-002, resolved O-001
- 2026-08-05T14:00Z -- project-log -- +D-001, +O-001
```

**Expected reading.**

- **Needs migration** on two counts: `.daikenja/ledger.md` with no `open.md`,
  and a timestamp `last_checkpoint`.
- **In force:** D-007, D-006, D-003, D-001, and D-004 pending a question.
  The chain D-002 -> D-005 -> D-007 ends at D-007, so **D-002 and D-005 are
  dropped**. D-004's `-> superseded D-008` is a **malformed tail**: it is body
  text by the rule, so D-004 reads as in force, and the proposal asks.
- **Could not read:** the `Book the cutover war room` line -- three fields, no
  ID.
- **Open items:** O-006, O-005, O-004, O-003 move; O-002 and O-001 are
  resolved and dropped. O-006's `Blocked by O-005.` becomes a `Blocked by:`
  prefix naming O-005 in words. O-004's `Blocked by O-002.` names a resolved
  item: the prefix is dropped and the proposal says so. O-006's
  `Contradicts D-006.` is a question.
- **Questions in the proposal:** D-004's tail; a revisit condition for all five
  decisions (asked once); a why for D-001 and D-004; O-006 against D-006; the
  unreadable line.
- **Approval line, files outside the ledger:** the config entry before and
  after; the card stays where it is; backup
  `C:/GitHub/atlas/.daikenja/ledger.2026-11-03.bak.md`; dropped: 2 superseded
  decisions, 2 resolved items, 4 Changelog lines, all kept in the backup.

**Answers given in the walk.** D-004 is still in force -- the tail was typed
by mistake. Revisit: "if the cutover date moves" for D-007 and D-003, "never"
for D-001 and D-006, "if finance rejects the replica cost" for D-004. Why for
D-001: "running two stores doubles the reconciliation work"; for D-004:
"rollback reads from the replica". O-006 is not settled: keep it, saying which
decision it questions. The war-room line is restated as written, with its date
and owner. All approved whole.

**Expected `C:/GitHub/atlas/DECISIONS.md`** -- scaffolded from the template,
whose comment block is kept and elided here:

```markdown
<!-- decisions-format: 1 -->
# Decisions

Decisions in force. Read the area that covers a path before changing it; add
or edit an entry in the same pull request when a change settles something
future work must respect.

<!-- ...template comment, unchanged... -->

## Migration

Paths: `.`

- **Cut over on a Sunday morning, not a Saturday.** — the data team's
  Saturday batch overlaps the window. Revisit: if the cutover date moves.
  Source: https://example.com/atlas/runbook
- **Every service writes to the shared audit log.** — imposed by the platform
  programme's architecture board. Revisit: never.
- **Keep the legacy read replica online for 30 days after cutover.** —
  rollback reads from the replica. Revisit: if finance rejects the replica
  cost.
- **Freeze schema changes from 2026-08-20 until cutover completes.** — two
  teams have pending migrations and both agreed to hold. Revisit: if the
  cutover date moves.
- **Atlas replaces the legacy store, with no dual-write period.** — running
  two stores doubles the reconciliation work. Revisit: never.
```

**Expected `C:/GitHub/atlas/.daikenja/open.md`** -- from the template, comment
elided:

```markdown
<!-- daikenja-open-format: 1 -->
# atlas open items

<!-- ...template comment, unchanged... -->

## Open items

- 2026-08-19 -- @benimaru -- Blocked by: who signs off audit-log exemptions. Confirm whether the gateway can be exempted from the shared audit log, which DECISIONS.md makes binding.
- 2026-08-18 -- @gobta -- Book the cutover war room.
- 2026-08-16 -- @unassigned -- Find out who signs off audit-log exemptions.
- 2026-08-13 -- @gobta -- Confirm the 30-day replica cost with finance. [budget sheet](https://example.com/atlas/budget)
- 2026-08-11 -- @shion -- Write the rollback runbook and dry-run it once.
  The dry run needs a full-size dataset.

## Context links

- Runbook -- https://example.com/atlas/runbook
- Legacy store schema -- ./docs/legacy-schema.md

## Sources

- Platform standards page -- https://example.com/wiki/standards
  modified: 2026-08-10T09:12Z
  read: 2026-08-11
  covers: the mandatory controls and which services they bind.
```

**Expected config entry:**

```yaml
  atlas:
    path: C:/GitHub/atlas
```

**Expected on disk besides:** `.daikenja/ledger.2026-11-03.bak.md`, identical
to the old ledger; no `.daikenja/ledger.md`; `.daikenja/project.md` untouched.
`Cut over on a weekday evening` is in the backup and not in `DECISIONS.md`.

**The failures this catches:** a superseded decision migrated as if in force;
a malformed tail settled by guessing; a `Contradicts` carried as a marker; a
`Blocked by:` left naming an item that no longer exists; the unreadable line
dropped silently; the old ledger removed before the new files exist.

## Input B -- q4-planning, a project with no folder

`daikenja.yaml`:

```yaml
projects:
  harbor:
    path: C:/GitHub/harbor
  q4-planning:
    paths: []
    ledger: ~/.claude/daikenja/ledgers/q4-planning.md
    last_checkpoint: 2026-09-10T08:00Z
```

`~/.claude/daikenja/ledgers/q4-planning.md`:

```markdown
# Q4 planning ledger

## Decisions

- 2026-09-02 -- D-002 -- @rimuru -- Supersedes D-001. Planning closes on 2026-10-15, not at the end of October -- finance locks budgets on the 20th.
- 2026-08-25 -- D-001 -- @rimuru -- Planning closes at the end of October. -> superseded by D-002

## Open items

- [ ] 2026-09-05 -- O-002 -- @benimaru -- Collect the platform team's headcount ask.
- [x] 2026-08-26 -- O-001 -- @shion -- Agree the planning template. -> resolved 2026-09-01

## Context links

- Planning space -- https://example.com/wiki/q4-planning

## Changelog

- 2026-09-05T08:30Z -- project-log -- +O-002
- 2026-09-02T11:00Z -- project-log -- +D-002, superseded D-001, resolved O-001
- 2026-08-25T09:00Z -- project-log -- +D-001, +O-001
```

and its card beside it, `~/.claude/daikenja/ledgers/q4-planning.project.md`
(the old `<name>.project.md` rule).

Run as `/daikenja:setup-project q4-planning`: no directory could match it.

### Walk B1 -- the default: a new folder outside any repository

1. Suggested target: `C:/GitHub/q4-planning`, a sibling of the registered
   `C:/GitHub/harbor`, named after the key.
2. It does not exist; `git -C C:/GitHub rev-parse --show-toplevel` fails, so it
   is outside any repository. The proposal offers a new folder and `git init`.
3. The proposal opens with:

   ```
   This moves q4-planning's ledger out of a private folder
   (~/.claude/daikenja/ledgers/q4-planning.md) into a git repository at
   C:/GitHub/q4-planning, where it will be committed with whatever else lives
   there.
   ```

**Answers given in the walk.** Revisit for D-002: "if finance moves its lock
date". Approved whole.

**Expected `C:/GitHub/q4-planning/DECISIONS.md`**, template comment elided:

```markdown
<!-- decisions-format: 1 -->
# Decisions

Decisions in force. Read the area that covers a path before changing it; add
or edit an entry in the same pull request when a change settles something
future work must respect.

<!-- ...template comment, unchanged... -->

## Planning

Paths: `.`

- **Planning closes on 2026-10-15, not at the end of October.** — finance
  locks budgets on the 20th. Revisit: if finance moves its lock date.
```

**Expected `C:/GitHub/q4-planning/.daikenja/open.md`**, template comment
elided:

```markdown
<!-- daikenja-open-format: 1 -->
# q4-planning open items

<!-- ...template comment, unchanged... -->

## Open items

- 2026-09-05 -- @benimaru -- Collect the platform team's headcount ask.

## Context links

- Planning space -- https://example.com/wiki/q4-planning

## Sources
```

**Expected config entry** -- the pathless config entry this fixture is for:

```yaml
  q4-planning:
    paths:
      - C:/GitHub/q4-planning
```

**Expected on disk besides:** `C:/GitHub/q4-planning/.git`; the card at
`C:/GitHub/q4-planning/.daikenja/project.md`, moved from the ledgers folder;
the backup `~/.claude/daikenja/ledgers/q4-planning.2026-11-03.bak.md`,
identical to the old ledger, which is gone. The backup is named after the old
file, not `ledger.<date>.bak.md`, so two projects in one ledgers folder never
collide.

### Walk B2 -- the suggested target is inside a repository

Same input, except that `harbor`'s registered path is
`C:/Work/notes/harbor-notes`, a sub-folder registered on request, and
`C:/Work/notes` is a git repository.

1. Suggested target: `C:/Work/notes/q4-planning`.
2. It does not exist; `git -C C:/Work/notes rev-parse --show-toplevel` prints
   `C:/Work/notes`. **Nothing is proposed yet.** The run names the repository
   and asks:

   ```
   C:/Work/notes/q4-planning would be inside the git repository C:/Work/notes,
   so the ledger would be committed with everything else there. Use it, or
   pick another folder?
   ```

3. Answered "pick another": back to step 1, no suggestion forced. Answered
   "use it": `C:/Work/notes` is the repository registered, and the proposal
   still opens with the private-folder line, naming `C:/Work/notes`.

**The failures this catches:** a ledger written into another repository's
working tree without asking; the private-to-repository move not stated; a
`rev-parse` run on a folder that does not exist and its failure read as
"outside any repository" when the nearest existing parent is inside one.

## Input C -- quill, a ledger and card at a non-default location

```yaml
projects:
  quill:
    path: C:/GitHub/quill
    ledger: docs/records/quill-ledger.md
```

`C:/GitHub/quill` is a git repository holding
`docs/records/quill-ledger.md` and its card `docs/records/quill-ledger.project.md`,
and nothing under `.daikenja/`:

```markdown
# Quill ledger

## Decisions

- 2026-07-30 -- D-001 -- @shion -- Every font file ships subset to Latin-1. Full sets tripled the bundle. [issue](https://example.com/quill/issues/31)

## Open items

- [ ] 2026-08-02 -- O-001 -- @unassigned -- Decide whether to ship a CJK fallback.

## Context links

## Changelog

- 2026-08-02T10:00Z -- project-log -- +O-001
- 2026-07-30T15:20Z -- project-log -- +D-001
```

Readers do not flag this one -- the legacy location is empty -- but they
ignore its `ledger:` key with a notice, and the old file goes unread. It needs
migration because of the key.

**Answers given in the walk.** Revisit for D-001: "if a CJK market is added".
Approved whole.

**Expected:** `C:/GitHub/quill/DECISIONS.md` with one entry,
`**Every font file ships subset to Latin-1.** — full sets tripled the bundle.
Revisit: if a CJK market is added. Source: https://example.com/quill/issues/31`,
under one area; `C:/GitHub/quill/.daikenja/open.md` with
`- 2026-08-02 -- @unassigned -- Decide whether to ship a CJK fallback.` and an
empty Context links section; the card moved to
`C:/GitHub/quill/.daikenja/project.md`; the backup
`C:/GitHub/quill/docs/records/quill-ledger.2026-11-03.bak.md` beside where the
old ledger was, and `docs/records/quill-ledger.md` and its old card gone. The
entry loses its `ledger:` key:

```yaml
  quill:
    path: C:/GitHub/quill
```

**The failure this catches:** dropping the `ledger:` key without moving what
it pointed at, which strands the old ledger where nothing will ever read it.

## Input D -- lantern, a repository that already has a `DECISIONS.md`

```yaml
projects:
  lantern:
    path: C:/GitHub/lantern
```

`C:/GitHub/lantern/DECISIONS.md`, written by plan-staged-rollout:

```markdown
<!-- decisions-format: 1 -->
# Decisions

Decisions in force. Read the area that covers a path before changing it; add
or edit an entry in the same pull request when a change settles something
future work must respect.

## Release

Paths: `.github/workflows/`, `CHANGELOG.md`

- **Releases are cut from tags only, never from a branch.** — a branch build
  shipped an unreviewed commit once. Revisit: never. Source: #12
```

and `C:/GitHub/lantern/.daikenja/ledger.md`, with no `open.md`:

```markdown
# Lantern ledger

## Decisions

- 2026-08-10 -- D-002 -- @gobta -- Every endpoint is versioned in the path, never by header. Clients cache by URL.
- 2026-08-01 -- D-001 -- @gobta -- Releases are cut from tags only.

## Open items

## Context links

## Changelog

- 2026-08-10T09:00Z -- project-log -- +D-002
- 2026-08-01T09:00Z -- project-log -- +D-001
```

**Answers given in the walk.** Revisit for D-002: "if a gateway takes over
versioning". The new area's paths: `src/api/`. Approved whole.

**Expected `C:/GitHub/lantern/DECISIONS.md`** -- adopted, not replaced: the
title, intro, `## Release` and its entry are byte-identical to before, D-001 is
a duplicate of the Release entry and is not added, and one area is appended:

```markdown
## API

Paths: `src/api/`

- **Every endpoint is versioned in the path, never by header.** — clients
  cache by URL. Revisit: if a gateway takes over versioning.
```

No `.daikenja/open.md` is created: nothing moves into it, and `project-log`
scaffolds a file only for a batch that writes to it. The backup is
`.daikenja/ledger.2026-11-03.bak.md`, the old ledger is gone, and the config
entry is unchanged.

**The failure this catches:** replacing an existing `DECISIONS.md` with the
template, or adding the same rule twice in two wordings.
