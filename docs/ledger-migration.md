# Ledger migration

Depends-on (reverse index -- hand-maintained, checked against SKILL.md
headings by tests/check-invariants.py):
- § Which projects need migration -- setup-project "Step 2a: migrate an old ledger", setup-user "Proposing the upgrade"
- § Reading the old ledger -- setup-project "Step 2a: migrate an old ledger"
- § What moves where -- setup-project "Step 2a: migrate an old ledger"
- § A project with no folder -- setup-project "Step 2a: migrate an old ledger"
- § The proposal -- setup-project "Step 2a: migrate an old ledger"
- § Writing, in order -- setup-project "Step 2a: migrate an old ledger"

How a project's old single-file ledger becomes `DECISIONS.md` and
`.daikenja/open.md`, run per project by `/daikenja:setup-project`. Readers
already refuse the old file and point here through `/daikenja:setup-user`; this
page is the one place the old file is read again.

**It is self-contained on purpose.** The old file's grammar is restated below,
only as far as a migration needs it, so this page keeps working after the old
format's own document is gone. The new files are specified by
[`decisions-format.md`](decisions-format.md) and
[`open-format.md`](open-format.md); nothing here restates them.

**Three rules hold throughout.** Nothing is written until the user approves one
proposal for the whole project. The ledger entries are written by
`/daikenja:project-log`, never by `setup-project` itself, per
[`project-log-reference.md`](project-log-reference.md) § A batch handed over by
another skill. Nothing is lost: everything the new files do not carry stays in
the dated backup.

## Which projects need migration

A `projects:` entry in `daikenja.yaml` needs migration when any of these holds:

- it has a `ledger:` key;
- it has `paths: []`, or neither `path` nor `paths` -- a project with no folder;
- its home repository, the first path, holds `.daikenja/ledger.md` -- readers
  flag it only with no `open.md` beside it, but an old ledger next to an
  `open.md` is a migration that stopped part-way, and it resumes the same way;
- its `last_checkpoint` is a single timestamp rather than a map.

**The old ledger is** the file the `ledger:` key names -- a relative value
resolved against the first path, an absolute one as written -- or, with no key,
`<home>/.daikenja/ledger.md`. A key naming a file that does not exist, or an
entry with only a timestamp `last_checkpoint`, has nothing to move: the
migration is then the config edit alone, proposed and approved the same way.

## Reading the old ledger

The old file is Markdown with up to five `##` sections, found by their exact
headings: `Decisions`, `Open items`, `Context links`, `Sources`, `Changelog`.
The `#` title means nothing. HTML comments and blank lines are skipped. A line
indented two or more spaces with no list marker continues the entry above it.

**Decisions and open items share one line shape:**

```
<marker><date> -- <id> -- <owner> -- <body>[<tail>]
```

- **Marker** first, stripped before splitting: `- ` in Decisions, `- [ ] `
  (open) or `- [x] ` (resolved) in Open items.
- **Split on ` -- ` at most three times**: date (`YYYY-MM-DD`), ID, owner
  (`@` plus one token, `@unassigned` for none), body. The body may contain
  ` -- ` itself.
- **IDs** are `D-nnn`, `O-nnn` and `S-nnn`, three digits or more. They mean
  nothing after migration; they are read only to follow the references below.
- **A tail** is what follows the body's **last** ` -> `, and only when it
  matches one of two forms exactly: `-> superseded by D-nnn`, or
  `-> resolved <YYYY-MM-DD>` optionally followed by `, see D-nnn`. Anything else
  after a ` -> ` is body text.
- **Body markers** are sentences that may open a body, in this order:
  `Supersedes D-nnn.`, `Imposed.`, `Blocked by <id>.` and `Contradicts <id>.`
  (any number), `Approximate date.`, then the body proper.

**Which decisions are in force.** A decision is in force unless it carries a
`superseded by` tail. Follow each tail to the end of its chain -- `D-002`
superseded by `D-005`, `D-005` superseded by `D-009` -- and only the decision
at the end is migrated. The tail is authoritative over the newer entry's
`Supersedes D-nnn.` sentence. Each of these is a question in the proposal,
never settled by guessing:

- a `Supersedes D-nnn.` whose target carries no tail -- both read as in force;
- a tail naming a decision that does not exist, or a chain that loops;
- **a malformed tail** -- a ` -> ` followed by "superseded" or "resolved" that
  does not match either form, such as `-> superseded D-005`. By the rule it is
  body text and the entry reads as in force, which is rarely what was meant.

**Any other line that does not fit** its section's shape is listed in the
proposal under "Could not read", with what is wrong. It is not migrated unless
the user restates it.

**Context links** are `- <label> -- <target>`, split once. **Sources** are
`- <S-id> -- <label> -- <target>`, split at most twice, followed by optional
field lines (`modified:`, `read:`, `covers:`, `does not answer:`). The
**Changelog** is not read at all.

## What moves where

| Old | New |
|---|---|
| A decision in force | One entry in `DECISIONS.md`, shaped by `decisions-format.md` § Shape. |
| A superseded decision | Dropped. It stays in the backup. |
| An open item, `- [ ]` | One line in `open.md` § Open items: `- <date> -- <owner> -- <text>`, date and owner kept. |
| A resolved item, `- [x]` | Dropped: closing an item deletes it. It stays in the backup. |
| A context link | Carried over as written, to `open.md` § Context links. |
| A source | Carried over to `open.md` § Sources with its ID removed; the field lines exactly as written. |
| The Changelog | Dropped; git is the history from here. It stays in the backup. |

**A decision entry is rewritten, not copied.** The old body is prose; the new
entry states the rule, a why clause, a revisit condition and a source:

- **The rule** is the decision as it stands now, in the body's own words.
- **The why** comes from the body or its continuation lines. **`Imposed.`**
  becomes part of it -- "imposed by the platform architecture board" -- naming
  who, from the prose after the marker.
- **Revisit** is asked for when the body does not give one. When many entries
  lack it, ask once for all of them, and let the user answer per entry.
- **Source** is a link or reference the body ends with, when there is one.
- **The date, owner and `Approximate date.`** are dropped: decisions carry no
  date or owner. `Supersedes` sentences go with the decisions they name.
- **Area.** `project-log` places each entry by its rules; with no area yet,
  the proposal suggests areas named for what the entries are about, and one
  area with `Paths: \`.\`` when nothing in them says.
- **Repository.** In a project with several repositories, each decision goes
  to the repository whose code it constrains, home for a project-wide one, and
  the proposal asks where the material does not say.

**An open item keeps its text**, with two rewrites:

- **`Blocked by <id>.`** naming an item that migrates becomes
  `Blocked by: <that item, in words>.` -- a short phrase from its text, with no
  period inside it. Naming a resolved item, a decision, or an ID that resolves
  to nothing, the prefix is dropped and the proposal says so.
- **`Contradicts <id>.`** is never carried. Each one is a question: whether the
  conflict is already settled, and, when it is not, how the item should say in
  its own words which decision it questions. Two decisions contradicting each
  other is a question about which one stands; only that one migrates.

`Approximate date.` on an open item stays as ordinary text. An `O-nnn`,
`D-nnn` or `S-nnn` left anywhere in migrated text is pointed out, with the
words that should replace it proposed.

**An existing `DECISIONS.md` is adopted.** Its entries stay exactly as they
are, migrated ones are added to its areas or to new ones, and one it already
holds is not added twice. The same holds for an existing `open.md`, which can
only exist when the old ledger sits at a location the `ledger:` key named.

**The config edit**, in the same approval:

- **`paths`** set, home first: an existing entry keeps its order; a project
  with no folder gains the target from § A project with no folder.
- **The `ledger:` key** removed.
- **A timestamp `last_checkpoint`** removed. A map is left alone. The next
  catchup is a first run.

**The project card** moves to `<home>/.daikenja/project.md` when it is anywhere
else. The old card sat beside the old ledger: `project.md` beside `ledger.md`,
and `<name>.project.md` beside any other `<name>.md`. A card already at the
target is left alone, and a second one found beside the old ledger is a
question, never an overwrite.

**The backup** is the old ledger renamed in the same folder:
`ledger.<YYYY-MM-DD>.bak.md` for `ledger.md`, and `<name>.<YYYY-MM-DD>.bak.md`
for any other `<name>.md`, today's local date. Byte for byte, nothing edited. A
backup by that name already there is reused when it is identical to the old
ledger -- a resumed run -- and otherwise asked about, never overwritten.

## A project with no folder

A project registered with no paths keeps its old ledger in a private folder,
usually `~/.claude/daikenja/ledgers/<key>.md`. It now needs a git repository.

1. **Ask for the target folder.** Suggest a sibling of a root already
   registered for another project, named after the key: with
   `C:/GitHub/harbor` registered, `C:/GitHub/<key>`. With no root registered,
   ask with no suggestion.
2. **Check it before proposing anything:**
   `git -C <target> rev-parse --show-toplevel`, run on the nearest folder that
   exists when the target does not exist yet.
   - **Inside a repository** -- including its root. Name that repository, say
     the ledger would be committed with it, and ask whether that is meant. A no
     goes back to step 1. A yes registers the repository's root, per
     `setup-project` Step 2's rules, including its question when that root
     already belongs to another project.
   - **Outside any repository** -- the default. Propose a new folder there and
     `git init` in it.
3. **The approval line says the content changes place.** It is the first line
   of the proposal for this project:

   ```
   This moves <key>'s ledger out of a private folder
   (~/.claude/daikenja/ledgers/<key>.md) into a git repository at <target>,
   where it will be committed with whatever else lives there.
   ```

## The proposal

One proposal per project, shown by `project-log` as a `project-log via
setup-project` batch, in its usual shape -- the exact lines grouped by file --
with these additions:

- **The approval line** of § A project with no folder, first, when it applies.
- **The files outside the ledger**, after the entries: the config entry before
  and after, the card move, the backup's path, and `git init` when it runs.
- **What was left behind**, as counts: superseded decisions, resolved items and
  Changelog lines dropped, each kept in the backup.
- **"Could not read"** and the questions above, in `project-log`'s "Questions
  before I write" block.

**The batch names its targets by absolute path.** `project-log` does not
resolve this project from the config for it, since the config is part of what
changes; the refusals for an unmigrated ledger and for an entry with no paths
do not apply to this batch, and every other check does.

**It is approved whole, never in tranches.** The user may drop entries or edit
them -- a dropped one is named and stays in the backup -- but nothing is
written until the one yes, so a half-migrated ledger never exists on disk.

## Writing, in order

After the yes, in this order, each step only when the previous one succeeded:

1. `git init` in a new target folder, when one was proposed.
2. **Copy** the old ledger to its backup name.
3. `project-log` writes `DECISIONS.md` and `open.md`.
4. The config edit, with the Edit tool, touching only this entry.
5. The card move.
6. **Remove** the old ledger, now that its backup is identical.

A failure stops the run there and says which steps ran and which did not. The
old ledger is still in place until step 6, so a stopped migration can be run
again. Nothing is committed: the user commits the new files and the rename with
the work they belong to.
