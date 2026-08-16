---
name: project-catchup
description: Reports what changed in a project's Daikenja ledger since the user last checked, then advances the checkpoint on approval. Use when the user says "catch me up", "what changed since I last looked", "what's new", "what did I miss", or "bring me up to speed" -- personal, delta-shaped asks about a project they already know. Not for a first look at a project (that is /daikenja:project-summary) or a lookup of one specific decision (that is /daikenja:project-decisions). This is the only skill that writes last_checkpoint in daikenja.yaml; it never touches ledger content.
metadata:
  owner: Carlos
  version: 1
  writes: ~/.claude/daikenja/daikenja.yaml (last_checkpoint only)
---

# Catchup

Reports what changed since the user's last checkpoint, then moves the
checkpoint. The one read skill that writes anything, and it writes exactly one
config key, never the ledger.

## Step 0: read the contracts

Read these before doing anything. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/reading.md` -- the shared resolve-and-parse
  mechanism every read skill follows.
- `${CLAUDE_PLUGIN_ROOT}/docs/ledger-format.md` -- entry grammar, Changelog
  grammar.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-contract.md` -- `last_checkpoint`'s
  format and who writes what.

## Step 1: resolve config, project and ledger

Follow `reading.md` § Step A and § Step B.

**No project match, or the project matches but carries no `last_checkpoint`.**
This is a first run. There is no baseline to diff against, so the "delta" is
the whole current ledger. Say so plainly:

```
No checkpoint on file for this project. Showing everything currently in the
ledger. Once you approve, I will set a checkpoint so next time is a real
delta.
```

Proceed to Step 3 with an empty changelog cutoff (every line counts as new).

## Step 2: read the ledger

Follow `reading.md` § Step C. Read the whole file, not just the Changelog --
the Changelog gives you *which* IDs changed, but the current text of each
entry only lives in its section.

## Step 3: compute the delta

Collect every Changelog line whose timestamp is **strictly newer** than
`last_checkpoint` (or every line, on a first run). Do this by comparing
timestamps, not by stopping at the first older line -- a human may have
reordered other sections, and even the Changelog itself makes no ordering
guarantee a skill may depend on, per `ledger-format.md` § Ordering.

From those lines, collect the IDs named, each with the verb it was recorded
under (`+`, `~`, `resolved`, `superseded`, `-`). The same ID can appear on more
than one line across the window; keep the most recent verb. Collect
`+link`/`-link` entries the same way, keyed by label instead of ID.

For every ID still resolvable, look up its **current** text in the Decisions
or Open items section -- report what the entry says now, not a stale
snapshot. For an ID that no longer resolves (`-D-nnn` was the verb, or a
hand-deletion left the Changelog naming something gone), report it as removed
in one line and move on, per `ledger-format.md`'s rule that an unresolvable
Changelog ID is reported, not an error.

For every label still resolvable, look up its current target in the Context
links section. For a label recorded with `-link` (or one that no longer
appears in that section), report it as removed in one line and move on, same
as an unresolvable ID.

**No new lines found.** Say so and stop before proposing a checkpoint move --
there is nothing to advance past that the user hasn't already seen, though a
courtesy re-confirmation of the current checkpoint is fine.

```
No changes since <last_checkpoint>.
```

## Step 4: report the delta

Group by section, newest change first. One line per entry, current state:

```
Since 2026-08-13T17:40Z:

Decisions
- D-002 (new) -- @priya -- Ramp the Harbor rollout 5% / 25% / 100% over three days.

Open items
- O-001 (resolved) -- @sam -- Confirm the 30-day replica cost with finance. -> resolved 2026-08-14, see D-002
- O-003 (new, @unassigned) -- Decide who is on call during the cutover window.

Context links
- Runbook (new) -- https://example.com/atlas/runbook
```

Call out unowned new open items -- they are what `project-gaps` would also
flag, and the user is seeing them for the first time.

## Step 5: propose and write the checkpoint

Propose the new checkpoint as **now**, UTC, minute precision
(`date -u +%Y-%m-%dT%H:%MZ`), the same format the Changelog already uses:

```
Advance the checkpoint for <project> to 2026-08-14T18:02Z?
```

Wait for approval. Silence is not approval.

- **Approved.** Edit `~/.claude/daikenja/daikenja.yaml`, the matched project's
  `last_checkpoint` key only, surgically -- not a rewrite. If the project is
  unregistered, there is nowhere to write it: say so and name
  `/daikenja:setup-user` as the way to register it, then stop without writing.
- **Declined.** Leave the checkpoint untouched and say so. The next run
  reports the same delta again, which is correct -- nothing was missed.

Never write anything else in `daikenja.yaml`. The single-writer rule governs
the ledger; this carve-out is `last_checkpoint` alone, per
`config-contract.md` § Who writes what.

## Failure cases

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | Treat as a first run against ledger defaults. Note that no checkpoint can be written until `/daikenja:setup-user` runs and this project is registered. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. |
| No ledger at the resolved path | Report per `reading.md` § Step B and stop. Name `/daikenja:project-log`. |
| A Changelog ID resolves to no entry | One line saying so, then continue with the rest of the delta. |
| Project unregistered | Show the delta from the ledger on disk (it still resolves per "ledger on disk wins"), but say the checkpoint cannot be saved until the project is registered. |
