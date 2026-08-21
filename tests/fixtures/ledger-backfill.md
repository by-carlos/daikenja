# Fixture: recording an existing project in bulk

Synthetic. Invented project, invented people, `example.com` links only. Nothing
here comes from real work content, and no path below exists on any machine.

Exercises the four backfill rules in `docs/ledger-format.md` against one
starting ledger, in three walks: a first bulk write of entries older than
everything already in the file, a second bulk write arriving three days later,
and a `project-catchup` run that has to expand what both of them wrote. It also
fixes what must *not* happen, because three of the four rules are only visible
when something is left alone.

The walks are run by hand -- this repo has no test runner. Walk 1 and Walk 2 are
`project-log` runs entered from `setup-project`; Walk 3 is `project-catchup`.

---

## The starting ledger

`C:/GitHub/lantern/.daikenja/ledger.md`. A project that has been logged
incrementally for a few weeks. Every entry's ID and date agree, because nothing
has ever been backfilled into it.

```markdown
# lantern ledger

## Decisions

- 2026-08-18 -- D-003 -- @shion -- Ship the lantern index behind a feature flag until the backfill completes.
- 2026-08-12 -- D-002 -- @unassigned -- Keep the v1 search endpoint alive for 60 days after cutover.
- 2026-08-04 -- D-001 -- @souei -- Lantern replaces the legacy search cluster.

## Open items

- [ ] 2026-08-17 -- O-002 -- @unassigned -- Decide who owns the flag flip.
- [ ] 2026-08-05 -- O-001 -- @gabiru -- Confirm the index rebuild window with ops.

## Context links

- Lantern runbook -- https://example.com/lantern/runbook

## Changelog

- 2026-08-18T09:05Z -- project-log -- +D-003
- 2026-08-17T14:20Z -- project-log -- +O-002
- 2026-08-12T10:00Z -- project-log -- +D-002
- 2026-08-05T08:40Z -- project-log -- +O-001
- 2026-08-04T16:30Z -- project-log -- +D-001
```

## The configuration for the walks

```yaml
daikenja_version: 0.5.1

profile:
  name: Carlos
  role: Solutions Architect
  tone: standard
  stale_after_days: 21

projects:
  lantern:
    path: C:/GitHub/lantern
    last_checkpoint: 2026-08-20T00:00Z
```

---

## Walk 1: the first bulk write

**When.** 2026-08-21, Changelog timestamp `2026-08-21T10:15Z`.

**The sources.** An architecture wiki holding four decisions, two of which carry
no date at all, and a spreadsheet of three open questions. Both are also
proposed as context links.

**What the user supplies when asked for the two missing dates.** "The fan-out
page went up in April 2026." and "That one I can only place in 2025 somewhere."
Nothing else about those two is recoverable.

### What gets written

```
Decisions -- new
- 2026-02-10 -- D-004 -- @souei -- Use one index per tenant, not a shared index with a tenant filter.
- 2025-11-03 -- D-005 -- @unassigned -- Buy the managed vector tier rather than self-hosting. [evaluation](https://example.com/lantern/vector-eval)
- 2026-04-01 -- D-006 -- @souei -- Approximate date. The wiki page recording this carries no date; it was created in April 2026. Cap query fan-out at 32 shards.
- 2025-01-01 -- D-007 -- @unassigned -- Approximate date. Placed in 2025 by @carlos; the wiki records no month. Lantern is an internal service, with no public API.

Open items -- new
- [ ] 2026-03-15 -- O-003 -- @gabiru -- Agree the acceptance criteria for search relevance.
- [ ] 2026-07-09 -- O-004 -- @unassigned -- Decide whether tenant indexes are rebuilt in place or side by side.
- [ ] 2025-12-08 -- O-005 -- @shion -- Decide whether per-tenant indexes need separate backups.

Context links -- new
- Architecture wiki -- https://example.com/lantern/wiki
- Search relevance sheet -- https://example.com/lantern/relevance

Changelog
- 2026-08-21T10:15Z -- project-log via setup-project -- +D-004..D-007, +O-003..O-005, +link "Architecture wiki",
  +link "Search relevance sheet"
```

### What the file looks like afterwards

```markdown
## Decisions

- 2026-08-18 -- D-003 -- @shion -- Ship the lantern index behind a feature flag until the backfill completes.
- 2026-08-12 -- D-002 -- @unassigned -- Keep the v1 search endpoint alive for 60 days after cutover.
- 2026-08-04 -- D-001 -- @souei -- Lantern replaces the legacy search cluster.
- 2026-04-01 -- D-006 -- @souei -- Approximate date. The wiki page recording this carries no date; it was created in April 2026. Cap query fan-out at 32 shards.
- 2026-02-10 -- D-004 -- @souei -- Use one index per tenant, not a shared index with a tenant filter.
- 2025-11-03 -- D-005 -- @unassigned -- Buy the managed vector tier rather than self-hosting. [evaluation](https://example.com/lantern/vector-eval)
- 2025-01-01 -- D-007 -- @unassigned -- Approximate date. Placed in 2025 by @carlos; the wiki records no month. Lantern is an internal service, with no public API.

## Open items

- [ ] 2026-08-17 -- O-002 -- @unassigned -- Decide who owns the flag flip.
- [ ] 2026-08-05 -- O-001 -- @gabiru -- Confirm the index rebuild window with ops.
- [ ] 2026-07-09 -- O-004 -- @unassigned -- Decide whether tenant indexes are rebuilt in place or side by side.
- [ ] 2026-03-15 -- O-003 -- @gabiru -- Agree the acceptance criteria for search relevance.
- [ ] 2025-12-08 -- O-005 -- @shion -- Decide whether per-tenant indexes need separate backups.
```

### What Walk 1 checks

1. **Insert position, not insert location.** The four new decisions sort into the
   file by date. None of them lands under the H2 heading, because none is newer
   than `D-003`. `D-006` goes above `D-004` because 2026-04-01 is above
   2026-02-10, not because it was proposed later.
2. **IDs are never bent to match dates.** They are allocated in proposal order
   -- `D-004` through `D-007` -- and the resulting section reads
   `D-003, D-002, D-001, D-006, D-004, D-005, D-007` top to bottom. That
   decorrelation is the expected outcome, not a defect to tidy.
3. **Approximate dates are marked and derived, never invented.** `D-006` and
   `D-007` open with `Approximate date.` and say where the date came from.
   "April 2026" normalized to `2026-04-01` and "2025 somewhere" to
   `2025-01-01`, and the proposal said so before the write.
4. **The Changelog line is compacted losslessly.** Two dense ranges plus a
   continuation line carrying the two context links. Expanded, it names nine
   changes.

### What must not happen in Walk 1

- **No renumbering.** Nothing reassigns `D-007` to `D-004` to make the oldest
  entry take the lowest number. The Changelog line already names these IDs.
- **No invented date.** If the user had said "no idea" to either question, that
  entry is dropped and named as dropped. `Approximate date.` never licenses
  picking one.
- **No sparse range.** Had the run touched only `D-004`, `D-005` and `D-007`,
  `+D-004..D-007` would be wrong -- it would claim a change to `D-006` that
  never happened. The correct summary is `+D-004..D-005, +D-007`.
- **Nothing else moves.** `D-001` through `D-003` and `O-001` through `O-002`
  are untouched, in the same order, byte for byte.

---

## Walk 2: a second bulk write, three days later

**When.** 2026-08-24, Changelog timestamp `2026-08-24T11:40Z`.

**The source.** An exported chat channel nobody had read when Walk 1 ran. It
holds two more decisions and one more open question, and one of its decisions
replaces `D-005`, which Walk 1 wrote.

### What gets written

```
Decisions -- new
- 2026-07-14 -- D-008 -- @souei -- Supersedes D-005. Self-host the vector tier after all -- the managed tier has no eu-central-1 region.
- 2026-01-01 -- D-009 -- @shion -- Approximate date. The channel export carries no timestamps before the platform migration; @shion placed this in January 2026. Retry a failed shard query once, then fail the whole request.

Decisions -- superseding D-005
- 2025-11-03 -- D-005 -- @unassigned -- Buy the managed vector tier rather than self-hosting. [evaluation](https://example.com/lantern/vector-eval) -> superseded by D-008

Open items -- new
- [ ] 2026-05-30 -- O-006 -- @unassigned -- Decide whether shard retries count against the tenant's query quota.

Changelog
- 2026-08-24T11:40Z -- project-log via setup-project -- +D-008..D-009, superseded D-005, +O-006
```

### What the Decisions section looks like afterwards

```markdown
- 2026-08-18 -- D-003 -- @shion -- Ship the lantern index behind a feature flag until the backfill completes.
- 2026-08-12 -- D-002 -- @unassigned -- Keep the v1 search endpoint alive for 60 days after cutover.
- 2026-08-04 -- D-001 -- @souei -- Lantern replaces the legacy search cluster.
- 2026-07-14 -- D-008 -- @souei -- Supersedes D-005. Self-host the vector tier after all -- the managed tier has no eu-central-1 region.
- 2026-04-01 -- D-006 -- @souei -- Approximate date. The wiki page recording this carries no date; it was created in April 2026. Cap query fan-out at 32 shards.
- 2026-02-10 -- D-004 -- @souei -- Use one index per tenant, not a shared index with a tenant filter.
- 2026-01-01 -- D-009 -- @shion -- Approximate date. The channel export carries no timestamps before the platform migration; @shion placed this in January 2026. Retry a failed shard query once, then fail the whole request.
- 2025-11-03 -- D-005 -- @unassigned -- Buy the managed vector tier rather than self-hosting. [evaluation](https://example.com/lantern/vector-eval) -> superseded by D-008
- 2025-01-01 -- D-007 -- @unassigned -- Approximate date. Placed in 2025 by @carlos; the wiki records no month. Lantern is an internal service, with no public API.
```

### What Walk 2 checks

1. **A second batch appends, it never renumbers.** `D-008` and `D-009` take the
   next two free IDs even though both are dated before four of the entries above
   them. This is the case that stalls a session that allocated Walk 1's IDs
   chronologically: renumbering here would leave Walk 1's Changelog line naming
   different content.
2. **Both batches interleave correctly.** `D-008` (2026-07-14) lands between
   `D-001` (2026-08-04) and `D-006` (2026-04-01), and `D-009` (2026-01-01)
   between `D-004` and `D-005`. The insert rule does not care which run wrote
   the neighbours.
3. **Supersession still marks both entries**, and `D-005` does not move. The
   tail is appended in place, per `ledger-format.md` § Section: Decisions.
4. **A short summary is not compacted.** `superseded D-005` and `+O-006` are
   written out. Only the two consecutive creations are ranged.

---

## Walk 3: `project-catchup` reads both bulk lines

**When.** 2026-08-25. `last_checkpoint` is `2026-08-20T00:00Z`, so both bulk
lines are inside the window and the five pre-existing lines are not.

### What the delta must contain

Joining the continuation line and expanding the two ranges yields **twelve
changes**, and every one of them is reported:

| From | Expands to |
|---|---|
| `+D-004..D-007` | `+D-004`, `+D-005`, `+D-006`, `+D-007` |
| `+O-003..O-005` | `+O-003`, `+O-004`, `+O-005` |
| `+link "Architecture wiki", +link "Search relevance sheet"` | both links, the second one read off the continuation line |
| `+D-008..D-009` | `+D-008`, `+D-009` |
| `superseded D-005` | `D-005`, which overrides its earlier `+` |
| `+O-006` | `+O-006` |

`D-005` appears under two verbs across the window. The most recent one wins, so
it is reported as superseded, not as new: six decisions changed in the window,
of which five are new.

Grouping consecutive IDs in the *report* is fine and reads better than ten
lines. Dropping any of them is not.

### What Walk 3 checks

- **A continuation line is joined before the summary is split on commas.** Read
  without joining, the delta silently loses the "Search relevance sheet" link
  and nothing says so.
- **A range is expanded, not reported as one change.** `+D-004..D-007` is four
  entries, and the report names four.
- **The most-recent-verb rule survives expansion.** The `+` for `D-005` comes
  from an expanded range and the `superseded` from a plainly written item; the
  later line still wins.
- **Staleness after a backfill.** A `project-gaps` run on the same day reports
  `O-003`, `O-004`, `O-005` and `O-006` as stale against `stale_after_days: 21`,
  because they are dated when they were raised -- every backfilled open item is
  stale on the first run. `O-001` (2026-08-05) is 20 days old and is not. That
  is the threshold working, and `setup-project` said it would happen before the
  seed.

### Malformed compactions, for the failure path

Neither of these is repaired or guessed at. `project-catchup` reports the line
and what is wrong with it, then continues with the rest of the delta.

```
- 2026-08-24T11:40Z -- project-log -- +D-009..D-004
- 2026-08-24T11:40Z -- project-log -- +D-004..O-006
```

The first runs backwards. The second names endpoints in two different sections.
