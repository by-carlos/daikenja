# tests/

Fixtures the skills are exercised against, plus one script. Nothing here is
read at runtime, and no skill points at this directory -- it exists so a
stage's acceptance checks can be re-run later against the same inputs.

- [`check-invariants.py`](check-invariants.py) -- enforces the invariants
  every v2 build stage checked by hand: `claude plugin validate .` exits
  clean, and every `skills/*/SKILL.md` frontmatter block parses as YAML with
  a `name` matching its directory and a `description`. Requires `pyyaml`
  (`pip install pyyaml`) and the `claude` CLI on `PATH`. Run it with
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
  receives, is seeded as a control and must stay unreported.
- [`fixtures/preflight-clean-draft.md`](fixtures/preflight-clean-draft.md) --
  two drafts that are complete on the facts. The first has nothing to find
  and should come back unchanged with cycle 2 skipped; the second buries its
  ask, opens with "as discussed", asks a bare rhetorical question and closes
  on a hollow tricolon, while still containing every date, owner and
  deadline a fix could need. Both must finish with no questions.

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

Every fixture is synthetic: invented project, invented people, `example.com`
links. Nothing in this directory may contain real work content, personal data or
organization data.

Invented people are named from *That Time I Got Reincarnated as a Slime*
(lowercase, e.g. `diablo`, `benimaru`), never real-looking first names or
bare initials -- both read as specific individuals, and a fixed source keeps
the next fixture from inventing its own convention. `sample-transcript.md`'s
three-label trap (`Diablo` / `diablo` / `D`) stays a single person's name in
different cases, not three different characters.
