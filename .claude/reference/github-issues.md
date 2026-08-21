# Filing issues on this repo

Read this before opening a GitHub issue on `by-carlos/daikenja`. The one-line
trigger lives in the repo `CLAUDE.md`; the detail is here so it costs nothing
until you actually need it.

## When to file

**Suggest before you file.** When investigation turns up adjacent work, name it
in one line and offer to open an issue. File it once the maintainer agrees, or
when they have said up front to capture findings. Do not silently expand the
scope of the task you were given, and do not file issues for trivia you would
just fix in the current change.

**Floor test -- describing it must cost less than doing it.** This file, a
four-section body, a provenance line and a board decision is the right price for
work worth remembering. It is the wrong price for three one-line doc edits. So
before filing, ask whether the follow-up is **mechanical**: no design call to
make, the exact edits already located, Size XS. If it is, the offer to the
maintainer is **"want me to just fix this?"** -- a short branch off `main` and
one PR -- not an issue. This extends the trivia rule above to trivia noticed
*outside* the current change, which otherwise has no path but the full ceremony.
File instead only when the maintainer declines the fix, or when the item needs a
decision, a discussion, or a session that is not this one.

"Fix it now" is not free either: it costs a branch, a commit, a PR and a merge
gate. That is cheaper than an issue for a handful of mechanical edits and more
expensive for anything else. When it is genuinely close, say so in one line and
let the maintainer pick.

**One rabbit hole at a time.** Finish or safely stabilise the current task
first, then capture the tangent. The issue is how the rest gets remembered.

**An issue's output usually belongs in the issue, not the repo.** Findings,
option comparisons and recommendations the maintainer has not accepted yet go in
a comment. Only a durable fact about how the plugin works earns a repo change,
edited into the document that already owns it. This repo documents what Daikenja
**is**, never what was proposed.

## This repo is public

**An issue body is published the moment it is filed**, and stays indexed even if
it is edited or deleted afterwards. Editing removes it from the rendered page,
not from the record. Treat every filing as one-way.

**Scrub before filing.** No hostnames, LAN IPs or subnets, container or VM
names, personal filesystem paths, email addresses, tokens, or raw log and
console pastes. Redact to generic placeholders -- `<host>`, `10.x.x.x`,
`/path/to/repo` -- and keep the reproduction abstract enough to stand on its
own. Name the repo (`by-carlos/daikenja`), never the checkout directory it
happens to sit in on one machine.

Two things are deliberately *not* covered by this rule, because they are part of
what Daikenja documents rather than facts about anyone's machine: the plugin's
own config paths (`~/.claude/daikenja/…`, a project's `.daikenja/`), and the
invented projects and people in `tests/fixtures/`.

**Show the rendered body and get an explicit OK before filing -- every time.**
This gate is not waived by a general "capture these" from the maintainer, and
not by the filing being obviously routine. Public is a one-way door.

The same rules apply to pull request bodies, review comments and issue comments.

## Body format

**The issue form is the source of truth, not this section.**
`.github/ISSUE_TEMPLATE/follow-up.yml` defines the sections and the constraint
on each one. Read it before filing and fill every field it names, whether you
are filing through the web form or building a body for `gh issue create`. The
summary below is orientation only; where the two disagree, the form wins.

Four sections, in this order.

**1. In plain terms.** What is wrong or wanted, who it affects, and what happens
today, in three to five sentences. **No file paths, line numbers, function or
skill names, or issue numbers** -- those belong in Context. The ban is what
makes the section work: with the identifiers gone, the only thing left to write
is behaviour and consequence, which is what a reader needs months later. If it
reads like a shorter Context, it has failed.

**2. Context.** What was observed, when, and the evidence: file paths with line
numbers, command output, dates. Write it so it still makes sense months later to
someone who was not in the session.

**3. Options.** The candidate approaches with a recommendation, not just a
problem statement. Say which one you would pick and why, and name any option you
rejected and what rules it out.

**4. AI prompt.** A self-contained blockquote that a fresh session can act on
cold. Name the paths, the goal, the binding constraints, what NOT to touch, and
how to verify. This is the deliverable: it is what turns the issue back into
work.

**`gh issue create` does not apply the form.** GitHub enforces templates only in
the web UI, so `--body` and `--body-file` bypass it silently. An agent filing
from the CLI has to reproduce the sections by hand, as `### <label>` headings
matching the form's labels, so that CLI-filed and web-filed issues read the
same.

Cross-reference related issues by number so a chain of follow-ups stays linked.

## Provenance — say where the issue came from

Months later the hard question is rarely *what* the issue says. It is *why this
was filed at all*. Answer it in the issue itself, as the last line of **Context**:

```
_Surfaced while working on by-carlos/daikenja#<N> — <who or what was working>, <DD Mon YYYY>._
```

An AI agent puts its own session identifier in that middle slot, so the work can
be traced back to the conversation that produced it. Claude Code sessions have
one in `$CLAUDE_CODE_SESSION_ID`. A human contributor writes what they were doing
instead. Either way the date is absolute (see Dates below).

When nothing was in play, name the activity rather than an issue:
`_Surfaced during <short phrase> — <who>, <date>._`

**That `#<N>` mention is the relationship.** GitHub posts a cross-reference onto
the origin issue's timeline, so it reads "…mentioned this issue" and links back
without anyone editing it. GitHub has no generic "relates to" link — this is it.
A label is not a substitute, because a label carries no target.

## Relationships — which link to use, and when

GitHub has exactly three typed issue relationships that matter here. Reach for
the weakest one that is literally true.

| Situation | What to set |
|---|---|
| Noticed while doing something else — the common case | **Nothing.** The provenance line's mention is the link. |
| This genuinely cannot start until another issue lands | `gh issue create --blocked-by <n>` (or `--blocking <n>`) |
| One job that clearly wants splitting | A parent with sub-issues — **propose it first**, see below |

**Never nest a spin-off as a sub-issue** of whatever surfaced it. It hides the
work inside a parent nobody reopens and leaves that parent looking unfinished
forever.

**Do propose a split** when a single issue genuinely wants one — the parts need
different levels of effort, or it is too big to land as one reviewable change.
Name the proposed pieces in one line each and create the parent only once the
maintainer agrees.

**`--blocked-by` means blocked, not preferred.** If two issues are merely nicer
in a given order, say so in a sentence and set no dependency: a fake blocker
stalls a queue and misrepresents the work.

**Filing more than one issue at a time obliges you to say which comes first.**
End the batch with a plain "Start with #N." — one issue, no hedging.

## Labels

Apply the existing repo labels that fit. Check with `gh label list` first and do
not invent new ones. At the time of writing the repo carries only the GitHub
defaults, so `documentation`, `enhancement` and `bug` cover most cases.

## Board fields

**Leave the issue's board Status at its default.** Only a dedicated workflow
tool, or an explicit request from the maintainer, may move an issue's Status.

Issues from this repo go to the **"Claude Plugins"** project (project 3), a
board shared with `by-carlos/claude-plugins` and `by-carlos/plan-staged-rollout`.
Filter by the Repository field before reading anything off it as a view of this
repo.

The remaining board fields (priority, size, effort) are set by whoever files
with board access, under the maintainer's own filing contract. That contract is
deliberately not reproduced here, because it covers repos beyond this one.

**If you are filing without board access, file the issue and stop there.** A
body that stands on its own is the deliverable; the board fields are not your
problem.

## Starting work on an issue

Provenance runs both ways. Filing records where an issue came from; **picking one
up records who is acting on it.** Before the first commit, post one comment:

```
🤖 Claude Code session `<session-id>` picking this up — <one line on the approach>. Branch: `<branch>`.
```

A human contributor says the same thing without the session identifier. Either
way it is one comment, posted when work actually begins — not on reading,
triaging, or answering a question about the issue. Say what you intend to do; a
bare "picking this up" is noise, while the approach line is what makes sense
beside the diff months later.

**No closing comment.** The pull request that closes the issue already carries
the outcome. Comment a second time only if you *abandon* the issue without a PR,
saying so and why, so the next person does not re-derive it.

Keep the robot marker if you are an agent. Commands run with the maintainer's own
credentials, so the comment appears under a human account — the marker is the
only thing distinguishing agent-written comments from theirs.

## Dates

Use absolute dates in issue bodies, never relative ones. Write "15 Aug 2026",
not "last Tuesday". This matches the rule Daikenja applies to its own generated
output, and it is the only form that survives being read months later from
another time zone.

## Worked example

Issue #2 ("Remove the non-overridable em dash / en dash ban from the default
voice") follows this format end to end. Read it before writing your first one.
