# Fixture: relationships and imposed decisions

Synthetic. Invented project, invented people, `example.com` links only. Nothing
here comes from real work content, and no path below exists on any machine.

Exercises `docs/ledger-format.md` § Body markers -- `Imposed.`, `Blocked by
<id>.` and `Contradicts <id>.` -- against `project-decisions`, `project-gaps`
and `project-log`. The project is `lattice`, an API gateway built by one team
inside a larger programme run by other teams, which is the situation the
markers exist for: some of its decisions were made by the team and some were
handed to it.

The walks are run by hand; this repo has no test runner. **Every walk assumes
today is 2026-09-15 and `stale_after_days` is 21** -- the profile's value, with
no override on this project -- so the staleness arithmetic below is fixed rather
than drifting with the calendar.

Four things this fixture exists to pin down:

1. A `Contradicts` marker on an open item pointing at a decision that is still
   in force, and found from **both** ends.
2. A `Blocked by` marker, including one whose blocker is already resolved --
   which nothing rewrites.
3. An imposed decision with **no owner**, which is never a gap.
4. A body containing `->` as ordinary punctuation, which must not parse as a
   tail. `D-009` is that line.

`D-004` carries a deliberate defect -- a marker naming an `O-014` this ledger
does not have -- so the report-and-continue path has something to report. It is
the only broken thing in the file; everything else is well formed.

Depends on: ledger-format.md "Body markers", ledger-format.md "Relationships between entries", ledger-format.md "A decision imposed from outside", project-decisions "Step 5: surface relationships and origin", project-gaps "Step 3: filter", project-log-reference.md "Record a relationship only where the source says so", project-log-reference.md "Mark a decision that was imposed"

---

## The ledger these walks read

~~~markdown
# lattice ledger

## Decisions

- 2026-08-20 -- D-010 -- @unassigned -- Imposed. Published by the programme's architecture board on its standards page. Every service writes to the shared audit log within 30 days of onboarding. [standards page](https://example.com/lattice/standards)
- 2026-08-18 -- D-009 -- @benimaru -- Ship the rate limiter as middleware, not a sidecar. A sidecar needs a second deploy per release -> that cost lands on every team, not just this one.
- 2026-08-12 -- D-008 -- @rimuru -- Supersedes D-005. The gateway fronts the reporting API as well as the ingest API.
- 2026-08-01 -- D-007 -- @unassigned -- Supersedes D-003. Imposed. Contradicts O-001. Approximate date. Taken from the programme's security baseline, which records no dates; that page was published in August 2026. Client certificates rotate every 90 days, run by the programme's own tooling.
- 2026-07-28 -- D-006 -- @shion -- Blocked by O-004. Move the gateway onto the shared ingress.
- 2026-07-15 -- D-005 -- @rimuru -- The gateway fronts the ingest API only. -> superseded by D-008
- 2026-06-20 -- D-004 -- @benimaru -- Blocked by O-014. Adopt the programme's shared error catalogue.
- 2026-06-10 -- D-003 -- @rimuru -- Client certificates are issued for a year and rotated by hand. -> superseded by D-007
- 2026-05-30 -- D-002 -- @unassigned -- Keep the legacy gateway online for 30 days after cutover.
- 2026-05-22 -- D-001 -- @benimaru -- Build the gateway as one service, not one deployment per tenant.

## Open items

- [ ] 2026-09-08 -- O-008 -- @shuna -- Blocked by O-004. Draft the audit-log retention note for the tenant handbook.
- [ ] 2026-08-22 -- O-007 -- @gobta -- Blocked by O-003. Publish the exemption request to the architecture board.
- [ ] 2026-08-21 -- O-006 -- @shion -- Contradicts D-010. Decide whether health-check traffic can stay out of the shared audit log.
- [ ] 2026-08-19 -- O-005 -- @souei -- Blocked by O-004. Size the audit-log volume the reporting API will add.
- [ ] 2026-08-17 -- O-004 -- @unassigned -- Get the architecture board's exemption criteria in writing.
- [x] 2026-08-14 -- O-003 -- @benimaru -- Confirm which programme forum publishes the standards. -> resolved 2026-08-16
- [ ] 2026-08-02 -- O-002 -- @gabiru -- Decide the rate-limit thresholds per tenant.
- [ ] 2026-06-02 -- O-001 -- @unassigned -- Decide whether the gateway can use long-lived client certificates.

## Context links

- Programme standards page -- https://example.com/lattice/standards
- Exemption request template -- https://example.com/lattice/exemption-template

## Changelog

- 2026-09-08T09:20Z -- project-log -- +O-008
- 2026-08-22T15:40Z -- project-log -- +O-007
- 2026-08-21T16:20Z -- project-log -- +D-010, +O-006, +link "Programme standards page"
- 2026-08-19T08:40Z -- project-log -- +O-005
- 2026-08-18T11:05Z -- project-log -- +D-009
- 2026-08-17T14:30Z -- project-log -- +O-004
- 2026-08-16T09:00Z -- project-log -- resolved O-003
- 2026-08-14T10:10Z -- project-log -- +O-003
- 2026-08-12T15:45Z -- project-log -- +D-007, +D-008, superseded D-003, superseded D-005, +link "Exemption request template"
- 2026-08-02T09:30Z -- project-log -- +O-002
- 2026-07-28T10:00Z -- project-log -- +D-006
- 2026-07-15T11:20Z -- project-log -- +D-005
- 2026-06-20T08:15Z -- project-log -- +D-004
- 2026-06-10T16:00Z -- project-log -- +D-003
- 2026-06-02T09:45Z -- project-log -- +O-001
- 2026-05-30T10:30Z -- project-log -- +D-002
- 2026-05-22T14:00Z -- project-log -- +D-001
~~~

`D-007` was written on 2026-08-12 and dated 2026-08-01, which is why its
Changelog line sits with `D-008` rather than at its own date. That is the
`Approximate date.` marker doing its job, not a defect.

---

## Walk 1: an imposed decision, found from its own end

User message:

> What did we decide about audit logging?

Expected: `D-010` matches. The reply must say it was **imposed**, and by whom
-- the prose after the marker names the architecture board -- because that
changes the response from "revisit it" to "comply, seek an exemption, or
escalate". The reverse scan must surface `O-006`, which carries `Contradicts
D-010.` and is invisible from `D-010`'s own line.

Must not happen:

- Reporting `D-010`'s `@unassigned` as a missing owner or a gap. Nobody on this
  side made it; that is the honest attribution.
- Silently dropping `Imposed.` as though it were part of the sentence that
  follows it.
- Walking on from `O-006` to whatever `O-006` relates to. One hop.

## Walk 2: every marker at once, and the chain behind it

User message:

> Show me D-007.

Expected: all four markers read correctly and in order -- it supersedes
`D-003`, it was imposed, it contradicts `O-001`, and its date is the user's
approximation with the derivation stated after it. The supersession chain is
walked to its end (`D-003`, which carries the matching tail), and `O-001` is
surfaced as a live open item that the imposed decision has effectively
overtaken.

This is the case the markers were added for: an open question of ours that a
decision from outside has already answered, sitting unresolved because nobody
noticed. Before markers existed both entries were true, unrelated as far as any
skill could tell, and the contradiction was only visible to a person reading the
whole file.

Must not happen: treating `Contradicts O-001.` as a supersession, resolving
`O-001`, or reading `Approximate date.` as anything other than body text.

## Walk 3: a body with an arrow in it

User message:

> What did we decide about the rate limiter?

Expected: `D-009` comes back as one decision, its body intact through the arrow
-- "A sidecar needs a second deploy per release -> that cost lands on every
team, not just this one." The last ` -> ` on that line is followed by "that
cost lands...", which matches neither `resolved <date>` nor `superseded by
D-nnn`, so it is body text.

This is the check that the marker convention cost the grammar nothing. The
tail forms are unchanged, so a line that parsed one way before parses that way
still. **A run that reports `D-009` as superseded, or truncates its body at the
arrow, has broken the tail rule** -- and would have broken it identically
before this fixture existed.

Must not happen: a tail, a truncation, or a "malformed line" report.

## Walk 4: a marker naming an entry that is not there

Any read of this ledger -- `project-decisions`, `project-gaps`,
`project-summary`.

Expected: one line reporting that `D-004` carries `Blocked by O-014.` and this
ledger has no `O-014`, then the run continues normally. Per
`docs/ledger-format.md` § Reading rules, rule 6: the line is well formed and
only the reference inside it is not, so rule 4 does not reach it.

Must not happen: rewriting `D-004`, guessing that `O-004` was meant -- it is one
character away and that is exactly why guessing is banned -- treating the whole
line as malformed, or failing the run.

## Walk 5: the audit

User message:

> What's still open on lattice?

Expected, with today 2026-09-15 and a 21-day threshold:

```
Gaps in lattice (stale_after_days: 21, using the profile default)

Unowned (2)
- Decide whether the gateway can use long-lived client certificates (O-001) -- 2026-06-02 (105 days, also stale)
- Get the architecture board's exemption criteria in writing (O-004) -- 2026-08-17 (29 days, also stale)

Stale (6, older than 21 days)
- Decide whether the gateway can use long-lived client certificates (O-001) -- 2026-06-02 (105 days, also unowned)
- Decide the rate-limit thresholds per tenant (O-002) -- 2026-08-02 (44 days)
- Get the architecture board's exemption criteria in writing (O-004) -- 2026-08-17 (29 days, also unowned)
- Size the audit-log volume the reporting API will add (O-005) -- 2026-08-19 (27 days) -- blocked by getting the exemption criteria in writing (O-004, still open)
- Decide whether health-check traffic can stay out of the shared audit log (O-006) -- 2026-08-21 (25 days)
- Publish the exemption request to the architecture board (O-007) -- 2026-08-22 (24 days) -- blocked by confirming which forum publishes the standards (O-003), which was resolved on 2026-08-16
```

`D-004`'s broken reference is reported alongside this, per walk 4 -- this skill
reads the whole file even though only Open items are in scope for the filter, so
it sees the marker and reading rule 6 applies to it here as anywhere else.

Four things this walk fixes:

- **`O-008` is not reported at all**, even though it carries `Blocked by
  O-004.` and its blocker is open and unowned. It is owned and seven days old,
  so it fails both conditions. Being blocked is not a gap and never becomes
  one -- the marker changes the report, never the filter.
- **`O-007`'s blocker is already resolved**, so the line says so. That is the
  most useful thing this annotation produces: the item is not waiting on
  anything any more and is still sitting.
- **`O-006`'s `Contradicts D-010.` is not annotated here.** A contradiction is
  a reconciliation somebody owes, not a reason an item sat;
  `project-decisions` is where it surfaces.
- **No decision appears anywhere in this report**, including the two imposed
  ones and the two unowned ones. The scope is Open items and the markers do not
  widen it.

Must not happen: an "unowned decision" section, `D-010` or `D-007` reported for
having no owner, `O-008` reported for being blocked, or a blocker's own
blockers chased.

## Walk 6: writing a relationship the user states

User message:

> Log an open item: we can't turn on the shared ingress until the exemption
> criteria land. That's blocked by O-004. Owner @souei.

Expected: the same-turn dictated path. The user named the relationship and the
ID resolves, so the marker is byte-determined and nothing has to be inferred.
The written line, shown verbatim afterwards:

```
- [ ] 2026-09-15 -- O-009 -- @souei -- Blocked by O-004. Turn on the shared ingress.
```

`O-004` is **not** edited. Nothing is written on the other end of the
relationship, and the Changelog line names one change: `+O-009`.

Must not happen: a marker on `O-004`, two Changelog verbs, or a proposal step
-- this one qualifies for the same-turn path on all four conditions.

## Walk 7: a relationship the material only implies

User message:

> Log an open item to size the ingress capacity. Feels like it's the same
> dependency as the audit-log work.

Expected: propose-then-wait, and the proposal contains the entry **without** a
marker, plus one line in "Questions before I write" asking whether it is
blocked by `O-004` and naming why the run did not assume it. "Feels like the
same dependency" is the user thinking aloud, not a stated relationship.

Must not happen: `Blocked by O-004.` written on the strength of that sentence.
A relationship nobody stated is a relationship nobody agreed to, and it reads
in the file exactly like one somebody did.

## Walk 8: an imposed decision arrives

User message:

> Log that the programme's architecture board has mandated mutual TLS between
> all internal services from 2026-10-01. Nothing we can do about it.

Expected: a decision opening `Imposed.` and naming the board, owner
`@unassigned`. Alongside it, **an offer** -- not an entry -- to raise the open
item for who on this side owns the response, because that is the part
`project-gaps` can audit and the material does not name anybody.

```
- 2026-09-15 -- D-011 -- @unassigned -- Imposed. Mandated by the programme's architecture board. Mutual TLS between all internal services from 2026-10-01.
```

Must not happen: an open item written without being asked for, `@unassigned`
reported as a problem, the decision attributed to whoever relayed it, or the
offer holding back a dictated write.

## Walk 9: a marker whose ID does not resolve

User message:

> Add to that last one that it's blocked by O-020.

Expected: the marker is **not** written. One line naming `O-020` and asking
which entry was meant, since this ledger's open items stop at `O-009`. The
alternative is writing `D-004`'s defect on purpose.

Must not happen: writing the marker anyway, creating an `O-020` to make the
reference valid, or silently dropping the request without saying so.
