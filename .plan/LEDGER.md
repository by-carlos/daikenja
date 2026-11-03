# Replace the ledger with DECISIONS.md, open.md and git history — build ledger

Statuses: `todo → doing → done`, plus `blocked` (waiting on a human or an
external gate — the stage becomes a runbook) and `skipped` (decided against,
one-line reason). Partial completion is a normal, resumable state.

Keep table rows to **ONE line** — detail goes in the notes block below, never
in a table cell. Sessions read the status table plus only the notes blocks of
the stages they `depend` on (the final review stage reads all of it). Update
your stage's row and notes block at the end of every session (Operating
protocol, finish protocol).

## Status

| Stage | Status | Verified | Date | Result |
|---|---|---|---|---|
| S0 Format specs and file templates | done | yes | 2026-11-03 | Shared spec copied byte-identical; open-format.md (199 lines) and both templates landed |
| S1 Config, resolution and reading contracts | done | yes | 2026-11-03 | Config, resolution, reading and card contracts moved to DECISIONS.md/open.md; D-21 amended |
| S2 project-log writes both files | todo | — | — | — |
| S3 Catchup and decisions read git history | todo | — | — | — |
| S4 Gaps, summary, list and sources skills | done | yes | 2026-11-03 | Four skills read DECISIONS.md/open.md; two-repo sources fixture walked |
| S5 Judgement, thread, meeting-review and other readers | doing | yes | 2026-11-03 | Readers moved to DECISIONS.md/open.md; DAIKENJA-PROJECT-DATA-UNREADABLE token for S7 |
| S6 setup-project registers git-backed projects only | todo | — | — | — |
| S7 Slack bot reports unreadable project data | todo | — | — | — |
| S8 Migration from the old ledger | todo | — | — | — |
| S9 User guide, README and retiring ledger-format.md | todo | — | — | — |
| SF Plan review | todo | — | — | — |

## Notes

As-built notes, acceptance evidence, gotchas, handoff notes, follow-ups. One
block per stage; sessions read only the blocks of their `depends` stages.

### S0 Format specs and file templates

As built — the shapes later stages consume (all in `docs/open-format.md`):

- **Open item line:** `- <YYYY-MM-DD> -- <@owner> -- <text>`, split on ` -- `
  at most twice; no checkbox, no ID. Date first, then owner (the old
  date/owner order with the ID dropped). `@unassigned` kept for `project-gaps`.
- **`Blocked by:` prefix:** opens the text, names the other item in words, runs
  to the first `. `/end of line. A prefix naming an item no longer in the file
  is read as "names an item no longer open" (it was closed). `project-log`
  offers to drop the prefix when it closes the named item.
- **Items are found by their words**; `project-log` asks on an ambiguous match.
  New items go under the heading; no skill depends on order.
- **Sections:** `## Open items`, `## Context links`, `## Sources` — all three
  required. Context link and source head lines are both `- <label> -- <target>`
  (split once); sources keep the four field lines (`modified:`, `read:`,
  `covers:`, `does not answer:`). Sources content otherwise untouched (#293).
- **Version rule (both files):** newer → readers warn once per run,
  `project-log` refuses the whole batch; **no version line → read as version 1,
  `project-log` adds it in its next approved write**; unparseable line →
  reported, read as 1. The no-line and unparseable cases are an addition beyond
  D-4's wording, needed for hand-made `DECISIONS.md` files.
- **Reading rules** carried over from `ledger-format.md` § Reading rules, minus
  the Changelog/ID/range rules; a missing H2 still reports and asks.
- `templates/open.md` has `{{PROJECT}}` in the H1; `templates/DECISIONS.md` has
  none (shared spec's H1 is `# Decisions`) and is copied as it stands.

Acceptance (run in `../daikenja-s0`):

```
$ cmp docs/decisions-format.md <scratch>/upstream-decisions-format.md
(exit 0, no output)
$ wc -l docs/decisions-format.md docs/open-format.md
  161 docs/decisions-format.md
  199 docs/open-format.md
$ head -n 1 docs/open-format.md templates/open.md templates/DECISIONS.md
==> docs/open-format.md <==
<!-- daikenja-open-format: 1 -->
==> templates/open.md <==
<!-- daikenja-open-format: 1 -->
==> templates/DECISIONS.md <==
<!-- decisions-format: 1 -->
$ python3 tests/check-invariants.py
All invariant checks passed.
```

Upstream fetched with `gh api repos/by-carlos/plan-staged-rollout/contents/skills/staged-rollout/references/decisions-format.md -H "Accept: application/vnd.github.raw"` on 2026-11-03.

Follow-ups (not this stage's): `docs/README.md` does not list the two new specs
yet — S9 (its step on the docs index). `templates/README.md`'s intro still says
`project-log` scaffolds "the ledger"; S9 retires `templates/ledger.md` and can
reword it then. `open-format.md` sits at 199 lines: any addition by a later
stage needs a matching cut to keep Done check 4.

Actuals: 2026-11-03T06:59:45.244Z → 2026-11-03T07:04:03.589Z · 4 min · tokens in=50 out=17740 cache_read=3136960 cache_write=118578 · subagents=0
Artifacts check: match

### S1 Config, resolution and reading contracts

As built — what S2 to S6 cite (all in `docs/config-resolution.md` unless named):

- **Renamed headings.** § Finding the ledger → **§ Finding `DECISIONS.md` and
  `open.md`** (anchor `#finding-decisionsmd-and-openmd`); § Resolving `ledger`
  is gone, replaced by **§ Reading several repositories** and **§ Legacy keys
  and unmigrated ledgers** (D-21). `reading.md` keeps its Step A0–D headings,
  so no skill's `Depends-on` citation of it moved.
- **Lookup:** `<path>/DECISIONS.md` for every path, in `paths` order, plus any
  `Moved:` file; `<home>/.daikenja/open.md`, home = first path; no match → the
  current directory is the one root. A missing file of the pair reads as empty;
  none existing → `No ledger yet in <home>. Run /daikenja:project-log to create one.`
- **`Ledger:` line** now lists every file read, absolute, a missing one marked
  `(not created yet)`. New notice shapes are in `reading.md` § Notices, shared
  wording (needs-migration ×2, leftover `ledger:`, newer format, `<file>, line <n>`).
- **Card** is `<home>/.daikenja/project.md`; the `<name>.project.md` form is
  gone (`project-card.md` § Location). S8 moves cards kept beside old ledgers.
- **`last_checkpoint`** (`config-schema.md` § Field notes): map of repository
  path, written exactly as in `paths`, to SHA. Missing entry, unresolvable SHA
  or an old scalar timestamp → first run for that repository, reason stated
  (F13); catchup writes the map on its next write. S3 implements.
- **`project-log` and a key:** the pathless-only key rule is removed from the
  config docs; they now defer to `project-log`'s own § Step 2. Fixture walk 3d
  (refuse a key that has paths) is kept as today's behaviour — S2 decides.
- **D-21 amended:** the legacy check keys on `.daikenja/ledger.md` at home with
  **no `open.md` beside it**, whether or not a `DECISIONS.md` exists, so a
  plan-staged-rollout `DECISIONS.md` cannot hide an unmigrated ledger.
  `project-log` refuses to scaffold or write either file over it. S2 implements
  the refusal.

**Outside Artifacts (one-phrase citation repoints only, for the acceptance
grep):** `skills/project-list/SKILL.md` (Step 0 and Step 2 item 3),
`skills/project-log/SKILL.md` (Step 2 item 3), `skills/setup-project/SKILL.md`
(Step 2), `docs/ledger-format.md` (intro). Each now names the renamed heading;
the surrounding text still describes the `ledger:` key and pathless projects
and is S4's, S2's, S6's and S9's to rewrite. `check-skill-size.py` (with
BASE_SHA/HEAD_SHA set): no file crossed the size trigger.

Acceptance (run in `../daikenja-s1`):

```
$ python3 tests/check-invariants.py
All invariant checks passed.
$ git grep -n "Finding the ledger" -- . ":!.plan" ":!CHANGELOG.md" ":!docs/upgrading.md"
(exit 1, no output)
$ git grep -nE "ledger:|paths: \[\]" -- docs/config-schema.md docs/config-resolution.md templates/daikenja.yaml
docs/config-resolution.md:189:- **A leftover `ledger:` key** is ignored. The run says so in one line naming
docs/config-resolution.md:191:- **A `paths: []` entry**, or one with neither `path` nor `paths`, is
docs/config-resolution.md:305:| A project entry still has a `ledger:` key | Ignored. One line naming the key and `/daikenja:setup-user`, then continue with the fixed paths. |
```

All three hits are D-21 legacy-handling sentences (§ Legacy keys and
unmigrated ledgers, and its Failure behavior row); no live use remains.

Hand walk, `tests/fixtures/project-resolution.md` against the new rules — all
twelve walks hold:

- Walk 1: `harbor-rollout` by longest prefix; `Ledger:` names
  `C:/GitHub/harbor/DECISIONS.md` and `.daikenja/open.md`.
- Walk 2: from `quill-web`, home is `quill-gateway` (first path), so `open.md`
  is read there; all three `DECISIONS.md` named, `quill-infra`'s not created yet.
- Walks 3, 3b, 3c: `beacon-charter` (`paths: []` + absolute `ledger:`) — by key
  it stops on "needs migration" for read and write; by directory it never
  matches, so its old ledger folder resolves as unregistered with no ledger.
- Walk 3d: `project-log quill-programme` refused, no fallback — unchanged.
- Walk 4: key from the wrong directory reads quill's two existing
  `DECISIONS.md`, each entry naming its repository.
- Walks 5, 9: unknown key stops and lists the four registered keys.
- Walk 6: nested `harbor-migrator` wins; files under its own path.
- Walks 7, 8: `project-list` reports per-file existence and `beacon-charter`
  as needing migration (exact report format is S4's).

Hand walk, default-location case (`tests/fixtures/ledger-location.md` Config
F): home `C:/GitHub/shion-kitchen` has `.daikenja/ledger.md` and no `open.md`
→ § Legacy keys and unmigrated ledgers applies before "No ledger yet" → one
line and stop, nothing parsed:

```
The ledger at C:/GitHub/shion-kitchen/.daikenja/ledger.md needs migration -- run /daikenja:setup-user.
```

The variant with a plan-staged-rollout `DECISIONS.md` present ends the same way.

Follow-ups (not this stage's): `docs/future-work.md` § The ledger still
describes body markers per `ledger-format.md` — S9 with the retirement.
`docs/config-versioning.md` needed no change (its one "ledger entry" mention is
generic). `docs/README.md` still lists `ledger-format.md` and not the two new
specs — S9, per S0's note. S8 extends the S1 `docs/upgrading.md` section
("Your ledger's config moves to …") with the migration part.

Actuals: 2026-11-03T07:14:30.948Z → 2026-11-03T07:25:43.776Z · 11 min · tokens in=114 out=59293 cache_read=9415398 cache_write=194955 · subagents=0
Artifacts check: outside: docs/ledger-format.md, skills/project-list/SKILL.md, skills/project-log/SKILL.md, skills/setup-project/SKILL.md

### S2 project-log writes both files
_(empty)_

### S3 Catchup and decisions read git history
_(empty)_

### S4 Gaps, summary, list and sources skills

As built:

- **`project-gaps`** reads `open.md` (every line is open; no checkbox filter)
  plus every repository's `DECISIONS.md` for version warnings and malformed
  lines only. Staleness from the date raised. `Blocked by:` is matched against
  the other items by words: still open → "blocked by <words> (still open, since
  <date>)"; no match → the `reading.md` § Notices "names an item no longer
  open" line; several matches → says ambiguous, never picks. One hop.
- **`project-summary`** lists every `DECISIONS.md` entry grouped by repository,
  then area; no superseded count (history is `project-decisions`' job, from
  git). Open items keep `Blocked by:` as text. Sources always listed (the
  section is now required).
- **`project-list`**: an entry with no paths is reported only as "needs
  migration" (no "reachable by name" line); per-repository `DECISIONS.md` and
  home `open.md` existence; leftover `ledger:` noted; home `ledger.md` without
  `open.md` → needs migration. Unregistered scan looks for `.daikenja/open.md`
  and legacy `.daikenja/ledger.md`, never a bare `DECISIONS.md` (other tools
  write it). `project-resolution.md` Walks 7–9 already match this shape.
- **`project-sources`** reads Sources from `open.md`, names sources by label
  (no `S-nnn`, no Changelog line); a missing `## Sources` heading is now a
  reported defect, an empty one a one-line stop.
- **Fixture** `sources-ledger.md` is now `meridian` across
  `meridian-controls` (home) and `meridian-services`, with a `Blocked by:` to
  an open item, one to a closed item, and a newer-format variant. The old
  pointer to `sample-ledger.md` as the "no Sources section" case is dropped.

Acceptance (run in `../daikenja-s4`):

```
$ python3 tests/check-invariants.py
All invariant checks passed.
$ BASE_SHA=<merge-base> HEAD_SHA=<head> python3 tests/check-skill-size.py
check-skill-size: no file crossed the size trigger.
```

Hand walk, `tests/fixtures/sources-ledger.md`, today 2026-09-15:

- Step B resolves `meridian` to three files:
  `Ledger: C:/GitHub/meridian-controls/DECISIONS.md, C:/GitHub/meridian-services/DECISIONS.md, C:/GitHub/meridian-controls/.daikenja/open.md`.
  Run from `C:/GitHub/meridian-services` the same line comes back (longest
  prefix → `meridian`; home is the first path).
- `project-summary` shows **2** decisions: Tracking from `meridian-controls`
  and Controls from `meridian-services` (imposed by the board). Reading only
  the first repository would show 1 — the case the fixture exists to catch.
- `project-gaps` at 21 days: unowned + stale = the reconciliation-owner item
  (25 days). At 5 days the reconciliation schedule is stale and annotated
  "blocked by who reconciles the control list (still open, since 2026-08-21)"
  — its words match the open unowned item; the ingest item's "the exemption
  renewal sign-off" matches nothing, so it gets the no-longer-open line.
- `project-sources`: moved 2 (standards page, control sheet), no baseline 1,
  could not check 1, unchanged 1 — unchanged from before; field lines read as
  continuations.
- Variant `decisions-format: 2` in `meridian-services`: one warning line, then
  the same results.

Follow-ups (not this stage's): `tests/fixtures/ledger-relationships.md` still
walks `project-gaps` against `Blocked by O-007.` / `Contradicts` markers from
`ledger-format.md`; its `Depends on` headings still resolve, so the invariants
pass, but its content is the old grammar — S9 with the `ledger-format.md`
retirement. `ledger-backfill.md`, `ledger-location.md` and
`setup-user-upgrade.md` mention these skills only in passing and were left.
The `project-catchup` and `project-log` lines in `sources-ledger.md` are
minimal; S2/S3 may sharpen them.

Actuals: 2026-11-03T07:32:54.495Z → 2026-11-03T07:39:04.884Z · 6 min · tokens in=62 out=28316 cache_read=4352539 cache_write=133613 · subagents=0
Artifacts check: match

### S5 Judgement, thread, meeting-review and other readers

As built:

- **The token (S7 consumes it).** Exact text `DAIKENJA-PROJECT-DATA-UNREADABLE`.
  In the `message` form of `judgement` and `thread` -- the path the bot calls
  (`/daikenja:judgement message`, `/daikenja:thread message`) -- the whole
  deliverable is one line, nothing before or after it:

  ```
  DAIKENJA-PROJECT-DATA-UNREADABLE <key> needs-migration
  DAIKENJA-PROJECT-DATA-UNREADABLE <key> newer-format
  ```

  `<key>` is the project key, or `-` for an unregistered directory. The
  matching `reading.md` notice line goes in the report around the message,
  outside the sentinels. Needs migration = no repository in `daikenja.yaml`, or
  `.daikenja/ledger.md` at home with no `open.md` (D-21); newer format = any
  file's version line above what the plugin knows (D-4). The `answer` form is
  unchanged in kind: needs migration gives the notice and stops; a newer
  version is read with one warning.
- **Citations without IDs:** a decision is named topic-first with the
  repository whose `DECISIONS.md` holds it in parentheses -- `the cutover-day
  decision (harbor)` -- and an `open.md` item with `(open item)`.
  `response-format.md` § Entries are named topic-first, ID in parentheses now
  says this in its body.
- `judgement` reads every registered repository's `DECISIONS.md` in full; the
  superseded-decision rule became "every entry is in force; two repositories'
  entries that disagree are both named". `Ledger:` lines carry `<files>` per
  `reading.md` § Step B.
- `meeting-review` hands `project-log` decisions as rule + why (no owner field
  in `DECISIONS.md`, so who closed it stays in the report and handoff) and
  open items with owner and date raised; no IDs, no markers, no Changelog
  writer.
- `preflight`/`preflight-reference.md`: check 6 reads both files; needs
  migration reports "already answered" as not checked; newer version read with
  its warning.
- `remember-persona` now cites `open-format.md` § Section: Open items for what
  an owner handle refers to.
- `self-review` and `learn-voice`: no change needed -- their mentions are the
  word "ledger" only (D-7) and "contradicts a `Fixed` rule", not the format.

Acceptance (run in `../daikenja-s5`):

```
$ python3 tests/check-invariants.py
All invariant checks passed.
$ BASE_SHA=<origin plan branch> HEAD_SHA=<HEAD> python3 tests/check-skill-size.py
check-skill-size: no file crossed the size trigger.
```

Both re-run after merging S4 (#311) into the stage branch: same output.

Hand walk 1, `tests/fixtures/judgement.md` Walk 1 (`answer` form, Subject A)
against the fixture's synthetic `C:/GitHub/ember/DECISIONS.md` (invented
project `ember`, invented people gabiru/hakurou/shion): content resolves
`ember` by `#ember-warehouse`; `Ledger: ember, matched by #ember-warehouse
(C:/GitHub/ember/DECISIONS.md, C:/GitHub/ember/.daikenja/open.md)`; the
verdict cites "the storage-engine decision (ember)" and "the retention
question (open item)" -- no ID anywhere. Walks 2 and 6 cite "the nightly load
window decision (ember)" the same way.

Hand walk 2, `judgement` unreadable data (fixture Walks 7 and 8, Subject B):

- Needs migration: `message project ember`, `.daikenja/ledger.md` present and
  no `open.md` -> legacy check of `reading.md` § Step B fires first, nothing
  read; report line `The ledger at C:/GitHub/ember/.daikenja/ledger.md needs
  migration -- run /daikenja:setup-user.`; message
  `DAIKENJA-PROJECT-DATA-UNREADABLE ember needs-migration`, no verdict.
- Newer format: `DECISIONS.md` line 1 `<!-- decisions-format: 2 -->` -> report
  line `C:/GitHub/ember/DECISIONS.md was written by a newer format (version 2);
  update the Daikenja plugin.`; message
  `DAIKENJA-PROJECT-DATA-UNREADABLE ember newer-format`, no verdict.

Hand walk 3, `thread` unreadable data (`/daikenja:thread message project
ember`, the fixture's Subject A as the thread):

- Needs migration (same files as walk 2): Step 2b gives the notice in place of
  the `Ledger` line and reads nothing; § Form `message` -> "Project data
  unreadable produces no summary" -> deliverable
  `DAIKENJA-PROJECT-DATA-UNREADABLE ember needs-migration`, no Thread/Asking
  block.
- Newer format (same file as walk 2): Step 2b reads with one warning; the
  message form -> `DAIKENJA-PROJECT-DATA-UNREADABLE ember newer-format`, no
  block.

Follow-ups (not this stage's):

- **S9:** rename `response-format.md` § Entries are named topic-first, ID in
  parentheses to drop "ID in parentheses", with its reverse index and the
  citing skills (catchup, decisions, gaps, summary, sources, preflight,
  project-log, compose) once S2-S4 have landed -- renaming it now would
  collide with three parallel stages. `docs/README.md:52` and
  `skills/compose/SKILL.md:191` still say "ID in parentheses".
- **S9:** `docs/ledger-format.md`'s reverse index still lists remember-persona
  under § Who an owner handle refers to; it goes with the file.
- **S3:** `tests/fixtures/sample-ledger.md` is still old-format;
  `sample-drafts-preflight.md` Draft 3 now expects "the events-table schema
  freeze (beacon)", so S3's conversion should keep that entry's words and put
  it in a repository named `beacon`.
- **S2:** `sample-thread.md` and `sample-thread-followup.md` describe
  `project-log`'s proposals (scaffold, duplicates); only the scaffold sentence
  was repointed here.
- `tests/fixtures/judgement.md` Walks 1-3 still show an older answer shape
  (`Verdict:` lines, `AI review summary` header in Walk 2) than the skill's
  current markers -- predates this plan; left as is.

Actuals: 2026-11-03T07:33:01.914Z → 2026-11-03T07:43:12.064Z · 10 min · tokens in=110 out=33383 cache_read=8739823 cache_write=162317 · subagents=0
Artifacts check: match

### S6 setup-project registers git-backed projects only
_(empty)_

### S7 Slack bot reports unreadable project data
_(empty)_

### S8 Migration from the old ledger
_(empty)_

### S9 User guide, README and retiring ledger-format.md
_(empty)_

<!-- One ### S<N> block per stage. Templates for the states you'll hit:

  done      — paste the real acceptance output, then the as-built summary and
              any gotchas the next stage needs to know.
  actuals   — every session on the stage, whatever its outcome, adds one
              `Actuals:` line (`scripts/effortlog.py usage`, its `line` as is);
              `/plan-close` sums them against the estimates.
  artifacts — the finish protocol adds one `Artifacts check:` line
              (`scripts/artifacts_check.py`, its line as is); a record, never
              a gate — the final review judges each `outside` line.
  doing     — tick the completed Steps checkboxes in the stage file; write a
              handoff note here (what's left, where to resume).
  blocked   — record exactly what human/external action unblocks it, as a
              runbook the human can follow; no faked progress. Where that row
              and runbook get committed depends on whether the stage branch
              exists yet — see PLAN.md, Operating protocol, "Recording a
              block". A mid-stage block lands on the stage branch, so this
              file's copy on the plan branch keeps reading `doing` and the
              block is recorded in BLOCKED.md instead. Discovered mid-run that
              the stage needs a resource only the local machine has? Use the
              literal reason `needs-local` in the Result cell (or the
              BLOCKED.md section) instead of a generic note — see PLAN.md,
              "Recording a block", "The discovered case".
  skipped   — one-line reason; if this stage owned acceptance/verification
              work nothing else covers, say so here too, so SF sees it.
  follow-up — a shortcut or scope-creep item spotted here that became (or
              should become) its own stage; name it so the review stage sees it.
  added     — a stage added after the scaffold opens its notes block with its
              `Added by` line and the scope referee's verdict (PLAN.md,
              "Adding a stage").
-->

### SF Plan review
_(empty)_
