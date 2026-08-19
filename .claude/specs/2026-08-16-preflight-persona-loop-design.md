# Design: preflight as a persona review loop

**Date:** 16 Aug 2026
**Status:** approved design, fully implemented. PR 1 of § 10.3 landed 16 Aug
2026 (#30), PR 2 landed 16 Aug 2026 (#33), PR 3 landed 16 Aug 2026 (#37).
One deviation: § 13.3 criterion 4 was dropped rather than verified, and the
no-subagent fallback it covers is documented as an unsupported path.
Amended 19 Aug 2026 (#38): D12 and § 7.7 add a per-reviewer model tier. D4 is
unchanged by it.
**Affects:** `skills/preflight`, `skills/compose`, `docs/`, `templates/personas.md`, one new skill

---

## 1. Summary

`preflight` stops being a one-shot verdict and becomes a bounded review loop.
It runs the existing six substance checks, dispatches a set of reviewer
personas as subagents, applies the wording fixes they raise, re-checks once,
and returns a revised message plus a list of the facts only the user can
supply.

The rule that makes the loop safe: **the loop may change wording, never
content.** Anything a persona raises that cannot be fixed from material already
in the draft becomes a question back to the user, never an invented sentence.

## 2. Problem

Today `preflight` reports a verdict and stops. In practice the verdict --
"this would not fly with X" -- is the *start* of the work, not the end of it.
The user then drives a manual loop by hand: interpret the objection, rewrite,
re-check, repeat. That loop is mechanical enough to automate and slow enough
to be worth automating.

The current skill also under-delivers on its own name. A real preflight is a
systematic walkaround where the pilot fixes what they find and re-checks;
iteration is already in the metaphor.

## 3. Decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | `preflight` absorbs the loop; the name does not change | The aviation metaphor already covers check → fix → re-check. Zero rename cost. |
| D2 | Ship a fixed archetype roster in `docs/reviewer-personas.md` | Reproducible, versioned, tunable by PR. Derived-on-the-fly reviewers cannot be tuned when they give bad critique. |
| D3 | Cap 2 cycles; wording fixes applied throughout; content gaps collected and reported once at the end | After the first rewrite what remains is almost always content, which no further cycle can fix. Collecting rather than halting avoids bouncing back at the user two or three separate times. |
| D4 | One subagent per persona, dispatched in parallel | Genuine isolation: no persona sees another's critique, so nobody defers. Chosen over in-context sequential passes with the portability cost understood and accepted. |
| D5 | Cap 4 dispatched archetypes; the busy reader is pinned; inference picks the rest | Length and a buried ask are failure modes on essentially every message regardless of audience. |
| D6 | Named personas have their own quota, separate from the archetype cap | A named person is a delta on an archetype, not a substitute for one. Naming someone must not cost a lens. |
| D7 | Satisfy both where possible. Archetype conflicts resolve silently toward the real audience; conflicts between two actual recipients are reported, never resolved | There is no "primary recipient" -- multi-recipient messages are the norm, so arbitrating toward one addressee arbitrates toward a fiction. |
| D8 | `compose` Step 2's rewrite rules extract to `docs/rewrite-rules.md` | Two consumers, one contract -- exactly what the S6 decision did to create `substance-checks.md`. |
| D9 | Report depth keys off the existing `profile.tone` | `config-contract.md` already defines `tone` as "how much the skills explain themselves". No new config key. |
| D10 | A new writer skill owns every `personas.md` write; `preflight` and `compose` route through it | Mirrors the ledger's single-writer rule, where only `log` writes and `meeting-review` writes through it. |
| D11 | Learned personas are written silently and reported after | Chosen deliberately over propose-then-approve, for friction. Constrained by the guardrails in § 7.3. |
| D12 | Each reviewer is dispatched on a model tier carried by its archetype, set in `docs/reviewer-personas.md` and passed as the subagent's `model` at dispatch | Added 19 Aug 2026 (#38). An archetype simulating a *degraded* reader is made worse by a stronger model, not better -- asked to skim, a capable reader reads properly and then reports what a skimmer would have missed. Extends D4 rather than replacing it: the briefs stay in the doc and the dispatch shape is unchanged. |

## 4. Identity and boundary

**`preflight`** takes a draft (or a plain description of what the user wants to
raise) and returns a *challenged and revised* draft plus the open questions.
Its cycle 0 is the current skill's entire job, preserved and still reported.

**`compose`** is unchanged in purpose: wording you want improved, one message
out, done. It remains the place to go when the draft does not need
challenging. Its Step 2 moves to a shared doc (D8); this is a behaviour-neutral
refactor, version 3 → 4.

**`doc-review`** is untouched. Documents only, read-only, never rewrites.

## 5. The archetype roster

Ships as `docs/reviewer-personas.md`. Each archetype exists because it catches
a failure mode the others miss; redundant personas burn spawns to say the same
thing twice.

Archetypes are **reading behaviours, never people**, and carry no personal
names.

| Archetype | Reads for | Catches |
|---|---|---|
| **The busy reader** *(pinned)* | Speed | Reads line one and the last line only. Length, buried asks, second-read sentences |
| **The fact-checker** | Truth | Unsupported claims, imprecise numbers, anything answerable with "well, actually" |
| **The risk reader** | Exposure | What gets quoted back at you. HR, legal, compliance, escalation |
| **The executive** | The decision | Any C-level or head-of. No technical depth, no project history, no patience |
| **The tone-sensitive reader** | Register | Directness landing as aggression, brevity landing as dismissal, implied blame |
| **The subtext reader** | Implication | The gap between what is said and how it will be received -- passive aggression, false cheer, unintended implication |
| **The machine reader** | Machine processing | Sarcasm and irony flattened to literal, rhetorical questions answered literally, "that thing we discussed" with no antecedent, multiple asks where an agent picks one |
| **The person being asked to do the work** | Self-interest | Unclear ownership, being volunteered, unrealistic timing |
| **The dissenter** *(inference-only, never pinned)* | Persuasion | Unaddressed objections, assumptions stated as settled |

Each archetype also carries a model tier, added by D12. See § 7.7.

Two checks run **in the main context, always, and are never dispatched** --
they are properties of the text rather than a different reader, so a separate
head adds nothing:

- **AI-tell check.** Does this read as machine-written -- tidy tricolons, hollow
  transitions, over-hedging, generic enthusiasm. Always on because `compose`
  drafts the user's messages, so an always-on drafting tool warrants an
  always-on counterweight. Its findings are always wording-type, so it can
  never add to the questions list.
- **Non-native English readability.** Long sentences, idioms, uncommon words
  with a common alternative, culturally-specific references. Always on because
  `compose`'s stated purpose is landing well with a non-native audience.

**Non-native English is deliberately a check and not an archetype.** The one
thing a dispatched non-native reader would add over a text scan is
*misreading* -- extracting the wrong meaning rather than finding a sentence
hard -- and that failure mode is already covered from two directions by the
machine reader (literal versus intended) and the subtext reader (said versus
received). What remains after subtracting those is text properties, which need
no separate head.

The term stays **"non-native English"** rather than "international reader",
matching the two places the repo has already settled on it: `doc-review`'s
checklist item and `compose`'s own description. A third term for one concept
is drift.

**Known limitation of both checks:** they run in the main context, which has
read the draft, the thread and the surrounding conversation, so they know what
the message *means* and are weak judges of whether the words alone carry it.
The dispatched busy reader partially mitigates this, since it reads cold.

## 6. Persona resolution

### 6.1 Three layers, composing

Most specific wins, and they layer rather than replace -- the same idiom as
`voice.md` ← `writing-style.md`:

| Layer | Source | Wins over |
|---|---|---|
| 3 | **Inline description at invocation** -- "S has power, no clue, loves K" | everything |
| 2 | The addressee's `personas.md` entry, if one matches | the archetype |
| 1 | The archetype the person embodies | -- |

S therefore reviews as *the executive archetype, in full* + *her `personas.md`
entry* + *whatever the user said inline this run*.

The inline path is the **primary** one. It is how the user actually works, and
their own phrasing already carries the archetype signal: "has power but does
not have a clue" *is* the executive; "tends to challenge everything" *is* the
fact-checker.

### 6.2 Rules

1. **Only people the draft actually addresses become reviewers.**
   `personas.md` is an index, not a roster to sweep -- the same thing
   `meeting-review` already says about it. This is what stops a large
   engineering org from exploding the reviewer count.
2. **A named addressee takes a persona slot, which is counted separately from
   the archetype cap** (D6). Naming someone never costs a lens.
3. **Inference skips an archetype a named persona already carries in full** --
   not to save a slot, but because a generic executive alongside M-as-executive
   returns duplicate findings. The freed slot goes to the next uncovered lens,
   so the count stays at 4.
4. **A `personas.md` entry is scoped to that person and never modifies a
   shipped archetype for anyone else.** Changing an archetype's behaviour
   globally is a PR to `docs/reviewer-personas.md`, not an edit to a user file.
5. **More addressees than persona slots** → direct addressees beat cc'd, and
   the report names who was dropped. Persona slots cap at 2.
6. **Named in the draft but absent from `personas.md` and undescribed inline**
   → archetypes only. Silent, not an error, matching `meeting-review`.
7. Briefs may carry **relational context** ("loves K", "reports to V") even
   though it is not a lens. The risk reader needs it.

### 6.3 Absent files

`personas.md` absent is **silent**, matching `compose` Step 5, which treats
personas as optional input. The `Reviewers:` line names what ran, which makes
a notice redundant.

## 7. The loop

### 7.1 Flow

**Cycle 0 -- substance checks.** The six from `docs/substance-checks.md`, run
in the main context, verdict reported. Unchanged from today's skill.

**Cycle 1 -- dispatch.** Personas selected per § 5 and § 6. One subagent each,
all in a single parallel block. Each subagent sees **only the draft and its own
brief** -- not the other personas, and not the cycle-0 verdict, since showing it
anchors them onto checks that already ran.

**Cycle 2 -- only personas that raised something in cycle 1 are
re-dispatched**, against the revised draft. They confirm resolved or restate.
New wording findings are applied; new content findings join the questions list.
Zero wording findings in cycle 1 skips cycle 2 entirely.

### 7.2 The critique contract

Every finding a subagent returns must carry:

```
Anchor:  "<short quote of the exact phrase it is reacting to>"
Problem: <what goes wrong for this specific reader>
Type:    wording | content
Fix:     <the concrete rewrite>          -- wording only
Missing: <what fact is absent>           -- content only, never a guess at its value
```

The anchor requirement is lifted from `meeting-review`: a finding that cannot
be tied to a specific span of the draft is vague enough to be noise.

### 7.3 The adjudication rule -- the safety hinge

**The main context adjudicates the wording/content call and does not trust the
subagent's label.** A subagent can mislabel a content gap as wording and
smuggle an invented fact in through its suggested `Fix`.

Every proposed wording fix gets one test: *is this expressible using only
material already in the draft?* If the fix introduces a fact not in the source,
it is reclassified as content and goes to the questions list.

**The rewrite step is never dispatched.** Rewriting is where invention happens,
so it stays in the one place that has read `docs/rewrite-rules.md`,
`docs/voice.md` and the user's `writing-style.md`.

### 7.4 Conflicts

**There is no "primary recipient" to arbitrate toward.** Work messages
routinely go to several people at once, so a rule that picks one addressee is
picking a fiction. Conflicts resolve in three steps:

1. **Try to satisfy both.** Most conflicts are false ones -- length can usually
   come out somewhere other than the constraint the fact-checker wants kept.
   A satisfied-both fix is applied like any other wording fix and needs no
   disclosure.
2. **Archetype versus archetype**, where neither is a real addressee: resolve
   silently toward whichever real audience the message actually has.
   Archetypes are proxies for readers, not readers, and a proxy does not
   outrank a person.
3. **Recipient versus recipient**, where both are people the message is
   genuinely addressed to and no fix serves both: **report it and resolve
   nothing.** An irreconcilable conflict between two real recipients is a
   finding in its own right -- it usually means the message is serving two
   audiences and wants splitting, or that one audience needs a separate note.
   Say that, rather than quietly picking a winner.

Case 3 is reported alongside the content questions in § 9, since like them it
is something only the user can settle.

### 7.5 No dispatch available

One notice line, then personas run in-context sequentially and everything else
is identical. This follows `config-contract.md`'s standing failure rule: *one
notice line, then continue with reduced behaviour; hard-stop only when the
missing thing is the task itself.* Dispatch is a preference, not a dependency.

### 7.6 Cost

Cycle 1 with two named addressees is 6 spawns; cycle 2 re-dispatches only those
who raised something. A messy draft with two addressees runs to roughly 9-10
spawns. This is the accepted price of D4.

Since D12 those spawns are no longer all at one price. Two of the nine
archetypes run on `haiku` and three on `sonnet`, so a session on Opus stops
paying top-tier rates for the busy reader -- the one persona that is better
cheap. Cost was not the reason for the tiers and it does not set them, but it
moves the right way.

### 7.7 The model each reviewer runs on

Added 19 Aug 2026 with D12 (#38).

**The finding this rests on, verified rather than assumed.** Claude Code's
`Agent` tool takes a `model` parameter at dispatch time, so a skill can ask for
a model for a subagent it spawns without shipping that subagent as an
`agents/*.md` definition. Its documented resolution order is
`CLAUDE_CODE_SUBAGENT_MODEL` → the per-invocation parameter → the definition's
`model:` frontmatter → the main conversation's model. Skill frontmatter still
has no `model` key, which is what made this look impossible; the knob is on the
dispatch, not on the skill.

This is why D4 survives. The briefs stay in `docs/reviewer-personas.md`, one
subagent per persona is still dispatched in parallel, and nothing moves into
nine shipped agent files that would then have to be kept in sync with the
roster.

**The tiers, and why they split this way.** The table lives in
`docs/reviewer-personas.md` § What each reviewer runs on and is written down
in exactly one place. The busy reader and the machine reader take `haiku`,
because both simulate a *degraded* reader and the limitation is the persona --
a strong model asked to skim reads properly and then reports what a skimmer
would have missed, which is a different and weaker signal. The executive, the
tone-sensitive reader and the person being asked to do the work take `sonnet`:
an ordinary reader with one preoccupation, a narrow lens, a rigid output
contract. The fact-checker, the risk reader, the subtext reader and the
dissenter take `opus`, because they simulate a reader sharper than normal and
risk and subtext are the most judgment-heavy lenses in the roster.

**Family aliases only.** `haiku`, `sonnet`, `opus` -- never `claude-opus-5`.
Aliases survive a version bump and versioned IDs rot.

**The main context is not on the table**, and always wants the strongest model
available: § 7.3 adjudication is the safety hinge, and the two always-on checks
and the rewrite also run there. That is what the Opus notice at the top of the
skill is for, and it now says explicitly that it is about that context rather
than about the reviewers.

**A tier is not user-configurable**, on the same reasoning that fixes the
roster (D2). A `personas.md` entry sets no tier; a named addressee inherits the
tier of the archetype it embodies. `CLAUDE_CODE_SUBAGENT_MODEL` overrides
everything, which is Claude Code's precedence and the clean way to pin the
whole roster to one model.

**Where nothing dispatches** -- claude.ai, per § 7.5 -- no tier applies and
every reviewer runs on the session model. The mandatory `Reviewed:` line
already reports that the run went that way, so this needs no second notice.

## 8. Learned personas

`preflight` and `compose` capture personas described inline that are not
already in `personas.md`, and route the write through the new writer skill
(D10). Writes are silent and reported after (D11), under three guardrails:

1. **Only what the user stated, never inferred.** No embellishment into a
   character study. The same no-invention rule the rest of the plugin follows.
2. **Behavioural, not evaluative.** "Challenges technical claims", not "is
   obstructive." This is better reviewer input, and it keeps the file from
   becoming a liability if it is ever read by someone else.
3. **Silent means append-only for new people.** Amending an entry the user
   wrote by hand is *proposed*, not silent -- adding a section is additive and
   reversible; rewriting their prose is a different act.

The report names the file and shows the exact entry added, so it can be edited
or deleted.

**This changes `config-contract.md`'s who-writes-what table**, which currently
states `personas.md` is "written by the user, by hand" and that Daikenja "never
edits it". That row must be updated deliberately as part of this work.

### 8.1 The `setup-user` boundary

"One writer" was never strictly true. `setup-user` already writes
`personas.md`: its frontmatter declares it and its Step 4 copies the blank
template when the file is absent. The split, which `config-contract.md` must
state rather than imply:

- **`setup-user` owns creation.** It copies the blank template if and only if
  no file exists, and its existing rule stands untouched -- existence is the
  only test, and it never inspects or overwrites user prose.
- **The new skill owns every content write.** Appending a learned entry is the
  only way content reaches the file from Daikenja.

These are different acts on the same file, not two writers competing for one
job, which is why the ledger's stricter single-writer rule does not transfer
unchanged.

The new skill's **name is deliberately left open** until implementation, when
its description has to be drafted anyway and nothing downstream depends on the
choice. Candidates considered: `learn-persona`, `persona-log`,
`remember-persona`.

## 9. Output

Verdict first, deliverable second, evidence third:

```
Verdict: <ready to send | needs 2 facts from you before it goes>

<the revised message>

Needs you
1. [the fact-checker] The message says the migration "will take a while" --
   they need the actual window to plan around it. You have not stated one.

Reviewers: busy reader (always on), the executive (the ask lands with a
director), S (named in the draft)

Applied: 4 wording fixes across 2 cycles.
Conflict: kept the constraint the fact-checker wanted over the executive's cut
for length -- the message is addressed to the fact-checker.
Learned: added S to ~/.claude/daikenja/personas.md.
```

**Depth keys off `profile.tone`** (D9). Under `direct`, the six substance
checks collapse to one line when they all pass and only failures are itemised.
Under `guided`, all six appear plus every finding with its anchor and the
reasoning behind each fix. `standard` sits between.

## 10. Files touched

### 10.1 Skills

| Skill | Change |
|---|---|
| `skills/preflight/SKILL.md` | **Rewritten.** Name unchanged. Version 1 → 2, description rewritten for triggering. |
| `skills/compose/SKILL.md` | **Modified.** Version 3 → 4. Step 2 replaced by a pointer to `docs/rewrite-rules.md`; learned-persona handoff added. |
| `skills/<persona-writer>/SKILL.md` | **New.** Owns every content write to `personas.md`. Name settled at implementation (§ 8.1). |
| `skills/setup-user/SKILL.md` | **Boundary note only.** Its create-if-absent behaviour is unchanged; the note records that content writes now belong elsewhere (§ 8.1). |
| `skills/meeting-review/SKILL.md` | **None.** Reads `personas.md`, never writes it. Its "not a roster" rule stays true under learned entries. |
| `thread`, `log`, `catchup`, `decisions`, `gaps`, `summary`, `doc-review`, `self-review` | **None.** No contact with this work. |

**No renames.** `preflight` keeps its name; no existing skill moves.

### 10.2 Other files

| Path | Change |
|---|---|
| `docs/rewrite-rules.md` | **New.** Extracted verbatim from `compose` Step 2. |
| `docs/reviewer-personas.md` | **New.** The archetype roster in § 5. Nine briefs, each written well enough to drive a subagent. |
| `docs/future-work.md` | **New.** See § 12. |
| `docs/config-contract.md` | Who-writes-what table updated for `personas.md` (§ 8, § 8.1). |
| `templates/personas.md` | Note that Daikenja may now append entries. |
| `README.md` | Skill list: the `preflight` bullet rewritten, one bullet added. |
| `tests/fixtures/` | A draft with a content gap, a draft with a recipient-versus-recipient conflict, a clean draft that exits after cycle 1. |
| `CHANGELOG.md` | Entries under `## [Unreleased]`. A `feat` in the batch means a minor bump at release. |

### 10.3 Sequencing -- three pull requests

The work splits along dependency lines into three independently reviewable
PRs, each roughly one to two sessions. This is deliberately *not* run as a
`staged-rollout` `.plan/`: the PR is already the natural stage boundary, and
this spec is already the persistent plan, so a `.plan/` folder would track the
same work twice alongside the repo's existing branch → PR → `CHANGELOG`
`[Unreleased]` flow.

| PR | Contents | Depends on |
|---|---|---|
| **1** | `docs/rewrite-rules.md` extraction and the `compose` refactor | -- |
| **2** | The persona writer skill, the `config-contract.md` change, the `setup-user` boundary, `templates/personas.md` | -- |
| **3** | `docs/reviewer-personas.md`, the `preflight` rewrite, learned-persona wiring, fixtures, `README.md`, `docs/future-work.md` | 1, 2 |

PR 1 is behaviour-neutral and shippable on its own. **If PR 3 proves larger
than a single session once planned in detail, escalate that stage alone to
`staged-rollout`** -- upgrading the path mid-task is the sanctioned direction,
and starting light costs nothing if it turns out to be enough.

## 11. Failure cases

| Situation | Behaviour |
|---|---|
| No draft and no description given | Ask for one. Do not guess what the user wants to raise. |
| Subagent dispatch unavailable | One notice, run personas in-context sequentially (§ 7.5). |
| A subagent returns a finding with no anchor | Discard it. An unanchored finding is noise. |
| A subagent's wording `Fix` introduces a fact not in the draft | Reclassify as content (§ 7.3). Never apply it. |
| Every persona returns nothing | Report it plainly. A clean draft produces a short report, not a padded one. |
| `personas.md` absent | Silent. Archetypes only. |
| `daikenja.yaml` malformed | Stop and name the first line that does not parse, per `config-contract.md`. |
| More addressees than persona slots | Direct beats cc'd; report who was dropped. |
| User asks for the message to be *sent* | Decline. This skill has no send action. |

## 12. Future work

Written into `docs/future-work.md` as **known limitations of the current
design, not as a wishlist** -- `.claude/reference/github-issues.md` requires
that this repo document what Daikenja *is*, never what was proposed. Framed as
limits, these are facts about the shipped behaviour:

- **Group-level personas are not supported.** Only individual entries are read.
  "Everyone in platform is deeply technical and hates hedging" has nowhere to
  live.
- **User-defined archetypes are not supported.** The roster in
  `docs/reviewer-personas.md` is fixed and changes only by PR.
- **Persona onboarding by sampling past messages is not supported.** Personas
  are learned only from what the user states inline.

The third is worth a GitHub issue in its own right once the writer skill from
D10 exists, since that skill is its natural home.

## 13. Verification

There is no test runner. `tests/fixtures/` is exercised by hand through the
skills, per the repo's own convention.

### 13.1 Fixture runs require `claude --plugin-dir .`

**A normal session cannot exercise a working-tree skill change at all.** The
`Skill` tool resolves Daikenja from the installed plugin cache
(`~/.claude/plugins/cache/<marketplace>/daikenja/<version>/`), and a
local-marketplace install *copies* the repo at install time rather than
referencing it live -- a fact this repo already documents. Edits in the working
tree are invisible to that copy.

This is not theoretical. PR 1 attempted to verify D8 by running `compose`
against `tests/fixtures/sample-drafts-preflight.md` before and after the
change. Both runs loaded a skill still reporting `version: 3` with the
pre-extraction Step 2 body, so neither exercised the edit and the comparison
produced no signal in either direction.

**Any acceptance run not made under `claude --plugin-dir .` is testing the last
released copy, not the change under test.** Treat a fixture result obtained any
other way as void rather than as a pass.

### 13.2 Text-only changes are proven textually, not by running anything

A skill *is* its instruction file. A change that moves or rewords instructions
without altering what the skill decides is proven behaviour-neutral by a
verbatim diff against the pre-change text -- a stronger proof than comparing
two runs of a generative skill, whose output varies between runs regardless.
This is how D8 was actually accepted in PR 1, after the fixture route produced
nothing.

Reserve fixture runs for changes that alter what a skill decides.

### 13.3 Acceptance criteria

1. A draft with a stated content gap produces a question, never an invented
   fact, on every fixture run.
2. A draft whose only problems are wording exits after cycle 1 with no
   questions.
3. A conflict between two real recipients is reported rather than resolved,
   per § 7.4 case 3. An archetype-versus-archetype conflict is not.
4. With dispatch unavailable, the same fixtures produce the same
   *classification* of findings through the in-context fallback (§ 7.5).
5. A learned persona is appended to `personas.md` without altering any entry
   the user wrote by hand (§ 8).
