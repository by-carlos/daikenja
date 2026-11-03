# Fixture: blocks and imposed decisions

Synthetic. Invented project, invented people, `example.com` links only. Nothing
here comes from real work content, and no path below exists on any machine.

Exercises the two relationships the ledger still records -- a `Blocked by:`
prefix between open items, and an imposed decision's origin in its why clause
-- against `project-decisions`, `project-gaps` and `project-log`. The project
is `lattice`, an API gateway built by one team inside a larger programme run by
other teams, which is the situation both exist for: some of its decisions were
made by the team and some were handed to it.

The walks are run by hand; this repo has no test runner. **Every walk assumes
today is 2026-09-15 and `stale_after_days` is 21** -- the profile's value, with
no override on this project -- so the staleness arithmetic below is fixed rather
than drifting with the calendar.

Four things this fixture exists to pin down:

1. An imposed decision says so in its why clause, carries no owner, and is never
   a gap.
2. A `Blocked by:` prefix, including one naming an item that is no longer in the
   file -- which nothing rewrites.
3. A contradiction is never recorded: an open item a new decision settles is
   closed in the same batch, or the user is asked.
4. A relationship is written only where the material states it.

Depends on: open-format.md "`Blocked by:`", open-format.md "Closing an item", open-format.md "Writing", decisions-format.md "Shape", project-decisions "Step 5: surface relationships and origin", project-gaps "Step 3: filter", project-log "Check for duplicates first", project-log-reference.md "Record a relationship only where the source says so", project-log-reference.md "Mark a decision that was imposed"

---

## The files these walks read

`C:/GitHub/lattice/DECISIONS.md`:

~~~markdown
<!-- decisions-format: 1 -->
# Decisions

Decisions in force. Read the area that covers a path before changing it; add
or edit an entry in the same pull request when a change settles something
future work must respect.

## Gateway

Paths: `gateway/`

- **The gateway fronts the reporting API as well as the ingest API.** — the
  reporting team has no other edge. Revisit: if reporting gets its own edge.
  Source: https://example.com/lattice/thread/31
- **The rate limiter ships as middleware, not a sidecar.** — a sidecar needs a
  second deploy per release, and that cost lands on every team. Revisit: never.
  Source: https://example.com/lattice/thread/27

## Security

Paths: `certs/`, `infra/audit/`

- **Every service writes to the shared audit log within 30 days of
  onboarding.** — imposed by the programme's architecture board. Revisit: if
  the board grants an exemption. Source: https://example.com/lattice/standards
~~~

`C:/GitHub/lattice/.daikenja/open.md`:

~~~markdown
<!-- daikenja-open-format: 1 -->
# lattice open items

## Open items

- 2026-09-08 -- @shuna -- Blocked by: the exemption criteria in writing. Draft the audit-log retention note for the tenant handbook.
- 2026-08-22 -- @gobta -- Blocked by: which programme forum publishes the standards. Publish the exemption request to the architecture board.
- 2026-08-21 -- @shion -- Decide whether health-check traffic can stay out of the shared audit log.
- 2026-08-19 -- @souei -- Blocked by: the exemption criteria in writing. Size the audit-log volume the reporting API will add.
- 2026-08-17 -- @unassigned -- Get the architecture board's exemption criteria in writing.
- 2026-08-02 -- @gabiru -- Decide the rate-limit thresholds per tenant.
- 2026-06-02 -- @unassigned -- Decide whether the gateway can use long-lived client certificates.

## Context links

- Programme standards page -- https://example.com/lattice/standards
- Exemption request template -- https://example.com/lattice/exemption-template

## Sources
~~~

`@gobta`'s prefix names an item that is not in the file: it was closed by
deleting its line, which is what git shows for it. That is the deliberate
case for the "no longer open" reading, not a defect.

---

## Walk 1: an imposed decision, found by its subject

User message:

> What did we decide about audit logging?

Expected: the `Security` entry on the shared audit log matches. The reply must
say it was **imposed**, and by whom -- its why clause names the architecture
board -- because that changes the response from "revisit it" to "comply, seek
an exemption, or escalate". It names the repository it came from.

Must not happen:

- Reporting a missing owner. `DECISIONS.md` entries have none.
- Saying that the health-check item contradicts this decision as if that were
  recorded. Nothing in either file links them; the item is a question in its
  own words.

## Walk 2: the audit

User message:

> What's still open on lattice?

Expected, with today 2026-09-15 and a 21-day threshold, in `project-gaps`'
report shape (its Step 4), the closed blocker in `reading.md` § Notices,
shared wording:

```
Gaps in lattice (stale_after_days: 21, using the profile default) -- ownership and staleness, not severity

Unowned (2)
- Decide whether the gateway can use long-lived client certificates -- 2026-06-02 (105 days, also stale)
- Get the architecture board's exemption criteria in writing -- 2026-08-17 (29 days, also stale)

Stale (6, older than 21 days)
- Decide whether the gateway can use long-lived client certificates -- 2026-06-02 (105 days, also unowned)
- Decide the rate-limit thresholds per tenant -- 2026-08-02 (44 days)
- Get the architecture board's exemption criteria in writing -- 2026-08-17 (29 days, also unowned)
- Size the audit-log volume the reporting API will add -- 2026-08-19 (27 days)
  -- blocked by the exemption criteria in writing (still open, since 2026-08-17)
- Decide whether health-check traffic can stay out of the shared audit log -- 2026-08-21 (25 days)
- Publish the exemption request to the architecture board -- 2026-08-22 (24 days)
  -- "Publish the exemption request to the architecture board" is blocked by "which programme forum publishes the standards", which names an item no longer open.
```

Four things this walk fixes:

- **`@shuna`'s item is not reported at all**, even though it is blocked by an
  open, unowned item. It is owned and seven days old, so it fails both
  conditions. Being blocked is not a gap -- the prefix changes the report,
  never the filter.
- **`@gobta`'s blocker is no longer in the file**, so the line says it is no
  longer open. That is the most useful thing the annotation produces: the item
  is not waiting on anything any more and is still sitting.
- **No decision appears anywhere in this report**, including the imposed one.
  The scope is Open items.
- **No ID appears.** Items are named by their words.

Must not happen: an "unowned decision" section, `@shuna`'s item reported for
being blocked, or a blocker's own blockers chased.

## Walk 3: writing a block the user states

User message:

> Log an open item: we can't turn on the shared ingress until the exemption
> criteria land. Owner @souei.

Expected: the same-turn dictated path. The user stated the block and named an
item that is in the file, so the prefix is byte-determined. The written line,
shown afterwards under its file:

```
- 2026-09-15 -- @souei -- Blocked by: the exemption criteria in writing. Turn on the shared ingress.
```

The exemption-criteria item is **not** edited. Nothing is written on the other
end of the block.

Must not happen: a prefix on the named item, a proposal step, or a prefix that
names the item in words matching no line.

## Walk 4: a block the material only implies

User message:

> Log an open item to size the ingress capacity. Feels like it's the same
> dependency as the audit-log work.

Expected: propose-then-wait, and the proposal contains the item **without** a
prefix, plus one line in "Questions before I write" asking whether it is
blocked by getting the exemption criteria in writing, and saying why the run
did not assume it. "Feels like the same dependency" is the user thinking aloud.

Must not happen: a `Blocked by:` written on the strength of that sentence.

## Walk 5: an imposed decision arrives

User message:

> Log that the programme's architecture board has mandated mutual TLS between
> all internal services from 2026-10-01. Nothing we can do about it.

Expected: propose-then-wait, because the revisit condition is not stated. The
proposal places it in `Security` and carries the origin in the why clause:

```
C:/GitHub/lattice/DECISIONS.md
  ## Security
  + - **Mutual TLS between all internal services from 2026-10-01.** — imposed
      by the programme's architecture board. Revisit: <asked below>.

Questions before I write:
- What would reopen the mutual-TLS mandate -- or is it "never"?
- Nobody on this side owns the response to the mandate yet. Raise an open item
  for it, and who owns it?
```

Must not happen: an `Imposed.` marker, an owner on the entry, an open item
written without being asked for, or the decision attributed to whoever relayed
it.

## Walk 6: a decision that settles an open item

User message:

> The programme's security baseline says client certificates rotate every 90
> days, run by their tooling, and that's final. Log it.

Expected: the duplicate check finds the long-lived certificates item, which
this decision answers. One batch proposes both the entry and the item's
deletion, so the contradiction never exists in the files:

```
C:/GitHub/lattice/DECISIONS.md
  ## Security
  + - **Client certificates rotate every 90 days, run by the programme's
      tooling.** — imposed by the programme's security baseline. Revisit:
      never.

C:/GitHub/lattice/.daikenja/open.md
  Open items
  - - 2026-06-02 -- @unassigned -- Decide whether the gateway can use long-lived client certificates.
```

"That's final" is the revisit condition: never. Must not happen: writing the
decision and leaving the item open, recording that the two contradict, or
deleting the item without showing it in the proposal.

## Walk 7: a block naming an item that is not there

User message, after Walk 3:

> Add to that last one that it's also blocked by the vendor contract review.

Expected: no item in `open.md` matches "the vendor contract review", so the
prefix is **not** written. One line asking which item was meant.

Must not happen: writing the prefix anyway, creating an item to make it match,
or silently dropping the request.

## Walk 8: closing a blocker

User message:

> The board published the exemption criteria. Close that item.

Expected: the user named the item, so the same-turn path deletes the
exemption-criteria line and shows it. Beside it, an **offer** to drop
`Blocked by: the exemption criteria in writing.` from the items that carry it
-- `@souei`'s and `@shuna`'s, and Walk 3's if it ran -- listed line by line.
Those edits are not dictated, so they wait for a yes. Had the closing come from
a pasted thread, the deletion and the offered edits would be one proposal.

Must not happen: dropping the prefixes without a yes, or leaving them
unmentioned. A prefix left in place is still correct: readers then say it
names an item that is no longer open, as `@gobta`'s does.
