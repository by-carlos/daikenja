---
name: tensei
description: 'Installs, updates, or removes the Tensei conversational persona (~/.claude/daikenja/tensei.md) and its CLAUDE.md import line, diffing an existing copy and backing up anything it would overwrite.'
metadata:
  owner: Carlos
  version: 1
  writes: ~/.claude/daikenja/tensei.md, an import line appended to ~/.claude/CLAUDE.md, ~/.claude/daikenja/.tensei-manifest.json, backups under ~/.claude/backups/tensei-<UTC timestamp>/
disable-model-invocation: true
---

# Tensei

Install or reconcile the Tensei persona -- the answer-shaping, markers and
register document at `~/.claude/daikenja/tensei.md`, imported by a
`@~/.claude/daikenja/tensei.md` line at the end of `~/.claude/CLAUDE.md` -- on
the machine this session is running on.

**Slash-only, on purpose.** This skill writes a file outside the project, in
the user's home directory, and can append a line to the `CLAUDE.md` that
governs every session on the machine. Nothing about "set up my persona" or
"install tensei" should make it fire by itself -- the user runs
`/daikenja:tensei` when they mean to. `disable-model-invocation: true` is what
enforces that.

**Not part of `daikenja.yaml`, and no dependency on `setup-user`.** Tensei
governs conversation, not deliverables -- it is a different contract from
`voice.md` and unrelated to the `profile:` block, `personas.md`, or
`writing_style`. A user can run this skill with no Daikenja configuration on
disk at all, so it carries its own environment gate (Step 0) rather than
assuming `setup-user` already ran.

**Not a blank template, unlike `personas.md` and `writing-style.md`.** Those
two are copied once, on absence, and never inspected again -- the user owns
everything written into them from that point on. `templates/tensei.md` is
maintained content this plugin ships and revises; an installed copy the user
has not hand-edited can be updated to a newer shipped version. Step 2's
five-state model is what makes that safe: it never overwrites a copy the user
changed without saying so first.

## Step 0: the environment gate

Try to list `~/.claude/` (the real OS home directory, not the project working
tree) and confirm it looks like a live Claude Code install -- at least one of
`~/.claude/settings.json`, `~/.claude/CLAUDE.md` or `~/.claude/plugins/`
exists there.

- **It resolves and at least one marker exists.** Proceed.
- **It does not resolve, is empty, or none of the markers exist.** Stop and
  say:

  ```
  This session has no persistent home directory with a Claude Code install in
  it, which this skill needs to read and write ~/.claude/daikenja/. Nothing
  was written.
  ```

## Step 1: read what already exists

Before asking anything:

- `~/.claude/daikenja/tensei.md` -- read it if present.
- `~/.claude/daikenja/.tensei-manifest.json` -- read it if present. Malformed
  JSON: **stop**, name the file, say the user should fix or remove it. Never
  rewrite a file that could not be read.
- `~/.claude/CLAUDE.md` -- read it if present, and check whether a line
  reading exactly `@~/.claude/daikenja/tensei.md` already exists (compare
  after stripping the line ending and surrounding whitespace, and anywhere in
  the file, not only at the end -- another installer may have placed it inside
  a slot of its own).

## Step 2: state and report

Hash the shipped payload
(`${CLAUDE_PLUGIN_ROOT}/templates/tensei.md`) and, if present, the installed
file, with a short inline command rather than eyeballing a diff --
`python -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" <path>`
works on every platform this plugin supports.

| Installed | Manifest `installed_hash` | Compare | State |
|---|---|---|---|
| absent | -- | -- | `new` |
| present | absent | installed == shipped | `unchanged` (untracked -- see the adoption note below) |
| present | absent | installed != shipped | `conflict` (no record to tell a local edit from an independently-placed file) |
| present | present | installed == shipped | `unchanged` |
| present | present | installed == manifest hash, shipped != manifest hash | `update` |
| present | present | installed != manifest hash, shipped == manifest hash | `local-edit` |
| present | present | installed != manifest hash, shipped != manifest hash | `conflict` |

One report before asking anything:

| State | Say |
|---|---|
| `new` | Not installed here -- propose installing it. |
| `unchanged` | Nothing to do for the file. |
| `update` | Installed copy is untouched since last install and the payload moved -- propose a clean update, and show the diff (`diff <installed> <shipped>` or equivalent). |
| `local-edit` | The user edited the installed copy by hand and the payload did not move -- propose leaving it, report it once. Never install over it silently. |
| `conflict` | Both moved, or there is no manifest to tell the two apart -- show the diff, offer to overwrite or leave it, never install silently. |

A `local-edit` or `conflict` an install would discard is named plainly -- the
backup in Step 4 is the only place the discarded version survives.

Report the import line's presence in the same pass: missing -- propose adding
it alongside a file install. A bare import line with no file behind it is
never useful, so never propose it alone.

A `plan` reporting `unchanged` with the import line already present is one
line: "Already installed and current -- nothing to change." No gate follows.

**Adoption.** `unchanged` with **no manifest** is the one exception: the file
matches the payload but nothing records that, so the next update would read a
later hand edit as a `conflict` instead of a `local-edit`. Say so in one line
and offer to record the manifest -- a new file, no other write, no backup
needed. Its `import_line_added_by_skill` is `false`: this run did not add the
line. Declining is fine and leaves everything as it was.

## Step 3: the gate

One closed question. The question text carries the state and whether the
import line will be added -- Step 2 already delivered the detail in its own
turn.

Options, at minimum:

- **Install (Recommended)** -- writes the file (`new`/`update`) and the
  import line if missing. Never touches a `local-edit` or `conflict` file.
- **Install and overwrite my local edit** -- offered only when the state is
  `local-edit` or `conflict`; say plainly that the local version is backed
  up, not discarded outright.
- **Record the manifest only** -- offered only in the adoption case above;
  writes `.tensei-manifest.json` and nothing else.
- **Nothing** -- stop, write nothing.

**Never write without an explicit yes.**

## Step 4: apply

1. **Back up whatever is about to be replaced**, before writing anything:
   copy the current `~/.claude/daikenja/tensei.md` (if it exists) to
   `~/.claude/backups/tensei-<UTC timestamp>/tensei.md`, and, only if the
   import line is about to be added and `~/.claude/CLAUDE.md` already exists,
   copy it to `~/.claude/backups/tensei-<UTC timestamp>/CLAUDE.md` first.
2. **Write `~/.claude/daikenja/tensei.md`** verbatim from
   `${CLAUDE_PLUGIN_ROOT}/templates/tensei.md`, if the gate approved a file
   write.
3. **Append the import line** (`@~/.claude/daikenja/tensei.md`, on its own
   line, at the end of the file) if the gate approved it and it is not
   already present. Keep the file's existing line ending (CRLF stays CRLF),
   make sure the previous last line is terminated before appending, and end
   the file with one newline. Create `~/.claude/CLAUDE.md` with just that
   line if the file does not exist yet.
4. **Write the manifest** at `~/.claude/daikenja/.tensei-manifest.json`:

   ```json
   {
     "installed_hash": "<sha256 of the file just written>",
     "installed_at": "<UTC ISO-8601 timestamp>",
     "import_line_added_by_skill": true
   }
   ```

   Set `import_line_added_by_skill` only if this run is the one that added
   it; otherwise carry forward whatever the existing manifest already had for
   that field. Merge onto the existing manifest rather than replacing it
   wholesale, so a manifest that later gains fields is never clobbered here.

Close with one report, per
`${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- the result leads: what was
written, what was backed up and where. Say plainly that the new `CLAUDE.md`
import takes effect on the **next** session -- this one already loaded the
old file.

## Step 5: uninstalling

On an explicit ask to remove or revert the persona (not the default flow):

1. One closed gate first (`Uninstall?`), same mechanics as Step 3.
2. **Back up the current file and `CLAUDE.md`** exactly as in Step 4 before
   removing anything.
3. **Remove `~/.claude/daikenja/tensei.md`** if the user chose to.
4. **Remove the import line** only if
   `~/.claude/daikenja/.tensei-manifest.json` records
   `"import_line_added_by_skill": true`. A line the user wrote in by hand
   independently is never touched -- if the manifest doesn't say this skill
   added it, leave `CLAUDE.md` alone and say why in one line.
5. **Delete the manifest.**

Report what was removed and where the backup landed.

## Re-running this skill

Safe at any time. A re-run with nothing to do is one line and writes
nothing, including no manifest rewrite. It never touches a `local-edit` file
without the explicit overwrite option in Step 3, and never resolves a
`conflict` on its own.

## Coexisting with other installers of `CLAUDE.md`

Other tooling may own and regenerate `~/.claude/CLAUDE.md` from a skeleton
(the `carlos` plugin's `setup-wow` does, and keeps a slot for exactly this
import line). The contract that keeps the two from fighting:

- This skill only ever **appends one plain line** or **removes that exact
  line**; it never restructures the file, and it never reads anything under
  `~/.claude/reference/` or any other installer's manifest.
- After this skill appends the line, an installer that hashes `CLAUDE.md` will
  see it as changed on its next run. That is correct: it should surface the
  line and carry it forward, not silently drop it. If it does drop it, a re-run
  of this skill reports the line as missing and re-adds it.
- If another installer later moves the line into its own slot,
  `import_line_added_by_skill` stays whatever this skill recorded -- the line
  is still the one this skill added, wherever it now sits, so uninstall still
  removes it.
- `~/.claude/daikenja/tensei.md` and `.tensei-manifest.json` are this skill's
  alone. Nothing else should write them, and this skill writes nothing else.

## Failure cases

| Situation | What to do |
|---|---|
| No persistent `~/.claude` (Step 0) | **Stop.** Nothing written. Never write into the project tree instead. |
| `${CLAUDE_PLUGIN_ROOT}/templates/tensei.md` cannot be read | **Stop.** Name the path. Never reconstruct the payload from memory. |
| `.tensei-manifest.json` will not parse | **Stop.** Name the file, say the user should fix or remove it. Never rewrite a file that could not be read. |
| No manifest, and the installed file differs from shipped | Correct behaviour, not an error: reads as `conflict`. Show the diff and ask. |
| No manifest, and the installed file matches shipped | `unchanged`, untracked. Offer to record the manifest (Step 2, Adoption); never treat it as an error. |
| `CLAUDE.md` contains the import line more than once | Report it; on an install leave the file alone (the import is already active), on an uninstall remove every copy only if the manifest says this skill added it, otherwise none. |
| State is `local-edit` | Leave it by default. Report it once. Only the explicit overwrite option in Step 3 installs over it. |
| `~/.claude/CLAUDE.md` does not exist yet | The import line is absent by definition; adding it creates the file with just that line. Not a failure. |
| The user declines the gate | Write nothing, say so in one line, close. Not a failure. |
| Uninstall asked for a line the manifest didn't record as added by this skill | Leave `CLAUDE.md` untouched, remove the file only if that step was chosen, say in one line why the line was left. |
| `~/.claude/CLAUDE.md` will not parse as UTF-8 text (binary or corrupt) | **Stop.** Report the problem; never guess at where to insert or remove the import line. |
