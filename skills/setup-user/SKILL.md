---
name: setup-user
description: One-time (and re-runnable) setup for Daikenja. Checks that the session is Claude Code, creates ~/.claude/daikenja/daikenja.yaml from the template, captures the user's profile, copies the blank persona and writing-style files if they are not already there, registers the current project, and reports which connected tools the other skills can use. Run explicitly with /daikenja:setup-user -- it never fires on its own.
metadata:
  owner: Carlos
  version: 1
  writes: ~/.claude/daikenja/daikenja.yaml, ~/.claude/daikenja/personas.md (if absent), ~/.claude/daikenja/writing-style.md (if absent)
disable-model-invocation: true
---

# Setup user

The skill every other Daikenja skill assumes has already run. It writes
`daikenja.yaml`, nothing else -- `personas.md` and `writing-style.md` get a
blank starting copy if the user has none, but the user owns their content from
that point on.

**Slash-only on purpose.** This skill asks personal questions and writes files
outside the project. Nothing about "help me get started" or "set up my config"
should make it fire on its own -- the user runs `/daikenja:setup-user` when they
mean to. `disable-model-invocation: true` is set for that reason.

## Step 0: the environment gate

Daikenja is Claude Code only (see `README.md`). `plugin.json` has no field that
can declare this, so this is the runtime check the whole surface decision rests
on. Do this before anything else, before asking the user anything.

Try to list `~/.claude/` (the real OS home directory, not the project working
tree) and confirm it looks like a live Claude Code install -- at least one of
`~/.claude/settings.json`, `~/.claude/CLAUDE.md` or `~/.claude/plugins/`
exists there.

- **It resolves and at least one marker exists.** Proceed.
- **It does not resolve, is empty, or none of the markers exist.** Stop and
  say:

  ```
  Daikenja only works in Claude Code. This session does not have a persistent
  home directory with a Claude Code install in it, which Daikenja needs to read
  and write ~/.claude/daikenja/. Nothing was written.
  ```

**Say honestly what this does and does not prove.** It confirms persistent,
unsandboxed filesystem access outside the current working tree exists, which is
what Daikenja actually needs. It is not a positive identification of the Claude
Code binary. Any surface that happens to grant the same unrestricted
home-directory access would pass it too -- at the time this was written that is
not known to include Cowork (folder-scoped by design) or claude.ai chat
(no persistent filesystem at all), but the check is testing the capability, not
reading a flag that says "Claude Code."

## Step 1: read what already exists

Before asking anything, check what is already on disk. This is what makes a
second run reconcile instead of clobber.

- `~/.claude/daikenja/daikenja.yaml` -- read it if present. Malformed YAML:
  stop, name the first line that does not parse, same as every other skill's
  failure behavior. Never rewrite a file you cannot parse.
- `~/.claude/daikenja/personas.md`, `~/.claude/daikenja/writing-style.md` --
  note only whether each exists. Never open them to check content; existence is
  the only thing that decides whether to copy the template.
- The current directory's normalized path (forward slashes, no trailing slash),
  and whether any `projects:` entry already has this exact `path`.

## Step 2: create the config directory and file

If `~/.claude/daikenja/` does not exist, create it.

If `daikenja.yaml` does not exist, copy
`${CLAUDE_PLUGIN_ROOT}/templates/daikenja.yaml` to
`~/.claude/daikenja/daikenja.yaml` verbatim, then fill it in Step 3. Do not skip
the copy and hand-build a file from memory of the schema -- the template is the
source of the comments the user keeps.

If `daikenja.yaml` already exists, Step 3 edits it surgically (the Edit tool,
not a rewrite) so hand-added keys -- `norms_doc`, per-project overrides, other
projects -- survive untouched.

## Step 3: capture the profile

One short round, not an interrogation. Ask for what is missing or say what is
already set and ask if they want to change it:

```
Setting up Daikenja. Three questions, all short:

1. Your name, as it should appear on ledger entries you own.
2. Your role (optional, one or two words -- skip with "-").
3. How much you want the skills to explain themselves: direct / standard
   (default) / guided.

If you also want org, team or domain on file, add them now or skip -- they are
optional and you can fill them in `daikenja.yaml` by hand later.
```

`name` is the only required field (per `docs/config-contract.md`). If the user
skips it, say the config is incomplete until it is set and stop without
writing a half-filled file -- do not write `profile.name:` empty.

Write the answers into the `profile:` block with the Edit tool, one key at a
time, on top of whichever fields already had values. Leave `writing_style` and
`personas` at the template's defaults (`./writing-style.md`, `./personas.md`)
unless the user says otherwise -- Step 4 is what makes those paths real.

## Step 4: copy the prose templates, only if absent

For each of `personas.md` and `writing-style.md`:

- **Missing.** Copy `${CLAUDE_PLUGIN_ROOT}/templates/<name>` to
  `~/.claude/daikenja/<name>` verbatim.
- **Already there.** Leave it alone. Say so in one line ("writing-style.md
  already exists, not touched") and move on. This holds even if the existing
  file is still the untouched template -- existence is the only test, per the
  stage contract. Never inspect or overwrite user prose.

## Step 5: register the current project

Compute the current directory's normalized path (forward slashes, no trailing
slash). Compare against every `projects:` entry's `path`, normalized the same
way.

- **Exact match already exists.** Say which project key it is registered under
  and leave the entry alone -- registration is idempotent, not a place to
  silently change a key someone chose.
- **No match.** Propose a new entry, key defaulting to the directory's own
  name (ask if the user wants a different label), and add it under `projects:`:

  ```yaml
  <dir-name>:
    path: <normalized absolute path>
  ```

  Leave `ledger`, `last_checkpoint`, `stale_after_days` and `norms_doc` unset --
  they default per `docs/config-contract.md` and get written by the skills that
  actually need them (`log`, `catchup`).

## Step 6: report tool availability

State plainly which connected tools the other skills can use this session, and
what degrades without them. Do not guess at tools that are not visible in this
session -- report what is actually connected.

```
Tools available this session:
- <connector/tool> -- <skill(s) that use it>, or "none connected -- <skill>
  will need pasted text/links instead"
```

At minimum cover: a link-fetching capability (`thread`, `log` follow a pasted
link), and any chat connector (Slack, email, Teams) if one is present. This is
informational -- it never blocks the rest of setup.

## Step 7: confirm

One or two lines: what was written or left alone, and where.

```
Daikenja is set up. Wrote ~/.claude/daikenja/daikenja.yaml (profile: name=Carlos,
tone=standard). writing-style.md and personas.md already existed and were not
touched. Registered this project as `billing-api` at C:/GitHub/billing-api.
```

## Re-running this skill

Safe at any time. It never overwrites `personas.md` or `writing-style.md` once
they exist, never touches a `projects:` entry that already matches the current
path, and only edits the `profile:` keys the user answers in Step 3 -- everything
else already in `daikenja.yaml` is left as it was found.

## Failure cases

One notice line, then continue with reduced behavior. Hard-stop only when the
missing thing is the task itself -- same rule every Daikenja skill follows.

| Situation | What to do |
|---|---|
| Not Claude Code (Step 0) | **Stop.** Nothing written. See Step 0's message. |
| `daikenja.yaml` exists but is malformed | **Stop.** Name the first line that does not parse. Never guess the intent and never rewrite the file. |
| User skips `name` | **Stop** before writing `daikenja.yaml`. Say the config is incomplete and ask again next run. |
| `~/.claude/daikenja/` cannot be created (permissions, etc.) | **Stop.** Name the path and the error. |
| A pointed-at prose file path in an existing config does not resolve | One notice naming the path, then continue -- this is `setup-user` reporting the same failure mode every reading skill uses, not something it repairs. |
