# Preflight reference

Depends-on (reverse index -- hand-maintained, checked against SKILL.md
headings by tests/check-invariants.py):
- § Re-running on the same draft -- preflight "Step 1: take the input as given"
- § Conflicts -- preflight "Step 6: adjudicate -- the safety hinge"
- § Step 9: learned personas -- preflight "Step 9: learned personas"
- § Reporting a re-run -- preflight "Step 10: report"
- § When dispatch is unavailable -- preflight "When dispatch is unavailable"
- § Failure cases -- preflight "Failure cases"
- § What this skill does not do -- preflight "What this skill does not do"

The `preflight` sections a run reaches only on some branches. Every rule here
is `preflight`'s own and binding on it exactly as if it sat in `SKILL.md`;
nothing else reads this file.

**This is not a contract two skills agree on**, which is what the rest of
`docs/` holds. It is one skill's instructions, kept here rather than inline so
a run that never reaches a branch never pays to read it. `SKILL.md` names the
section to read at the point each branch opens, and a run that opens none of
them reads none of this file.

## Re-running on the same draft

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

## Conflicts

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

## Reporting a re-run

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

## When dispatch is unavailable

**This path is weaker than a dispatched run**, for whatever reason subagent
dispatch did not run. It was run against the `preflight` fixtures on
19 August 2026 and found the planted content gaps and the unresolvable
recipient conflict, so it is no longer untested -- but what it cannot produce
is isolation, and no amount of testing changes that.

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
| Check 4 fails because the message carries several asks at once | Split or label them directly in Step 7, like any other wording fix. Report it in `Applied:`, never in `Needs you`. |
| Check 4 fails because there is no specific ask at all | Content gap. The sender has to say what they want; nothing in the draft supplies it. |
| Check 6 finds a pre-existing answer | Report it topic-first with its ID in `Already answered:`, and ask only whether to defer. Never add it to `Needs you`, and never count it toward the verdict's fact count. |
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
