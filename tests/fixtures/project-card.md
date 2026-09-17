# Fixture: project cards and content-based resolution

Synthetic. Invented projects, invented people, `example.com` links. Nothing
here comes from real work. Used by the acceptance checks for the project
card: `setup-project`'s card offer, `project-summary`'s Scope block, and
`thread`'s Step 2b, which places a thread against a project by key, by
directory or by content and adds the `Ledger:` line.

Depends on: project-card.md "Location", project-card.md "Resolving a project by content", thread "Step 2b: place the thread", project-summary "Step 3: build the overview", setup-project "Step 3b: offer the project card"

---

## The registry

```yaml
profile:
  name: Rimuru

projects:
  harbor:
    path: C:/GitHub/harbor

  atlas-migration:
    path: C:/GitHub/atlas

  q4-planning:
    paths: []
    ledger: C:/Users/rimuru/.claude/daikenja/ledgers/q4-planning.md

  billing-api:
    path: C:/GitHub/billing-api
```

Card locations that follow from it, per `project-card.md` § Location:

| Project | Ledger | Card |
|---|---|---|
| harbor | `C:/GitHub/harbor/.daikenja/ledger.md` | `C:/GitHub/harbor/.daikenja/project.md` |
| atlas-migration | `C:/GitHub/atlas/.daikenja/ledger.md` | `C:/GitHub/atlas/.daikenja/project.md` |
| q4-planning | `C:/Users/rimuru/.claude/daikenja/ledgers/q4-planning.md` | `C:/Users/rimuru/.claude/daikenja/ledgers/q4-planning.project.md` |
| billing-api | `C:/GitHub/billing-api/.daikenja/ledger.md` | `C:/GitHub/billing-api/.daikenja/project.md` -- **does not exist** |

`billing-api` has a ledger but no card. `q4-planning`'s card is the
`<name>.project.md` form: a `project.md` in the shared `ledgers/` directory
would belong to no project in particular.

## The cards

`C:/GitHub/harbor/.daikenja/project.md`:

```markdown
# harbor card

## Scope

Harbor is the per-tenant rate limiter in front of the booking API. It covers
the limiter service, its rollout to tenants and the limiter configuration;
it does not cover the booking API itself or tenant onboarding.

## Owns

- channel: #harbor-rollout
- repo: northwind/harbor
- tracker: HARB
- doc: https://example.com/harbor/runbook

## People

- @diablo -- rollout owner
- @benimaru -- platform lead
- @souei -- operations
```

`C:/GitHub/atlas/.daikenja/project.md`:

```markdown
# atlas-migration card

## Scope

Atlas replaces the legacy order store for the payments team. It covers the
data migration, the cutover and the 30-day fallback window; it does not cover
the reporting warehouse, which stays on the legacy store.

## Owns

- channel: #atlas-dev
- repo: northwind/atlas
- tracker: ATL

## People

- @priya -- migration lead
- @sam -- finance liaison
```

`C:/Users/rimuru/.claude/daikenja/ledgers/q4-planning.project.md`:

```markdown
# q4-planning card

## Scope

Quarterly planning for the platform group: which programmes get headcount and
which are paused. It decides priorities, not designs.

## Owns

- doc: https://example.com/wiki/q4-planning

## People

- @rimuru -- chair
```

## The harbor ledger, as `thread` reads it

The state `sample-thread.md` and `sample-thread-followup.md` leave behind, so
the `Ledger:` walks below have something to touch:

```markdown
## Decisions

- 2026-08-14 -- D-001 -- @diablo -- Ramp the rate limiter 5% / 25% / 100% over three days from 2026-08-17, not a single flag flip. [thread](https://example.com/slack/harbor-rollout/p1)

## Open items

- [ ] 2026-08-14 -- O-001 -- @unassigned -- Define the rollback trigger for the ramp: who pulls it and on what p99 number.
- [ ] 2026-08-14 -- O-002 -- @unassigned -- Write the customer comms before Monday 2026-08-17.
```

---

## Walk 1: resolved by handle, from an unrelated directory

The user runs `/daikenja:thread` from `C:/GitHub/scratch` (no project
matches) and pastes a thread headed `#harbor-rollout -- 3 messages`, in which
souei proposes pulling the ramp at 25% if p99 doubles, and diablo agrees.

- No key was named; the directory resolves nothing; content resolution runs.
- `#harbor-rollout` is owned by exactly one card, harbor. Decisive.
- The `Ledger:` line names the project, the path, the decision touched and
  the open item the thread appears to resolve:

```
Ledger: harbor, matched by #harbor-rollout (C:/GitHub/harbor/.daikenja/ledger.md)
-- touches the ramp decision (D-001); appears to resolve the rollback-trigger
question (O-001).
```

What must not happen: `O-001` is not flipped, nothing is written, and the
line does not say "resolved". If the user then says "log that", it is
`/daikenja:project-log`'s run, not this skill's.

## Walk 2: resolved by scope, as a candidate

Same directory. The pasted thread has no channel header and names no ticket
or repository. Its subject is "the limiter config still lives in env vars;
should we move it to the config service before the next tenant wave?"

- No handle decides. harbor's Scope names the limiter and its configuration;
  atlas-migration's does not; q4-planning decides priorities, not designs.
- harbor is a **candidate**, stated as such, and its ledger is not read as
  the user's until they confirm:

```
Project: probably harbor -- confirm, and I will check its ledger.
```

- On "yes, harbor": the `Ledger:` line follows, opening
  `Ledger: harbor, confirmed by you (C:/GitHub/harbor/.daikenja/ledger.md)`,
  so it says the match was confirmed by the user rather than decided by a
  handle.

What must not happen: reading harbor's ledger and reporting "touches D-001"
before the user has confirmed the candidate.

## Walk 3: the cross-check catches a mismatch

The user runs `/daikenja:thread` from `C:/GitHub/harbor` and pastes a thread
headed `#atlas-dev -- 5 messages` about the fallback-window cost.

- The directory resolves harbor. That is the project for the summary.
- The content cross-check finds `#atlas-dev` on atlas-migration's card, and
  says so in one line before the `Ledger:` line, which stays on harbor:

```
This thread is from #atlas-dev, which belongs to atlas-migration, not to
harbor.
Ledger: harbor (C:/GitHub/harbor/.daikenja/ledger.md) -- nothing on this
subject.
```

What must not happen: silently switching to atlas-migration's ledger. The
user chose the directory; the line lets them choose again.

## Walk 4: a project with no card is not a candidate

The user pastes a thread about "the invoice retry queue" from `C:/GitHub/scratch`.

- `billing-api` has a ledger but no card, so it is never considered. No
  other Scope fits.
- The summary carries no `Ledger:` line and says nothing about resolution:
  `thread` stays silent on a non-match, per `thread` § Step 2b and
  `project-card.md` § Resolving a project by content, tier 3. The
  one-line `No registered project matches this content. billing-api has no
  card, so it could not be checked.` form is for a caller asked to resolve
  outright, which nothing shipped yet is.

What must not happen: a notice about `daikenja.yaml`, cards or resolution
in the middle of the thread summary.

## Walk 5: a shared handle decides nothing

Suppose atlas-migration's card also listed `- channel: #harbor-rollout`.
Walk 1's thread then matches two cards on the same handle. The result is
undecided, both keys are named, and the run falls through to Scope as a
candidate at most -- never a coin toss between the two.

## Walk 6: `project-summary` opens with the card

`/daikenja:project-summary harbor` from anywhere:

```
harbor ledger -- C:/GitHub/harbor/.daikenja/ledger.md
Card: C:/GitHub/harbor/.daikenja/project.md

Scope
Harbor is the per-tenant rate limiter in front of the booking API. It covers
the limiter service, its rollout to tenants and the limiter configuration;
it does not cover the booking API itself or tenant onboarding.
- channel: #harbor-rollout
- repo: northwind/harbor
- tracker: HARB
- doc: https://example.com/harbor/runbook

Decisions in force (1)
...
```

`/daikenja:project-summary billing-api` prints one line in place of the Scope
block and continues:

```
No project card at C:/GitHub/billing-api/.daikenja/project.md. Run /daikenja:setup-project to add one.
```

## Walk 7: `setup-project` offers the card once

Run in `C:/GitHub/billing-api`, already registered. Steps 2 and 3 are no-ops
that say so. Step 3b finds no card and asks once. The user answers "invoicing
and dunning for the booking platform, channel #billing, repo
northwind/billing-api, tracker BIL, I own it as @rimuru". The proposed file
is shown in full before any write:

```markdown
# billing-api card

## Scope

Invoicing and dunning for the booking platform.

## Owns

- channel: #billing
- repo: northwind/billing-api
- tracker: BIL

## People

- @rimuru -- owner
```

Run again in `C:/GitHub/harbor`, where a card exists: Step 3b says so and
touches nothing. It never shows the existing card's content back for
confirmation and never offers to rewrite it.
