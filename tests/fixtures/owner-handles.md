# Fixture: owner handles nobody has checked

Synthetic. Invented people, `example.com` links only. Nothing here comes from
real work content, and no path below exists on any machine.

Exercises the two halves of handle drift, against
[`sample-ledger.md`](sample-ledger.md), the beacon project.

Walks 1-8 cover `project-log` § Say when a handle is new: a handle the ledger
already knows, a handle only `personas.md` knows, a handle neither knows, two
spellings of one person, `@unassigned`, and two configuration states -- no
personas file and a broken `drive:` pointer.

Every message in walks 1-8 is a fact the user dictated, so the same-turn path is
the baseline across all eight and none of them waits for approval. Walk 8 is
where that is spelled out: an unfamiliar handle produces a notice, not a
question, so it never demotes a dictated run to propose-then-wait. Walk 7 is the
only stop, and it comes from the config failure rather than from the handle.
Walks 9-11 are not dictated -- they enter `project-log` from another skill,
which per that skill's § The same-turn path for dictated facts never takes this
path at all.

Walks 9-11 cover `meeting-review` § Step 4: attribute, which runs *before* that
check and is what stops most second spellings being minted at all: a speaker the
user has recorded under a handle the transcript label would not have produced, a
speaker recorded nowhere, and a speaker two personas could both be.

The walks are run by hand; this repo has no test runner. Each states the user's
message and what the run must and must not do.

Depends on: project-log "Say when a handle is new", project-log "The same-turn path for dictated facts", meeting-review "Step 4: attribute", config-resolution.md "Resolving `writing_style` and `personas`", config-resolution.md "Failure behavior"

---

## The personas file these walks assume

Whatever `profile.personas` resolves to. Walks 1-5 and 8 assume this content;
walks 6 and 7 replace it; walks 9-11 assume it plus the three extra sections
below. It deliberately does **not** cover everyone in the beacon ledger -- it is
the user's own prose, not a roster, and a person missing from it is the normal
case.

~~~markdown
# Personas

## Diablo

**Known as.** Diablo Ward. `@diablo`, diablo@example.com.

**Who they are.** Runs the platform team. Owns the events table.

**How to write to them.** Short. Lead with the ask.

## Shion

**Known as.** Shion Oni. `@shion`, `@shion.o`, chat ID `U04SHION`.

**Who they are.** Data lead. New to the beacon project.

*Recorded by Daikenja on 2026-08-19 from what you said while drafting. Edit or
delete this freely.*
~~~

The beacon ledger's owners are `@rimuru`, `@diablo`, `@benimaru` and
`@unassigned`. So `@diablo` is in both places, `@shion` is in the personas file
only, `@rimuru` and `@benimaru` are in the ledger only, and neither place has
heard of anybody else.

---

## Walk 1: a handle the ledger already uses

User message:

> Log the decision that Diablo signs off the canary region before it starts.
> Owner @diablo.

Expected: step 1 of the check finds `@diablo` as the owner of `D-003` and
`O-005` already. Known. **No notice, and `personas.md` is never read** -- the
run resolves nothing, downloads nothing, and would behave identically if the
pointer were broken.

Must not happen: a notice, a personas read, or any mention of the handle in the
reply.

## Walk 2: a handle only the personas file knows

User message:

> Add an open item: @shion confirms the events table retention before the
> canary.

Expected: step 1 finds no `@shion` in the beacon ledger, so step 2 resolves
`profile.personas` and finds the `## Shion` section, whose `Known as` names
`@shion`. Known. No notice.

The read happening here and not in Walk 1 is the whole cost model: the file is
touched only when a run carries a handle the ledger cannot account for.

Must not happen: reporting `@shion` as new because this ledger has never used
it. The file is exactly what that case is for.

## Walk 3: a handle neither place knows

User message:

> Add an open item: @gobta writes the canary abort criteria.

Expected: neither place has `@gobta`. The four same-turn conditions all hold and
the notice is a notice, not a question, so it fails none of them. The entry is
written in the same turn and the notice is shown beside the written lines and
the Changelog line, exactly as the run would have gone without the check:

~~~
New owner handles:
- @gobta -- not in this ledger and not in personas.md.
~~~

Offering `/daikenja:remember-persona` alongside it is fine. Running it is not.

Must not happen: blocking the write, holding it for approval, dropping the run
to propose-then-wait because the handle was unfamiliar, asking who `@gobta` is
as a question the run waits on, rewriting the handle, or writing anything at all
to `personas.md`.

## Walk 4: two spellings of one person

User message:

> Log the decision that @benimaru.k owns the data-team sign-off for the row
> counts.

Expected: `@benimaru.k` is in neither place, **and** the ledger already uses
`@benimaru` on `O-001`. The notice names the near miss and asks in a form the
user answers in one word:

~~~
New owner handles:
- @benimaru.k -- not in this ledger and not in personas.md. The ledger already
  uses @benimaru. Same person?
~~~

This is the case the whole check exists for. Both spellings landing silently is
the failure being prevented, and it is invisible once written.

Must not happen: choosing `@benimaru` on the user's behalf, merging the new
entry into `O-001`, or writing both spellings without a word.

## Walk 5: no owner at all

User message:

> Add an open item: somebody needs to confirm the beacon alert thresholds.

Expected: nobody is named, so the owner is `@unassigned` -- and the check does
not run for it. No notice. `@unassigned` is the documented value for no owner,
not a person the run has failed to recognize.

Must not happen: reporting `@unassigned` as an unfamiliar handle, or asking who
should own it. Both are failures the same-turn path already exists to avoid.

## Walk 6: no personas file

Same message as Walk 3, with `profile.personas` unset -- or set to a local path
with no file at it.

Expected: not an error. The check falls back to the ledger alone and says so in
the same line, so the user knows the comparison was the narrower one:

~~~
New owner handles:
- @gobta -- not in this ledger. No personas.md configured, so that is the whole
  comparison.
~~~

The entry is still written in the same turn. An unset key is an absent key, and
an absent key fails no same-turn condition -- the narrower comparison changes
what the notice says, not which path the run takes.

Must not happen: a stop, a drop to propose-then-wait, a scaffold of
`personas.md` from `project-log`, or a silent notice that does not say the
comparison was narrower.

## Walk 7: a `drive:` pointer that does not resolve

Same message as Walk 3, with `profile.personas: drive:personas.md` and the
connector absent from the session.

Expected: **stop, before anything is written.** A `drive:` pointer means the
user asked for that behavior and the request failed, which
`docs/config-resolution.md` § Failure behavior separates from a key nobody set.
Name the file and the reason, show the lines that would have been written so
the entries are not lost, and say plainly that nothing was written.

This is the one thing that does stop a run Walk 3 shows writing in the same
turn. The stop comes from the config failure, not from the handle: a `drive:`
pointer that does not resolve halts the whole run whichever path it was on, so
it is not the same-turn conditions failing.

Must not happen: falling back to the local default path, treating it as an
unconfigured key, or writing the entry and reporting the failure afterwards.

Note what makes this reachable at all: Walk 1's message with the same broken
pointer writes normally, because the handle never leaves the ledger check. The
stop bites only on a run that both has an unfamiliar handle and cannot read the
file that would settle it.

## Walk 8: why the notice does not demote a dictated run

User message:

> Log the decision that @gobta owns the abort criteria for the canary.

Expected: all four same-turn conditions still hold. The notice is a **notice**,
not a question, so condition 3 is not failed and the run does not drop to
propose-then-wait. The entry is written in the same turn, and the notice is
shown next to the written lines and the Changelog line.

The check still runs **before** the write. A handle reported after the write is
a handle already in the file.

Must not happen: converting a dictated write into a proposal because the handle
was unfamiliar, or writing first and checking second.

---

## The extra personas walks 9-11 assume

Appended to the file above. `Souei` is recorded under a handle their speaker
label would not produce, and the two Gabirus are the ambiguity.

~~~markdown
## Souei

**Known as.** Souei Tempest. `@souei.t`, chat ID `U04SOUEI`.

**Who they are.** Runs customer comms for the beacon rollout.

## Gabiru H

**Known as.** Gabiru Hiryu. `@gabiru.h`.

**Who they are.** Storage team.

## Gabiru S

**Known as.** Gabiru Souka. `@gabiru.s`.

**Who they are.** Storage team, joined in July.
~~~

## Walk 9: a speaker recorded under a different handle

A transcript in which the line

> [00:01:20] Souei: I will have the customer comms written by Wednesday.

produces an action item.

Expected: before deriving anything, the speaker label `Souei` matches the
`## Souei` section, whose `Known as` records `@souei.t`. The entry is owned by
**`@souei.t`**, not the `@souei` the label alone would have produced. One line
under `Notes` says the handle came from `personas.md` and is not what the label
would give, so the user can overrule it.

When those entries reach `project-log`, its own check accounts for `@souei.t`
from `personas.md` and reports nothing. That is the whole point of the ordering:
the drift never exists, so there is nothing to warn about.

Must not happen: `@souei` in the entry; resolving silently, with no `Notes`
line; a write to `personas.md`; or treating the recorded handle as an invented
one because the transcript never spelled it.

## Walk 10: a speaker no persona covers

The same transcript, for the line

> [00:04:10] Benimaru: I will take the runbook dates.

Expected: `Benimaru` matches no section heading and no `Known as` identifier.
The label is used, exactly as before this rule existed: **`@benimaru`**. This is
the common case and it is not an error -- `personas.md` is not a roster.

No `Notes` line is owed for it, beyond the existing one-line note at the end of
the report when the transcript names people the config does not cover.
`project-log`'s check then finds `@benimaru` already owns `O-001` in the beacon
ledger and reports nothing.

Must not happen: an error, a stop, a question the run waits on, or a handle
invented for them from anything other than their own label.

## Walk 11: two personas could both be this speaker

The same transcript, for the line

> [00:09:52] Gabiru: I will confirm the storage headroom before the canary.

Expected: `Gabiru` matches no section heading, and matches the first name in
**both** `Gabiru H`'s and `Gabiru S`'s `Known as`. Do not guess. Fall back to
the transcript's own label -- **`@gabiru`** -- and say so in one line under
`Notes`, naming both personas:

~~~
Notes
- Gabiru could be Gabiru Hiryu (@gabiru.h) or Gabiru Souka (@gabiru.s). Used
  the transcript's label, @gabiru. Tell me which and I will fix it.
~~~

`project-log`'s check then reports `@gabiru` as a handle neither the ledger nor
`personas.md` accounts for, naming a near miss. Both mechanisms firing on one
entry is correct, not duplication: the note says the run could not tell, the
check says the handle it settled on is new.

Must not happen: picking either persona; picking the one recorded first, or most
recently; merging the two personas; asking a question the run waits on before
producing the report; or dropping the `Notes` line because the downstream check
will mention the handle anyway.

---

## What must not happen in any walk

- **A handle the user supplied is never rewritten.** Not to match a near miss,
  not to lowercase it, not to expand it. Walk 9 is not an exception: nobody
  supplied a handle there, so `meeting-review` chose which one to mint, and it
  chose the recorded one over a derived one.
- **`personas.md` is never written.** Not by `project-log`, not by
  `meeting-review`. Not created, not appended to, not corrected.
  `remember-persona` owns every content write to it.
- **Nothing is ever rejected.** There is no list of legal owners. The check
  reports and the ledger stays free text.
- **`@unassigned` is never reported.**
- **The check never adds a question the run waits on.** "Same person?" invites
  a correction and does not block anything. The proposal's "Questions before I
  write" block is for what genuinely blocks a write, and an unfamiliar handle is
  never one.
- **The check is not an audit of the file.** A ledger already holding both
  `@benimaru` and `@benimaru.k`, on a run that writes neither, reports nothing.
  Walk 4 catches the second spelling as it arrives, which is the only moment
  this check exists for.
