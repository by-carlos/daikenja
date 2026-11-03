# Fixture: a two-repository ledger tracking sources

Synthetic. Invented project, invented people, `example.com` links only. Nothing
here comes from real work content, and no path below exists on any machine.

Exercises `docs/open-format.md` § Section: Sources and § `Blocked by:`, and
`docs/config-resolution.md` § Reading several repositories, against
`project-sources`, `project-summary`, `project-gaps`, `project-catchup` and
`project-log`. The project is `meridian`, a compliance programme tracked almost
entirely from documents other teams own -- a wiki, a ticket system and a chat
space -- which is the situation the Sources section exists for. It spans **two
repositories**, the smallest case that tells reading every repository's
`DECISIONS.md` apart from reading only the first.

The walks are run by hand; this repo has no test runner. **Every walk assumes
today is 2026-09-15**, and takes "what the connectors report" from the table
below rather than from any live system.

Six things this fixture exists to pin down:

1. A source with **every field present** (the exemption register), read and
   reported cleanly.
2. A source with **no `modified:`** (the audit epic) -- no baseline, so a check
   can say when it was read, never whether it moved. It is neither "moved" nor
   "unchanged".
3. A source that **moved since its recorded read** (the standards page): the
   reported value differs from the stored one. The comparison is for
   difference, not date arithmetic -- the control mapping sheet pins that with
   a revision number instead of a timestamp.
4. A field line is a **continuation line**: skills that know nothing about
   sources (`project-gaps`, `project-decisions`) must read this file without
   reporting a single malformed line.
5. **Both repositories' `DECISIONS.md` are read**, each entry named with the
   repository it came from, whichever directory the run starts in.
6. **One `Blocked by:` item names an item still open, and another names an item
   no longer in the file**, so `project-gaps` has both annotations to make.

The escalations channel names a system no connector serves, so the
reduced-behaviour path has something to report.

Depends on: open-format.md "Section: Sources", open-format.md "`Blocked by:`", config-resolution.md "Reading several repositories", project-sources "Step 3: check each source", project-summary "Step 3: build the overview", project-gaps "Step 3: filter", project-gaps "Step 4: report", project-catchup "Step 3: compute the delta", project-log-reference.md "Record a source"

---

## The configuration

```yaml
projects:
  meridian:
    paths:
      - C:/GitHub/meridian-controls
      - C:/GitHub/meridian-services
```

Home is `meridian-controls`, the first path, so `open.md` lives there.

## The files these walks read

`C:/GitHub/meridian-controls/DECISIONS.md`:

~~~markdown
<!-- decisions-format: 1 -->
# Decisions

## Tracking

Paths: `.`

- **Track the programme from the board's own documents, not a mirror of
  them.** — a mirror goes stale the day the board edits a page. Revisit: if
  the board stops publishing. Source: https://example.com/portal
~~~

`C:/GitHub/meridian-services/DECISIONS.md`:

~~~markdown
<!-- decisions-format: 1 -->
# Decisions

## Controls

Paths: `services/`

- **Every control maps to a wiki page owned by the compliance board.** —
  imposed by the compliance board. Revisit: never. Source:
  https://example.com/wiki/standards
~~~

`C:/GitHub/meridian-controls/.daikenja/open.md`:

~~~markdown
<!-- daikenja-open-format: 1 -->
# meridian open items

## Open items

- 2026-08-21 -- @unassigned -- Agree who reconciles the control list when the standards page changes.
- 2026-08-25 -- @asahi -- Blocked by: who reconciles the control list. Publish the reconciliation schedule.
- 2026-09-08 -- @kaito -- Blocked by: the exemption renewal sign-off. Move the ingest service onto the new control set.

## Context links

- Board portal -- https://example.com/portal

## Sources

- Escalations channel -- https://example-chat.example.com/rooms/meridian-esc
  read: 2026-09-01
  covers: live exceptions and who approved them.
- Control mapping sheet -- https://example.com/sheets/controls
  modified: revision 37
  read: 2026-09-02
  covers: which control maps to which service.
- Standards page -- https://example.com/wiki/standards
  modified: 2026-08-28T09:12Z
  read: 2026-08-28
  covers: the mandatory controls and their wording.
  does not answer: rollout timing; the page scopes controls, not schedules.
- Audit epic -- https://example.com/tickets/EPIC-88
  read: 2026-09-05
  covers: audit findings and their owners.
- Exemption register -- https://example.com/wiki/exemptions
  modified: 2026-09-10T15:40Z
  read: 2026-09-11
  covers: which services hold an exemption and until when.
  does not answer: why an exemption was granted; the register records outcomes only.
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

- **`Ledger:` line** names all three files: both `DECISIONS.md` and the one
  `open.md` in `meridian-controls`.
- **Moved (2):** the standards page -- stored `2026-08-28T09:12Z`, now
  `2026-09-14T08:55Z`; the control mapping sheet -- stored `revision 37`, now
  `revision 41`. The second is the non-timestamp case: the values differ, so it
  moved, and no date arithmetic was possible or needed.
- **No baseline (1):** the audit epic -- read 2026-09-05, no `modified:`
  stored. Its system also reports nothing usable now, so even a recorded
  re-read today would still leave it without a baseline; the report says the
  value is unknown and never substitutes a fetch date.
- **Could not check (1):** the escalations channel -- one line naming the
  missing connector. The run continues; nothing hard-stops.
- **Unchanged (1):** the exemption register -- stored and reported values
  identical. A count is enough.
- Sources are named by label; no `S-nnn` appears anywhere. The offer to record
  a refresh covers only sources actually re-read in the session, and routes
  through `project-log`, which writes `open.md` in one approved batch.

## What `project-summary` must report

- **Decisions in force (2)**, grouped by repository: "Track the programme from
  the board's own documents" under `meridian-controls` -- Tracking, and "Every
  control maps to a wiki page owned by the compliance board" under
  `meridian-services` -- Controls, reported as imposed by the board. Run from
  `C:/GitHub/meridian-services`, the summary still opens with the same `Ledger:`
  line and reads `open.md` from `meridian-controls`.
- **Open items (3)**, each with owner and date raised; the two `Blocked by:`
  prefixes are kept as text.
- All five sources -- label, target, `read:` date -- and no staleness: it
  queries nothing.

**The failure this catches:** a summary that shows one decision -- whichever
repository the run started in -- because only one `DECISIONS.md` was read.

## What `project-gaps` must report

The default 21-day threshold applies (no override on the project).
2026-09-15 minus 2026-08-21 is 25 days, so the unowned item is also stale;
2026-09-15 minus 2026-08-25 is 21 days, which is **not greater than** 21, so
the reconciliation schedule is not stale.

```
Gaps in meridian (stale_after_days: 21) -- ownership and staleness, not severity

Unowned (1)
- Agree who reconciles the control list when the standards page changes -- 2026-08-21 (25 days)

Stale (1, older than 21 days)
- Agree who reconciles the control list when the standards page changes -- 2026-08-21 (25 days, also unowned)
```

- The reconciliation schedule is **not reported**: owned, and 21 days is not
  past the threshold. Its `Blocked by:` does not make it a gap.
- The ingest-service item is not reported either (owned, 7 days).

**Variant: `stale_after_days: 5` on the project.** Both blocked items are now
stale, and each gets its annotation:

```
Stale (3, older than 5 days)
- Agree who reconciles the control list when the standards page changes -- 2026-08-21 (25 days, also unowned)
- Publish the reconciliation schedule -- 2026-08-25 (21 days)
  -- blocked by who reconciles the control list (still open, since 2026-08-21)
- Move the ingest service onto the new control set -- 2026-09-08 (7 days)
  -- "Move the ingest service onto the new control set" is blocked by "the exemption renewal sign-off", which names an item no longer open.
```

- The first blocker matches the unowned item by its words; the second matches
  no line in `## Open items`, so it was closed.
- Nothing about sources, and no source field line reported as malformed.
- Both `DECISIONS.md` are read (Step 2) and contribute no gap.

## What the other skills must do with these files

- **`project-catchup`** with `last_checkpoint` SHAs for both repositories
  reports changes per repository from `git log <sha>..HEAD -- DECISIONS.md
  .daikenja/open.md`; `meridian-services` has no `open.md`, so only its
  `DECISIONS.md` can change there.
- **`project-log`** recording a new source writes a head line with no ID,
  directly under `## Sources`.

## Variant: a newer format version

Change the first line of `C:/GitHub/meridian-services/DECISIONS.md` to
`<!-- decisions-format: 2 -->`. Every read skill above still reads the file and
reports the same result, with exactly one line, once per run:

```
C:/GitHub/meridian-services/DECISIONS.md was written by a newer format (version 2); update the Daikenja plugin.
```

`project-list` does not open either file, so it prints no warning.
