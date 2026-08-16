# Known limitations

What Daikenja does not do, and where the edge of a shipped feature sits. These
are facts about current behaviour, not a roadmap -- nothing here is promised,
scheduled, or in progress. A limitation leaves this file only when the
behaviour actually changes.

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

**Every reviewer runs on the session's model.** A skill cannot declare a model,
so the personas `preflight` dispatches all inherit whatever the session is set
to. There is no way to run a persona that simulates a fast, careless reader on a
cheaper model than one that simulates a forensic one. `preflight` notices when
it is not on Opus and says so in one line, which is the whole of the mitigation.

**The two always-on checks read with full context.** The AI-tell check and the
non-native English check run in `preflight`'s own context, which has already
read the draft, the thread and the conversation around it. They know what the
message means, which makes them weak judges of whether the words alone carry
it. Only the dispatched reviewers read cold.
