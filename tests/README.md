# tests/

Fixtures the skills are exercised against, plus one script. Nothing here is
read at runtime, and no skill points at this directory -- it exists so a
stage's acceptance checks can be re-run later against the same inputs.

- [`check-invariants.py`](check-invariants.py) -- enforces the invariants
  every v2 build stage checked by hand: `claude plugin validate .` exits
  clean; every `skills/*/SKILL.md` frontmatter block parses as YAML with
  a `name` matching its directory and a `description`; `docs/upgrading.md`'s
  version headings are well-formed, newest-first and each named in
  `CHANGELOG.md` too; `fixtures/ledger-backfill.md` agrees with
  `docs/ledger-format.md` -- its two bulk writes replayed through the stated
  insert rule, and its Changelog lines through the continuation-join and
  range expansion, the only fixture checked by script rather than by hand,
  because the ordering rule is the only part of the ledger contract that is
  arithmetic instead of judgement; `scripts/build-claude-ai-skills.py` exits
  clean; and this directory's own index agrees with what's on disk -- every
  file under `fixtures/` is named in this README and vice versa. Requires
  `pyyaml` (`pip install pyyaml`) and the `claude` CLI on `PATH`. Run it with
  `python tests/check-invariants.py`; CI runs it on every push and pull
  request via `.github/workflows/ci.yml`.

- [`fixtures/sample-thread.md`](fixtures/sample-thread.md) -- a thread with one
  agreed decision, one proposal nobody agreed to, and two unresolved items.
  Exercises the `project-log` classifier, including its refusal to log a
  parked suggestion as a decision.
- [`fixtures/sample-thread-followup.md`](fixtures/sample-thread-followup.md) --
  the same conversation with two later messages. Logging it after the first
  fixture must update entries in place instead of appending near copies.
- [`fixtures/sample-ledger.md`](fixtures/sample-ledger.md) -- a complete,
  well-formed beacon-project ledger: four decisions with one supersession
  pair (`D-002`/`D-004`), five open items with one resolved, one context
  link, and a changelog accounting for every write, including one entry
  written by `project-log` so the fixture covers both the pre- and
  post-rename writer name. The healthy-ledger control fixture; its `D-003`
  schema-freeze decision is what `sample-drafts-preflight.md`'s third draft
  checks against.
- [`fixtures/malformed-ledger.md`](fixtures/malformed-ledger.md) -- a ledger with
  a misspelled section heading and an entry missing its owner field, plus a legal
  continuation line as a control. A skill must report all of it and write
  nothing.
- [`fixtures/broken-supersession.md`](fixtures/broken-supersession.md) -- a
  ledger with two mismatched supersession pairs (a body claiming `Supersedes`
  with no matching tail, and a tail with no matching claim), plus a correctly
  matched pair as a control. Exercises `project-decisions`' tail-is-authoritative
  handling: it must report both mismatches, naming both IDs, and never repair
  the ledger.

- [`fixtures/ledger-backfill.md`](fixtures/ledger-backfill.md) -- an
  incrementally kept `lantern` ledger plus three walks that exercise the four
  rules a bulk backfill depends on: a first bulk write whose entries are all
  older than what is already in the file, a second bulk write arriving three
  days later that supersedes an entry the first one wrote, and a
  `project-catchup` run over both. It fixes the resulting entry order (IDs and
  dates deliberately decorrelated, and never renumbered), two `Approximate
  date.` entries with the derivation the user supplied, a Changelog line
  carrying both compactions -- a dense ID range and a continuation line -- and
  the twelve changes `catchup` must recover from them. Its "what must not
  happen" lists are the point: a sparse range, a renumbering and an invented
  date are each shown as the wrong answer. Two malformed ranges at the end
  exercise the report-and-continue path.

- [`fixtures/owner-handles.md`](fixtures/owner-handles.md) -- a synthetic
  personas file plus eight walks over `project-log`'s owner-handle check,
  against `sample-ledger.md`: a handle the ledger already uses, a handle only
  the personas file knows, a handle neither knows, two spellings of one person,
  `@unassigned`, no personas file at all, an unresolvable `drive:` pointer, and
  a dictated write. It fixes the two things the check is easiest to get wrong --
  that a handle the ledger already knows never reads `personas.md`, and that
  the notice is a notice rather than a question the run waits on.

- [`fixtures/ledger-relationships.md`](fixtures/ledger-relationships.md) -- a
  `lattice` gateway ledger built by one team inside a programme run by others,
  plus nine walks over the body markers `docs/ledger-format.md` § Body markers
  defines. It fixes the four things easiest to get wrong: a `Contradicts`
  marker found from both ends although the file records only one, a `Blocked
  by` whose blocker is already resolved and which nothing rewrites, an imposed
  decision with no owner that is never a gap, and a body containing `->` as
  punctuation that must not parse as a tail. One entry carries a marker naming
  an ID the ledger does not have, so the report-and-continue path of reading
  rule 6 has something to report. The walks pin today to 2026-09-15 and the
  threshold to 21 days, so the `project-gaps` output is exact rather than
  drifting with the calendar.
- [`fixtures/dictated-log-requests.md`](fixtures/dictated-log-requests.md) --
  four scenarios walking `project-log`'s same-turn dictated-write path against
  `sample-ledger.md`: a clean write, an unnamed owner that must default to
  `@unassigned` rather than asking, a duplicate that drops to
  propose-then-wait, and a pasted thread whose two ambiguities land in one
  "Questions before I write" round instead of being asked one at a time.
- [`fixtures/sources-ledger.md`](fixtures/sources-ledger.md) -- a `meridian`
  compliance-programme ledger carrying a Sources section, plus a
  connector-report table, exercising `docs/ledger-format.md` § Section:
  Sources against `project-sources`, `project-summary`, `project-catchup` and
  `project-log`. Pins four cases: a fully-populated source, one with no
  `modified:` baseline (read date only, never "moved" or "unchanged"), one
  that moved since its recorded read, and the no-Sources-section case, which
  is covered instead by `sample-ledger.md`. Walks assume today is 2026-09-15.

### `meeting-review`

- [`fixtures/sample-transcript.md`](fixtures/sample-transcript.md) -- a
  22-minute Harbor rollout-sync transcript, continuing the story from
  `sample-thread.md`. Layers transcript mess (three speaker labels for one
  person, a repeated point, a side conversation, an inaudible passage) on top
  of the classification cases: one real decision, one restated-not-new
  decision, one parked suggestion, an owned action item, an unowned one, and
  an unresolved question. Exercises the `meeting-review` classifier against
  both at once.

### `thread` and `compose`

- [`fixtures/sample-reply-thread.md`](fixtures/sample-reply-thread.md) -- a
  four-message thread where hakurou pushes for a Friday cutover and rigurd
  pushes back citing an unfinished validation step and a runbook link,
  ending before rigurd's reply is drafted. Exercises the `thread` ->
  `compose` handoff: the runbook link must survive into the drafted reply
  untouched.

### `preflight`

- [`fixtures/sample-drafts-preflight.md`](fixtures/sample-drafts-preflight.md)
  -- three drafts for `preflight`'s verdict: one with full context, a named
  owner and a dated ask that should pass; one with no context and no
  specific ask; and one asking a question already settled by
  `sample-ledger.md`'s `D-003` schema-freeze decision. Exercises the
  verdict, not the wording, including the check against a supplied ledger.

The three below exercise the review loop rather than the verdict, and are
only meaningful under `claude --plugin-dir .` -- a normal session loads the
last released copy of the skill, so a result obtained any other way is void.

- [`fixtures/preflight-content-gap.md`](fixtures/preflight-content-gap.md) --
  a reindex approval request whose duration, replica impact and date are
  stated nowhere in the file. The loop must return them as questions. Any
  run that produces a number for them has invented it, which is the one
  failure the wording-never-content rule exists to prevent.
- [`fixtures/preflight-recipient-conflict.md`](fixtures/preflight-recipient-conflict.md)
  -- a cutover message addressed to a director who stops reading after ten
  lines and to the engineer who has to run the five-step rollback, with the
  inline briefs that make both of them real recipients. No fix serves both,
  so the conflict is reported and not resolved. A third conflict, between
  the busy reader and the fact-checker over an error code neither of them
  receives, is seeded as a control and must stay unreported. This is also the
  draft that catches a cycle-2 reviewer closing a finding on untouched text:
  no finding may leave the report unless the rewrite made an edit in answer to
  it, and "it costs us five days on the rollout plan and nothing else" is the
  sentence that has to stay raised until the sender supplies what else it
  costs. Its two invented recipients also carry the personas check: pasted
  without this file's synthetic header, as a person would paste a draft,
  neither name may reach `~/.claude/daikenja/personas.md` without a question
  first, and the review must finish either way.
- [`fixtures/preflight-clean-draft.md`](fixtures/preflight-clean-draft.md) --
  two drafts that are complete on the facts. The first has nothing to find
  and should come back unchanged with cycle 2 skipped; the second buries its
  ask, opens with "as discussed", asks a bare rhetorical question and closes
  on a hollow tricolon, while still containing every date, owner and
  deadline a fix could need. Both must finish with no questions.
- [`fixtures/preflight-rerun.md`](fixtures/preflight-rerun.md) -- a
  certificate-rotation approval run twice: run 1 is missing the window and the
  failure mode and must ask for both; the user answers both in the
  conversation; run 2's revised draft states them but introduces one new gap
  (when an on-call shift starts). Run 2 must report the first two as settled
  since the last run, never re-ask them, and -- as a second consecutive run
  still ending `needs facts` -- state that the remaining set is exactly the
  one new fact and name it.

### `doc-review`

- [`fixtures/doc-review-clean.md`](fixtures/doc-review-clean.md) -- the
  Beacon rollout runbook: a dated rollout rule, a rollback trigger with a
  named owner, and named ownership for every remaining responsibility. The
  clean control paired with `doc-review-problems.md`, built to pass
  `doc-review`'s checklist without findings.
- [`fixtures/doc-review-problems.md`](fixtures/doc-review-problems.md) --
  the Harbor rollout runbook, seeded with one issue per `doc-review` check:
  an undefined term (`GKR`), an undated rollback rule, an unowned task
  (customer comms), a "Fast path" section that flatly contradicts the
  rollout rule stated above it, and a closing note claiming the doc "still
  applies today" for a 2024 cutover with nothing to support that. Exercises
  the full checklist in one document.

### `self-review`

Walking any fixture below against a real session needs a scratch
`daikenja.yaml`: `profile.name`'s first token must match the fixture's
invoker (`rimuru`), and `profile.norms_doc` must point at
`fixtures/self-review-norms.md`. Run it against your live configuration
instead and the walk either stops on "which participant are you" or reads
your own norms document in place of the fixture's.

- [`fixtures/self-review-norms.md`](fixtures/self-review-norms.md) -- a
  synthetic Quill-team norms document covering direct-question answering,
  stating what has been verified, not committing another team's dates,
  reply-time expectations when someone is blocked, and incident ownership.
  Used to turn on `self-review`'s ROLE CHECK by pointing `norms_doc` at this
  file.
- [`fixtures/self-review-thread.md`](fixtures/self-review-thread.md) -- a
  14-message thread where the invoker (`rimuru`) makes mistakes at all
  three severity tiers, including one that misleads a colleague into
  acting on a wrong fact (calling a reindex idempotent when it silently
  duplicates rows), with enough mistakes in total to exercise the findings
  cap and the parked remainder.
- [`fixtures/self-review-thread-colleague.md`](fixtures/self-review-thread-colleague.md)
  -- a 9-message thread where a colleague (`gobta`) behaves badly throughout
  -- public blame, sarcasm aimed at a person, dismissing a stated
  constraint twice -- while the invoker (`rimuru`) handles it well until
  the final message, where he accepts a date he had just called
  unachievable without saying what would be dropped to hit it. Exercises
  `self-review`'s third-party check: findings must land on the invoker
  alone, never on `gobta`.

### `setup-user`

- [`fixtures/setup-user-upgrade.md`](fixtures/setup-user-upgrade.md) -- five
  `daikenja.yaml` files for the upgrade branch, each with the walk it is for: no
  version key (the state every pre-0.6.0 install is in, which must produce a
  proposal and never a stop), an older version, the current version (a silent
  no-op -- an ordinary re-run must not get noisier), a file that does not parse
  (Step 1 stops and Step 2 never runs, even though a readable version sits on
  the first line), and a version *ahead* of the installed one, which must never
  be stamped backwards. The older-version file carries a second and third walk,
  over one read skill and over `project-log`, confirming each emits the one-line
  notice and then continues without migrating or stamping anything.

### `setup-project`

- [`fixtures/setup-project-seed.md`](fixtures/setup-project-seed.md) -- a
  `daikenja.yaml` with one unrelated project registered, an invented
  `quill-gateway` repository that already keeps four decision records and a
  three-question register, and three walks over it: a first registration under
  a key that differs from the directory name, a re-registration of the same
  path that must leave that key alone, and a seed run the user only partly
  approves. The sources are seeded with one decision, one suggestion nobody
  agreed to, one open item whose date exists nowhere, a superseded record the
  user asks to drop while keeping its replacement, a standing team policy that
  reads like one of the project decisions without being the same fact, and a
  Confluence space no connector can reach. Exercises the tranche flow, the restate-before-proposing
  rule against a user who replies about something else, and the refusal to
  invent a date.

### Project resolution

- [`fixtures/project-resolution.md`](fixtures/project-resolution.md) -- one
  `daikenja.yaml` holding every legal project shape -- a single-value `path`
  written before `paths` existed, a three-repository `paths` list, a
  `paths: []` project with an absolute `ledger:`, a `paths: []` project with
  no ledger location at all, and a project nested inside another -- plus eight
  walks over it. Covers the scalar form resolving unchanged, a multi-path
  project resolving its ledger against its **first** path rather than the path
  that matched, a pathless project resolving through its absolute `ledger:`,
  the same shape without one stopping on the ledger rather than on the project,
  a project key that resolves from the wrong directory, a key that resolves to
  nothing, nesting still winning on the longest prefix, and the `project-list`
  report.
  The two failures it exists to catch are silent: a ledger resolved against
  whichever repository the user was standing in, and a bad key answered from
  the current directory.
- [`fixtures/ledger-location.md`](fixtures/ledger-location.md) -- five
  `daikenja.yaml` configurations walking `ledger:` key resolution: no key, a
  relative key, an absolute key outside the project root, an absolute key that
  does not exist on this machine, and a registered project that resolves to
  the user's home directory. Pins that an authoritative `ledger:` key never
  falls back to the default path even when it cannot be written, and that the
  home-directory refusal is a distinct check from "is this a registered
  project?", not a collapse of the two.

### `learn-voice`

- [`fixtures/learn-voice-samples.md`](fixtures/learn-voice-samples.md) -- 33 of
  the invoker's own messages across four sources and three audiences, sized
  deliberately between the corpus floor and the corpus bar so a run has to say
  the evidence is thin. Six traits are seeded to be found (openers, a
  greeting split by register, bullets past three items, how a request is
  softened and sharpened, US spelling, summary-first past roughly 120 words),
  four to be observed and kept out because `docs/voice.md` fixes them
  (shouting, relative dates, an undecodable idiom, and two floor-keeping idioms
  that are not findings at all), and two never to be recorded -- the project's
  own vocabulary, and anything about the three colleagues in the corpus. Four
  walks over it: the whole corpus against an untouched template, a block whose
  authorship cannot be separated and must be refused, the DM block alone as an
  under-the-floor stop, and a re-run against a file the user has hand-written a
  line into, which must be diffed and not replaced.

Every fixture is synthetic: invented project, invented people, `example.com`
links. Nothing in this directory may contain real work content, personal data or
organization data.

Invented people are named from *That Time I Got Reincarnated as a Slime*
(lowercase, e.g. `diablo`, `benimaru`), never real-looking first names or
bare initials -- both read as specific individuals, and a fixed source keeps
the next fixture from inventing its own convention. `sample-transcript.md`'s
three-label trap (`Diablo` / `diablo` / `D`) stays a single person's name in
different cases, not three different characters.
