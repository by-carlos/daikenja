# Dictated-log requests

Synthetic requests for walking `project-log`'s batch-and-approve path and its
same-turn path by hand, against the beacon project's two ledger files below.
Everything here is invented; links are `example.com` only. Each scenario states
the user's message and the path the skill must take. **Every scenario assumes
today is 2026-09-15.**

Depends on: project-log "The same-turn path for dictated facts", project-log "Check for duplicates first", project-log "Classify before you write", project-log "Place each decision", project-log "Step 2: resolve the config, the project and the files", project-log "Step 4: read what is already there", project-log-reference.md "Step 3: scaffold the ledger when it is missing", open-format.md "Version line"

```yaml
profile:
  name: rimuru
projects:
  beacon:
    paths:
      - C:/GitHub/beacon
```

## The files these scenarios read

Scenarios 1-4 run from `C:/GitHub/beacon` against these two files. Scenarios
5-7 change one thing each and say what.

`C:/GitHub/beacon/DECISIONS.md`:

~~~markdown
<!-- decisions-format: 1 -->
# Decisions

Decisions in force. Read the area that covers a path before changing it; add
or edit an entry in the same pull request when a change settles something
future work must respect.

## Rollout

Paths: `rollout/`, `.github/workflows/canary.yml`

- **Beacon rolls out region by region, never to every region at once.** — a
  bad config stays in one region. Revisit: if traffic moves behind a global
  load balancer. Source: https://example.com/beacon/thread/12

## Dashboard

Paths: `dashboard/`

- **The dashboard reads the events table, never the raw log.** — the raw log
  is not retained past a week. Revisit: never.
~~~

`C:/GitHub/beacon/.daikenja/open.md`:

~~~markdown
<!-- daikenja-open-format: 1 -->
# beacon open items

## Open items

- 2026-08-10 -- @benimaru -- Write the canary runbook.
- 2026-08-04 -- @unassigned -- Pick the second rollout region.

## Context links

- Rollout plan -- https://example.com/beacon/rollout-plan

## Sources
~~~

## Scenario 1: clean dictated decision (same-turn path)

User message:

> Log the decision that the beacon dashboard ships with the rollout, not after
> it, because support needs it on day one. Revisit if support gets its own
> tooling.

Expected: all four same-turn conditions hold -- a plain description, the kind
named ("the decision that"), the rule, the why and the revisit condition all in
the user's words, one repository, and the `Dashboard` area covers it. No
duplicate. The skill writes immediately and shows the written line under its
file, then says it is not committed:

~~~
C:/GitHub/beacon/DECISIONS.md -- Dashboard
- **The dashboard ships with the rollout, not after it.** — support needs it
  on day one. Revisit: if support gets its own tooling.
~~~

No `Source:` clause: the dictation names none, and none is invented. No ID, no
owner, no date on the entry. Nothing is written to `open.md`.

## Scenario 2: dictation with an unnamed owner (still same-turn)

User message:

> Add an open item: someone needs to check the beacon alert thresholds before
> the canary starts.

Expected: nobody is named, so the owner is `@unassigned` -- a valid value, not
a question to ask. The skill writes, directly under `## Open items`, in the same
turn:

~~~
C:/GitHub/beacon/.daikenja/open.md -- Open items
- 2026-09-15 -- @unassigned -- Check the beacon alert thresholds before the canary starts.
~~~

Asking "who owns this?" here is the failure this path exists to remove.

## Scenario 3: dictation that hits a duplicate (drops to propose-then-wait)

User message:

> Log that we're rolling beacon out region by region.

Expected: the duplicate check finds the `Rollout` entry already recording that
fact, and the user did not name it. The run drops to propose-then-wait, quotes
that entry, and proposes nothing or an edit to it -- it must not append a near
copy. There is no ID to name it by; it is named by its area and its words.

## Scenario 4: pasted thread (one batch naming both files)

User message: a pasted thread --

> **gobta:** the canary runbook is done, merged it this morning
> **benimaru:** then we hold the canary until the runbook review is signed off?
> **rimuru:** agreed, hold it until the review is signed off, otherwise on-call
> is guessing
> **benimaru:** and the budget page needs a link from the ledger

Expected: pasted material, so propose-then-wait. One batch, grouped by file:

~~~
C:/GitHub/beacon/DECISIONS.md
  ## Rollout
  + - **The canary does not start until the runbook review is signed off.** —
      otherwise on-call is guessing. Revisit: <asked below>.

C:/GitHub/beacon/.daikenja/open.md
  Open items
  - - 2026-08-10 -- @benimaru -- Write the canary runbook.

Questions before I write:
- What would reopen the canary hold -- or is it "never"?
- The budget page: is the project tracked from it (a source) or is it a useful
  address (a context link)? And what is its link?
~~~

The runbook item is closed by deleting its line -- no checkbox, no tail. The
hold is a decision (rimuru agreed, nobody objected) and meets the keep rule:
someone could start the canary early without knowing. It goes to the `Rollout`
area, whose `Paths:` covers the canary workflow. No `Source:`: a paste has no
link. Both questions land in one block in one round; if the user then edits the
proposal, neither is asked again. Nothing is written before the approval, and
the confirmation afterwards says the change is not committed.

## Scenario 5: a newer `DECISIONS.md` format (refuse the whole batch)

Same files, except the first line of `DECISIONS.md` is
`<!-- decisions-format: 2 -->`.

User message:

> Log the decision that the canary starts in eu-west because it has the lowest
> traffic, revisit never, and add an open item for @benimaru to book the canary
> review.

Expected: Step 4 reads the version lines first. `DECISIONS.md` is newer than
this plugin knows, and the batch writes to it, so the **whole batch** is
refused -- including the open item, which would have gone to `open.md`, a file
at a version the plugin knows:

~~~
C:/GitHub/beacon/DECISIONS.md was written by a newer format (version 2);
update the Daikenja plugin before logging. Nothing was written. The version
rule is in ${CLAUDE_PLUGIN_ROOT}/docs/open-format.md.
~~~

Must not happen: writing the open item alone, writing the decision in the
version-1 shape, rewriting the version line, or reading the file as broken. A
reading skill would read this same file and warn once; only `project-log`
refuses.

## Scenario 6: an existing `DECISIONS.md` another tool wrote (extend it)

`C:/GitHub/beacon/DECISIONS.md` is replaced by this file, written by
plan-staged-rollout's closeout. There is **no** `.daikenja/` folder at all --
no `open.md`, no old ledger.

~~~markdown
<!-- decisions-format: 1 -->
# Decisions

Decisions in force. Read the area that covers a path before changing it; add
or edit an entry in the same pull request when a change settles something
future work must respect.

ADRs: docs/adr/

## Release

Paths: `.github/workflows/`, `CHANGELOG.md`

- **Releases are cut from `main` by tag, never from a branch.** — a branch
  release shipped an unreviewed fix. Revisit: never. Source: #41
~~~

User message: a pasted thread --

> **benimaru:** release workflow stays tag-only, but we also need the canary
> gate in it before any tag publishes, the last bad release skipped it
> **rimuru:** yes, gate it. nothing publishes without a green canary. I'll
> chase who owns the canary dashboards

Expected: propose-then-wait. The `DECISIONS.md` is **adopted**: the new entry
goes at the end of its `Release` area, and every other line of the file --
title, intro, `ADRs:` line, the existing entry -- is untouched. The template is
never copied over it. `open.md` does not exist, so it alone is scaffolded from
the template, folded into the same approval:

~~~
C:/GitHub/beacon/DECISIONS.md
  ## Release
  + - **No release publishes without a green canary run.** — the last bad
      release skipped it. Revisit: <asked below>.

C:/GitHub/beacon/.daikenja/open.md  (creating it from the template)
  Open items
  + - 2026-09-15 -- @rimuru -- Find out who owns the canary dashboards.

Questions before I write:
- What would reopen the canary gate -- or is it "never"?
~~~

The existing "tag-only" entry is not duplicated: the thread restates it, so it
is already there. Must not happen: a scaffolded `DECISIONS.md`, a second
`# Decisions` heading, the file reformatted, or the existing entry rewritten.

## Scenario 7: an old ledger at the legacy location (refuse to scaffold)

`C:/GitHub/beacon/.daikenja/ledger.md` exists in the old format, with IDs and a
Changelog, and there is no `.daikenja/open.md` beside it. Run it twice: once
with scenario 6's `DECISIONS.md` present, once with no `DECISIONS.md` at all.

User message:

> Add an open item: @gobta writes the canary abort criteria.

Expected, both times: Step 2 finds the unmigrated ledger before anything else,
and the run stops with one line, writing nothing and scaffolding nothing:

~~~
The ledger at C:/GitHub/beacon/.daikenja/ledger.md needs migration -- run /daikenja:setup-user.
~~~

A present `DECISIONS.md` does not lift the refusal: it may have been written by
another tool, and the old ledger beside it is still unmigrated. Must not
happen: a new `open.md` scaffolded next to the old ledger, the item written into
the old ledger, the old ledger parsed or edited, or the same-turn path taken
because the message qualified for it.
