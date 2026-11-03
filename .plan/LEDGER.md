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
| S2 project-log writes both files | done | yes | 2026-11-03 | project-log writes DECISIONS.md and open.md in one batch; D-4/D-21 refusals; skill 28% smaller |
| S3 Catchup and decisions read git history | done | yes | 2026-11-03 | Catchup diffs git per repository from a validated SHA; decisions reads every DECISIONS.md with git history |
| S4 Gaps, summary, list and sources skills | done | yes | 2026-11-03 | Four skills read DECISIONS.md/open.md; two-repo sources fixture walked |
| S5 Judgement, thread, meeting-review and other readers | done | yes | 2026-11-03 | Readers moved to DECISIONS.md/open.md; DAIKENJA-PROJECT-DATA-UNREADABLE token for S7 |
| S6 setup-project registers git-backed projects only | done | yes | 2026-11-03 | Registration is git-only, home asked and written first, seed via project-log; skill 23203→23144 bytes |
| S7 Slack bot reports unreadable project data | done | yes | 2026-11-03 | Bot posts one fixed line on the unreadable token; --check names unreadable projects |
| S8 Migration from the old ledger | done | yes | 2026-11-03 | setup-project Step 2a runs docs/ledger-migration.md; four fixture inputs walked, all match |
| S9 User guide, README and retiring ledger-format.md | done | yes | 2026-11-03 | Guide, README, diagrams and changelog describe the new ledger; ledger-format.md, its template and fixture retired |
| S10 Fix: align the migration batch exemption | done | yes | 2026-11-04 | project-log exempts the migration batch from both refusals; config docs name the migration; no-folder walk writes both files |
| SF Plan review | done | yes | 2026-11-04 | Redo 1 clean: root DECISIONS.md (14 entries from 22 decisions), pointer line, cold reader no misses; one issue for closeout |

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

As built -- what S3 to S9 can assume of `project-log`'s output:

- **One batch, grouped by file.** The proposal shows every line verbatim under
  the absolute path of the file it lands in (`+` added, `-` deleted, an edit
  both); "Not kept", "New owner handles" and "Questions before I write" blocks
  follow. No IDs, no Changelog line, no markers except `Blocked by:` on open
  items. Closing an item deletes its line.
- **Same-turn dictated path kept**, narrowed: the dictation is the approval of
  a batch of at most about three entries. A decision qualifies only when the
  rule, why and revisit condition are all in the user's words and its file and
  area exist; scaffolding a file or proposing a new area always proposes.
  Assumption, not a frozen decision: #292's "proposes entries in a batch, and
  the user approves them" is read as allowing a dictation to be that approval.
- **Decision entries** follow `decisions-format.md` § Shape with its em dash.
  `Source:` is written only when the material names one, never invented. Why
  and revisit are asked for when missing. The keep rule filters decisions from
  interpreted material ("Not kept" block); a dictated decision was kept by the
  user.
- **Placement:** single repository is automatic; in a multi-repository project
  a decision goes to the repository whose code it constrains, project-wide ones
  to home, and an unclear one is a question (#292 option 6). Area by `Paths:`,
  a new area proposed when none covers.
- **Owners** only on open items; the handle check reads `open.md` owners, then
  `personas.md`.
- **Refusals:** newer version in any file the batch would write refuses the
  whole batch (D-4); `.daikenja/ledger.md` at home with no `open.md` refuses to
  scaffold or write (D-21), except the migration's own batch -- **D-21 amended**
  for S8. A named key: no match stops, `paths: []` gets the needs-migration
  line, any other match is refused as before (walk 3d unchanged; key writes
  could now be allowed since files sit at fixed paths -- not done, left for a
  later issue).
- **Other skills' batches** (`project-log-reference.md` § A batch handed over by
  another skill): `setup-project`'s seed, the migration and `meeting-review`
  go through every check; an existing `DECISIONS.md` is extended, never
  overwritten; large batches may be approved in tranches.
- **Never commits** (D-6); Step 8 says "Not committed".
- `SKILL.md` 27494 -> 19676 bytes (baseline at v0.12.0: 27460).

No `docs/upgrading.md` note and no changelog entry: nothing on disk changes
beyond S1's note; S9 writes this stage's changelog entry (D-14).

Acceptance (run in `../daikenja-s2`, re-run after merging S4's landing into
the stage branch):

```
$ python3 tests/check-invariants.py
All invariant checks passed.
$ BASE_SHA=<origin plan branch> HEAD_SHA=<HEAD> python3 tests/check-skill-size.py
check-skill-size: no file crossed the size trigger.
```

After the S4 merge, `ledger-relationships.md` Walk 2 was aligned to S4's
gaps report shape (header suffix, block annotation on an indented line, the
`reading.md` § Notices line for a closed blocker) -- which also settles S4's
follow-up on that fixture.

Hand walk, `tests/fixtures/dictated-log-requests.md` (today 2026-09-15):

- Scenario 1: dictated decision with why and revisit -> same turn, written
  under `DECISIONS.md` § Dashboard, no `Source:`, no owner, "Not committed".
- Scenario 2: open item, no owner -> `@unassigned`, same turn, `open.md`.
- Scenario 3: duplicate of the Rollout entry -> propose, quoting it by words.
- Scenario 4 (the batch naming both files): the pasted thread yields one
  proposal with `C:/GitHub/beacon/DECISIONS.md` (+ canary-hold entry in
  Rollout) and `C:/GitHub/beacon/.daikenja/open.md` (- the runbook item), and
  one questions block (revisit condition; source or context link, and its URL).
- Scenario 5 (`<!-- decisions-format: 2 -->`): Step 4 reads the version line
  before Step 5, the batch writes `DECISIONS.md`, so the whole batch is refused
  -- the open item too -- with the plugin-update line citing
  `${CLAUDE_PLUGIN_ROOT}/docs/open-format.md`. Nothing written.
- Scenario 6 (existing plan-staged-rollout `DECISIONS.md`, no `.daikenja/`):
  Step 2 finds no legacy ledger; Step 3 adopts `DECISIONS.md` (entry appended
  to its Release area, title/intro/`ADRs:` line/existing entry untouched) and
  scaffolds only `open.md` from the template inside the same approval; the
  restated tag-only rule is a duplicate, not re-added.
- Scenario 7 (old `.daikenja/ledger.md`, no `open.md`; with and without a
  `DECISIONS.md`): Step 2 item 4 stops with
  `The ledger at C:/GitHub/beacon/.daikenja/ledger.md needs migration -- run /daikenja:setup-user.`
  before Step 3 or Step 5 -- nothing scaffolded, nothing written, same-turn
  path never reached.

`ledger-relationships.md` and `owner-handles.md` were walked the same way; the
walk caught that owner-handles Walk 8 (a decision into a fixture with no
`DECISIONS.md`) must propose rather than write in the same turn, and that a
named `paths: []` key should get the migration line rather than the generic
refusal -- both fixed (`ddf3667`).

Follow-ups (not this stage's):
- `tests/README.md` still describes `dictated-log-requests.md` as four
  scenarios against `sample-ledger.md`, and `owner-handles.md` /
  `ledger-relationships.md` in old-format terms -- S9 (D-14 keeps
  `tests/README.md` for stages that add or remove a fixture).
- `sample-thread.md`, `sample-thread-followup.md` and `malformed-ledger.md`
  cite `project-log` headings that still exist but walk old-format output --
  S3 owns `malformed-ledger.md`; the two thread fixtures are S5's or S9's.
- `ledger-relationships.md` Walks 1-2 pin `project-decisions` and
  `project-gaps` behaviour (imposed origin from the why clause; gaps report
  without IDs, `Blocked by:` naming an item no longer open). S3 and S4 should
  check their rewrites against it and repoint its `Depends on:` if their step
  headings move.
- `meeting-review` and `setup-project` still describe `project-log via <skill>`
  with a Changelog writer field -- S5 and S6.
- Allowing `project-log <key>` from outside the project now that files sit at
  fixed paths -- would change `project-resolution.md` walk 3d; an issue if
  wanted.

Actuals: 2026-11-03T07:32:41.930Z → 2026-11-03T07:44:44.380Z · 12 min · tokens in=90 out=56579 cache_read=7410517 cache_write=177190 · subagents=0
Artifacts check: match

### S3 Catchup and decisions read git history

As built -- what later stages cite:

- **`project-catchup`** headings: Step 2 is now **"read and check each
  checkpoint"** (validation, the four first-run cases and their exact lines);
  Step 3 **"compute the delta"**, Step 4 **"report the delta"** and Step 5
  **"propose and write the checkpoint"** keep their names, so `ledger-backfill.md`,
  `sources-ledger.md` and `response-format.md` citations still resolve.
- **SHA safety:** `^[0-9a-fA-F]{7,40}$` first; only a passing value reaches
  git, as `--end-of-options "<sha>^{commit}"` (rev-parse) or
  `--end-of-options "<sha>..HEAD"` (log/diff). Checked on git 2.56: both forms
  work. A scalar `last_checkpoint` is never validated or passed to git.
- **Writes the full 40-character SHA** from `rev-parse HEAD`; an unchanged
  repository is left out of the proposal; a scalar is replaced by the map.
- **Uncommitted edits** come from `git status --porcelain` plus `git diff HEAD`,
  reported under "Not committed yet" and not covered by the checkpoint (D-6).
- **`project-decisions`**: Step 4 is now **"follow the history in git"**
  (`git log -p` on a fixed file path; the entry's words never go into a
  command); Step 5 **"surface relationships and origin"** and Step 6 **"show
  the result"** keep their names. Imposed is read from the why clause (D-2);
  open items that question an entry replace `Contradicts`. An ADR `Source:` is
  read locally; issue/PR links are shown, never fetched.
- **Fixtures:** `broken-supersession.md` retired (supersession markers no
  longer exist). `sample-ledger.md` and `malformed-ledger.md` are now a
  `DECISIONS.md` plus `open.md` pair in fenced blocks. Former IDs, for the
  fixtures that still cite them: beacon D-004 = "Roll the beacon service out
  region by region" (Rollout); D-003 = the events-table schema freeze (Data);
  D-001 = "Beacon replaces the old telemetry pipeline" (Rollout); D-002 is gone
  (replaced); O-005..O-002 kept as open items with their owners; O-001
  (resolved, `@benimaru`) is deleted per D-10. Harbor's old D-002 owner defect
  is now an open item missing its owner.

Acceptance (run in `../daikenja-s3`, re-run after merging S2's, S4's and S5's
landed PRs into the stage branch; the ledger status table was the one conflict,
resolved by keeping both rows. S5's new `response-format.md` wording -- the
parentheses say where an entry lives -- was matched in both skills' Step 4/6
prose. The walk output below was identical before and after the re-sync):

```
$ python3 tests/check-invariants.py
All invariant checks passed.
$ BASE_SHA=<plan tip> HEAD_SHA=<stage tip> python3 tests/check-skill-size.py
check-skill-size: no file crossed the size trigger.
```

Hand walk of `tests/fixtures/catchup-git-history.md`: both repositories built
in the scratchpad from the fixture's commits (script `walk.sh`, author dates
fixed, `core.autocrlf false`), then the skill's Step 2/3/5 commands run as
written. Output, trimmed to the decisive lines:

```
C1=f0c24f5… C3=8e4759e… I1=e359226…
== Walk 1: checkpoint map {app: C1, infra: I1}
  lumen-app: f0c24f5… resolves
  -- log lumen-app f0c24f5..HEAD
     8e4759e 2026-09-12 Noor Keep an origin fallback for launch month
     8ad5632 2026-09-10 Tomas Log the launch date
  -- diff
     +- 2026-09-10 -- @unassigned -- Decide who announces the launch on the status page.
     -- 2026-09-03 -- @unassigned -- Pick the launch date.
     -- **Static assets are served from one CDN, with no origin fallback.** — a
     +- **Static assets are served from one CDN, with the origin as a fallback for
     +## Launch
     +- **Launch on Tuesday 2026-10-06, not the Monday before.** — the support rota
  lumen-infra: e359226… resolves
  -- log lumen-infra e359226..HEAD          (empty: no changes)
  -- status (not committed yet) lumen-app
      M .daikenja/open.md
     +- 2026-09-15 -- @tomas -- Book the launch-day war room.
== Walk 2: {app: 0123abcd0123abcd}, infra no entry
  lumen-app: 0123abcd0123abcd does NOT resolve -> first run
  lumen-infra: no entry -> first run
  -- status (not committed yet) lumen-app
      M .daikenja/open.md
== Walk 3: scalar 2026-09-01T09:00Z
  scalar (not a map) -> predates the new ledger; first run for both; never validated or passed to git
== Walk 4: metacharacters
  lumen-app: REJECTED by validation -- not passed to git     ("c0ffee1; rm -rf ~")
  lumen-infra: REJECTED by validation -- not passed to git   ("--output=/tmp/x")
== Step 5 proposal values
  lumen-app HEAD=8e4759e… passes validation
  lumen-infra HEAD=e359226… passes validation
```

The three Done-check-7 paths hold: (1) changes since a SHA -- Walk 1 reports
four changes in `lumen-app` by current wording (new launch decision, edited CDN
decision, closed launch-date item, new unowned status-page item) and none in
`lumen-infra`; (2) unresolvable SHA -- Walk 2 says "The checkpoint for lumen-app
(0123abcd0123abcd) is not in its history any more, so this is a first run
there." and shows the whole current content; (3) uncommitted -- the war-room
item is listed under "Not committed yet" in all four walks. Scalar timestamp --
Walk 3 says the checkpoint predates the new ledger and proposes `{lumen-app:
<C3>, lumen-infra: <I1>}`. Metacharacter SHAs -- Walk 4 rejects both values at
the regex; no git command receives them. The walk found one gap, fixed in the
skill: Step 5 did not say an unchanged repository is left out of the proposal.

**Outside Artifacts:** none. `project-catchup/SKILL.md` grew from 9.7 KB to
12.6 KB (1.3x the last release, under the 2x trigger); `project-decisions`
from 9.0 KB to 9.8 KB.

Follow-ups (not this stage's):

- (Resolved on re-sync: S2 made `owner-handles.md` and
  `dictated-log-requests.md` self-contained, and S5 reworded
  `sample-drafts-preflight.md` to "the events-table schema freeze (beacon)",
  which the new `sample-ledger.md` still holds.)
- `tests/fixtures/ledger-backfill.md` Walk 3 still expands Changelog ranges
  through `project-catchup` "Step 3: compute the delta" (heading kept, content
  gone), and `check-invariants.py` checks that fixture against
  `ledger-format.md` -- S9 retires both with `ledger-format.md`.
- `docs/ledger-format.md`'s reverse index still lists `project-catchup` and
  `project-decisions` "Step 0: read the contracts" -- harmless (the heading
  exists), gone when S9 deletes the file.
- `docs/config-writers.md`'s reverse index has never listed `project-catchup`,
  which cites § Who writes what -- S9's docs pass, if it wants it complete.

Actuals: 2026-11-03T07:32:46.766Z → 2026-11-03T07:44:55.858Z · 12 min · tokens in=94 out=44396 cache_read=7645355 cache_write=160326 · subagents=0
Artifacts check: match

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

Both re-run after merging S4 (#311) and then S2 (#313) into the stage branch: same output each time.

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

As built -- what S8 and S9 can assume of `setup-project`:

- **Git-only registration.** Every path written is a git repository, checked
  with `git -C <dir> rev-parse --show-toplevel` in Step 1. Inside a repository
  below its root, the root is proposed (a sub-folder only on request). A plain
  folder gets a one-line `git init` offer; a no writes nothing. "No folder at
  all" gets the offer of a new folder named after the key. The pathless branch,
  the `paths: []` + absolute `ledger:` write and the `ledger` per-project key
  (Step 3) are gone; Step 3 now offers `stale_after_days` and `norms_doc` only.
  `writes:` frontmatter names `git init`; skill metadata version 2 → 3.
- **Home (D-8).** Asked in the same round as the key when registering a new
  project ("does it span other repositories, and which is home?"), and written
  first. Appending a repository to an existing entry never reorders -- matches
  `config-resolution.md`'s "do not reorder the list afterwards".
- **Card** is `<home>/.daikenja/project.md` (Step 3b), per S1's
  `project-card.md` § Location; the `<name>.project.md` derivation is gone.
- **Needs migration.** An exact match whose home holds `.daikenja/ledger.md`
  with no `open.md` gets the `config-resolution.md` § Legacy keys line naming
  `/daikenja:setup-user`; Steps 3 and 3b run, Step 4 (seed) does not. **S8**
  replaces this with the migration branch (D-20) -- Step 2's "A matched entry
  that needs migration" paragraph and its failure-table row are the hook.
  "What this skill does not do" still says it does not migrate; S8 rewords.
- **Seeding** hands batches to `project-log` per
  `project-log-reference.md` § A batch handed over by another skill (one
  tranche = one approval; project-log scaffolds either file inside it). Step 4a
  now also looks for an existing `DECISIONS.md` (adopted, only what it lacks
  is added) and `doc/adr/`. ADR rules rewritten for the new format: one entry
  per decision in force with `Source: <ADR>`, newest only; a replaced record
  and an answered register question are not proposed; `project-log` adds the
  `ADRs:` line. Dropped: ID-order allocation, `Approximate date.` marker
  (approximations now per § Backfilling), the supersession-pair rule.
  Decisions carry no date; why/revisit missing → questions. Step 5 says the
  files are not committed (D-6).
- `SKILL.md` 23203 → 23144 bytes (v0.12.0 baseline 23187). Headings cited
  elsewhere (Steps 0, 1, 2, 3, 3b, 4a, 4c, "Setup project") unchanged.
- `templates/README.md`: intro names both ledger files and the card beside
  `open.md`; `ledger.md` described as no longer scaffolded, kept until its
  format doc is retired (S9 deletes both). `templates/project.md`: comment says
  "beside open.md".
- `tests/fixtures/ledger-location.md` not edited: its one `setup-project`
  mention (refusing `~` / `~/.claude`, Config E) still holds.

**For S9's changelog entry (D-14, D-15):** `setup-project` no longer registers
a project without a folder -- every project lives in a git repository, and a
plain folder is offered `git init`. It asks which repository is home for a
multi-repository project and writes it first, no longer offers the `ledger`
key, and seeds `DECISIONS.md` / `open.md` through `project-log`, extending an
existing `DECISIONS.md` rather than replacing it.

Acceptance (run in `../daikenja-s6`):

```
$ python3 tests/check-invariants.py
All invariant checks passed.
$ BASE_SHA=$(git merge-base HEAD origin/feat/292-replace-ledger-decisions-md-open) HEAD_SHA=$(git rev-parse HEAD) python3 tests/check-skill-size.py
check-skill-size: no file crossed the size trigger.
$ git grep -nE "pathless|paths: \[\]|daikenja/ledgers" -- skills/setup-project templates/README.md templates/project.md tests/fixtures/setup-project-seed.md
(exit 1, no output)
```

Re-run after merging S3 (#314) into the stage branch: same output; S3 touched
no S6 file.

Hand walks, `tests/fixtures/setup-project-seed.md` (rewritten: six walks):

- **Code repository (Walk A).** `C:/GitHub/quill-gateway` is a repo root, no
  exact match → "new or another repository?" → new, key `gateway`, just this
  repo → entry `gateway: paths: [C:/GitHub/quill-gateway]` with
  `stale_after_days: 30` and `norms_doc`, no `ledger:` key. Card offered at
  `C:/GitHub/quill-gateway/.daikenja/project.md`. Seed declined, so no ledger
  file is created (only `project-log` scaffolds). Walk B: exact match → key
  left alone, straight to Step 4.
- **Seed (Walk C).** Step 4a finds `docs/adr/` and `docs/open-questions.md`,
  no `DECISIONS.md` → index-and-depth notice. Decisions tranche to
  `project-log`: ADR-0001, ADR-0003 (revisit asked), ADR-0004
  (`Source: ADR-0004`), sam's cutover hold, the standing rule -- ADR-0002 and
  Q-03 never proposed; `DECISIONS.md` scaffolded in the same approval with
  `ADRs: docs/adr/`. The user's "put the old TLS one in too" is declined as
  current-only. Open items tranche answered around → restated; then Q-01
  (`2026-05-21 -- @sam`) and Q-02 (`2026-06-02 -- @unassigned`) to
  `.daikenja/open.md`, in-flight item dropped (no date), 30-day stale notice
  given first. Feature-flag idea not kept; ADR-0003 and the standing rule stay
  two entries. Confirm: counts, "not committed".
- **Multi-repository (Walk D).** Run from `C:/GitHub/harbor-api`; new project
  `harbor`, also `C:/GitHub/harbor-docs`, home harbor-docs → both repo roots →
  `paths: [C:/GitHub/harbor-docs, C:/GitHub/harbor-api]`, home first though
  the run started in harbor-api; card at harbor-docs. Variant D2: quill-web
  appended to `gateway` after quill-gateway, named as staying home, no
  reorder.
- **Non-code folder (Walk E).** `C:/Work/vendor-onboarding` has no `.git` →
  `git init` offered before any write; yes → `git init`, entry with that one
  path; no → nothing written. "No folder at all" → offer of a new folder with
  `git init`; never an entry with no paths.
- **Existing `DECISIONS.md` (Walk F).** `C:/GitHub/lantern` with a
  plan-staged-rollout `DECISIONS.md` (Release area, tag-only entry). Step 4a
  names it as adopted. `project-log` (Step 3 adopt, Step 7 "a new area at the
  end of the file") adds `## API` with `Paths:` and the versioning entry; the
  restated tag-only rule is a duplicate, not re-added. `open.md` scaffolded
  from the template in its own tranche with the unowned changelog question.
  Title, intro, Release area and its entry byte-identical afterwards; nothing
  overwritten.

Follow-ups (not this stage's):

- **S9:** `docs/guide/install.md` § A project with no folder,
  `docs/guide/ledger.md` (lines ~59, ~110), `docs/guide/faq.md` (~36, ~57),
  `docs/guide/your-data.md` (~40, ~87) and `docs/guide/commands.md` (~70)
  still describe registering a project with no folder; the setup-project guide
  text should also mention the `git init` offer and the home question.
- **S8:** see "Needs migration" above.

Actuals: not recorded -- cloud session, `scripts/effortlog.py` (plugin) not available. Session 2026-11-03, ended 2026-11-03T10:45Z.
Artifacts check: match (by hand, `git diff --name-only` against the plan branch; `scripts/artifacts_check.py` not available in this cloud session)

### S7 Slack bot reports unreadable project data

As built:

- **Token handling (`prompts.py`).** `UNREADABLE_TOKEN =
  "DAIKENJA-PROJECT-DATA-UNREADABLE"`, reasons `needs-migration` /
  `newer-format`. `extract_output` checks the raw output first, before the
  sentinel pass: a line that is the token, a key and a known reason (stray
  backticks, `>` or `*` around it tolerated; mid-sentence or an unknown
  reason is not a match) logs `project data unreadable: project <key>,
  <reason>` at WARNING and returns `PROJECT_DATA_UNREADABLE`: "I could not
  read this project's ledger, so I have not answered. Its project data needs
  attention from whoever runs me." No `setup-user` text, no key in the
  thread. `runner.py` needed no code change -- the line flows out as the
  answer the handler posts, like `NO_ANSWER`.
- **`--check` (done, no git).** `config.project_data_states()` reads
  `~/.claude/daikenja/daikenja.yaml` and each project's files on disk:
  needs-migration = no `path`/`paths`, or home `.daikenja/ledger.md` with no
  `open.md`; newer-format = a root `DECISIONS.md` or the home `open.md` whose
  version line is above `decisions-format: 1` / `daikenja-open-format: 1`.
  `__main__.project_data_line()` prints `projects:   needs attention: <key>
  (<state>), ...`, `N, all readable`, `none registered`, or `unknown -- <why>`.
  `Moved:` sub-folder `DECISIONS.md` files are not version-checked (root files
  only).
- **Docs.** `config.py` comment, `runner.py` docstring and `bot/README.md`
  name `DECISIONS.md` and `.daikenja/open.md`; README gains the `projects:`
  line and an "Unreadable project data" paragraph. Test fixtures citing
  `.daikenja/ledger.md` as the current ledger now use the new paths; the
  `LocalPathTests` docstring keeps the old path because it quotes a real run.
  "Ledger" stays the user-facing word (D-7).
- **Tests added:** `UnreadableProjectDataTests` (7, both states assert the
  fixed line and the log line), a `run_command` test per state in
  `test_runner.py`, `ProjectDataLineTests` (4) in `test_main.py`.

Acceptance (run in `../daikenja-s7`):

```
$ python -m pytest bot/tests -q
477 passed, 11 subtests passed in 1.30s
$ python3 tests/check-invariants.py
All invariant checks passed.
$ git diff --stat origin/feat/292-replace-ledger-decisions-md-open -- bot/requirements.txt
(no output)
$ git grep -nE "subprocess|git " -- bot/daikenja_bot
bot/daikenja_bot/config.py:381:    asks git (D-17). A project is `needs-migration` when it has no repository
bot/daikenja_bot/preflight.py:21,88,122  (existing: `claude plugin details`)
bot/daikenja_bot/runner.py:20,47,135,181,195,206,221  (existing: `claude -p`)
```

The only new hit is the docstring line saying the bot never asks git; no new
call into git or any new subprocess.

Follow-ups (not this stage's):

- **S9:** `docs/guide/slack-bot.md` should mention the fixed
  "could not read this project's ledger" line and `--check`'s `projects:`
  line in its operator-after-upgrade sequence.

Actuals: 2026-11-03T07:58:35.395Z → 2026-11-03T08:06:49.659Z · 8 min · tokens in=98 out=27956 cache_read=6743070 cache_write=119672 · subagents=0
Artifacts check: match

### S8 Migration from the old ledger

As built -- what S9 and SF can assume of the migration:

- **`docs/ledger-migration.md`** (233 lines, no `ledger-format` citation) is
  the procedure, self-contained: which entries need migration (a `ledger:`
  key, no paths, an old `.daikenja/ledger.md` -- also beside an `open.md`, the
  resume case -- or a timestamp `last_checkpoint`), the old grammar it reads
  (three-split, the two tails, the five body markers, supersession chains to
  the end, tail authoritative), what moves where, the no-folder target check,
  the proposal and the write order.
- **Backup = the old ledger renamed, beside itself**: copied first (step 2),
  original removed last (step 6, after `cmp`), so a failed run leaves the old
  ledger in place and can be repeated; an identical backup of the same day is
  reused. Name is `<stem>.<YYYY-MM-DD>.bak.md`: `ledger.<date>.bak.md` for
  `ledger.md`, `q4-planning.<date>.bak.md` for a no-folder project's
  `ledgers/q4-planning.md`, so two projects in one ledgers folder never
  collide. **Deviation from Acceptance's literal wording** for the pathless
  walk -- flagged for SF; D-11 itself names only the default case.
- **Approved whole, never in tranches**, as a `project-log via setup-project`
  batch naming its targets by absolute path; the user may drop or edit
  entries (dropped ones stay in the backup). The config edit, card move,
  backup and `git init` are shown in the same proposal; `setup-project`
  performs them after the yes, `project-log` writes the two files.
- **Decision rewrite:** rule + why + revisit + source; `Imposed.` folds into
  the why; date, owner, `Approximate date.`, `Supersedes` dropped; revisit
  asked once for all when missing. **Open items:** `Blocked by <id>.` naming a
  migrating item -> `Blocked by: <words>.`; naming a resolved item, a decision
  or nothing -> dropped and said; `Contradicts` -> always a question, never
  carried. Malformed tails (` -> superseded/resolved` not matching a form) and
  unparsable lines are questions / "Could not read", never guessed.
- **`setup-project`** v3 -> v4: Step 1 accepts a key argument (the only way to
  reach a no-folder project); Step 2's needs-migration paragraph now routes to
  new **Step 2a: migrate an old ledger**; failure table and "does not do"
  reworded. 23144 -> 24537 bytes (v0.12.0 baseline 23187). **D-20 holds**:
  the skill-size check passes, detail lives in the doc.
- **`setup-user`** v7 -> v8: "Proposing the upgrade" lists each project that
  needs migration with `/daikenja:setup-project <key>`, proposes no edit for
  the config keys, stamps the version as usual. 21845 -> 22747 bytes (v0.12.0 baseline 21290).
- **D-22 holds**; its revisit case (no registered root) is handled by asking
  with no suggestion. `rev-parse` runs on the nearest existing folder, since
  the target usually does not exist yet.
- `docs/upgrading.md` `## [Unreleased]`: new five-part section "Your old
  ledger migrates to `DECISIONS.md` and `open.md`" plus the bot operator
  sequence (update plugin, `setup-user` + migrate, pull bot checkout,
  restart, `--check`); S1's section now says setup-user does it *through*
  setup-project. `CHANGELOG.md` `### Changed` entry (D-14: S8 writes its own).

Acceptance (run in `../daikenja-s8`):

```
$ python3 tests/check-invariants.py
All invariant checks passed.
$ BASE_SHA=$(git merge-base HEAD origin/feat/292-replace-ledger-decisions-md-open) HEAD_SHA=$(git rev-parse HEAD) python3 tests/check-skill-size.py
check-skill-size: no file crossed the size trigger.
$ grep -n "ledger-format" docs/ledger-migration.md
(exit 1, no output)
```

Walks, in a scratch folder (`C:/` -> `<scratch>/C`, `~` -> `<scratch>/home`),
each input copied out of `tests/fixtures/ledger-migration.md`, each git repo
`git init`-ed, steps run in the procedure's order (backup copy, the two
files, config edit, card move, `cmp` then remove). Every resulting ledger file
was compared with the fixture's expected block (template comment masked):
all MATCH.

**Input A (atlas, synthetic ledger).** Reading: D-005 and D-002 carry
`superseded by` tails (chain D-002 -> D-005 -> D-007), D-004 carries the
malformed `-> superseded D-008`, and Open items has one unparsable line
(`- [ ] 2026-08-18 -- @gobta -- Book the cutover war room.`). Result:

```
$ find . -path ./.git -prune -o -type f -print | sort
./.daikenja/ledger.2026-11-03.bak.md
./.daikenja/open.md
./.daikenja/project.md
./DECISIONS.md
$ git status --short
 D .daikenja/ledger.md
?? .daikenja/ledger.2026-11-03.bak.md
?? .daikenja/open.md
?? DECISIONS.md
$ cat ~/.claude/daikenja/daikenja.yaml
projects:
  atlas:
    path: C:/GitHub/atlas
$ grep -n "Cut over on a weekday evening" DECISIONS.md      # superseded D-002
(exit 1, no output)
$ grep -n "Cut over on a weekday evening" .daikenja/ledger.2026-11-03.bak.md
11:- 2026-08-08 -- D-002 -- @rimuru -- Cut over on a weekday evening. [thread](https://example.com/t/4417) -> superseded by D-005
$ grep -c "Saturday, not a weekday" DECISIONS.md            # superseded D-005
0
```

`DECISIONS.md`:

```markdown
<!-- decisions-format: 1 -->
# Decisions

Decisions in force. Read the area that covers a path before changing it; add
or edit an entry in the same pull request when a change settles something
future work must respect.

<!-- template comment, byte-identical to templates/ -->

## Migration

Paths: `.`

- **Cut over on a Sunday morning, not a Saturday.** — the data team's
  Saturday batch overlaps the window. Revisit: if the cutover date moves.
  Source: https://example.com/atlas/runbook
- **Every service writes to the shared audit log.** — imposed by the platform
  programme's architecture board. Revisit: never.
- **Keep the legacy read replica online for 30 days after cutover.** —
  rollback reads from the replica. Revisit: if finance rejects the replica
  cost.
- **Freeze schema changes from 2026-08-20 until cutover completes.** — two
  teams have pending migrations and both agreed to hold. Revisit: if the
  cutover date moves.
- **Atlas replaces the legacy store, with no dual-write period.** — running
  two stores doubles the reconciliation work. Revisit: never.
```

`.daikenja/open.md`:

```markdown
<!-- daikenja-open-format: 1 -->
# atlas open items

<!-- template comment, byte-identical to templates/ -->

## Open items

- 2026-08-19 -- @benimaru -- Blocked by: who signs off audit-log exemptions. Confirm whether the gateway can be exempted from the shared audit log, which DECISIONS.md makes binding.
- 2026-08-18 -- @gobta -- Book the cutover war room.
- 2026-08-16 -- @unassigned -- Find out who signs off audit-log exemptions.
- 2026-08-13 -- @gobta -- Confirm the 30-day replica cost with finance. [budget sheet](https://example.com/atlas/budget)
- 2026-08-11 -- @shion -- Write the rollback runbook and dry-run it once.
  The dry run needs a full-size dataset.

## Context links

- Runbook -- https://example.com/atlas/runbook
- Legacy store schema -- ./docs/legacy-schema.md

## Sources

- Platform standards page -- https://example.com/wiki/standards
  modified: 2026-08-10T09:12Z
  read: 2026-08-11
  covers: the mandatory controls and which services they bind.
```

**Input B1 (q4-planning, no folder; default target).**

```
config before:  q4-planning: {paths: [], ledger: ~/.claude/daikenja/ledgers/q4-planning.md, last_checkpoint: 2026-09-10T08:00Z}
nearest existing: C/GitHub
$ git -C C:/GitHub rev-parse --show-toplevel
fatal: not a git repository (or any of the parent directories): .git   (exit 128 -> new folder + git init)
config after:
  q4-planning:
    paths:
      - C:/GitHub/q4-planning
$ ls ~/.claude/daikenja/ledgers
q4-planning.2026-11-03.bak.md
$ (in C:/GitHub/q4-planning) find . -path ./.git -prune -o -type f -print | sort; ls -d .git
./.daikenja/open.md
./.daikenja/project.md        <- moved from ledgers/q4-planning.project.md
./DECISIONS.md
.git
$ grep -c "closes at the end of October" DECISIONS.md      # superseded D-001
0
```

`DECISIONS.md`:

```markdown
<!-- decisions-format: 1 -->
# Decisions

Decisions in force. Read the area that covers a path before changing it; add
or edit an entry in the same pull request when a change settles something
future work must respect.

<!-- template comment, byte-identical to templates/ -->

## Planning

Paths: `.`

- **Planning closes on 2026-10-15, not at the end of October.** — finance
  locks budgets on the 20th. Revisit: if finance moves its lock date.
```

`.daikenja/open.md`:

```markdown
<!-- daikenja-open-format: 1 -->
# q4-planning open items

<!-- template comment, byte-identical to templates/ -->

## Open items

- 2026-09-05 -- @benimaru -- Collect the platform team's headcount ask.

## Context links

- Planning space -- https://example.com/wiki/q4-planning

## Sources
```

The approval line is the fixture's Walk B1 step 3 text (content moves from a
private folder into a repository).

**Input B2 (suggested target inside a repository).**

```
suggested: C/Work/notes/q4-planning  nearest existing: C/Work/notes
$ git -C C:/Work/notes rev-parse --show-toplevel   -> C:/Work/notes (exit 0)
-> names the repository and asks; nothing proposed or written
$ ls -A C:/Work/notes
.git
harbor-notes
```

On "use it", the same private-folder line opens the proposal, naming
`C:/Work/notes`.

**Input C (quill, ledger and card at a non-default location).**

```
config before:  quill: {path: C:/GitHub/quill, ledger: docs/records/quill-ledger.md}
config after:
  quill:
    path: C:/GitHub/quill
$ find . -path ./.git -prune -o -type f -print | sort
./.daikenja/open.md
./.daikenja/project.md                         <- moved from docs/records/quill-ledger.project.md
./DECISIONS.md
./docs/records/quill-ledger.2026-11-03.bak.md   <- old ledger renamed beside itself; nothing stranded
```

**Input D (lantern, existing `DECISIONS.md`).**

```
$ diff DECISIONS.before DECISIONS.md          # only additions
13a14,20
> 
> ## API
> 
> Paths: `src/api/`
> 
> - **Every endpoint is versioned in the path, never by header.** — clients
>   cache by URL. Revisit: if a gateway takes over versioning.
$ grep -n "Releases are cut from tags only" DECISIONS.md
12:- **Releases are cut from tags only, never from a branch.** — a branch build
$ find . -path ./.git -prune -o -type f -print | sort
./.daikenja/ledger.2026-11-03.bak.md
./DECISIONS.md
```

D-001 (tag-only) is a duplicate of the Release entry and is not added; no
`open.md`, since nothing moves into it.

Follow-ups (not this stage's):

- **S9 / an issue:** `project-log-reference.md` § A batch handed over by
  another skill exempts the migration batch from "the unmigrated-ledger
  refusal" only; `ledger-migration.md` § The proposal also exempts it from
  the `paths: []` stop (`project-log` Step 2 items 2 and 4), since the batch
  names its targets by absolute path. One sentence there would align them.
- **S9:** `config-writers.md` -- the card row says no skill moves a card, and
  `daikenja.yaml`'s projects row does not mention the migration's edit
  (dropping `ledger:` / a timestamp `last_checkpoint`) or the backup rename.
  `config-resolution.md` § Legacy keys says "the migration in `setup-user`";
  it runs in `setup-project` now, reached from `setup-user`.
- **S9:** user guide pages (`docs/guide/`) for the migration and the
  `setup-project <key>` argument.
- **SF:** the pathless backup name (`<key>.<date>.bak.md`, not
  `ledger.<date>.bak.md`) -- accept or amend D-11.

Actuals: not recorded -- cloud session, `scripts/effortlog.py` (plugin) not available. Session 2026-11-03.
Artifacts check: match (by hand, `git diff --name-only` against the plan branch -- every path is in `## Artifacts`; `scripts/artifacts_check.py` not available in this cloud session)

### S9 User guide, README and retiring ledger-format.md

As built:

- **Guide and README.** `docs/guide/ledger.md` rewritten around the two files:
  what each holds (with an example of each), where they live (every
  repository's `DECISIONS.md`, `open.md` in home), adoption of an existing
  `DECISIONS.md`, `project-log` never commits (D-6), catchup from git with the
  unresolvable-SHA first run and "not committed yet", the two notices
  (needs migration, newer format -- D-4), "Projects without a folder are gone"
  (D-15), § Moving from the old ledger, card at `.daikenja/project.md`. Other
  pages link to that page rather than restating it. `install.md` § A project
  with no folder became **§ A project that is not code** (the `git init` and
  new-folder offers); the anchor changed and every inbound link was moved.
  `faq.md` gains "Where did my project with no folder go?" and "I logged
  something, but my colleagues cannot see it". `commands.md`: `project-log`
  takes no name; `setup-project <name>` migrates. `slack-bot.md` gains the
  fixed unreadable-ledger line (S7 follow-up), the "reads files, never git"
  note, and **§ After a Daikenja update** with the five-step operator sequence
  (F12). "Ledger" kept throughout (D-7). README: two files plus git, a
  `DECISIONS.md` example replacing the old ID line, and the D-15 sentence.
- **Diagrams.** `how-it-works.svg` (Record card names both files; catchup reads
  git; footer says you commit) and `where-data-lives.svg` (project column is
  the repository: `DECISIONS.md`, `.daikenja/open.md`, card). Both rendered
  with Playwright and checked for overflow; `<desc>`/`aria-label` updated and
  the README and `your-data.md` alt text kept identical to them.
- **Changelog (D-14).** Entries for S0 and S7 under Added; S2, S3 (catchup and
  decisions), S4, S5, S6 and this stage under Changed; the spec/template
  retirement under Removed. S1's Removed entry already says plainly that
  pathless projects are gone (D-15); S6's entry repeats it in user words.
- **Retirement.** Deleted `docs/ledger-format.md`, `templates/ledger.md` and
  `tests/fixtures/ledger-backfill.md` (the only fixture depending on the old
  spec). Check (e) is now **format version lines**: both specs and both
  templates start with their version line and each template matches its spec;
  negative-tested (version 2 in `templates/open.md`, and a removed line 1) --
  both fail as expected. `upgrading.md` 0.3.0 note now names the file as plain
  code text. `docs/README.md` lists `decisions-format.md`, `open-format.md`
  and `ledger-migration.md` (S0/S1 follow-up). CONTRIBUTING, `CLAUDE.md` and
  `AGENTS.md`: the frozen grammar is each file's version line and the
  `open.md` item line (` -- `, two-split bound); `decisions-format.md` is
  changed upstream, then copied.
- **`tests/README.md`** (a fixture was removed, so D-14 allows the edit):
  check (e) description, the `Depends on:` example, and the stale descriptions
  of `owner-handles.md`, `ledger-relationships.md`, `dictated-log-requests.md`,
  `sources-ledger.md`, `project-card.md` and `project-resolution.md` now match
  what those fixtures hold (S2 and S4 follow-ups).

**Outside Artifacts** (both forced by the deletion's link check and the
acceptance grep): `docs/future-work.md` -- § The ledger rewritten from body
markers to `Blocked by:` by words (S1 follow-up), and the `project-log` fork
paragraph points at the two new specs; `templates/README.md` -- the
`ledger.md` bullet removed.

Acceptance (run in `../daikenja-s9`, plan branch `03f8df1` unchanged since
the stage branched, so no sibling re-sync):

```
$ python3 tests/check-invariants.py
All invariant checks passed.
$ git grep -nE "pathless|ledgers/" -- README.md docs/guide
(exit 1, no output)
$ test ! -e docs/ledger-format.md && echo gone
gone
$ wc -l docs/decisions-format.md docs/open-format.md
  161 docs/decisions-format.md
  199 docs/open-format.md
$ git grep -n "ledger-format.md" -- . ":!.plan" ":!CHANGELOG.md" ":!docs/upgrading.md"
(exit 1, no output)
$ test ! -e templates/ledger.md && echo gone
gone
$ (cd bot && python -m pytest tests -q)
477 passed, 11 subtests passed in 0.86s
```

Done check 5, exactly as `PLAN.md` writes it -- every hit outside
`CHANGELOG.md` and `docs/upgrading.md` history is D-21 legacy handling (the
rule, or a test/fixture exercising it):

```
$ git grep -nE "pathless|paths: \[\]|daikenja/ledgers" -- . ":!.plan" ":!docs/ledger-migration.md" ":!tests/fixtures/ledger-migration.md" ":!tests/fixtures/setup-user-upgrade.md"
CHANGELOG.md:196,200,1045,1051,1076,1344,1345,1349,1356       (history; S1's Removed entry)
bot/tests/test_main.py:118            "  atlas:\n    paths: []\n"  (S7's needs-migration test input)
docs/config-resolution.md:191         D-21 § Legacy keys and unmigrated ledgers
docs/project-log-reference.md:231     D-21 failure row: paths: [] -> needs migration
docs/upgrading.md:49,78,82,94,261,534,535,558,580   (Unreleased note + released history)
skills/project-gaps/SKILL.md:126      D-21 failure row
skills/project-list/SKILL.md:80,209   D-21 reporting
skills/project-log/SKILL.md:106       D-21 refusal
skills/project-sources/SKILL.md:153   D-21 failure row
skills/project-summary/SKILL.md:149   D-21 failure row
tests/fixtures/ledger-location.md:113,114,129          Config D: legacy no-paths entry -> needs migration
tests/fixtures/project-resolution.md:52,53,63,100,116,121,132,135   Walks 3-3c: legacy entry -> needs migration
```

`tests/README.md` no longer hits: its two descriptions that did were stale and
were reworded. The two fixtures' walk headings still say "a pathless project"
for the legacy entry they test; left as fixture content, not a claim -- SF
may want them renamed.

Follow-ups (not this stage's -- for SF to route):

- **S5's rename**, assigned to S9 but outside its Artifacts and touching eight
  skills: `response-format.md` § "Entries are named topic-first, ID in
  parentheses" -> drop "ID in parentheses", with its reverse index, the citing
  skills' `Depends-on` lines, `docs/README.md:52` and
  `skills/compose/SKILL.md:191`. Not done here: it changes skill files and
  `check-skill-size` baselines, which this docs stage does not own.
- **S8's doc gaps**, outside Artifacts: `config-writers.md` card row ("no skill
  moves a card") and `daikenja.yaml` projects row (the migration's edit and
  backup rename); `config-resolution.md` § Legacy keys still says "the
  migration in `setup-user`" (it runs in `setup-project`, reached from
  `setup-user`); `project-log-reference.md` § A batch handed over by another
  skill exempts the migration batch from the unmigrated-ledger refusal only,
  while `ledger-migration.md` also exempts it from the `paths: []` stop.
- S3: `config-writers.md`'s reverse index does not list `project-catchup`.
- `tests/fixtures/project-resolution.md` intro says "ten walks"; it has
  twelve `## Walk` headings (3b-3d) -- predates this stage.

Actuals: not recorded -- cloud session, `scripts/effortlog.py` (plugin) not available. Session 2026-11-03.
Artifacts check: outside: docs/future-work.md, templates/README.md (by hand, `git diff --name-only` against the plan branch; `scripts/artifacts_check.py` not available in this cloud session)

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

### S10 Fix: align the migration batch exemption

Added by SF — `project-log`'s text stops a no-folder migration that `docs/ledger-migration.md` exempts, so a pathless ledger cannot migrate as written (#292 item 5, Done check 6) — referee: grows

Preflight (2026-11-04): clone clean and synced on the plan branch, not ahead,
brief stamp current (`a99ce0485efb`), no `BLOCKED.md`, S9 merged (#318). No
root `DECISIONS.md` yet (D-12 lands it at close), so no decisions in force to
show. Same S3 orphan SF reported (worktree entry for the gone
`../daikenja-s3` and local branch `...-s3`, PR #314 merged): not removed.
Weight: opus / effort `medium` (`CLAUDE_EFFORT=medium`), matches the index.

**Changes.**
- `skills/project-log/SKILL.md` Step 2: one sentence at the step's head says
  the migration's batch skips config resolution, so item 2's no-paths stop and
  item 4's `paths: []` and unmigrated-ledger refusals do not apply to it; the
  per-item "unless the batch is the migration's own" clause in item 4 is gone,
  so it is said once. Every other run is unchanged.
- `docs/project-log-reference.md` § A batch handed over by another skill: the
  bullet now exempts the batch from both refusals, in
  `ledger-migration.md`'s words.
- `docs/config-resolution.md` § Legacy keys: "the migration in
  `setup-project`, reached from `setup-user`".
- `docs/config-writers.md`: card row names the migration's card move as the
  one exception; projects row names the migration's entry edit (drop
  `ledger:`, remove a timestamp `last_checkpoint`, set `paths` for a no-folder
  project) and the backup rename; reverse index lists `project-catchup` "Step
  0: read the contracts" and "Step 5: propose and write the checkpoint".
- `CHANGELOG.md` `## [Unreleased]` › Changed: one bullet. No
  `docs/upgrading.md` entry -- nothing on disk changes.
- `tests/fixtures/ledger-migration.md` unchanged: the expected output does not
  change.

**The three sentences.**
- `skills/project-log/SKILL.md` Step 2: "**The migration's own batch skips
  this resolution**: it names its targets by absolute path, so item 2's
  no-paths stop and item 4's `paths: []` and unmigrated-ledger refusals do not
  apply to it (`project-log-reference.md` § A batch handed over by another
  skill)."
- `docs/project-log-reference.md` § A batch handed over by another skill:
  "The refusals for an unmigrated ledger and for an entry with no paths do not
  apply to this batch -- it is the run both point at -- and every other check
  does."
- `docs/ledger-migration.md` § The proposal (unchanged): "the refusals for an
  unmigrated ledger and for an entry with no paths do not apply to this batch,
  and every other check does."

**No-folder walk** (`tests/fixtures/ledger-migration.md` Input B, Walk B1,
`/daikenja:setup-project q4-planning`, entry `paths: []`), through the changed
text:
1. `ledger-migration.md` § Writing, in order: after the one yes, step 1 runs
   `git init` in `C:/GitHub/q4-planning`; step 2 copies the old ledger to
   `q4-planning.2026-11-03.bak.md`.
2. Step 3 hands the batch to `project-log` as `project-log via setup-project`,
   targets named by absolute path (`C:/GitHub/q4-planning/DECISIONS.md`,
   `C:/GitHub/q4-planning/.daikenja/open.md`). The config entry still reads
   `paths: []` (the config edit is step 4).
3. `project-log` Step 2: the head sentence applies -- the batch is the
   migration's own, so resolution is skipped. Item 2 (named key with no
   paths: stop) does not fire; item 4's `paths: []` stop does not fire; the
   unmigrated-ledger refusal does not fire (and would not match anyway: no
   `ledger.md` in the new home). Item 5's version notice is n/a.
4. `project-log` Step 3: neither file exists. Target directory
   `C:/GitHub/q4-planning` is not the OS home or `~/.claude`; it now has
   `.git` (writing step 1), so the not-a-repository question is skipped; the
   scaffold folds into the approval: `DECISIONS.md` from the template as it
   stands, `open.md` with `{{PROJECT}}` -> `q4-planning`.
5. Steps 4-8 run as for any batch (version refusal n/a on fresh templates,
   duplicate check against empty files, one approval -- the migration's whole
   yes), and `project-log` writes both files, matching the fixture's expected
   `DECISIONS.md` and `open.md`. Migration steps 4-6 then set `paths`, move
   the card and remove the old ledger. Result: matches; fixture unchanged.

Before this stage the walk stopped at step 3: item 2 (and item 4's
`paths: []` line) fired, ending the migration after `git init` and the backup
copy.

**Acceptance.**

```
$ python3 tests/check-invariants.py
All invariant checks passed.
$ BASE_SHA=origin/feat/292-replace-ledger-decisions-md-open HEAD_SHA=HEAD python3 tests/check-skill-size.py
check-skill-size: no file crossed the size trigger.
$ git grep -n "migration in .setup-user" -- docs
(no output, exit 1)
```

`skills/project-log/SKILL.md` 19676 -> 19880 bytes.

Actuals: 2026-11-03T12:23:11.098Z → 2026-11-03T12:26:14.237Z · 3 min · tokens in=60 out=10573 cache_read=3489879 cache_write=94580 · subagents=0

Artifacts check: match

### SF Plan review

Preflight (2026-11-04): clone clean and synced, plan branch not ahead, brief
stamp current (`d41461f3ebfd`), no `BLOCKED.md`, S9 merged (#318). One
**orphan**: a `git worktree list` entry for `../daikenja-s3` whose directory is
gone, and the local branch `feat/292-replace-ledger-decisions-md-open-s3`
(PR #314 merged). Not removed; closeout sweeps it.

#### Loose ends

Every loose end from the notes blocks, the Out of scope line and the
`Artifacts check:` lines, each with one outcome. Items the notes record as
settled by a later stage were re-checked in the tree and are listed as
resolved.

1. **Migration batch exemption disagrees** (S8, S9 follow-up).
   `docs/ledger-migration.md` § The proposal exempts the migration's batch
   from both the unmigrated-ledger refusal and the `paths: []` stop;
   `skills/project-log/SKILL.md` Step 2 item 4 and
   `project-log-reference.md` § A batch handed over by another skill exempt it
   from the first only. The config edit runs *after* `project-log` writes
   (§ Writing, in order, step 4 after step 3), so a pathless project's entry
   still reads `paths: []` when `project-log` resolves it: followed as
   written, the skill stops, and a no-folder migration ends after `git init`
   and the backup copy. Repairs #292 item 5 and Done check 6. -> **fix: S10** (maintainer's
   yes, 4 Nov 2026).
2. **`config-resolution.md` § Legacy keys says "the migration in
   `setup-user`"** (line 187); it runs in `setup-project`, reached from
   `setup-user` (S8, S9). -> **fix: S10**, with 1.
3. **`config-writers.md` card and projects rows** omit the migration: the card
   row says an existing card is never touched by any skill, and the
   `daikenja.yaml` projects row does not mention the migration's edit or the
   backup rename (S8, S9). -> **fix: S10**, with 1.
4. **`config-writers.md` reverse index** does not list `project-catchup`,
   which cites § Who writes what (S3, S9). -> **fix: S10**, with 1.
5. **`response-format.md` heading "Entries are named topic-first, ID in
   parentheses"** -- the body is right (entries carry no IDs; the parentheses
   hold the repository or `open item`), only the heading's name is stale, with
   its citations in eight skills' `Depends-on` lines, `docs/README.md:59` and
   `skills/compose/SKILL.md:191` (S5, S9). Touches skill files and size
   baselines. -> **issue**: by-carlos/daikenja#319 (filed 4 Nov 2026).
6. **`project-log <key>` from outside the project** could now be allowed,
   since files sit at fixed paths (S2). A feature, changes
   `project-resolution.md` walk 3d. -> **issue**: by-carlos/daikenja#320 (filed 4 Nov 2026).
7. **Pathless backup name** is `<stem>.<YYYY-MM-DD>.bak.md`
   (`q4-planning.<date>.bak.md` for `ledgers/q4-planning.md`), not D-11's
   `ledger.<date>.bak.md` (S8). -> **accepted, won't fix**: the stem form
   generalises D-11 so two no-folder projects in one folder never collide;
   the kept decision states the stem form.
8. **`tests/fixtures/judgement.md` Walks 1-3** show an older answer shape
   (`Verdict:` lines) than the skill's markers (S5). -> **accepted, won't
   fix** in this plan: predates it and touches nothing it changed.
9. **`tests/README.md:314` says "ten walks"** for `project-resolution.md`,
   which has twelve (S9). -> **accepted, won't fix**: predates the plan,
   cosmetic.
10. **`project-resolution.md` walk headings say "a pathless project"** (S9).
    -> **accepted, won't fix**: they name the legacy D-21 input the walks
    test, which Done check 5 allows.
11. **`sources-ledger.md`'s `project-catchup` and `project-log` lines are
    minimal** (S4). -> **accepted, won't fix**: correct, and the invariants
    pass; sharpening is optional.
12. **`docs/open-format.md` is at 199 lines** against the 200-line target
    (S0). -> **accepted, won't fix**: any later addition needs a matching cut;
    #292's target, not a defect.
13. **`Artifacts check: outside:` S1** -- `docs/ledger-format.md`,
    `skills/project-list`, `project-log`, `setup-project` `SKILL.md`. ->
    **accepted, won't fix**: one-phrase citation repoints of a renamed
    heading, forced by S1's acceptance grep; routine.
14. **`Artifacts check: outside:` S9** -- `docs/future-work.md`,
    `templates/README.md`. -> **accepted, won't fix**: de-links forced by the
    `ledger-format.md` deletion's link check; routine, and within the
    retirement S9 was for.
15. **No `Actuals:` for S6, S8, S9, and their artifacts checks done by hand**
    (cloud sessions without the plugin's scripts). -> **accepted, won't
    fix**: closeout's estimate sums cover S0-S5 and S7 only, and says so.
16. **D-21 "revisit after the first real upgrade"** (Default for now). ->
    **accepted, won't fix** as a loose end: an event, not a date, so it
    travels as the revisit clause of D-21's kept entry.
17. **Orphan worktree entry and branch for S3** (preflight). -> **accepted,
    won't fix** here: closeout sweeps merged worktrees and branches.

Resolved before this stage, re-checked in the tree: `docs/README.md` lists the
new specs (S0, S1); `templates/README.md` wording (S0); `future-work.md` body
markers (S1); `tests/README.md` stale descriptions (S2, S4);
`sample-thread*.md` and `malformed-ledger.md` hold no old-grammar IDs or
Changelog lines (S2, S3); `ledger-relationships.md` aligned (S2, S4);
`ledger-backfill.md` and `ledger-format.md` reverse-index notes gone with the
files (S3, S5); guide pages for no-folder projects, migration and the bot line
(S6, S7, S8). Out of scope records **no dated follow-ups**. D-20 and D-22
revisits ran at S8 and both held.

#### #292 "When this closes"

1. Spec replaces `ledger-format.md`, identical upstream copy, under 200 lines
   -- **met**: Done checks 3 and 4 below.
2. `project-log` writes both files in one batch; readers and the bot read
   them; catchup works from git -- **met**: S2, S3-S5, S7 rows; bot 477 tests
   pass.
3. Pathless projects gone; `setup-project` offers `git init` -- **met**: Done
   check 5 below hits only history and D-21 handling; `setup-project`
   frontmatter and Step 2 carry the `git init` offer (S6).
4. Home repository chosen at `setup-project`; readers read every
   `DECISIONS.md` -- **met**: S6 (home asked and written first), S3/S4
   two-repository walks.
5. Migration, pathless included, approved, dated backup, upgrade note --
   **met as walked** (S8, four fixture inputs; `upgrading.md` § Your old
   ledger migrates), **with loose end 1**: the skills' own text would stop a
   pathless migration at `project-log`.
6. Fixtures and invariant checks updated -- **met**: Done check 1 below.
7. Changelog entry under `## [Unreleased]` -- **met**: `CHANGELOG.md:8`, with
   Added, Changed and Removed sections (S1, S8, S9).

#### Done checks 1-5 (run in `../daikenja-sf` at `9309e61`)

```
$ python3 tests/check-invariants.py
All invariant checks passed.
$ python -m pytest bot/tests -q
477 passed, 11 subtests passed in 1.54s
$ cmp docs/decisions-format.md <by-carlos/plan-staged-rollout main: skills/staged-rollout/references/decisions-format.md>
(identical -- no output, exit 0)
$ test ! -e docs/ledger-format.md && echo gone; wc -l docs/decisions-format.md docs/open-format.md
gone
  161 docs/decisions-format.md
  199 docs/open-format.md
$ git grep -nE "pathless|paths: \[\]|daikenja/ledgers" -- . ":!.plan" ":!docs/ledger-migration.md" ":!tests/fixtures/ledger-migration.md" ":!tests/fixtures/setup-user-upgrade.md" | cut -d: -f1 | sort | uniq -c
      9 CHANGELOG.md
      1 bot/tests/test_main.py
      1 docs/config-resolution.md
      1 docs/project-log-reference.md
      9 docs/upgrading.md
      1 skills/project-gaps/SKILL.md
      2 skills/project-list/SKILL.md
      1 skills/project-log/SKILL.md
      1 skills/project-sources/SKILL.md
      1 skills/project-summary/SKILL.md
      3 tests/fixtures/ledger-location.md
      8 tests/fixtures/project-resolution.md
```

Same files and counts as S9's run. Every hit outside `CHANGELOG.md` and
`docs/upgrading.md` is a D-21 rule line (`paths: []` -> needs migration) or a
test/fixture exercising it.

#### #293 note (posted 4 Nov 2026 after the maintainer's yes, comment 6603263432; read back identical)

> Since #292 landed, the ledger is `DECISIONS.md` plus `.daikenja/open.md`,
> and this issue's references to `docs/ledger-format.md` (lines 487-574) point
> at a deleted file. What changed for Sources:
>
> - **Where it lives:** `## Sources` in `<home>/.daikenja/open.md`, the home
>   repository being the first entry of `paths`. The grammar is
>   `docs/open-format.md` § Section: Sources; read that in place of the
>   `ledger-format.md` Sources section in the prompt's read-first list.
> - **Shape:** unchanged except for the ID. A head line `- <label> -- <url or
>   path>` (no `S-001 --`), then the same optional two-space-indented fields,
>   in order: `modified:`, `read:`, `covers:`, `does not answer:`. Contents are
>   still never fetched.
> - **History and versioning:** no IDs, no Changelog; the record of what
>   changed is `git log` on the file. `open.md` starts with
>   `<!-- daikenja-open-format: 1 -->`, so a change to the Sources grammar is a
>   version bump: reading skills warn on a newer version, `project-log` refuses
>   to write. `open-format.md` is at 199 lines against a 200-line target, so
>   an addition needs a matching cut.
> - **Every project now lives in a git repository**; projects without a folder
>   are gone, which matters for where a glossary file "beside the ledger" goes.

#### Fixes

1. S10 Fix: align the migration batch exemption -- repairs #292 "When this
   closes" item 5 and Done check 6 (loose ends 1-4). Approved by the
   maintainer on 4 Nov 2026; referee: grows.

Every loose end above maps to exactly one outcome: fix S10 (1-4), issue
(5, 6), accepted, won't fix (7-17). Fixes used: 1 of 3.

**This pass added a fix**, so it wrote no `DECISIONS.md`, README change or
pointer line: Decision triage, README and cold reader wait for the redo. SF's
row is back to `todo`; once S10 is `done`, SF re-runs from the top as a redo
(`feat/292-replace-ledger-decisions-md-open-sf-redo-1`, `../daikenja-sf-redo-1`).

Actuals: 2026-11-03T11:29:23.827Z → 2026-11-03T12:20:29.632Z · 51 min · tokens in=156 out=53977 cache_read=11740225 cache_write=422491 · subagents=3
Artifacts check: match

#### Redo 1 (2026-11-04, `feat/292-replace-ledger-decisions-md-open-sf-redo-1`)

Run unattended (fired by a driver session): plan-flag defaults apply, nothing
was posted, and the kept-decisions list is applied for approval at the
plan→main merge.

Preflight: clone clean, synced and not ahead at `c01d95c`; brief stamp current
(`a99ce0485efb`); no `BLOCKED.md`; S9 (#318) and S10 (#322) merged; no stage
branch or worktree for SF. Same S3 orphan (worktree entry for the gone
`../daikenja-s3`, local branch `...-s3`, PR #314 merged): not removed. No root
`DECISIONS.md` before this run, so no decisions in force to show. Weight: opus
/ effort `high` (`CLAUDE_EFFORT=high`), matches the index.

**Loose ends, from the top.** Pass 1's items 1-17 re-checked against the tree:

- 1-4 (fix S10) -- **resolved by S10**, checked in the tree:
  `skills/project-log/SKILL.md` Step 2 head sentence exempts the migration's
  batch from item 2's no-paths stop and item 4's `paths: []` and
  unmigrated-ledger refusals, and names `setup-project`'s seed as resolving
  like every other run; `project-log-reference.md` § A batch handed over by
  another skill matches; `config-resolution.md:187` reads "the migration in
  `setup-project`, reached from `setup-user`"; `config-writers.md` card and
  projects rows name the migration, and its reverse index lists
  `project-catchup`. `git grep -n "migration in .setup-user" -- docs skills`:
  no output.
- 5, 6 -- issues #319 and #320, filed in pass 1. Unchanged.
- 7-17 -- accepted, won't fix, reasons as in pass 1. Unchanged.

A full re-read of every notes block (S0-S10) found these not in pass 1's
catalogue; each now has one outcome:

18. **Bot `--check` reads only the root `DECISIONS.md` for its version
    check**, not a `Moved:` sub-folder file (S7), so it can call a project
    readable where a skill would warn. -> **issue**, under `closeout will
    list` below.
19. **The bot hard-codes format version 1 for both files** (S7). ->
    **accepted, won't fix**: a version bump is a scoped format change
    (CLAUDE.md § Ledger format), which updates the bot with the skills.
20. **A same-turn dictation counts as the batch's approval** (S2's recorded
    assumption, not a frozen decision). -> **accepted, won't fix**: the
    entries are the user's own words, shown once, which is the approval #292
    asks for.
21. **No version line reads as version 1**, beyond D-4's wording (S0). ->
    **accepted, won't fix**: the rule is in the shared spec and
    `open-format.md`, so it is documented where readers look.
22. **Catchup's SHA commands need `--end-of-options`** (git 2.24 or later;
    checked on 2.56, S3). -> **accepted, won't fix**: 2.24 shipped in 2019,
    and an older git fails loudly, not silently.
23. **`ledger-location.md` and `setup-user-upgrade.md` left as written in S4**.
    -> **resolved**: the only old-grammar mention
    (`ledger-location.md:191`) describes the legacy input D-21 detects;
    invariants pass.
24. **Stale S2/S6/S1 hand-offs** (`meeting-review`/`setup-project` writer
    field, setup-project's "does not migrate", the card move). -> **resolved**:
    no Changelog writer field in either skill; `setup-project` line 451 now
    reads "does not migrate a project on its own initiative"; S8 moves the
    card.
25. **"Ten walks" location** -- S9's note puts it in the fixture's intro;
    it is `tests/README.md:314` (twelve walks in
    `tests/fixtures/project-resolution.md`). -> **accepted, won't fix**, as
    item 9.
26. **`LocalPathTests` docstring quotes the old `.daikenja/ledger.md` path**
    from a real run (S7). -> **accepted, won't fix**: a quotation, and Done
    check 5 does not match it.
27. **Pathless backup written `<key>` in S8's follow-up, `<stem>` elsewhere**.
    -> **accepted, won't fix**: covered by item 7; `ledger-migration.md:163`
    says `<name>.<YYYY-MM-DD>.bak.md`, and the kept entry says the same.
28. **How `project-log` tells the migration's batch from the seed** (S10). ->
    **accepted, won't fix**: by origin, stated in both texts -- Step 2 names
    the seed as resolving, and the reference names the migration's batch by
    its absolute-path targets.
29. **S10 re-walked only Input B1** (S10). -> **accepted, won't fix**: the
    exemption changes only the no-paths stops, which only a `paths: []` entry
    reaches; Inputs A, B2, C and D carry paths.
30. **Wording differs between the two exemption sentences** ("it is the run
    both point at", S10). -> **accepted, won't fix**: an explanatory clause;
    the rule is the same.
31. **S10's stale-phrase grep covered `docs/` only**. -> **resolved**: re-run
    over `docs skills`, no output.
32. **Typos and blank lines in the ledger notes** (S6 "a no writes nothing",
    S10's blank line before `Artifacts check:`). -> **accepted, won't fix**:
    `.plan/` is deleted at closeout.

Every loose end maps to exactly one outcome: fix S10 (1-4, resolved), issue
(5, 6, 18), accepted, won't fix (7-17, 19-22, 25-30, 32), resolved (23, 24,
31). No new fix: this is a **clean pass**. Fixes used: 1 of 3.

#### closeout will list

- **Issue: bot `--check` skips `Moved:` decisions files.** `--check`'s format
  version check (`project_data_states` in `bot/`) reads the root
  `DECISIONS.md` only; `docs/reading.md` has skills check every file they
  read, `Moved:` files included. Make `--check` follow `Moved:` lines, with a
  test. Not dated.
- **#293 note:** posted in pass 1 after the maintainer's yes (comment
  6603263432); nothing to post.

#### #292 "When this closes" (redo)

1. Spec replaces `ledger-format.md`, identical copy, under 200 lines --
   **met**: Done checks 3 and 4.
2. `project-log` writes both files in one approved batch; readers and the bot
   read them; catchup from git -- **met**: S2, S3-S5, S7; bot tests pass.
3. Pathless projects gone; `setup-project` offers `git init` -- **met**: Done
   check 5 hits only history and D-21 handling; S6.
4. Home repository chosen at `setup-project`; readers read every
   `DECISIONS.md` -- **met**: S6, S3/S4 two-repository walks.
5. Migration, pathless included, approved, dated backup, upgrade note --
   **met**: S8's four fixture inputs, and S10's no-folder walk through the
   changed `project-log` text; `upgrading.md` § Your old ledger migrates.
6. Fixtures and invariant checks updated -- **met**: Done check 1.
7. Changelog entry under `## [Unreleased]` -- **met**: `CHANGELOG.md`, Added,
   Changed and Removed, plus S10's Changed bullet.

#### Done checks 1-5 (redo, run in `../daikenja-sf-redo-1` at `c01d95c`)

```
$ python3 tests/check-invariants.py
All invariant checks passed.
$ python -m pytest bot/tests -q
477 passed, 11 subtests passed in 1.54s
$ cmp docs/decisions-format.md <by-carlos/plan-staged-rollout main: skills/staged-rollout/references/decisions-format.md>
(identical -- no output, exit 0)
$ test ! -e docs/ledger-format.md && echo gone; wc -l docs/decisions-format.md docs/open-format.md
gone
  161 docs/decisions-format.md
  199 docs/open-format.md
$ git grep -nE "pathless|paths: \[\]|daikenja/ledgers" -- . ":!.plan" ":!docs/ledger-migration.md" ":!tests/fixtures/ledger-migration.md" ":!tests/fixtures/setup-user-upgrade.md" | cut -d: -f1 | sort | uniq -c
      9 CHANGELOG.md
      1 bot/tests/test_main.py
      1 docs/config-resolution.md
      1 docs/project-log-reference.md
      9 docs/upgrading.md
      1 skills/project-gaps/SKILL.md
      2 skills/project-list/SKILL.md
      2 skills/project-log/SKILL.md
      1 skills/project-sources/SKILL.md
      1 skills/project-summary/SKILL.md
      3 tests/fixtures/ledger-location.md
      8 tests/fixtures/project-resolution.md
```

One more hit than pass 1: `skills/project-log/SKILL.md:90`, S10's exemption
sentence naming the `paths: []` refusal -- D-21 handling. Every hit outside
`CHANGELOG.md` and `docs/upgrading.md` is a D-21 rule line or a test of one.

#### Kept decisions

- D-1 — drop — plan branch and stage names; only mattered while the plan ran
- D-2 — entry — `DECISIONS.md` › Ledger files
- D-3 — entry — `DECISIONS.md` › Projects and configuration
- D-4 — entry — `DECISIONS.md` › Ledger files
- D-5 — entry — `DECISIONS.md` › Ledger files
- D-6 — entry — `DECISIONS.md` › Ledger files
- D-7 — entry — `DECISIONS.md` › Ledger files
- D-8 — entry — `DECISIONS.md` › Projects and configuration
- D-9 — entry — `DECISIONS.md` › Projects and configuration
- D-10 — entry — `DECISIONS.md` › Ledger files
- D-11 — entry — `DECISIONS.md` › Migration from the old ledger
- D-12 — drop — the root `DECISIONS.md` and the `CLAUDE.md` pointer line make it plain
- D-13 — drop — planning only
- D-14 — drop — the plan's changelog and write-territory split; `CLAUDE.md` § Releasing owns changelog rules
- D-15 — entry — `DECISIONS.md` › Projects and configuration (every project lives in a git repository; the release-note wording is dropped)
- D-16 — drop — CI's `validate` check runs the invariants on every PR
- D-17 — entry — `DECISIONS.md` › Slack bot
- D-18 — drop — the #293 note was posted
- D-19 — drop — planning only
- D-20 — entry — `DECISIONS.md` › Migration from the old ledger
- D-21 — entry — `DECISIONS.md` › Projects and configuration
- D-22 — entry — `DECISIONS.md` › Migration from the old ledger

No ADRs: #292 keeps the reasoning for the format swap. The git strategy,
worktree strategy and final review stage belong to the method and are left
out. Applied unattended — merging the plan→main PR approves it.

`CLAUDE.md` § Repo conventions gains the pointer line, worded as the spec's
*The pointer line*.

#### README and cold reader

The README already describes what the plan built (S9): the ledger as
`DECISIONS.md` plus `open.md` in the project's repository, projects without a
folder gone, and the docs table; testing lives in `CONTRIBUTING.md`
§ Validation, which it links. No README change.

Cold reader (fresh Sonnet subagent, repository only, told never to open
`.plan/`), first pass:

1. *How do I test this?* -- `python tests/check-invariants.py` and the bot
   suite; skills have no runner, fixtures are walked by hand (CONTRIBUTING.md
   § Validation, CLAUDE.md). Correct.
2. *Where do open items live, and what defines the grammar?* --
   `<home>/.daikenja/open.md`, home the first entry of `paths`;
   `docs/open-format.md`. Correct.
3. *Where is the old-ledger migration, and what runs it?* --
   `docs/ledger-migration.md`, run by `setup-project` Step 2a, proposed by
   `setup-user`'s upgrade branch, with a dated backup. Correct.
4. *Why does `project-log` never commit?* -- the user commits with the work;
   `project-catchup` lists uncommitted changes as "not committed yet".
   Correct.
5. *Why is `last_checkpoint` a SHA per repository?* -- git says what changed
   per repository; an unresolvable SHA is a first run, said so. Correct.
6. *Why not edit `docs/decisions-format.md`?* -- byte-identical copy of the
   shared spec; change upstream, then copy. Correct.
7. *Why does the bot not read git history?* -- it reads files on disk with a
   read-only tool allowlist and never calls git. Correct.

No misses, so nothing was fixed and no second pass was needed.

#### Acceptance (redo)

- Every loose end has exactly one outcome: list above (1-32), one issue under
  `closeout will list`, fixes 1 of 3.
- #292's seven items recorded met with evidence; Done checks 1-5 pasted.
- #293 note posted in pass 1 after the maintainer's yes.
- Clean pass: `#### Kept decisions` gives all 22 frozen decisions an outcome,
  applied unattended; every entry exists in the root `DECISIONS.md`
  (`python3 tests/check-invariants.py`: all passed with it in place).
- README describes the build; pointer line present in `CLAUDE.md`.
- Cold reader: questions, answers and (no) fixes above; last pass no misses.

Actuals: 2026-11-03T12:33:31.653Z → 2026-11-03T12:39:09.063Z · 6 min · tokens in=112 out=40620 cache_read=6759602 cache_write=288140 · subagents=2
Artifacts check: match
