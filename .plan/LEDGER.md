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
| S3 Catchup and decisions read git history | doing | yes | 2026-11-03 | Catchup diffs git per repository from a validated SHA; decisions reads every DECISIONS.md with git history |
| S4 Gaps, summary, list and sources skills | done | yes | 2026-11-03 | Four skills read DECISIONS.md/open.md; two-repo sources fixture walked |
| S5 Judgement, thread, meeting-review and other readers | done | yes | 2026-11-03 | Readers moved to DECISIONS.md/open.md; DAIKENJA-PROJECT-DATA-UNREADABLE token for S7 |
| S6 setup-project registers git-backed projects only | doing | yes | 2026-11-03 | Registration is git-only, home asked and written first, seed via project-log; skill 23203→23144 bytes |
| S7 Slack bot reports unreadable project data | done | yes | 2026-11-03 | Bot posts one fixed line on the unreadable token; --check names unreadable projects |
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
