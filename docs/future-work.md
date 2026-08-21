# Known limitations

What Daikenja does not do, and where the edge of a shipped feature sits. These
are facts about current behaviour, not a roadmap -- nothing here is promised,
scheduled, or in progress. A limitation leaves this file only when the
behaviour actually changes.

## On claude.ai

The writing skills -- `compose`, `doc-review`, `preflight`, `self-review` and
`thread` -- are uploaded there as five separate zips built by
`scripts/build-claude-ai-skills.py`. Everything below was measured on
19 August 2026 across six runs against the `preflight` fixtures.

**Nothing dispatches.** claude.ai has no subagents, so `preflight`'s reviewers
all run in one context and each has read the ones before it. That path finds
planted content gaps and the unresolvable recipient conflict, and it invents no
facts, but it cannot produce the isolation that makes a second opinion worth
having. Every report says which way it ran in its `Reviewed:` line, and cycle 2
re-reads rather than confirming.

**A skill is not reliably picked up from the description alone.** A long pasted
draft opening with "Poke holes in this before I send" was answered without the
skill loading at all. Naming it -- "use the preflight skill on this" -- loaded
it every time. This is about how the request is phrased, not about which skill.

**There is no ledger, so `preflight`'s sixth check never passes.** It reports
"already answered" as not checked rather than as a pass, which is the same
honest gap it reports in Claude Code when no ledger is configured.

**Neither setup skill is shipped there.** Creating `~/.claude/daikenja/` is
`setup-user`'s whole job, and the folder and the files inside it are made in
Claude Code. A claude.ai session that finds no `daikenja` folder in Drive cannot
create one. `setup-project` is absent for both reasons at once: it writes that
same config, and its seeding step reads a project working tree that a browser
session does not have.

**`remember-persona` writes to Drive, and only to Drive.** It appends the entry
by the replace-and-verify sequence in `docs/config-drive.md` -- download,
splice, create the replacement in the same folder, read it back, then trash the
old copy. Verified on 19 August 2026: the template was preserved byte for byte,
the entry landed below it with its recorded date, and one file was left in the
folder. The local path is not a fallback on this surface. The filesystem a skill
can reach there is a sandbox that is discarded with the session, so writing an
entry to it would report a success and lose the prose; when Drive cannot be
reached the skill prints the entry for the user to paste instead.

**Each connector call is approved separately.** That write asked four times --
download, create, download again, trash -- and a denial partway through leaves
the sequence unfinished. "Always allow" turns it into one approval for the
session. This is claude.ai's connector prompt, not something Daikenja controls.

**Skills do not sync between surfaces.** An upload to claude.ai is per user and
per skill, is not shared across an organization, and does not reach Claude Code
or the API. A change to a skill here means re-uploading the zip by hand. This
is Anthropic's design, not something Daikenja can package around.

**Code execution must be enabled** on the account, on a Pro, Max, Team or
Enterprise plan. Without it a custom skill does not load at all.

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
against the fixtures on claude.ai on 19 August 2026 -- the only surface where
this path runs at all -- it found the planted content gaps and the
unresolvable recipient conflict. That result does not lift the limitation: a
sequential reviewer has read the ones before it and defers to them, so the
isolation that makes a second opinion worth having is gone regardless of what
the path scores on a fixture. It says so when it happens. Treat what it
returns as weaker than a dispatched run.

**A reviewer's model tier cannot be changed.** Each archetype is dispatched on
the tier written against it in [`reviewer-personas.md`](reviewer-personas.md) --
`haiku` for the two that simulate a degraded reader, `sonnet` for the three with
one preoccupation, `opus` for the four that simulate a sharper-than-normal one.
That table is fixed and changes only by pull request, the same as the roster.
A `personas.md` entry sets no tier, and a named addressee inherits the tier of
the archetype it embodies. Setting `CLAUDE_CODE_SUBAGENT_MODEL` pins every
reviewer to one model and overrides all of it, which is Claude Code's own
precedence rather than something Daikenja offers.

**The tiers only exist where subagents do.** Where nothing dispatches --
claude.ai -- every reviewer reads in `preflight`'s own context on the session's
model, so the busy reader is no longer weaker than the rest and the risk reader
is no longer stronger. The `Reviewed:` line reports that the run went that way.

**The two always-on checks read with full context.** The AI-tell check and the
non-native English check run in `preflight`'s own context, which has already
read the draft, the thread and the conversation around it. They know what the
message means, which makes them weak judges of whether the words alone carry
it. Only the dispatched reviewers read cold.
