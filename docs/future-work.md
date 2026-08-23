# Known limitations

What Daikenja does not do, and where the edge of a shipped feature sits. These
are facts about current behaviour, not a roadmap -- nothing here is promised,
scheduled, or in progress. A limitation leaves this file only when the
behaviour actually changes.

## On claude.ai

claude.ai, the desktop-app Chat surface, and Cowork are not supported surfaces.
Daikenja is a Claude Code plugin, and nothing here is built or tested to run
anywhere else.

## Projects

**A project with no directory needs an absolute `ledger:`, and nothing enforces
that it has one.** `paths: []` makes a project addressable by name from
anywhere, which is what a programme spanning a wiki, a tracker and a chat space
needs; an absolute `ledger:` is what gives its record a location once there is
no root to be relative to. The two keys are independent, so a pathless entry
written without one resolves as a project and then fails at the ledger. Every
skill reports which of the two is missing rather than guessing a location, and
`setup-project` offers the key when it registers such a project -- but a
hand-edited file can still hold the half-configured shape.

**A project has exactly one ledger, in its first path** unless `ledger:` says
otherwise. For a project spanning three repositories that means the decisions
of all three live in the first one by default, and the other two carry
nothing. Reordering `paths` afterwards repoints the
ledger at a different file, which is why `setup-project` appends and never
reorders. There is no way to split one project's ledger across its
directories, and no way to merge two ledgers into one project.

**`project-list` does not search your disk.** Its scan for unregistered ledgers
covers the current directory tree three levels deep, plus the same depth under
the current VCS root. A ledger written somewhere else entirely is not found,
and the report says where it looked so the absence can be read correctly.

## The ledger

**Relationships are a documented convention, not a parsed form.** `Blocked by
<id>.` and `Contradicts <id>.` are literal sentences at the front of a body,
per [`ledger-format.md`](ledger-format.md) § Body markers -- ordinary text to
the grammar, which is what makes them free to add and free to change. A skill
finds them by looking; nothing validates them at write time beyond the checks
`project-log` runs, and a marker a human types by hand with the wrong shape is
simply body text nobody reads as a relationship. Tightening them into a parsed
form is deliberately left until real use shows which relationships recur.

**Those two are the only relationships.** "Evidence for", "depends on",
"reopens" and anything else are prose in the body, exactly as all of them were
before. The pair shipped is the pair that came out of real use; a third is a
change to the contract, not a convention a user can add locally and have skills
understand.

**A relationship is recorded in one direction and never walked further than one
hop.** The entry it names carries nothing, so a reader finds the other end by
scanning the file rather than by reading the line -- which is why every skill
that reports one scans both sections. Nothing walks a chain of blockers to its
root, and nothing detects a cycle: `O-005` blocked by `O-006` blocked by
`O-005` is reported as two ordinary blocks. Supersession is still the only
relationship walked to an end, because it is the only one that has one.

**Nothing retires a marker when what it names is settled.** Resolving an entry
does not strip the `Blocked by` markers pointing at it, and a reader takes the
block as lifted from the resolved entry's own checkbox -- `project-gaps` says so
on the line. Removing the marker is an edit somebody has to ask for. The
alternative would be a write touching entries the user never named.

**`Imposed.` records that a decision came from outside, not a structured
source.** Who imposed it is prose after the marker, so nothing can filter or
group by imposing body, and there is no way to record a decision that was
partly ours. The marker's absence means "decided here", which is an assumption
about every entry written before the marker existed -- true in practice, and
not something the file can distinguish from "nobody said".

**`project-gaps` still reads only Open items.** An unowned imposed decision is
not reported, on the grounds that `<owner>` on a decision is attribution rather
than accountability. The work an imposed decision creates on this side is an
Open item, and that is what the audit sees -- but only once somebody raises it.
`project-log` offers; nothing enforces.

**The ledger tracks ownership and staleness, not severity.** `project-gaps`
filters on exactly those two conditions -- `<owner>` is `@unassigned`, or the
entry is older than `stale_after_days` -- and nothing in the entry grammar
records how much an item matters. An item that blocks all work but was raised
yesterday and has an owner is invisible to the audit; a cosmetic item three
weeks old is reported identically. The audit is therefore a neglect report, not
a priority report, and reading it as the second thing produces a wrong picture
of what is urgent. A user who needs to track severity or consequence keeps that
outside the ledger, in whatever document already serves that purpose for them
-- Daikenja does not provide one.

## Reviewer personas

**Group-level personas are not supported.** `personas.md` is read as individual
entries, matched against the people a draft addresses. "Everyone in platform is
deeply technical and hates hedging" has nowhere to live -- it has to be written
once per person, or said inline each time.

**User-defined archetypes are not supported.** The roster in
[`reviewer-personas.md`](reviewer-personas.md) is fixed. A `personas.md` entry
layers on top of an archetype for one person and never changes what that
archetype does for anyone else, and there is no way to add a tenth reading
behaviour. Changing the roster is a pull request to that file.

**Personas are learned only from what the user states.**
`/daikenja:remember-persona` records a description the user gives it. It never
builds a picture of someone by reading past messages, threads or transcripts,
so there is no onboarding step that populates `personas.md` from a mailbox or a
Slack history. This one is deliberate rather than merely absent -- inferring
traits from someone's messages produces a character study nobody consented to,
and the no-invention rule the rest of the plugin follows would have to be
suspended to do it.

## The review loop

**`preflight` runs at most two cycles.** After the first rewrite what remains is
almost always content, which no further cycle can fix. A draft with deep
problems gets two passes and a list of questions, not convergence.

**Running the reviewers without subagents cannot preserve isolation.** When
dispatch is unavailable `preflight` falls back to reading each brief in
sequence in its own context, so the skill degrades instead of failing. Run
against the fixtures on 19 August 2026, this path found the planted content
gaps and the unresolvable recipient conflict. That result does not lift the
limitation: a sequential reviewer has read the ones before it and defers to
them, so the isolation that makes a second opinion worth having is gone
regardless of what the path scores on a fixture. It says so when it happens.
Treat what it returns as weaker than a dispatched run.

**A reviewer's model tier cannot be changed.** Each archetype is dispatched on
the tier written against it in [`reviewer-personas.md`](reviewer-personas.md) --
`haiku` for the two that simulate a degraded reader, `sonnet` for the three with
one preoccupation, `opus` for the four that simulate a sharper-than-normal one.
That table is fixed and changes only by pull request, the same as the roster.
A `personas.md` entry sets no tier, and a named addressee inherits the tier of
the archetype it embodies. Setting `CLAUDE_CODE_SUBAGENT_MODEL` pins every
reviewer to one model and overrides all of it, which is Claude Code's own
precedence rather than something Daikenja offers.

**The tiers only exist where subagents do.** Where nothing dispatches, every
reviewer reads in `preflight`'s own context on the session's model, so the busy
reader is no longer weaker than the rest and the risk reader is no longer
stronger. The `Reviewed:` line reports that the run went that way.

**The two always-on checks read with full context.** The AI-tell check and the
non-native English check run in `preflight`'s own context, which has already
read the draft, the thread and the conversation around it. They know what the
message means, which makes them weak judges of whether the words alone carry
it. Only the dispatched reviewers read cold.

## Running a skill in its own subagent

**Only `project-summary` runs forked.** It carries `context: fork` and
`background: false`, so its contract reads and its whole pass over the ledger
stay out of the calling conversation and only the finished overview comes back.
Nothing else does, and two skills were evaluated and deliberately left inline.

**`preflight` cannot fork, because a fork has no conversation.** Claude Code's
own documentation is explicit that a forked skill has no access to the calling
conversation's history, and three parts of this skill are defined over it:
Step 1's re-run rule, which fires on a draft this skill already reported on in
this conversation and works by collecting the directions the user has given
since; Step 9, which routes a person the user described inline; and Steps 1 and
2, which stop and ask the user a question mid-run. Forked, the first two become
dead text and the third cannot happen at all.

**`project-log` cannot usefully fork either, including by halves.** Forking the
classify-and-propose half and keeping the approval loop inline is the obvious
boundary and it does not pay: Step 7's insert rule and body-marker order and
Step 8's Changelog verbs all live in [`ledger-format.md`](ledger-format.md),
much the largest contract this skill reads, and they all execute in the parent
after the user approves -- so the parent reads that file whatever the boundary
is. Two mid-run questions also sit inside the proposed fork: Step 1's "nothing
was given, ask what to log", and Step 3's confirmation before scaffolding a
ledger, which is a separate approval from Step 5's.

**What would change this.** A forked context that carried the calling
conversation would answer all three of `preflight`'s objections at once, and a
way for a forked skill to put a question to the user and resume would answer
two of `project-log`'s. Neither exists. Until one does, the cost these two
skills used to pay per invocation is addressed by keeping only always-read
material in `SKILL.md`, with each skill's branch-only sections in
[`preflight-reference.md`](preflight-reference.md) and
[`project-log-reference.md`](project-log-reference.md).
