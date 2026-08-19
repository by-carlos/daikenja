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
by the replace-and-verify sequence in `docs/config-contract.md` -- download,
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

**Running the reviewers without subagents is not supported.** When dispatch is
unavailable `preflight` falls back to reading each brief in sequence in its own
context, so the skill degrades instead of failing. That path has never been run
against the fixtures, and it cannot preserve the isolation that makes a second
opinion worth having -- a sequential reviewer has read the ones before it and
defers to them. It says so when it happens. Treat what it returns as weaker
than a dispatched run.

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
