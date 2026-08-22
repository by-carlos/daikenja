# Dictated-log requests

Synthetic requests for walking `project-log`'s same-turn path by hand, against
`sample-ledger.md` (the beacon project). Everything here is invented; links are
`example.com` only. Each scenario states the user's message and the path the
skill must take.

Depends on: project-log "The same-turn path for dictated facts", project-log "Check for duplicates first", project-log "Classify before you write"

```yaml
profile:
  name: rimuru
```

## Scenario 1: clean dictated write (same-turn path)

User message:

> Log the decision that the beacon dashboard ships with the rollout, not after
> it.

Expected: all four same-turn conditions hold -- a plain description, the kind
named ("the decision that"), every field resolved (`@rimuru` is not named, the
user owns their own call; date is today), no duplicate in the ledger. The
skill writes `D-005` immediately and shows the written line and the Changelog
line verbatim. No proposal, no question.

## Scenario 2: dictation with an unnamed owner (still same-turn)

User message:

> Add an open item: someone needs to check the beacon alert thresholds before
> the canary starts.

Expected: nobody is named, so the owner is `@unassigned` -- a valid value, not
a question to ask. The skill writes `O-006` in the same turn. Asking "who owns
this?" here is the failure this path exists to remove.

## Scenario 3: dictation that hits a duplicate (drops to propose-then-wait)

User message:

> Log that we're rolling beacon out region by region.

Expected: the duplicate check finds `D-004` already recording that fact, and
the user did not name it. The run drops to propose-then-wait and proposes an
edit or nothing, by ID -- it must not append a near copy in the same turn.

## Scenario 4: pasted thread with ambiguities (one round of questions)

User message: a pasted thread --

> **gobta:** should we hold the canary until the runbook is done?
> **benimaru:** probably, and the budget page needs a link from the ledger
> **gobta:** ok let's see

Expected: pasted material, so propose-then-wait. Two questions exist (is the
canary hold agreed or still open? the budget page needs a link, but the
material does not say whether the project is tracked from it -- source or
context link?) and both land in one "Questions before I write" block in the
same round. If the user then edits the proposal, neither question is asked
again.
