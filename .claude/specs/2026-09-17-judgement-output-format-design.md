# Design: judgement, and the shape of what the bot posts

**Date:** 17 Sep 2026
**Status:** approved design, not yet implemented.
**Affects:** `skills/verdict` (renamed to `skills/judgement`), `skills/thread`,
`docs/response-format.md`, `bot/daikenja_bot/prompts.py`,
`bot/daikenja_bot/commands.py`, `tests/fixtures/`, and every file that names
`verdict`.

---

## 1. Summary

The Slack bot posted its first real answers on 17 Sep 2026, and the shape of
what it posted was wrong in four ways that the contracts made unavoidable
rather than accidental. This design fixes the shapes, renames the `verdict`
skill to `judgement`, and adds one shared rule to `response-format.md` that
the bot surface made visible for the first time.

Nothing here has been released. `verdict` and `bot/` are both under
`## [Unreleased]` in `CHANGELOG.md` and `plugin.json` is on `0.9.1`, so the
rename reaches no installed copy, needs no `docs/upgrading.md` entry, and
keeps no compatibility alias.

## 2. The evidence

Two real runs in a Slack channel, 17 Sep 2026.

**Run A, summary over a pasted block:**

```
Thread: pasted block, 2 messages, channel not stated
Asking: you, of yourself -- no one else has spoken; message [2] pings a bot
Open: whether SOL keeps database backups at all, or relies on high
availability plus a USB drive
Waiting on you: everything -- there is no counterparty in this thread yet
```

followed, in the posted message, by two bare fence lines rendering as an
empty code block.

**Run B, summary over a linked thread**, two hours later:

```
Thread: DBO group ping (Slack), 8 messages, Daisy Ding and you
Asking: Daisy -- (a) confirm the job schedule fix, (b) should she re-enable
        SOL logging and for how long, (c) which table holds the audit
```

Run B's opening line is what the contract is supposed to produce. Run A's is
the same contract read the other way. The defect is in the contract, not in
the model.

**Run C, the verdict form**, opened with
`Subject: pasted thread, 2 messages, channel not stated, 17 September 2026`
and then flattened the ledger line, three findings, an unestablished-claim
flag, the suggestion and the scope exclusion into one undifferentiated
bullet list, with confidence labels buried mid-sentence.

## 3. The four defects

**D1 -- the summary describes its own plumbing.** `thread` § Step 2 fixes
`Thread: [channel or subject, and how many messages]`. The `or` lets the
model satisfy the contract by naming the input mechanism (`pasted block`) and
narrating an absence (`channel not stated`). Both are facts about how the
bot was invoked, not about the thread, and a reader of a public channel
cannot use either.

**D2 -- the second person has no referent on a public surface.** `Waiting on
you`, `Daisy Ding and you`. In the Claude Code reply there is exactly one
reader and `you` is correct. In a posted message every other participant has
to guess who it means. The current contracts do not distinguish the two
surfaces, because until the bot existed there was only one.

**D3 -- a stray fence reaches Slack.** Run A ends with two bare ``` lines --
an empty code block. `mrkdwn.py` collapses a fence line to ``` but never
invents one, so the session emitted the pair inside the sentinels.
`prompts.py`'s `_unfence` strips a fence only when the whole deliverable is
one, so a trailing pair survives.

**D4 -- the verdict has no structure.** One bullet list carrying five
different kinds of statement. The `Subject:` line restates the input
mechanism and adds today's date, which the Slack timestamp already carries.
The ledger-absent case spends the first and most-read bullet saying that
nothing happened. Confidence sits mid-sentence where it cannot be skimmed.

## 4. Decisions

- **D-1: rename `verdict` to `judgement`.** Hard rename, no alias. Nothing
  is released, so nothing breaks. British spelling, matching the repository
  (`summarises`, `recognisable`).
- **D-2: the section that holds the bullets is `Basis`, and `Verdict` is
  the one-or-two-sentence takeaway that leads the message.** Two sections
  cannot both be called Verdict, and the bullets are what the verdict rests
  on.
- **D-3: `Tone` never leaves the session.** It exists to feed `compose`, and
  the bot never reaches `compose`. A bot publicly labelling a colleague's
  message `tense` has a cost and no use.
- **D-4: the `AI review summary` header is dropped from the posted form.**
  Its job is provenance -- marking the block as an AI pass rather than the
  user speaking -- and in Slack the `Daikenja APP` badge does that job
  already. `⚖️ **Verdict**` opens the message instead.
- **D-5: `Not checked` keeps its name.** `Unknowns` was considered and
  rejected: a scope exclusion is the review admitting what it did not cover,
  while `Unknowns` shifts the burden onto the world. An unstated scope
  exclusion is a defect of a review, and the label has to say so.
- **D-6: markers apply to both surfaces.** The block shapes are shared
  between the skill's `answer` form and the bot's `message` form. One shape
  means one contract and one set of extraction patterns.
- **D-7: the fence fix is deterministic, in the bot.** Strip fence lines
  during extraction rather than instructing the model not to emit them. The
  prompt already says not to; it happened anyway.

## 5. Shape: the summary block

Fixed by `thread` § Step 2 and restated by `judgement` § Step 2. Skills write
plain markdown; `mrkdwn.py` converts it.

```
🧵 **Thread** -- what it is about, who is in it, and how many messages
❓ **Asking** -- who is asking, and what they actually want
🔓 **Open** -- what is still undecided
⏳ **Waiting on** -- <name>: what is theirs
📒 **Ledger** -- <project>: what it has on this
🌡️ **Tone** -- neutral / tense / urgent
```

For a document, `📄 **Document**` replaces `🧵 **Thread**` and
`📌 **Claims**` replaces `❓ **Asking**`, as today.

Rules that change:

- **The `Thread` line leads with subject matter.** What the thread is about
  comes first, then who is in it, then the count. The line **never names how
  the content arrived** -- not `pasted block`, not `link`, not `forwarded` --
  and **never states an absence**. A channel that is not known is not
  mentioned; `channel not stated` is a defect.
- **`Waiting on` carries a name**, except in the `answer` form, where `you`
  is correct because there is one reader. One label, two values.
- **`Tone` is written in the `answer` form only.** Any form that leaves the
  session omits it, empty or not.
- Every other line is omitted when it would be empty, as today.

## 6. Shape: the `judgement` message form

Replaces `verdict` § Step 5 Form `message` in full.

```
⚖️ **Verdict**
One or two sentences that answer what the subject asks or judge what it
claims, each clause labelled with where it came from.

📒 **Ledger -- <project>**
• **<decision topic>** (D-005) -- what the subject says and how it bears on
  that decision. _certain · ledger_

🔍 **Basis**
• **<topic>** -- the finding. _certain · general knowledge_
• **<claim asserted, not established>** -- why it is not established.
  _certain · not established_

💡 **Suggestion**
• The action, framed as a suggestion.

🚧 **Not checked**
• One line.
```

Rules:

- **`📒 Ledger` is absent entirely when no project resolved.** Not a bullet
  saying no ledger was checked -- absent. The reason a project could not be
  resolved belongs in the short report around the message, never in the
  message. A resolved project is named by its human-readable name in the
  section header, never by a bare key alone.
- **Every `Basis` bullet opens with a bold topic and closes with an italic
  `_<confidence> · <source>_`.** Confidence is one of `certain`, `likely`,
  `guessing`. Source is `ledger`, `general knowledge`, or `not established`
  for a claim the subject presents as settled without establishing it.
- **`Suggestion` and `Not checked` are sections, not bullets in a list of
  findings.** Each is omitted only if it would be empty; `Not checked` is
  never empty.
- **No `Subject:` line and no date.** The surface carries both.
- **The deliverable is never wrapped in a code fence and never contains
  one**, even when the subject it is assessing quotes a fenced snippet. A
  quoted line is named or restated inline instead of fenced.
- A clean subject is `⚖️ **Verdict**` with its sentence and
  `🚧 **Not checked**` with its line. Nothing else.

The `answer` form keeps the same section shapes, gains the `🌡️ Tone` line in
its summary block, and keeps the `Ledger:` and `Card:` provenance lines that
`judgement` § Step 3 fixes, since those are conversation.

## 7. New shared rule: the second person belongs to conversation

Added to `docs/response-format.md` as its own section, with reverse-index
entries for `judgement`, `thread`, `compose` and `preflight`.

> A reply the user reads in their own session addresses them as `you`.
> Anything the skill hands back to leave that session -- a message to post,
> a document to share, a block to paste elsewhere -- names people instead.
> The second person has exactly one referent in a conversation and none in a
> channel, so a deliverable that says `you` is ambiguous to every reader it
> was written for.

This belongs in the shared contract rather than inside `judgement` because
`thread` and `preflight` also hand back leaving-the-session material.
`compose` was considered too, but its deliverable is a message written **as
the user, to a named recipient**, where `you` means that recipient and is
correct -- so `compose` is deliberately left out of the reverse index.

## 8. Bot changes

`bot/daikenja_bot/prompts.py`:

1. **`SUMMARY_LABELS` / `SUMMARY_OPENERS`.** `_EMPHASIS_PREFIX` learns a
   leading emoji so `🧵 **Thread** --` matches. The label set is unchanged
   apart from `Waiting on you` becoming `Waiting on`.
2. **`_verdict_block` loses its `AI review summary` anchor.** `VERDICT_HEADER`
   is deleted. The block is anchored on the `⚖️ Verdict` section and runs
   until a line that is none of: a known section header, a bullet, an
   indented continuation, or the lead sentence directly under `⚖️ Verdict`.
   The current rule stops at a blank line unless bullets resume, which
   cannot span sections; this is the substantial piece of work in the bot.
3. **Fence stripping.** After extraction, drop every line that `FENCE_RE`
   already matches (a line whose first non-space characters are three
   backticks) from the deliverable, for both commands. Neither deliverable
   ever legitimately contains a fence.
4. **`_TASK` and `_SKILL_INVOCATION`** name `judgement` and describe the new
   sections.

`bot/daikenja_bot/commands.py`: the `VERDICT` constant becomes `JUDGEMENT`
and the command word becomes `judgement`. No alias (D-1).

## 9. Rename scope

32 files name `verdict`. The mechanical set:

- `skills/verdict/` → `skills/judgement/`, and its `name:` field.
- `tests/fixtures/verdict.md` → `judgement.md`.
- `bot/`: `commands.py`, `prompts.py`, `config.py`, `confluence.py`,
  `preflight.py`, `subject.py`, `transcript.py`, `README.md`, and the seven
  test modules.
- `docs/`: `response-format.md`, `config-resolution.md`, `project-card.md`,
  `reading.md`, `preflight-reference.md`, `reviewer-personas.md`,
  `substance-checks.md`.
- `skills/preflight`, `skills/self-review`, `skills/remember-persona`.
- `README.md`, `tests/README.md`, `.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json`, `CHANGELOG.md` (the `## [Unreleased]`
  entry is rewritten, not appended to -- it describes an unreleased feature
  that is changing).
- `.claude/specs/2026-08-16-preflight-persona-loop-design.md` is a
  historical record and is **not** edited.

`tests/check-invariants.py` validates `response-format.md`'s reverse index
against SKILL.md headings, so the index entries move with the rename and
gain the new section from § 7.

## 10. Work order

One integration branch, `feat/judgement-output-format`, off `main`.

1. **The rename alone.** No shape changes. `tests/check-invariants.py` and
   the `bot/` test suite both pass unchanged apart from the name.
2. **The shared rule.** `docs/response-format.md` § the second person, plus
   reverse-index entries.
3. **The summary block.** `thread` § Step 2, `judgement` § Step 2, and the
   `SUMMARY_LABELS` regexes together, since the skill shape and the
   extraction pattern are one contract.
4. **The judgement message form.** `judgement` § Step 5 and `_verdict_block`
   together, for the same reason.
5. **Fence stripping**, with its own unit tests.
6. **Fixtures.** `tests/fixtures/judgement.md` and the `thread` fixtures
   gain a case for a subject with no channel and a case with a stray fence.

## 11. Verification

There is no test runner for the skills, so the shapes are exercised by hand
through the fixtures, per `tests/fixtures/` convention. The bot has a real
suite.

- `pytest` in `bot/` -- the extraction patterns, the fence stripping and the
  mrkdwn conversion are pure string transforms and are covered there.
- `python tests/check-invariants.py` -- the reverse index.
- By hand, through the bot, against a live thread: a linked thread, a pasted
  block with no channel, a subject that resolves a project, and a subject
  that resolves none. The last two are the ones that decide whether
  `📒 Ledger` appears and disappears correctly.

## 12. Out of scope

- `voice.md` is not changed. It governs how drafted prose reads, not how a
  report is sectioned.
- `skills/tensei` is not changed. Its markers are conversational and it
  already states that markers never appear inside a deliverable. The section
  markers in § 5 and § 6 are the deliverable's own, defined by these two
  skills, and the two sets are deliberately distinct.
- `compose` and `preflight` are not changed beyond the rename and picking up
  the § 7 rule, which their existing wording already satisfies.
- No release. The version stays `0.9.1` and the changelog entry stays under
  `## [Unreleased]`.
