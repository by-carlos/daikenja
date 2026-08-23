---
name: project-decisions
description: Looks up what was decided about a specific topic in a project's Daikenja ledger, including its supersession history, the entries it is blocked by or contradicts, and whether it was imposed from outside. Use when the user says "was this decided", "what did we decide about X", "what's the decision on X", "show me D-003", or "did we ever settle X" -- a targeted question about one decision or topic, not a full project overview or a delta since last time. Read-only; writes nothing. Accepts an optional project key -- `/daikenja:project-decisions <key>` reads that project from anywhere, without being in its directory.
metadata:
  owner: Carlos
  version: 1
---

# Decisions

A targeted lookup against the Decisions section. The user names a topic, an
ID, or a rough description; this skill finds the matching decision, its full
supersession chain, and everything else in the ledger that relates to it -- not
just the single entry that happens to match the words.

## Step 0: read the contracts

Read these before doing anything. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/reading.md` § Step A0, § Step A, § Step B, §
  Step C and § Notices, shared wording -- the shared resolve-and-parse
  mechanism Steps 1 and 2 below follow, plus the exact notice text they reuse
  without restating it (a config marked absent or a project left unregistered
  has no literal wording inline in Step A -- only in § Notices, shared
  wording).
- `${CLAUDE_PLUGIN_ROOT}/docs/ledger-format.md` § IDs, § Body markers, §
  Relationships between entries, § A decision imposed from outside, §
  Section: Decisions, § Section: Open items and § Reading rules for skills --
  exact-ID matching, the supersession tail, the one-hop relationship scan, and
  the reopen-vs-comply rule for an imposed decision.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. Read in full and not narrowed to a section: Step 6 explicitly
  follows only § Entries are named topic-first, ID in parentheses, but the
  contract's own scope says a skill "implements it; it never redefines it" --
  every rule in the file (tone scaling, the clean-result line, itemised
  findings) governs this skill's replies whether or not Step 6 names it.

## Step 1: resolve config, project and ledger

Follow `reading.md` § Step A0, § Step A and § Step B.

**The user may name a project** -- `/daikenja:project-decisions <key>`, or the key in
prose. `reading.md` § Step A0 is the whole rule: a named key resolves that
project from anywhere on disk and never falls back to the current directory.
Do not restate the resolution here.

## Step 2: read the ledger

Follow `reading.md` § Step C. Only the Decisions section is needed for the
match, but read the whole file -- a decision's body may reference an open item
or a context link worth surfacing alongside it, and Step 5's relationship scan
needs both sections regardless.

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
- **Another decision carries `-> superseded by D-nnn` naming this one.** Same
  case again, found from the tail instead of the body -- check whether the
  matched entry's own body opens `Supersedes <that decision's ID>.` to confirm
  it. If not, this is the mismatch below, found from the tail side.
- **Neither.** It is a single decision with no history. Show it alone.

Walk the whole chain if it is more than one hop -- a decision can be
superseded by a decision that was itself later superseded. Show it oldest to
newest so the reasoning arc reads in order.

Per `ledger-format.md`, **the tail is authoritative**. If a body claims
`Supersedes D-nnn.` but the named entry carries no matching tail (or the
reverse), report the mismatch naming both IDs, and treat the tail as the
status. Do not repair it.

## Step 5: surface relationships and origin

Supersession is one relationship and the ledger records two more, as body
markers rather than tails, per `ledger-format.md` § Relationships between
entries. They are written on one entry only, so this step looks **both ways**
for the decision Step 3 matched -- and for every decision Step 4 pulled in with
it, since a superseded entry's blockers are part of why it went.

- **Markers on the entry itself.** A body opening `Blocked by <id>.` or
  `Contradicts <id>.` names what constrains it. Resolve each ID against the
  entries read in Step 2 and show that entry's topic, not the bare ID.
- **Markers elsewhere naming it.** Scan **both sections** for entries whose
  body markers name this decision. An open item contradicting a decision
  already in force is the case worth surfacing most, and it is invisible from
  the decision's own line.
- **`Imposed.`** Say so. A decision this group made can be reopened by this
  group; an imposed one can only be complied with, exempted or escalated, and
  the prose after the marker names who imposed it. Never report an unowned
  imposed decision as a gap -- see `project-gaps`, whose scope is Open items.

**One hop, both directions.** Unlike a supersession chain, a relationship is
not walked transitively: report what directly relates to the matched decision
and stop. Two entries may legitimately contradict each other, and a blocked-by
graph may cycle, so there is no chain to walk to an end the way supersession
has one.

**Report a marker that resolves to nothing**, naming the entry carrying it and
the ID it names, per `ledger-format.md` § Reading rules, rule 6. Do not guess
which entry was meant and do not repair anything.

## Step 6: show the result

Topic first with the ID and status in parentheses, per `response-format.md`:

```
Cut over on a Saturday, not a weekday evening (D-005, current) -- @carlos --
the rollback window is four hours and nobody wants that on a work night.
[runbook](https://example.com/atlas/runbook)
  Supersedes:
  Cut over on a weekday evening (D-002) -- @carlos. [thread](https://example.com/t/4417)
```

Relationships go under the entry they belong to, one line each, still topic
first. Say which direction each one runs, because the file only records one of
them:

```
Every service writes to the shared audit log (D-009, current) -- @unassigned --
imposed by the platform programme's architecture board.
  Contradicted by:
  Confirm whether the gateway can be exempted from the shared audit log (O-008,
  open) -- @sam.
```

Include the date on every entry shown. If the decision links a context link or
an open item by ID in its body, surface that link as-is -- do not go fetch it.

## Failure cases

| Situation | What to do |
|---|---|
| `daikenja.yaml` absent | One notice, continue on ledger defaults. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse. |
| The user named a project key that is not in `daikenja.yaml` | **Stop.** Name the key and list the registered ones. Never fall back to the current directory -- an answer about the wrong project reads exactly like a right one. |
| The named project has no path and no absolute `ledger:` | **Stop.** One line: "`<key>` has no path and no absolute ledger in daikenja.yaml, so its ledger has no location." A pathless project *with* an absolute `ledger:` resolves normally. |
| No ledger at the resolved path | Report per `reading.md` § Step B and stop. Name `/daikenja:project-log`. |
| Supersession marked on only one of two entries | Report the mismatch, naming both IDs. The tail is authoritative; do not repair it. |
| A `Blocked by` or `Contradicts` marker names an ID with no entry | Report it -- which entry carries it, which ID it names -- then continue, per `ledger-format.md` § Reading rules, rule 6. Do not guess which entry was meant. |
| Two entries name each other, or a blocked-by chain cycles | Not an error. Report what directly relates and stop; this skill walks one hop, and only supersession is walked as a chain. |
| An imposed decision has no owner | Normal, and never a gap. `@unassigned` on an imposed decision is the honest attribution -- nobody on this side made it. Say it was imposed and who by; do not report it as missing an owner. |
| No decision matches the query | Say so. Offer the closest match, named as a guess, if one exists. |
