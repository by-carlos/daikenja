---
name: project-catchup
description: Reports what changed in a project's Daikenja ledger since the user last checked, then advances the checkpoint on approval. Use when the user says "catch me up", "what changed since I last looked", "what's new", "what did I miss", or "bring me up to speed" -- personal, delta-shaped asks about a project they already know, not a first look or a single decision lookup. This is the only skill that writes last_checkpoint in daikenja.yaml; it never touches ledger content. Accepts an optional project key -- `/daikenja:project-catchup <key>` reads that project from anywhere, without being in its directory.
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

- `${CLAUDE_PLUGIN_ROOT}/docs/reading.md` § Step A0, § Step A, § Step B, §
  Step C and § Notices, shared wording -- the shared resolve-and-parse
  mechanism Steps 1 and 2 below follow, plus the exact notice text they reuse
  without restating it (a config marked absent or a project left unregistered
  has no literal wording inline in Step A -- only in § Notices, shared
  wording).
- `${CLAUDE_PLUGIN_ROOT}/docs/ledger-format.md` § IDs, § Body markers, §
  Section: Decisions, § Section: Open items, § Section: Context links, §
  Section: Sources, § Section: Changelog, § Compacting a long summary and §
  Reading rules for skills -- ID range expansion, the markers this skill
  carries through unchanged, each section's own grammar for looking up a
  changed ID's current text, and the delta-reporting rules.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-schema.md` § Field notes --
  `last_checkpoint`'s format.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-writers.md` -- who writes what. This doc
  has no subsections to narrow to -- the whole file is that one topic.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. Read in full and not narrowed to a section: Step 4 explicitly
  follows only § Entries are named topic-first, ID in parentheses, but the
  contract's own scope says a skill "implements it; it never redefines it" --
  every rule in the file (tone scaling, the clean-result line, itemised
  findings) governs this skill's replies whether or not Step 4 names it.

## Step 1: resolve config, project and ledger

Follow `reading.md` § Step A0, § Step A and § Step B.

**The user may name a project** -- `/daikenja:project-catchup <key>`, or the key in
prose. `reading.md` § Step A0 is the whole rule: a named key resolves that
project from anywhere on disk and never falls back to the current directory.
Do not restate the resolution here.

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

**Join continuation lines before reading a summary.** A Changelog summary may
run onto lines indented two spaces carrying no list marker. Strip each one's
indent and join it to the summary with a single space, then split on commas as
usual, per `ledger-format.md` § Compacting a long summary. A continuation line
left unjoined is a set of changes dropped from the delta with nothing saying so.

**Then expand ranges.** A summary item of the form `<verb><first>..<last>` --
`+D-006..D-009`, `resolved O-004..O-006` -- stands for every ID from `<first>`
to `<last>` inclusive, each carrying that verb. Expand it and treat the results
exactly as if the IDs had been named one by one. A bulk write is where this
happens, so one line can expand to thirty changes. Reporting a range as a single
change, or skipping it because it does not look like an ID, is the same data
loss.

From those lines, collect the IDs named, each with the verb it was recorded
under (`+`, `~`, `resolved`, `superseded`, `-`). The same ID can appear on more
than one line across the window; keep the most recent verb. Collect
`+link`/`-link` entries the same way, keyed by label instead of ID.

For every ID still resolvable, look up its **current** text in its own
section -- Decisions, Open items, or Sources for an `S-nnn`, whose current
text is its head line -- and report what the entry says now, not a stale
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

Group by section, newest change first. One line per entry, current state.
Topic first with the ID and the change in parentheses, per
`response-format.md` -- the ledger line is ID-first, the reply is not. A
decision carrying `Imposed.` is reported as imposed, and a `Blocked by
<id>.` or `Contradicts <id>.` marker on a reported entry is carried into its
reworded line, not dropped:

```
Since 2026-08-13T17:40Z:

Decisions
- Ramp the Harbor rollout 5% / 25% / 100% over three days (D-002, new) -- @priya

Open items
- Confirm the 30-day replica cost with finance (O-001, resolved) -- @sam -> resolved 2026-08-14, see the ramp decision (D-002)
- Decide who is on call during the cutover window (O-003, new) -- @unassigned

Context links
- Runbook (new) -- https://example.com/atlas/runbook
```

Call out unowned new open items -- they are what `project-gaps` would also
flag, and the user is seeing them for the first time.

**A delta that follows a bulk write is long, and nothing in it is truncated.**
Grouping consecutive entries that took the same verb is fine and reads better
(`Decisions D-006 to D-021, all new -- seeded from the architecture wiki`), as
long as every ID is still accounted for. Say how many changes the window holds
before the list, so a long report is expected rather than alarming.

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
  `/daikenja:setup-project` as the way to register it, then stop without
  writing.
- **Declined.** Leave the checkpoint untouched and say so. The next run
  reports the same delta again, which is correct -- nothing was missed.

Never write anything else in `daikenja.yaml`. The single-writer rule governs
the ledger; this carve-out is `last_checkpoint` alone, per
`config-writers.md` § Who writes what.

## Failure cases

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | Treat as a first run against ledger defaults. Note that no checkpoint can be written until `/daikenja:setup-user` has configured Daikenja and `/daikenja:setup-project` has registered this project. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. |
| The user named a project key that is not in `daikenja.yaml` | **Stop.** Name the key and list the registered ones. Never fall back to the current directory -- an answer about the wrong project reads exactly like a right one. |
| The named project has no path and no absolute `ledger:` | **Stop.** One line: "`<key>` has no path and no absolute ledger in daikenja.yaml, so its ledger has no location." A pathless project *with* an absolute `ledger:` resolves normally. |
| No ledger at the resolved path | Report per `reading.md` § Step B and stop. Name `/daikenja:project-log`. |
| A Changelog ID resolves to no entry | One line saying so, then continue with the rest of the delta. |
| A Changelog range is malformed -- endpoints in different sections, or running backwards | Report the line and what is wrong, then skip that item and continue with the rest of the delta, per `ledger-format.md` § Reading rules, rule 5. Do not guess what it meant, do not expand it partially, and do not rewrite it. |
| Project unregistered | Show the delta from the ledger on disk (it still resolves per "ledger on disk wins"), but say the checkpoint cannot be saved until the project is registered. |
