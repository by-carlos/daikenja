# Fixture: owner handles nobody has checked

Synthetic. Invented people, `example.com` links only. Nothing here comes from
real work content, and no path below exists on any machine.

Exercises `project-log` § Say when a handle is new against
[`sample-ledger.md`](sample-ledger.md), the beacon project. Eight walks: a
handle the ledger already knows, a handle only `personas.md` knows, a handle
neither knows, two spellings of one person, `@unassigned`, and the three
configuration states -- no personas file, a broken `drive:` pointer, and a
dictated write.

The walks are run by hand; this repo has no test runner. Each states the user's
message and what the run must and must not do.

---

## The personas file these walks assume

Whatever `profile.personas` resolves to. Walks 1-5 and 8 assume this content;
walks 6 and 7 replace it. It deliberately does **not** cover everyone in the
beacon ledger -- it is the user's own prose, not a roster, and a person missing
from it is the normal case.

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

Expected: neither place has `@gobta`. One notice, in the proposal, and the write
proceeds on approval exactly as it would have without the check:

~~~
New owner handles:
- @gobta -- not in this ledger and not in personas.md.
~~~

Offering `/daikenja:remember-persona` alongside it is fine. Running it is not.

Must not happen: blocking the write, asking who `@gobta` is as a question the
run waits on, rewriting the handle, or writing anything at all to
`personas.md`.

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

The write proceeds on approval.

Must not happen: a stop, a scaffold of `personas.md` from `project-log`, or a
silent notice that does not say the comparison was narrower.

## Walk 7: a `drive:` pointer that does not resolve

Same message as Walk 3, with `profile.personas: drive:personas.md` and the
connector absent from the session.

Expected: **stop, before anything is written.** A `drive:` pointer means the
user asked for that behavior and the request failed, which
`docs/config-resolution.md` § Failure behavior separates from a key nobody set.
Name the file and the reason, show the proposal so the entries are not lost,
and say plainly that nothing was written.

Must not happen: falling back to the local default path, treating it as an
unconfigured key, or writing the entry and reporting the failure afterwards.

Note what makes this reachable at all: Walk 1's message with the same broken
pointer writes normally, because the handle never leaves the ledger check. The
stop bites only on a run that both has an unfamiliar handle and cannot read the
file that would settle it.

## Walk 8: a dictated write carrying a new handle

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

## What must not happen in any walk

- **A handle is never rewritten.** Not to match a near miss, not to lowercase
  it, not to expand it.
- **`personas.md` is never written by `project-log`.** Not created, not
  appended to, not corrected. `remember-persona` owns every content write to it.
- **Nothing is ever rejected.** There is no list of legal owners. The check
  reports and the ledger stays free text.
- **`@unassigned` is never reported.**
- **The check never adds a question the run waits on.** The proposal's
  "Questions before I write" block is for things that genuinely block a write;
  an unfamiliar handle is not one.
