# Fixture: a ledger tracking sources

Synthetic. Invented project, invented people, `example.com` links only. Nothing
here comes from real work content, and no path below exists on any machine.

Exercises `docs/ledger-format.md` § Section: Sources against `project-sources`,
`project-summary`, `project-catchup` and `project-log`. The project is
`meridian`, a compliance programme tracked almost entirely from documents other
teams own -- a wiki, a ticket system and a chat space -- which is the situation
the section exists for.

The walks are run by hand; this repo has no test runner. **Every walk assumes
today is 2026-09-15**, and takes "what the connectors report" from the table
below rather than from any live system.

The fourth required case -- **a ledger with no Sources section at all** -- is
covered by `sample-ledger.md`, which predates the section: every read skill
must read it exactly as before, `project-summary` shows no Sources block for
it, and `project-sources` stops on the one-line notice naming
`/daikenja:project-log`.

Four things this fixture exists to pin down:

1. A source with **every field present** (`S-001`), read and reported cleanly.
2. A source with **no `modified:`** (`S-002`) -- no baseline, so a check can
   say when it was read, never whether it moved. It is neither "moved" nor
   "unchanged".
3. A source that **moved since its recorded read** (`S-003`): the reported
   value differs from the stored one. The comparison is for difference, not
   date arithmetic -- `S-004` pins that with a revision number instead of a
   timestamp.
4. A field line is a **continuation line**: skills that know nothing about
   sources (`project-gaps`, `project-decisions`) must read this file without
   reporting a single malformed line.

`S-005` names a system no connector serves, so the reduced-behaviour path has
something to report.

Depends on: ledger-format.md "Section: Sources", project-sources "Step 3: check each source", project-summary "Step 3: build the overview", project-catchup "Step 3: compute the delta", project-log-reference.md "Record a source"

---

## The ledger these walks read

~~~markdown
# meridian ledger

## Decisions

- 2026-08-20 -- D-002 -- @unassigned -- Imposed. Published by the compliance board. Every control maps to a wiki page owned by the board.
- 2026-08-12 -- D-001 -- @asahi -- Track the programme from the board's own documents rather than mirroring them.

## Open items

- [ ] 2026-08-21 -- O-001 -- @unassigned -- Agree who reconciles the control list when the standards page changes.

## Context links

- Board portal -- https://example.com/portal

## Sources

- S-005 -- Escalations channel -- https://example-chat.example.com/rooms/meridian-esc
  read: 2026-09-01
  covers: live exceptions and who approved them.
- S-004 -- Control mapping sheet -- https://example.com/sheets/controls
  modified: revision 37
  read: 2026-09-02
  covers: which control maps to which service.
- S-003 -- Standards page -- https://example.com/wiki/standards
  modified: 2026-08-28T09:12Z
  read: 2026-08-28
  covers: the mandatory controls and their wording.
  does not answer: rollout timing; the page scopes controls, not schedules.
- S-002 -- Audit epic -- https://example.com/tickets/EPIC-88
  read: 2026-09-05
  covers: audit findings and their owners.
- S-001 -- Exemption register -- https://example.com/wiki/exemptions
  modified: 2026-09-10T15:40Z
  read: 2026-09-11
  covers: which services hold an exemption and until when.
  does not answer: why an exemption was granted; the register records outcomes only.

## Changelog

- 2026-09-11T16:02Z -- project-log via project-sources -- ~S-001
- 2026-09-05T10:30Z -- project-log -- +S-004..S-005
- 2026-08-28T11:20Z -- project-log -- +S-001..S-003, +O-001
- 2026-08-20T09:00Z -- project-log -- +D-002, +link "Board portal"
- 2026-08-12T14:00Z -- project-log -- +D-001
~~~

## What the connectors report on 2026-09-15

The walk substitutes this table for the live systems. `example-chat` has no
connector in the session at all.

| Target | Reported now |
|---|---|
| https://example.com/wiki/exemptions | `2026-09-10T15:40Z` |
| https://example.com/tickets/EPIC-88 | nothing usable -- the system reports no last-modified |
| https://example.com/wiki/standards | `2026-09-14T08:55Z` |
| https://example.com/sheets/controls | `revision 41` |
| https://example-chat.example.com/rooms/meridian-esc | not reachable -- no connector |

## What `project-sources` must report

- **Moved (2):** the standards page (S-003) -- stored `2026-08-28T09:12Z`, now
  `2026-09-14T08:55Z`; the control mapping sheet (S-004) -- stored
  `revision 37`, now `revision 41`. The second is the non-timestamp case: the
  values differ, so it moved, and no date arithmetic was possible or needed.
- **No baseline (1):** the audit epic (S-002) -- read 2026-09-05, no
  `modified:` stored. Its system also reports nothing usable now, so even a
  recorded re-read today would still leave it without a baseline; the report
  says the value is unknown and never substitutes a fetch date.
- **Could not check (1):** the escalations channel (S-005) -- one line naming
  the missing connector. The run continues; nothing hard-stops.
- **Unchanged (1):** the exemption register (S-001) -- stored and reported
  values identical. A count is enough.
- The offer to record a refresh covers only sources actually re-read in the
  session, and routes through `project-log` (`~S-nnn`, writer
  `project-log via project-sources`, as the Changelog's top line shows a
  previous run already did).

## What the other skills must do with this file

- **`project-summary`** lists all five sources -- label, target, `read:` date
  -- and reports no staleness: it queries nothing.
- **`project-catchup`** on a checkpoint of `2026-09-01T00:00Z` reports a
  delta of exactly three changes: `+S-004..S-005` expanded to two additions,
  and `~S-001` resolved to the exemption register's current head line. The
  2026-08-28 line (`+S-001..S-003, +O-001`) is older than the checkpoint and
  contributes nothing.
- **`project-gaps`** reports the unowned open item (O-001) and nothing about
  sources -- a stale source is not a gap, and no source field line is reported
  as malformed.
- **`project-log`** allocating the next source ID reads `S-005` as the highest
  ever used and proposes `S-006`.
