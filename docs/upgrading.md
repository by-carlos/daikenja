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
**The first path in the list is the project root, and the ledger lives there** --
put the repository you already keep the ledger in at the top, or the ledger you
have stops being the one that gets read:

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
name, from anywhere, and it has nowhere to keep a ledger yet:

```yaml
# after
projects:
  q4-planning:
    paths: []
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
moves the project root and therefore repoints the ledger at a different file --
that is why `setup-project` appends and never reorders.

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
