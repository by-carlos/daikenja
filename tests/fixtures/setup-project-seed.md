# Fixture: setup-project registration and seeding

Synthetic. Invented project, invented people, `example.com` links only. Nothing
here comes from real work content, and no path below exists on any machine.

Exercises `setup-project` in three walks against one starting state: a first
registration, a re-registration of the same path, and a seed run whose proposed
entries are partially rejected. The seed sources deliberately include a decision
register the project already keeps, a source with no recoverable date, a
proposal nobody agreed to, a standing policy that reads like one of the project
decisions without being the same fact, and a source no connector can reach.

---

## The starting `daikenja.yaml`

Copy this to `~/.claude/daikenja/daikenja.yaml` for the walk, or hold it in the
conversation. One project is already registered and it is not this one.

```yaml
profile:
  name: Carlos
  role: Solutions Architect
  tone: standard
  writing_style: ./writing-style.md
  personas: ./personas.md
  stale_after_days: 21

projects:
  beacon:
    path: C:/GitHub/beacon
    last_checkpoint: 2026-08-15T09:00Z
```

## The project on disk

The walk runs from `C:/GitHub/quill-gateway`. It is a git repository, it has no
`.daikenja/` directory, and it already keeps its own decision records:

```
C:/GitHub/quill-gateway
  .git/
  README.md
  docs/
    adr/
      0001-gateway-replaces-edge-proxy.md
      0002-tls-terminates-at-the-gateway.md
      0003-schema-changes-go-through-the-pipeline.md
      0004-tls-terminates-at-the-load-balancer.md
    open-questions.md
  src/
```

Note the directory name is `quill-gateway`. Walk A registers it under a key the
user chooses instead, which is what Walk B then has to leave alone.

---

## Walk A -- first registration

No `projects:` entry matches `C:/GitHub/quill-gateway`, so a new one is
proposed. The user answers the key question and the per-project keys:

> **Key?** Call it `gateway`, not `quill-gateway`.
>
> **`ledger`?** Skip it.
>
> **`stale_after_days`?** 30 for this one.
>
> **`norms_doc`?** `https://example.com/quill/ways-of-working`

Then declines seeding for now:

> Not yet, I will seed it later.

## Walk B -- re-registration of the same path

Run again from `C:/GitHub/quill-gateway`, with Walk A's write in place. Nothing
about the directory has changed. The user says only:

> I want to seed it now.

The registration step has nothing to do, and the run is here for Step 4 alone.

---

## The seed sources

The user names these when Walk C asks, one category at a time.

### Source 1 -- the decision records in `docs/adr/`

Four records. `ADR-0004` supersedes `ADR-0002`. The bodies below are the whole
of what each record's summary says; the detail stays in the record.

| Record | Date decided | Owner | Summary |
|---|---|---|---|
| `ADR-0001` | 2026-05-04 | priya | The Quill gateway replaces the edge proxy. No dual-run period. |
| `ADR-0002` | 2026-05-19 | carlos | TLS terminates at the gateway. |
| `ADR-0003` | 2026-06-08 | priya | Schema changes reach production through the migration pipeline, never a hand-run script. |
| `ADR-0004` | 2026-07-13 | carlos | TLS terminates at the load balancer instead. Supersedes `ADR-0002`. |

Index at `https://example.com/quill/adr`.

### Source 2 -- the question register at `docs/open-questions.md`

Three numbered questions. One is already answered and closed.

| Question | Date raised | Owner | Status | Summary |
|---|---|---|---|---|
| `Q-01` | 2026-05-21 | sam | open | Who owns gateway certificate rotation after cutover? |
| `Q-02` | 2026-06-02 | (nobody named) | open | Agree what "gateway is done" means before the next planning round. |
| `Q-03` | 2026-06-30 | priya | closed 2026-07-13 | Where does TLS terminate? Answered by `ADR-0004`. |

### Source 3 -- a pasted Slack excerpt from `#quill-gateway`

Pasted, not linked, so it carries no URL.

> **sam** (2026-08-11) -- We agreed on the call this morning to hold the
> gateway cutover until the certificate rotation runbook exists. Nobody
> objected.
>
> **jordan** (2026-08-11) -- We could also move the whole thing behind a
> feature flag while we are at it. Just an idea, I have not thought it
> through.
>
> **priya** -- Somebody still needs to work out what happens to in-flight
> connections during the switch. I do not remember when that first came up.

Three candidates, and they are not the same kind. One is a decision. One is a
suggestion nobody agreed to. One is a real open item whose date is nowhere in
the material and which the user, when asked, cannot pin down either.

### Source 4 -- a Confluence space nobody can reach

> The gateway design space is at
> `https://example.com/wiki/spaces/QUILL/gateway-design`. Pull the decisions
> out of that too.

Walk this with no Confluence connector in the session.

### Source 5 -- a standing team rule the user pastes

Offered unprompted while the documents are being named:

> One more thing that should be in there. Quill's standing rule, it predates
> this project and holds across all of them: nothing is ever run by hand
> against production, whatever it is.

Same subject as `ADR-0003`, different kind. Merging the two loses which one a
later reader is bound by.

---

## Walk C -- seeding, partially rejected

Continues from Walk B. The user's replies to the tranches, in order:

**Decisions tranche.**

> Yes to all of them except the old TLS one -- I do not want the superseded
> call in there at all, just the current one.

That is a rejection with a consequence the run has to say out loud rather than
quietly absorb: a supersession is recorded on both entries, so approving
`ADR-0004` while dropping `ADR-0002` leaves a body claiming `Supersedes` with
nothing to point at. The run has to put the choice back to the user -- keep
both, or write the surviving decision without the `Supersedes` clause -- and
write neither until it is answered.

**Open items tranche.**

The user replies about something else entirely:

> By the way, can you also check whether the beacon ledger still has that
> schema freeze in it?

Nothing here approves anything. The next thing the run says has to restate what
is still unwritten before proposing anything further.

Then, once asked again:

> Yes to those, except drop the in-flight connections one -- I really cannot
> tell you when that was raised.

**Context links tranche.**

> No links, I will add those myself later.

## What the fixture is built to catch

Walked by hand, since this repo has no test runner. The seed run has to reach
the end of Walk C having written, through `project-log` and nothing else:

1. Nothing at all until a tranche is approved, and nothing from the tranche the
   user replied around.
2. No entry for jordan's feature-flag idea, which nobody agreed to.
3. No entry for priya's in-flight connections item, because no date for it
   exists in the material or in the user's head, and no date may be invented.
4. `Q-03` recorded as a resolved open item rather than a decision, with the
   decision that answered it named.
5. `ADR-0003` and the standing rule in Source 5 kept as two entries, not merged
   into one, even though both are about running things by hand.
6. Every entry dated when it was decided or raised, which makes most of them
   older than this project's 30-day staleness threshold on the day they land.
   The run has to say so before the user runs `/daikenja:project-gaps` and
   finds it out.
