# Rewrite-rules extraction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract `compose` Step 2's "rules you cannot break" into a shared
`docs/rewrite-rules.md` and point `compose` at it, so `preflight` can read the
same contract when it applies wording fixes inside its review loop.

**Architecture:** This repo has done this exact move once already. Decision S6
extracted the six substance checks out of `compose` into
`docs/substance-checks.md` when `preflight` needed the same logic, and both
skills now point at that document instead of restating it. This plan applies
the same pattern to the rewrite rules. The new document carries the rules plus
a "how a violation is reported" section naming each consumer, because `compose`
reports through its `Comment` block and `preflight` reports through its "Needs
you" list -- the rule is shared, the reporting channel is not.

**Tech Stack:** Markdown only. No code, no dependencies, no test runner. Skills
are prose instruction files read by Claude at runtime.

**Spec:** `.claude/specs/2026-08-16-preflight-persona-loop-design.md` --
decision **D8**, and § 10.3 PR 1.

## Global Constraints

- **This change is behaviour-neutral.** `compose`'s output on a given input
  must be identical before and after. The rules move; not one of them changes
  wording, scope or force. Task 1 exists to prove this rather than assume it.
- **`docs/` ships to users.** The whole repo is the plugin, so anything placed
  in `docs/` is distributed. `docs/rewrite-rules.md` is a runtime contract read
  by skills and belongs there. Contributor-facing material goes in `.claude/`.
- **Line endings are LF.** `.gitattributes` pins `* text=auto eol=lf` repo-wide.
  Before every commit, check `git diff --cached --stat` is proportional to the
  edit; a whole-file rewrite on a small change means CRLF crept in.
- **Match the surrounding prose style.** These docs use ` -- ` rather than an
  em dash, wrap at roughly 79 columns, and use `**bold**` for the key term in a
  rule. Copy the register of `docs/substance-checks.md`; it is the closest
  sibling to what this task creates.
- **Absolute dates, never relative.** Non-overridable per
  `docs/config-contract.md`.
- **`CHANGELOG.md` entries go under `## [Unreleased]`.** Never write a dated or
  versioned heading and never bump `.claude-plugin/plugin.json` here -- a
  release is its own atomic change, per `CLAUDE.md`.
- **Never push to `main`.** This work is on `feat/rewrite-rules-extraction`,
  branched off `main`, and lands through a PR. Merging needs the maintainer's
  explicit OK.

## File Structure

| Path | Responsibility |
|---|---|
| `docs/rewrite-rules.md` | **New.** The rules that bound any rewrite of a user's message, plus how each consumer reports a violation. Sole owner of this contract. |
| `skills/compose/SKILL.md` | **Modified.** Step 0 gains the new doc; Step 2 becomes a pointer; version 3 → 4. Stops owning the rules it now reads. |
| `docs/README.md` | **Modified.** Indexes the new doc, and is corrected -- it currently omits three docs that exist and claims `voice.md` is unwritten. |
| `CHANGELOG.md` | **Modified.** One entry under `## [Unreleased]`. |

---

### Task 1: Extract the rules into a shared doc and point `compose` at it

**Files:**
- Create: `docs/rewrite-rules.md`
- Modify: `skills/compose/SKILL.md` (frontmatter `version`, Step 0 list, Step 2 body)
- Test: `tests/fixtures/sample-drafts-preflight.md` (existing fixture, read-only)

**Interfaces:**
- Consumes: nothing. This is the first task.
- Produces: `docs/rewrite-rules.md` at that exact path, referenced by later
  skills as `${CLAUDE_PLUGIN_ROOT}/docs/rewrite-rules.md`. PR 3's `preflight`
  rewrite depends on this path and on the document containing a section headed
  `## How a violation is reported` with a `preflight` bullet.

- [ ] **Step 1: Capture the behaviour baseline before changing anything**

There is no test runner in this repo; fixtures are exercised by hand through
the skills. The baseline is the test oracle, so it must be written down before
the edit rather than reconstructed from memory afterwards.

Run the `compose` skill twice, against two drafts from the existing fixture
`tests/fixtures/sample-drafts-preflight.md`:

- **Draft 1** ("should pass") -- exercises the clean path where no rule is
  strained.
- **Draft 2** ("can someone look at the migration thing, it's broken again") --
  exercises the path where substance checks fail and a `Comment` is emitted.

Save both outputs verbatim to the session scratchpad:

```
<scratchpad>/compose-baseline-draft1.txt
<scratchpad>/compose-baseline-draft2.txt
```

Do not edit or tidy the captured output. It is only useful if it is exact.

- [ ] **Step 2: Create `docs/rewrite-rules.md`**

The rules below are moved **verbatim** from `skills/compose/SKILL.md` Step 2.
The only additions are the framing intro and the reporting section, both of
which mirror how `docs/substance-checks.md` is structured.

```markdown
# Rewrite rules

The rules that bound any rewrite of a user's message. Written once and shared
by two consumers, the same way `substance-checks.md` is:

- **`compose`** applies them to every draft it writes or rewrites.
- **`preflight`** applies them to every wording fix it takes from a reviewer
  persona inside its review loop.

Neither skill restates these rules in its own body. Both point here.

## Keep the meaning identical

Meaning includes: the core message, the ask or decision, who it is addressed
to, constraints, timing, owners, how serious or blocking it is, and how certain
the user is ("I think" vs "I know").

Never:

- Change the stance, the priority, or the confidence level.
- Add facts, promises, commitments, deadlines, owners or scope.
- Add `@mentions`, `@here` or `@channel` that were not already there.
- Change numbers, dates, owners or scope.

## Copy these across untouched

`@mentions`, `#channels`, links, ticket IDs, file paths, error messages, logs,
code blocks, quoted text, and any pasted lines that start with `>`. Only
surrounding spacing and punctuation may change.

## Prior conversation context has a hard boundary

Earlier turns in this session may inform framing, tone, audience, and what the
reader can be assumed to already know. They may never become propositional
content: no fact, name, number, date, commitment or characterization enters the
message unless it is in the pasted draft, the intent block, or the thread
itself.

This is not an exemption from the rules above. If something from prior context
belongs in the message, it is reported as a question, never written in.

## How a violation is reported

A rule that would have to be broken to satisfy some other goal is never
silently broken, and the missing piece is never invented to avoid the problem.
What changes between consumers is only where it is reported:

- **`compose`:** name it in the `Comment` block, in one line.
- **`preflight`:** it becomes a content finding on the "Needs you" list, since
  a rewrite that cannot be made without adding a fact is by definition not a
  wording fix.
```

- [ ] **Step 3: Point `compose` Step 0 at the new doc**

In `skills/compose/SKILL.md`, the Step 0 list currently names three documents.
Add the new one as the second entry, so the order matches the order the rules
are applied:

```markdown
- `${CLAUDE_PLUGIN_ROOT}/docs/voice.md` -- the default voice. Always applies,
  layered under the user's own `writing-style.md` if one exists.
- `${CLAUDE_PLUGIN_ROOT}/docs/rewrite-rules.md` -- the rules that bound every
  rewrite. This skill applies them; it does not restate them.
- `${CLAUDE_PLUGIN_ROOT}/docs/substance-checks.md` -- the six substance checks
  this skill runs as a silent pre-flight when the goal is a request.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-contract.md` -- how `writing_style` and
  `personas` resolve, and the failure-behavior table.
```

- [ ] **Step 4: Replace `compose` Step 2's body with a pointer**

Replace the whole of Step 2 -- from the `## Step 2: rules you cannot break`
heading through the end of the prior-conversation paragraph -- with:

```markdown
## Step 2: rules you cannot break

Apply `${CLAUDE_PLUGIN_ROOT}/docs/rewrite-rules.md` in full. That document is
the contract; this skill does not restate it.

A rule that cannot be honoured is named in the `Comment` block, per that
document's reporting section. Never break one silently, and never invent the
missing piece to avoid the problem.
```

Leave every other step in `compose` untouched. Step 3's "Technical check",
Step 6's substance pre-flight and Step 7's Comment rules already refer to this
behaviour and stay exactly as they are.

- [ ] **Step 5: Bump the `compose` version**

In `skills/compose/SKILL.md` frontmatter, change `version: 3` to `version: 4`.
Leave `name`, `description`, `owner` and `pairs-with` alone -- the description
still describes what the skill does, and D8 changes no behaviour.

- [ ] **Step 6: Verify behaviour is unchanged**

Re-run `compose` against the same two fixture drafts from Step 1, in a fresh
context so the skill is read from disk rather than remembered.

Diff each result against its baseline:

```bash
diff <scratchpad>/compose-baseline-draft1.txt <scratchpad>/compose-after-draft1.txt
diff <scratchpad>/compose-baseline-draft2.txt <scratchpad>/compose-after-draft2.txt
```

Expected: **no substantive difference.** The ask, the addressee, the force, the
confidence level, the preserved `@mentions` and the presence or absence of a
`Comment` must all match. Incidental wording variation between two runs of a
generative skill is expected and is not a failure; a changed ask, a changed
`Comment` verdict, or a dropped `@mention` is.

If anything substantive differs, **stop**. The extraction was not verbatim.
Diff `docs/rewrite-rules.md` against the original Step 2 text in
`git show HEAD:skills/compose/SKILL.md` and find what changed.

- [ ] **Step 7: Check line endings, then commit**

```bash
git add docs/rewrite-rules.md skills/compose/SKILL.md
git diff --cached --stat
```

Expected: `skills/compose/SKILL.md` shows roughly **12 insertions and 25
deletions** -- Step 2's body is exactly 24 lines (`skills/compose/SKILL.md:55-78`)
and is replaced by about 8, Step 0 gains a 3-line bullet, and the version line
changes. The file is 190 lines total, so a diff reporting anything near
`190 insertions, 190 deletions` is CRLF, not a real change: run
`sed -i 's/\r$//' skills/compose/SKILL.md` and re-stage before committing.

```bash
git commit -m "refactor: extract compose's rewrite rules to a shared doc

Moves compose Step 2's \"rules you cannot break\" verbatim into
docs/rewrite-rules.md and points compose at it, so preflight can apply the
same contract to the wording fixes it takes from reviewer personas.

Mirrors decision S6, which extracted the six substance checks out of compose
into docs/substance-checks.md for the same reason: two consumers, one
contract, neither restating it.

The new document adds a \"How a violation is reported\" section, because the
rule is shared but the reporting channel is not -- compose names a violation
in its Comment block, preflight surfaces it as a content finding.

Behaviour-neutral. Verified by running compose against drafts 1 and 2 of
tests/fixtures/sample-drafts-preflight.md before and after the change: the
ask, addressee, force, confidence level, preserved mentions and Comment
verdict are unchanged in both.

Implements D8 of .claude/specs/2026-08-16-preflight-persona-loop-design.md."
```

---

### Task 2: Correct and extend the docs index

**Files:**
- Modify: `docs/README.md`

**Interfaces:**
- Consumes: `docs/rewrite-rules.md` from Task 1.
- Produces: nothing later tasks depend on.

- [ ] **Step 1: Confirm the index is wrong before changing it**

```bash
ls docs/
```

Expected: `README.md`, `config-contract.md`, `ledger-format.md`, `reading.md`,
`substance-checks.md`, `voice.md`. The index lists only two of the five
contracts and has a "Still to land" section claiming `voice.md` is unwritten.

- [ ] **Step 2: Rewrite the index body**

Replace everything below the `# docs/` heading and its intro paragraph with:

```markdown
- [`ledger-format.md`](ledger-format.md) -- the ledger file layout, the entry
  line shape, and how skills read it.
- [`config-contract.md`](config-contract.md) -- the `daikenja.yaml` schema, the
  lookup order, precedence, and failure behavior.
- [`reading.md`](reading.md) -- the shared read mechanism for `catchup`,
  `summary`, `decisions` and `gaps`: resolve config, find the ledger, parse it.
- [`voice.md`](voice.md) -- the default writing voice, which a user's own
  `writing-style.md` layers on top of. The layering contract is fixed in
  `config-contract.md`.
- [`substance-checks.md`](substance-checks.md) -- the six checks a request has
  to pass, shared by `compose` and `preflight`.
- [`rewrite-rules.md`](rewrite-rules.md) -- the rules that bound any rewrite of
  a user's message, shared by `compose` and `preflight`.
```

The "Still to land" section is deleted, not updated. Everything it listed has
landed.

- [ ] **Step 3: Commit**

```bash
git add docs/README.md
git diff --cached --stat
git commit -m "docs: index rewrite-rules.md and correct the stale docs index

docs/README.md listed two of the five contracts in docs/ and carried a
\"Still to land\" section claiming voice.md was unwritten. voice.md,
substance-checks.md and reading.md all exist and are read by shipped skills.

Adds the new rewrite-rules.md entry, adds the three missing entries, and
drops the Still to land section."
```

---

### Task 3: Changelog and pull request

**Files:**
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: Tasks 1 and 2.
- Produces: the PR that PR 2 and PR 3 branch independently of.

- [ ] **Step 1: Add the changelog entry**

`CHANGELOG.md` already has a `## [Unreleased]` heading with a `### Changed`
section under it. Add this entry to the **existing** `### Changed` section
nearest the top -- do not create a second one.

```markdown
- `compose`'s rewrite rules moved out of the skill into a shared
  `docs/rewrite-rules.md`, so `preflight` can apply the same contract. No
  behaviour change to `compose` (`skills/compose/SKILL.md`,
  `docs/rewrite-rules.md`).
```

Do not bump `.claude-plugin/plugin.json`. A release is its own atomic change.

- [ ] **Step 2: Commit and push**

```bash
git add CHANGELOG.md
git commit -m "docs: changelog entry for the rewrite-rules extraction"
git push -u origin feat/rewrite-rules-extraction
```

- [ ] **Step 3: Open the PR**

Base `main`, head `feat/rewrite-rules-extraction`. The body must state that
this is behaviour-neutral, name the fixture drafts used to verify it, and link
D8 of the spec. Include the exact before/after comparison result from Task 1
Step 6 -- not a claim that it was checked, the actual outcome.

- [ ] **Step 4: Stop**

Do not merge. Merging needs the maintainer's explicit OK, per `CLAUDE.md`.
Report the PR URL and the verification outcome, and stop there.

---

## Notes for the executor

**`compose` is a live shipped skill.** If Step 6's verification shows a real
behaviour change, the correct move is to fix the extraction, not to accept the
new behaviour and update the baseline. D8 is explicitly a refactor.

**Do not touch `tests/README.md`.** It is stale -- seven of the thirteen
fixtures in `tests/fixtures/` are unlisted -- but that is out of scope here and
is being captured as its own issue.

**Do not start PR 2 or PR 3.** They are separate sessions with their own
branches off `main`, per § 10.3 of the spec.
