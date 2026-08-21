---
name: project-decisions
description: Looks up what was decided about a specific topic in a project's Daikenja ledger, including its supersession history. Use when the user says "was this decided", "what did we decide about X", "what's the decision on X", "show me D-003", or "did we ever settle X" -- a targeted question about one decision or topic, not the whole project. Not for a full project overview (that is /daikenja:project-summary) or a delta since last time (that is /daikenja:project-catchup). Read-only; writes nothing. Accepts an optional project key -- `/daikenja:project-decisions <key>` reads that project from anywhere, without being in its directory.
metadata:
  owner: Carlos
  version: 1
---

# Decisions

A targeted lookup against the Decisions section. The user names a topic, an
ID, or a rough description; this skill finds the matching decision and its
full supersession chain, not just the single entry that happens to match the
words.

## Step 0: read the contracts

Read these before doing anything. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/reading.md` -- the shared resolve-and-parse
  mechanism every read skill follows.
- `${CLAUDE_PLUGIN_ROOT}/docs/ledger-format.md` -- entry grammar, supersession.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. The result in Step 5 follows it.

## Step 1: resolve config, project and ledger

Follow `reading.md` § Step A0, § Step A and § Step B.

**The user may name a project** -- `/daikenja:project-decisions <key>`, or the key in
prose. `reading.md` § Step A0 is the whole rule: a named key resolves that
project from anywhere on disk and never falls back to the current directory.
Do not restate the resolution here.

## Step 2: read the ledger

Follow `reading.md` § Step C. Only the Decisions section is needed for the
match, but read the whole file -- a decision's body may reference an open item
or a context link worth surfacing alongside it.

## Step 3: match the query

- **An ID was given** (`D-003`). Exact match.
- **A topic or description was given.** Match by meaning against decision
  bodies, not just keyword overlap -- "the cutover schedule" should find a
  decision about cutting over on a Saturday even without the word "schedule."
- **No match found.** Say so plainly. Do not guess at a near match without
  naming it as a guess:

  ```
  No decision found about "<query>". Closest thing on record: the schema
  freeze from 2026-08-20 (D-003), if that's what you meant.
  ```

- **More than one plausible match.** List them briefly and ask which one, or
  show both if they are clearly related (a decision and the one it
  supersedes).

## Step 4: follow the supersession chain

Once a decision is found, check both directions:

- **It carries `-> superseded by D-nnn`.** It is no longer in force. Show it
  anyway, but lead with the current one and say the match is historical.
- **Another decision's body opens `Supersedes D-nnn.` naming this one.** Same
  case from the other side -- lead with the new decision.
- **Neither.** It is a single decision with no history. Show it alone.

Walk the whole chain if it is more than one hop -- a decision can be
superseded by a decision that was itself later superseded. Show it oldest to
newest so the reasoning arc reads in order.

Per `ledger-format.md`, **the tail is authoritative**. If a body claims
`Supersedes D-nnn.` but the named entry carries no matching tail (or the
reverse), report the mismatch naming both IDs, and treat the tail as the
status. Do not repair it.

## Step 5: show the result

Topic first with the ID and status in parentheses, per `response-format.md`:

```
Cut over on a Saturday, not a weekday evening (D-005, current) -- @carlos --
the rollback window is four hours and nobody wants that on a work night.
[runbook](https://example.com/atlas/runbook)
  Supersedes:
  Cut over on a weekday evening (D-002) -- @carlos. [thread](https://example.com/t/4417)
```

Include the date on every entry shown. If the decision links a context link or
an open item by ID in its body, surface that link as-is -- do not go fetch it.

## Failure cases

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | One notice, continue on ledger defaults. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. |
| The user named a project key that is not in `daikenja.yaml` | **Stop.** Name the key and list the registered ones. Never fall back to the current directory -- an answer about the wrong project reads exactly like a right one. |
| The named project has no path | **Stop.** One line: "`<key>` has no path in daikenja.yaml, so its ledger has no location yet." |
| No ledger at the resolved path | Report per `reading.md` § Step B and stop. Name `/daikenja:project-log`. |
| Supersession marked on only one of two entries | Report the mismatch, naming both IDs. The tail is authoritative; do not repair it. |
| No decision matches the query | Say so. Offer the closest match, named as a guess, if one exists. |
