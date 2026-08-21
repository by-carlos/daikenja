---
name: preflight
description: Challenges a draft before it goes out and hands back a revised version plus the facts only you can supply. Runs the six substance checks, then puts the draft in front of a set of reviewer personas -- the busy reader, the executive, the risk reader, a named recipient you describe -- fixes the wording problems they raise, and asks you about anything that needs a fact the draft does not contain. Use for "would this survive X", "poke holes in this", "what will they come back with", "is this ready to go", "should I even raise this", or "am I missing something before I send this". Not for making a message read better when nobody needs to challenge it, which is /daikenja:compose. This skill never sends anything.
metadata:
  owner: Carlos
  version: 8
  pairs-with: compose
---

# Preflight

A bounded review loop. Run the substance checks, put the draft in front of
reviewers who each read it for a different failure mode, apply what can be
fixed, re-check once, and hand back a revised draft plus the questions only the
user can answer.

A real preflight is a walkaround where the pilot fixes what they find and looks
again. Iteration is already in the name.

**The rule that makes the loop safe, and the one this skill cannot break:**

> **The loop may change wording. It may never change content.**

Anything a reviewer raises that cannot be fixed from material already in the
draft becomes a question back to the user. It never becomes an invented
sentence. This skill has no send action.

## The model this context runs on

Check this first, before Step 0.

The safety hinge is Step 6, where every proposed fix is tested against the
draft: one that needs an absent fact is reclassified instead of applied, and
one that needs nothing outside the draft is applied instead of sent back as a
question. That judgment is the whole difference between a loop that revises and
a loop that invents, and it is materially better on Opus.

**If you can tell you are not running on Opus, say this in one line, then
carry on:**

```
Running on <model>. This loop's adjudication step is materially better on Opus
-- `/model opus` and re-run if this message matters.
```

**This never blocks**, per `config-resolution.md`'s standing rule -- one notice
line, then continue with reduced behaviour. A weaker model still runs the whole
loop. It is just likelier to let an invented fact through Step 6, which is the
one error the user cannot see by reading the output.

**Say nothing when you are on Opus, and say nothing when you cannot tell.** A
hedged nag on every run is worse than no notice at all.

**This is about `preflight`'s own context, not the reviewers.** Each reviewer
is dispatched on the model tier its archetype carries, per
`docs/reviewer-personas.md` § What each reviewer runs on, whatever this context
is running on. A weak busy reader is the intended behaviour; a weak adjudicator
is not.

## Step 0: read the shared docs

Read these before doing anything. Do not work from memory of them.

- `${CLAUDE_PLUGIN_ROOT}/docs/substance-checks.md` -- the six checks in cycle 0.
- `${CLAUDE_PLUGIN_ROOT}/docs/reviewer-personas.md` -- the reviewer roster, the
  two always-on checks, the model tier each reviewer runs on, and the critique
  contract. This skill selects from that roster and never invents a reviewer.
- `${CLAUDE_PLUGIN_ROOT}/docs/rewrite-rules.md` -- the rules that bound every
  wording fix this skill applies.
- `${CLAUDE_PLUGIN_ROOT}/docs/voice.md` -- the default voice every rewrite is
  written in.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-resolution.md` -- how `writing_style` and
  `personas` resolve, and the failure-behavior table.
- `${CLAUDE_PLUGIN_ROOT}/docs/config-schema.md` § Field notes -- where
  `profile.tone` is defined.
- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- how the reply to the user
  is shaped. The report in Step 10 implements it.

## Step 1: take the input as given

- **A pasted draft.** The normal case, and the only shape the loop runs on.
  Everything below applies.
- **No draft, just a description** of what the user wants to raise ("should I
  even bring up that the migration slipped again?"). There is no text for a
  reviewer to read, so run cycle 0 against the description, report the verdict,
  and stop. Say what is missing and hand off: "Run `/daikenja:compose` when you
  want this drafted." Do not draft it here, not even a rough version.
- **Neither.** Ask for one. Do not guess what the user wants to raise.

Do not invent or fill in anything absent from what was given. A gap is a
finding, never something to guess at.

### Re-running on the same draft

If this skill already produced a report on a draft in this conversation, and
the input now is a revision of that same draft rather than a new one, this run
does not start cold.

First, collect every direction the user has given since that report -- an
answer to a `Needs you` question, a fact supplied outright, a conflict
resolved by choosing one side. State each as **settled** in one line and never
raise it again in this run, whether or not the revised draft's wording
visibly reflects it.

Then continue the loop from Step 2 as normal, and raise only what the earlier
report did not already ask: a genuinely new question, or a fact none of the
user's directions answered.

A draft with no earlier report in this conversation is not a re-run, whatever
it contains. Do not search for or assume a report that is not in front of you.

## Step 2: determine the goal

The six substance checks apply only when the goal is a `request` -- asking
someone to do, decide, or answer something. If the goal is obvious from the
input, use it. Otherwise ask one short question: "Is this asking someone to do
or decide something, or just informing them?"

- **A request.** Run cycle 0, then the loop.
- **Not a request** (announcement, FYI, status update). **Skip cycle 0 and go
  straight to the loop.** The substance checks do not apply, and say so in one
  line -- but an announcement can still be too long, land badly, or read as
  blame, and those are exactly what the reviewers catch.

## Step 3: cycle 0 -- the substance checks

Run all six checks from `docs/substance-checks.md` against the draft. Report
every check, pass or fail, per Step 10's depth rule.

For check 6, **already answered**, only check material this skill can actually
see:

- A pasted thread or conversation, if one was given alongside the draft.
- The project's ledger, if a project is configured and a ledger is found
  (`~/.claude/daikenja/daikenja.yaml`, resolved per `docs/config-resolution.md` §
  Resolution order; `.daikenja/ledger.md` if unconfigured). Read it the way
  `docs/reading.md` § Step A-C describes, for lookup only -- this skill never
  writes to it.

If neither is available, say so plainly rather than implying a broader check
happened: "Already answered: not checked -- no thread or ledger was available
to check against." That is not a pass and not a fail; it is an honest gap,
reported alongside the other five.

**A failing check does not stop the loop.** It is a content gap by definition --
the missing piece is a fact only the user has -- so it joins the questions list
in Step 10 and the loop carries on. Never invent the missing piece to turn a fail
into a pass.

## Step 4: select the reviewers

Two counts, kept separate. **Archetypes cap at 4. Persona slots cap at 2.**
Naming a person must never cost a lens.

### The archetypes

1. **The busy reader is pinned.** It runs on every draft, always, without
   inference. Length and a buried ask are failure modes on essentially every
   message regardless of audience.
2. **Infer three more** from the draft itself -- what it asks, who it lands on,
   and what it touches:

   | Signal in the draft | Reviewer |
   |---|---|
   | Money, HR, legal, security, an incident, or blame attached to a person | the risk reader |
   | A decision going to a director or above | the executive |
   | Numbers, causal claims, technical assertions | the fact-checker |
   | A request that lands on one identifiable person | the person being asked to do the work |
   | Frustration in the source, or a history the reader may take personally | the tone-sensitive reader |
   | Cheer, "as discussed", or anything the sender means more warmly than it reads | the subtext reader |
   | A ticket system, an assistant or an agent will read it; or the ask is compound | the machine reader |
   | The message is arguing a position someone has not accepted yet | the dissenter |

   The dissenter is **inference-only and never pinned**. It runs when the
   message is trying to persuade, and not otherwise.

3. **Skip an archetype a named persona already carries in full.** A generic
   executive alongside a named person who *is* the executive returns the same
   findings twice. The freed slot goes to the next uncovered lens, so the count
   stays at 4.

### The named personas

**Only people the draft actually addresses become reviewers.** `personas.md` is
an index, not a roster to sweep. This is what stops a large org from exploding
the reviewer count.

`personas.md` below means whatever `profile.personas` resolves to -- a local
file or a Google Drive file, per `config-resolution.md` § Resolving
`writing_style` and `personas`. Nothing in this skill changes with the form of
the pointer except what happens when it fails.

For each addressee, assemble a brief per `docs/reviewer-personas.md` § How a
brief is assembled -- the archetype they embody, plus their `personas.md` entry
if one matches, plus whatever the user said inline this run. Inline wins over
the file; the file wins over the archetype.

- **Named, with nothing known about them.** Not in `personas.md`, nothing said
  inline. Archetypes only. Not an error, but name the capture path: one line in
  the report that no `personas.md` entry exists for them and `/daikenja:remember-persona`
  is how to add one.
- **A local `personas` pointer does not resolve.** Silent. The `Reviewers:` line
  already names what ran, which makes a notice redundant.
- **A `drive:` pointer does not resolve, or reads back empty.** Stop and name
  the file, per `config-resolution.md` § Failure behavior. This one is not silent:
  reviewing without the personas the user configured would look like reviewing
  with them.
- **More addressees than slots.** Direct addressees beat cc'd. Name who was
  dropped in the report.

A `personas.md` entry is scoped to that person and **never modifies a shipped
archetype for anyone else**. Changing an archetype globally is a pull request to
`docs/reviewer-personas.md`.

## Step 5: cycle 1 -- dispatch

Dispatch **one subagent per selected reviewer, all in a single parallel block**.
Each subagent gets the draft and its own brief, and nothing else -- not the
other reviewers, not their findings, and **not the cycle-0 verdict**, which
would anchor it onto ground already covered.

Isolation is the point. A reviewer that can see another reviewer's critique
defers to it, and the second opinion stops being one.

**Dispatch each reviewer on the model tier its archetype carries**, from
`docs/reviewer-personas.md` § What each reviewer runs on. Pass the tier as the
subagent's model at dispatch, as the family alias that table gives -- `haiku`,
`sonnet` or `opus`, never a versioned model ID. A named addressee takes the
tier of the archetype it embodies.

**Do not raise or lower a tier to match the session.** The tiers are what each
persona simulates, not a budget. The busy reader is *meant* to be weaker than
the session -- a strong model asked to skim reads properly and then reports what
a skimmer would have missed, which is a different signal -- and the risk reader
is meant to be strong whatever the session is set to.

If the dispatch available to you takes no model, dispatch anyway and say
nothing. The tier is a preference, not a dependency, per `config-resolution.md`'s
standing rule: continue with reduced behaviour rather than stopping.

At the same time, in this context, run the two checks that never dispatch --
the AI-tell check and non-native English readability, both defined in
`docs/reviewer-personas.md`.

**Discard any finding that misses either bar in `docs/reviewer-personas.md`
§ The critique contract.** A finding that cannot quote the span it is reacting
to is too vague to act on, and a finding whose stated cost is only that a reader
might land somewhere else has not said what the draft loses by keeping the
phrase. Discard both outright. Do not go looking for what a finding might have
meant, and do not carry a weak one forward as a nitpick -- a finding that was
not worth applying is not worth mentioning either.

**Discarding is not overruling the reviewer.** Both bars are part of the brief
every reviewer was given, so a finding that misses one was never within the
contract to begin with. This is not the same as disagreeing with a finding that
clears both, which Step 6 and § Conflicts handle.

## Step 6: adjudicate -- the safety hinge

**Decide the wording-or-content call yourself. Do not trust the subagent's
label.** A reviewer can label either way round: it can call a content gap a
wording fix and smuggle an invented fact in through its suggested `Fix`, and it
can call a wording fix a content gap and send the user a question they did not
need. This is the one place both get caught.

Every proposed fix gets one test:

> **Is this expressible using only material already in the draft?**

- **Yes.** It is a wording fix. Apply it in Step 7.
- **No -- it introduces a fact, number, date, owner, constraint or commitment
  the draft does not contain.** Reclassify it as content. It goes to the
  questions list with the fact named, and the suggested `Fix` is discarded
  rather than softened into place.

**The test asks what the fix needs, not what the finding noticed.** A reviewer
often notices a problem by reasoning about something outside the draft. That
does not make the repair a content gap. Test the repair.

Prior turns in this conversation are not a source of content, per
`docs/rewrite-rules.md` § Prior conversation context. Knowing the answer does not
license writing it in. If it belongs in the message, it is a question.

### The hinge fails in two directions

Both directions are wrong, and neither is a safe default to drift toward.

**Inventing.** A fix that needs a fact the draft does not have is applied
anyway, and the message goes out carrying something the user never said. This
is the hinge's primary job and nothing below relaxes it: a fix that introduces
a fact, number, date, owner or commitment is content, every time, whatever
label the reviewer put on it.

**Over-referring.** A fix that needs nothing outside the draft is sent back as
a question. The user is asked for a fact the message did not need, and because
the verdict line counts outstanding facts, a draft that was ready to send is
reported as blocked. One unnecessary question also teaches the user that the
questions are optional, which is how a real one gets skipped.

**Deleting words is a wording fix.** A fix that only removes or rearranges what
is already on the page needs no fact from outside the draft, so it stays a
wording fix even when the reason to remove it turns on something only the
sender knows. Cut the words and say so.

Worked example. A reviewer flags "as discussed" in a draft whose reader may
remember no such discussion, and the same for "as you know". The repair is to
delete four words. The revised message says everything it said before without
them, and nothing outside the draft was needed to write it -- so it is a
wording fix, applied in Step 7, and it produces no question. Asking the user
"is 'as discussed' accurate?" turns a deletion into a blocker.

**When a phrase is a content gap.** Only when the message needs the absent fact
in order to stand -- cut the phrase, and the draft loses something it depends
on. "As we agreed on the call, I am proceeding on Tuesday" grounds the whole
ask in an agreement, and deleting the clause leaves the ask with no basis, so
what the agreement actually was is a question. "As discussed, here is the
staging failure" grounds nothing, and deleting it costs the message nothing.

### Conflicts

There is no "primary recipient" to arbitrate toward. Work messages routinely go
to several people at once, so a rule that picks one addressee is picking a
fiction. In order:

1. **Try to satisfy both.** Most conflicts are false ones -- length can usually
   come out somewhere other than the constraint the fact-checker wants kept. A
   fix that serves both is applied like any other and needs no disclosure.
2. **Archetype versus archetype**, where neither is a real addressee: resolve
   silently toward whichever real audience the message actually has. Archetypes
   are proxies for readers, not readers, and a proxy does not outrank a person.
   This is not reported.
3. **Recipient versus recipient**, where both are people the message genuinely
   addresses and no fix serves both: **report it and resolve nothing.** It
   usually means the message is serving two audiences and wants splitting, or
   that one audience needs a separate note. Say that, rather than quietly
   picking a winner.

Case 3 is reported alongside the content questions in Step 10, because like
them it is something only the user can settle.

## Step 7: rewrite -- never dispatched

Apply the accepted wording fixes here, in this context. **The rewrite step is
never delegated.** Rewriting is where invention happens, so it stays in the one
place that has read `docs/rewrite-rules.md`, `docs/voice.md` and the user's own
writing style.

- Apply `docs/rewrite-rules.md` in full. The ask, the stance, the confidence
  level, the owners, the timing and how blocking it is all survive untouched.
- Apply `docs/voice.md`, layered under the user's `writing_style` prose if the
  pointer resolves -- that prose reaches the file's `## Defaults` tier only, and
  a line contradicting a `## Fixed` rule is not applied
  (`profile.writing_style`, per `config-resolution.md`
  § Resolving `writing_style` and `personas` -- a local file or a Google Drive
  file). A local pointer that does not resolve gets one notice, then the default
  voice alone; a `drive:` pointer that fails stops the run, per that document's
  § Failure behavior.
- A rule that cannot be honoured is named in the report, never broken silently.

**Keep a record of what this step changed, finding by finding.** Against each
cycle-1 finding write either the edit made in answer to it, or nothing. A
content finding gets nothing by definition -- its repair needed a fact the draft
does not have. So does a finding left unfixed because no fix served both
recipients, per Step 6 case 3. Step 8 reads this record, and without it cycle 2
cannot tell a fix that landed from a sentence nobody touched.

## Step 8: cycle 2 -- re-check once

**Re-dispatch only the reviewers that raised something in cycle 1**, each on the
same model tier it ran on then, against the revised draft. They read the
revision and say whether each problem is still there.

- New wording findings are adjudicated and applied the same way.
- New content findings join the questions list.
- **Zero wording findings in cycle 1 skips cycle 2 entirely.** There is nothing
  to re-read.

### A finding is resolved only where Step 7 changed something

A cycle-2 reviewer **reads cold**. Step 5's isolation rule means it has not seen
its own cycle-1 finding, so what comes back is a second read of the revision and
not a memory of what it said the first time. It can therefore decide it no
longer minds a sentence nobody touched. On 20 August 2026 two reviewers did
exactly that: both closed a cycle-1 finding by citing a clause that was in the
original draft and had never been edited, and the finding left the report with
nothing in the message having changed.

So the resolution is not the reviewer's to give on its own:

> **A cycle-1 finding is recorded as resolved only where Step 7's record shows
> an edit made in answer to it. A finding with nothing recorded against it
> stands, whatever cycle 2 says about it.**

- **Step 7 edited for it and cycle 2 finds it gone.** Resolved. Drop it.
- **Step 7 edited for it and cycle 2 still raises it.** It stands. The edit did
  not land, which is the thing cycle 2 exists to catch.
- **Step 7 made no edit for it.** It stands as a **restate**, and cycle 2's
  reading changes nothing. Report it where it already sat -- a content finding
  in the `Needs you` list, an unresolvable recipient conflict in the conflict
  line.

**The test is the edit, not the wording of the anchor.** A length finding
answered by cutting a different paragraph was acted on, and cycle 2 may close
it. Where the record is empty nothing was acted on, and no reading of the
revision changes that.

This adds no cycle and no reviewer. It is a check on what the loop already
holds, applied before a finding is allowed to leave the report.

**If cycle 2 runs at all, it runs as a dispatch. Cost is not a reason to skip
it.** Judging in this context that a fix "plainly resolves" a reviewer's finding
is the exact unchecked self-assessment cycle 2 exists to prevent -- the reviewer
raised it, the reviewer has not seen the revision, and the reviewer is the one
who says whether it landed. Spawning fewer agents is not a saving if what you
bought was the confirmation.

**The loop stops here. Two cycles, no exceptions.** After the first rewrite what
remains is almost always content, which no further cycle can fix. Collect it and
report it once rather than bouncing back at the user three separate times.

## Step 9: learned personas

If the user described someone inline who has no entry in `personas.md`, route
that description to `/daikenja:remember-persona`, which is the only skill that
writes persona content. Pass on what the user actually said and nothing
inferred from the draft.

**Never route a person out of material that says it is synthetic.** Acceptance
fixtures and worked examples describe invented people, and writing them into the
user's real file pollutes it with people who do not exist. Skip the routing
silently and say so in one line in the report.

**Whether a person the material does not vouch for gets written is not this
skill's call.** A review almost always runs on a pasted draft, so almost every
person routed from here arrives with pasted material -- and `remember-persona`
holds the one test that decides what happens to those, per its Step 1 § Where
the description came from. Route the description with what the user said and
leave the decision there. Do not add a second test here, and do not pre-judge
which people are real.

The outcome comes back as one line for Step 10 -- `Learned:` where the entry was
written, `Not learned:` where it was offered instead. Either way this skill
carries on: it never waits for the answer, and a missing `personas.md` comes
back as one line too. Nothing about a persona blocks a review.

## Step 10: report

The shape below implements `response-format.md`; where the two ever disagree,
the contract wins. Verdict first, deliverable second, evidence third:

```
Verdict: needs 2 facts from you before it goes

<the revised message>

Needs you
1. [the fact-checker] The message says the migration "will take a while" --
   they need the actual window to plan around it. You have not stated one.
2. [substance check: attempts stated] The message asks priya to look at the
   failure but does not say what you already tried.

Reviewers: busy reader (always on), the executive (the ask lands with a
director), S (named in the draft)

Reviewed: dispatched, each reviewer reading cold.
Applied: 4 wording fixes across 2 cycles.
Conflict: R needs the rollback detail kept and M needs this under ten lines.
No fix serves both -- this may want to be two messages.
Learned: added S to ~/.claude/daikenja/personas.md.
```

The verdict line is `ready to send` or `needs <n> facts from you before it
goes`. Nothing else.

**`Learned:` has a counterpart that says nothing was written.** Where Step 9
routed someone and `remember-persona` offered the entry instead of writing it,
the line reads `Not learned: S came in with the material you pasted, so I have
not added them to ~/.claude/daikenja/personas.md. Say the word and I will.` It
is one line in the same place, it carries the question, and the verdict above it
is unaffected -- the review is finished either way.

**`Applied:` counts edits, not findings closed.** It is the number of wording
fixes Step 7 actually made across both cycles. A cycle-1 finding that stands
under Step 8 was never an edit, so it is not counted there and it does not
leave the report -- it stays in the `Needs you` list or the conflict line it
already belonged to.

### Reporting a re-run

When Step 1's re-run rule applied, the report carries one more line,
`Settled since last run:`, naming what the user's directions closed out since
the earlier report. It sits after `Needs you` when there is a list, or after
the draft when there is not:

```
Settled since last run: the window (12 minutes), and that in-flight requests
fail and must be retried rather than queuing.
```

**If this is the second consecutive run on the same draft and the verdict is
still `needs <n> facts`, say whether that is all of it.** State plainly
whether the remaining `Needs you` items are the complete set -- nothing else
is expected to surface on a further revision -- or whether more may still
emerge once the draft changes again. Name every remaining fact in the `Needs
you` list itself; this line adds only the finite-or-not statement, not a
second listing.

### The `Reviewed:` line is mandatory

**Every report carries it, on every run, whichever way the reviewers ran.** It
is not a warning that appears when something is wrong -- it is a statement of
how this particular run was produced, and it is written last, from what
actually happened, never from what was supposed to happen.

| How the reviewers ran | The exact line |
|---|---|
| Dispatched | `Reviewed: dispatched, each reviewer reading cold.` |
| In this context | `Reviewed: in sequence in this context -- no dispatch available, so the reviewers are not independent and each one had read the ones before it. Treat this as weaker than a dispatched run.` |

Stating it unconditionally is the point. A notice that only appears when
dispatch is missing asks this skill to notice an absence, and an absence is the
one thing it reliably fails to notice -- so the run that most needs the warning
is the run least likely to print it.

**When the reviewers ran in this context, cycle 2 confirmed nothing.** Say
`re-read once in the same context`, never `confirmed`. A reviewer that never
read the revision independently cannot confirm a fix landed, and a report that
says it did has invented the one thing the second cycle exists to buy.

**A dispatched cycle 2 is a second read of the revision, not a memory of the
first read.** The re-dispatched reviewer reads cold, per Step 5, and has not
seen its own cycle-1 finding. What it can settle is whether an edit landed. A
finding Step 7 never edited for is not its to close, per Step 8, and it stays
in the report whichever way the reviewers ran.

**Depth keys off `profile.tone`**, per `docs/config-schema.md` § Field notes:

| `tone` | What the report shows |
|---|---|
| `direct` | The six checks collapse to one line when they all pass. Only failures are itemised. |
| `standard` | Every check on its own line. Findings summarised without their anchors. |
| `guided` | All six checks, every finding with its anchor, and the reasoning behind each fix. |

**A clean draft produces a short report, not a padded one.** If every reviewer
returns nothing -- because nothing was raised, or because nothing raised cleared
the two bars -- say so plainly and hand back the draft unchanged.

That report is the verdict, the original draft and the evidence lines, and
nothing else:

```
Verdict: ready to send

<the draft, exactly as the user gave it>

Nothing to fix. No reviewer found anything that would change how this lands.

Reviewers: busy reader (always on), the machine reader (the ask is a dated
question someone may action from a summary)

Reviewed: dispatched, each reviewer reading cold.
Applied: no fixes -- cycle 2 skipped.
```

**No rewrite is offered on this path, not even as an option.** There is no
`Needs you` list, no nitpick, and no alternative version alongside the original.
A user who asked whether a draft was ready and gets back a criticism and a
replacement reads the original as having fallen short, whatever the covering
sentence says -- so the clean answer has to look clean. Offering a second version
"in case you prefer it" is the padded report wearing a hedge.

This is the one case the loop exists to handle well: a draft that really is fine
and should go out now.

## When dispatch is unavailable

**This path is weaker than a dispatched run, and it is the only path on
claude.ai**, where nothing dispatches. It was run against the `preflight`
fixtures on 19 August 2026 and found the planted content gaps and the
unresolvable recipient conflict, so it is no longer untested -- but what it
cannot produce is isolation, and no amount of testing changes that.

Run the reviewers in this context, sequentially, one brief at a time, and
report it in the mandatory `Reviewed:` line of Step 10. That line, not a
notice raised here, is what tells the user which run they got.

**No dispatch means no model tiers either.** Every reviewer reads in this
context on whatever the session is set to, so the busy reader is no longer
weaker than the rest and the risk reader is no longer stronger. Nothing extra
is said about it -- the `Reviewed:` line already reports that the run went this
way, and the tiers are part of what that line is admitting was not available.

The weakness is structural rather than incidental. A sequential reviewer has
already read the ones before it and will defer to them, which is exactly the
isolation that dispatching buys. Hold each brief separately and do not let a
later reviewer soften an earlier one's finding -- but do not claim the isolation
survived, because it did not.

## Failure cases

| Situation | What to do |
|---|---|
| No draft and no description given | Ask for one. Do not guess what the user wants to raise. |
| A description with no draft | Cycle 0 only. Report the verdict and hand off to `compose`. Never draft one here. |
| The input is a revision of a draft this skill already reported on in this conversation | Collect the user's directions given since that report, state them settled in one line, and never re-raise them. Raise only what is new. |
| Subagent dispatch unavailable | Run the reviewers in sequence and say so in the mandatory `Reviewed:` line. Cycle 2 re-reads, it never **confirms**. No model tier applies. |
| The dispatch available takes no model | Dispatch anyway, on the session model, and say nothing. The tier is a preference, not a dependency. |
| A finding arrives with no anchor | Discard it. An unanchored finding is noise. |
| A finding states its cost only as a possibility | Discard it. "Someone could misread this" with nothing behind it has not cleared the second bar, and a nitpick in the report is the padding it was discarded to prevent. |
| A wording `Fix` introduces a fact not in the draft | Reclassify as content. Never apply it, and never write the fact in. |
| A `Fix` only deletes or rearranges words already in the draft | Wording fix. Apply it. Do not ask the user whether the deleted phrase was accurate. |
| A cycle-2 reviewer calls a finding resolved but Step 7 made no edit for it | The finding stands, as a restate. Cycle 2 closes only what the rewrite changed. |
| Every reviewer returns nothing, or nothing they returned survived the bars | Verdict, the original draft unchanged, evidence lines. No rewrite, and none offered as an alternative. |
| The `personas` pointer does not resolve | Silent. Archetypes only. |
| Step 9 routed someone and `remember-persona` offered the entry rather than writing it | Report it as the `Not learned:` line and finish. Never wait for the answer, and never write the entry from here. |
| `daikenja.yaml` absent | Not fatal. Continue on the defaults; "already answered" falls back to whatever thread was pasted. |
| `daikenja.yaml` malformed | **Stop.** Name the first line that does not parse, per `config-resolution.md`. |
| No ledger at the resolved path | Not fatal. Report "already answered" as not checked and continue. |
| More addressees than persona slots | Direct beats cc'd. Name who was dropped. |
| Goal cannot be determined from the input | Ask the one question in Step 2. Do not guess. |
| The user asks for the message to be sent | Decline. This skill has no send action. |

## What this skill does not do

- It does not send, post or schedule anything.
- It does not draft a message from nothing. A description with no draft gets a
  verdict and a handoff to `/daikenja:compose`.
- It does not write `personas.md`. It routes through
  `/daikenja:remember-persona`, which owns every content write to that file.
- It does not write the ledger. It reads one for check 6 and nothing more.
- It does not invent a reviewer. The roster in `docs/reviewer-personas.md` is
  fixed and changes only by pull request.
- It does not run more than two cycles.
- It does not let cycle 2 close a finding the rewrite never touched.
- It does not let anyone change which model a reviewer runs on. The tiers live
  in `docs/reviewer-personas.md` and change only by pull request, like the
  roster itself. `CLAUDE_CODE_SUBAGENT_MODEL` still overrides them, because
  that is Claude Code's own precedence and not something this skill controls.
