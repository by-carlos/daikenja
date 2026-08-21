# Upgrading

What to do when a Daikenja release changes something that already exists on your
machine -- your `~/.claude/daikenja/daikenja.yaml`, your ledgers, or the commands
you type.

**This is not the changelog.** [`../CHANGELOG.md`](../CHANGELOG.md) records
*what changed*; this file records *what you have to do about it*. Most releases
appear in the changelog and not here, because most releases change nothing you
already have. Two files holding the same fact drift; two files holding different
facts do not.

## How to use it

Run `/daikenja:setup-user`. It reads the `daikenja_version` recorded in your
configuration, finds the sections below that are later than it, proposes the
exact edits, and writes them once you approve. Nothing here is applied to your
files without you seeing it first.

You can also just read down the page. Sections are **newest first**, so applying
several versions in sequence is reading from your recorded version upwards.
Everything here is written to be done by hand if you would rather.

## How this file is kept

- **One file, newest-version-first sections.** Not a folder of per-version
  files: applying three versions is one read and a scroll, and nothing has to
  enumerate or sort filenames to work out what applies.
- **Only versions that require user action get a section.** A release that
  changes nothing on your disk adds nothing here.
- **The note is written by the change, not by the release.** A pull request that
  changes the `daikenja.yaml` schema, the ledger grammar or location, a skill
  name, or any path the plugin reads adds its section under `## [Unreleased]` in
  the same commit, exactly as it adds its changelog entry. The release then only
  promotes that heading to a dated version. See
  [`../CONTRIBUTING.md`](../CONTRIBUTING.md).
- **Every section states the same five things, in this order:** what changed on
  disk, what happens if you do nothing, the exact edit as before-and-after,
  whether `setup-user` can make it for you, and whether it is reversible.
- The bracketed headings mirror `CHANGELOG.md`'s shape so the two can be
  promoted by the same release step and checked against each other. They are not
  links.

## [Unreleased]

### Your ledger can now record blocks, contradictions and imposed decisions

**What changed on disk.** Nothing. The entry grammar is untouched -- same
fields, same separator, same two tails -- and every line in every ledger you
have means exactly what it meant before. What grew is the set of **body
markers**: literal sentences that may open a body, joining the
`Supersedes D-nnn.` and `Approximate date.` markers you already had.

| New marker | Written on | Says |
|---|---|---|
| `Blocked by <id>.` | the entry that cannot move | it is waiting on the named entry |
| `Contradicts <id>.` | the newer of the two entries | both are on record and cannot both stand |
| `Imposed.` | a decision | it was made outside your group and is binding on you |

**What happens if you do nothing.** Nothing breaks and nothing is lost. Your
ledger keeps reading exactly as it does today, and every skill keeps behaving
the same way against it. You only miss the new reporting: `project-decisions`
showing what contradicts or blocks a decision and whether it was imposed, and
`project-gaps` naming what is blocking an item it already reports.

**The exact edit.** Optional, and only where you have already written a
relationship as prose. Move it to the front of the body as a marker, on the
entry that is *constrained* -- never on both entries:

```markdown
<!-- before: prose nothing can read -->
- [ ] 2026-08-19 -- O-008 -- @sam -- Can't start this until the exemption criteria land, see O-004.

<!-- after -->
- [ ] 2026-08-19 -- O-008 -- @sam -- Blocked by O-004. Start the shared ingress migration.
```

For a decision another team handed you and you cannot reopen, add `Imposed.`
and say who imposed it:

```markdown
<!-- before -->
- 2026-08-20 -- D-010 -- @unassigned -- Every service writes to the shared audit log. The architecture board published this.

<!-- after -->
- 2026-08-20 -- D-010 -- @unassigned -- Imposed. Published by the programme's architecture board. Every service writes to the shared audit log.
```

Where an entry needs several markers they run in one fixed order --
`Supersedes D-nnn.`, `Imposed.`, the relationship markers, `Approximate
date.`, then the body. `@unassigned` on an imposed decision is normal and is
still not reported as a gap.

**Can `setup-user` do it for you?** No, and deliberately. Which of your entries
block or contradict each other is a judgement about your own work, and
Daikenja's no-invention rule means nothing may write a relationship you did not
state. Ask `/daikenja:project-log` to add a marker to an entry by ID, or edit
the line by hand -- it is a markdown file.

**Reversible?** Yes, completely. Delete the marker sentence and the entry is
what it was. A ledger with markers is also readable by an older Daikenja, which
treats them as ordinary body text and shows them.

### A project can now span several directories, or none

**What changed on disk.** Nothing, unless you want it to. A `projects:` entry
gains an optional `paths:` key holding a list of directories. The `path:` key
you already have is the single-value form of exactly that, so **no file already
on your disk needs editing and none of them resolve any differently.** This
section exists because the schema grew, not because something you have has
stopped working.

**What happens if you do nothing.** Every project keeps resolving from its one
directory, exactly as before. What you do not get is the two shapes the list
allows: one project spanning several repositories, and a project with no
repository at all.

**The exact edit.** Only if you want one of those two shapes. To make one
project out of several directories, replace its `path:` with a `paths:` list.
**The first path in the list is the project root, and a relative `ledger:`
resolves against it** -- put the repository you already keep the ledger in at
the top, or the ledger you have stops being the one that gets read:

```yaml
# before
projects:
  platform-programme:
    path: C:/GitHub/platform-api

# after
projects:
  platform-programme:
    paths:
      - C:/GitHub/platform-api      # still the root: the ledger stays here
      - C:/GitHub/platform-web
      - C:/GitHub/platform-infra
```

To register work that has no directory -- a programme living in a wiki, a
tracker and a chat space -- give it an empty list. It is then reachable by
name, from anywhere. Pair it with an **absolute** `ledger:`, per the section
below: with no directory there is nothing for a relative one to be relative
to, and the two keys together are what make such a project work.

```yaml
# after
projects:
  q4-planning:
    paths: []
    ledger: C:/Users/you/.claude/daikenja/ledgers/q4-planning.md
```

**Can `setup-user` do it?** No, and it will not offer. Which of your projects
belong together is a judgement about your work, not a migration, and there is
no old shape for it to convert. `/daikenja:setup-project` is what makes these
edits: run it in the second directory of a project and it asks whether that is
a new project or another root of one you already track.
`/daikenja:project-list` shows you what is registered today.

**Reversible?** Yes, completely. A one-element `paths:` list and a `path:`
scalar mean the same thing, so collapsing a list back to a scalar restores the
file you had. The only irreversible act is reordering a `paths:` list, which
moves the project root and therefore repoints a relative `ledger:` at a
different file -- that is why `setup-project` appends and never reorders.

### A project's `ledger:` key now also accepts an absolute path

**What changed on disk.** Nothing in any file you already have. A project's
`ledger:` key in `daikenja.yaml` (under `projects: <key>:`) used to be
understood only as a path relative to that project's own directory. It now also
accepts an absolute path, resolving to that location verbatim -- useful for a
project with no repository of its own, where the recommended convention is
pointing it at `~/.claude/daikenja/ledgers/<project-key>.md`. See
`docs/config-resolution.md` § Resolving `ledger`.

**What happens if you do nothing.** Nothing changes. Every `ledger:` value
you already have is a relative path, which resolves exactly as it always has
-- relative to the project root, with `.daikenja/ledger.md` as the default
when the key is absent. This addition is purely a widening of what
the key accepts, not a change to what any existing value means.

**The exact edit.** Optional, and only if you want a project's ledger to live
outside its own directory:

```yaml
# before
projects:
  vendor-onboarding-programme:
    path: C:/Users/you/daikenja-projects/vendor-onboarding-programme

# after
projects:
  vendor-onboarding-programme:
    path: C:/Users/you/daikenja-projects/vendor-onboarding-programme
    ledger: C:/Users/you/.claude/daikenja/ledgers/vendor-onboarding-programme.md
```

**Can `setup-user` do it?** No. `ledger:` is a per-project key, owned by
`/daikenja:setup-project`, which offers it when registering or re-running
against a project. `setup-user` never touches `projects:` entries.

**Reversible?** Yes, for the pointer. Delete the key, or point it back at a
relative path, and Daikenja looks in the default location again -- this only
changes where it looks, never the ledger's own format. It does not move the
file for you: if you already have content at the absolute location, moving it
back under the project (or updating the key to point at wherever you leave it)
is yours to do by hand.
### Ledger entries may carry an approximate date, and a Changelog line may be compacted

**What changed on disk.** Nothing, until you write one. Two things a ledger may
now contain were not valid before:

- An entry whose date is only approximately known opens its body with the
  literal `Approximate date.`, followed by where the approximation came from.
- A Changelog summary may compact a run of consecutive IDs taking the same verb
  into a dense range (`+D-004..D-007`), and may continue onto lines indented two
  spaces when it is too long to read on one.

Both are additive. **No ledger already on your disk becomes invalid**, no
existing line changes meaning, and nothing is rewritten.

**What happens if you do nothing.** Nothing at all. Your existing ledgers are
already valid and every skill reads them exactly as before. You will only meet
either form when you record a project that already has history -- normally
through `/daikenja:setup-project` -- and even then `project-log` shows you the
exact lines before writing them.

**The exact edit.** There is none to make. For reference, this is what the new
forms look like:

```markdown
- 2026-04-01 -- D-006 -- @souei -- Approximate date. The wiki page recording this carries no date; it was created in April 2026. Cap query fan-out at 32 shards.
```

```
- 2026-08-21T10:15Z -- project-log via setup-project -- +D-004..D-007, +O-003..O-005,
  +link "Architecture wiki"
```

**Can `setup-user` make it for you.** There is nothing for it to make. This
section exists so that a ledger written by 0.6.0 or later, opened on an older
install, has a name.

**Is it reversible.** Yes, and by hand. Expanding a range back into
comma-separated IDs, joining a continued summary onto one line, or deleting the
`Approximate date.` marker all leave a ledger every version reads. Only the
readability is lost.

**One consequence worth knowing before you seed a project.** Entries dated to
when they were actually decided are older than `stale_after_days` the moment
they land, so `/daikenja:project-gaps` reports the open ones as stale on its
very next run. That is the audit working, not a fault in the entries.

### Your configuration now records which version wrote it

**What changed on disk.** `daikenja.yaml` gains one top-level key,
`daikenja_version`, holding the version of Daikenja that last wrote the file.
Nothing else about the file changes, and no existing key moves or changes
meaning. A file written before this release simply does not have the key, which
is a legal state meaning "written before this key existed".

**What happens if you do nothing.** Every Daikenja skill that reads
`daikenja.yaml` adds one line to its output, every run:

```
daikenja.yaml predates version tracking; <installed version> is installed -- run /daikenja:setup-user.
```

Nothing stops working and nothing is blocked -- it is one extra line. It does
not go away on its own, and it is there so that the next release which *does*
change something on your disk has a way to reach you.

**The exact edit.** One key at the top of the file:

```yaml
# before
profile:
  name: Carlos
```

```yaml
# after
daikenja_version: <the version you have installed>

profile:
  name: Carlos
```

**Can `setup-user` do it?** Yes, and this is the whole of the upgrade. Run
`/daikenja:setup-user` once; it stamps the key and the notice stops.

**Reversible?** Yes. Delete the line. The key is optional and its absence is a
supported state -- you get the notice back, nothing else.

## [0.3.0] - 2026-08-17

### Five project skills were renamed

**What changed on disk.** Nothing, in any file you own. This is a rename of
commands, not of data. Five skills gained a `project-` prefix:

| Before | After |
|---|---|
| `/daikenja:log` | `/daikenja:project-log` |
| `/daikenja:summary` | `/daikenja:project-summary` |
| `/daikenja:catchup` | `/daikenja:project-catchup` |
| `/daikenja:decisions` | `/daikenja:project-decisions` |
| `/daikenja:gaps` | `/daikenja:project-gaps` |

Ledger Changelog lines written before 0.3.0 name their writer `log` rather than
`project-log`. Those lines are correct as they stand and are read correctly:
[`ledger-format.md`](ledger-format.md) § Section: Changelog documents `log` as a
recognised writer name for exactly this reason.

**What happens if you do nothing.** The five old command names stop resolving --
Claude Code reports the command as not found. Your ledgers are unaffected: every
read skill accepts the old writer name, so no entry becomes unreadable and no
delta report loses anything.

**The exact edit.** Only in what you type, and in anything of your own that
names one of these commands -- notes, a project README, a saved prompt:

```
# before
/daikenja:catchup

# after
/daikenja:project-catchup
```

**Can `setup-user` do it?** No. There is nothing on disk to edit, so there is
nothing for it to propose. It reports the version gap and stamps
`daikenja_version`; the command names are yours to update where you use them.

**Reversible?** There is nothing to reverse -- no file changed. The old command
names are gone for good, so a ledger's old `log` lines are the only trace, and
they are supported indefinitely rather than migrated.
