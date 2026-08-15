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

**One rabbit hole at a time.** Finish or safely stabilise the current task
first, then capture the tangent. The issue is how the rest gets remembered.

**An issue's output usually belongs in the issue, not the repo.** Findings,
option comparisons and recommendations the maintainer has not accepted yet go in
a comment. Only a durable fact about how the plugin works earns a repo change,
edited into the document that already owns it. This repo documents what Daikenja
**is**, never what was proposed.

## Body format

Every issue carries these three sections, in this order.

**1. Context.** What was observed, when, and the evidence: file paths with line
numbers, command output, dates. Write it so it still makes sense months later to
someone who was not in the session.

**2. Options.** The candidate approaches with a recommendation, not just a
problem statement. Say which one you would pick and why, and name any option you
rejected and what rules it out.

**3. AI prompt.** A self-contained blockquote that a fresh session can act on
cold. Name the paths, the goal, the binding constraints, what NOT to touch, and
how to verify. This is the deliverable: it is what turns the issue back into
work.

Cross-reference related issues by number so a chain of follow-ups stays linked.

## Labels

Apply the existing repo labels that fit. Check with `gh label list` first and do
not invent new ones. At the time of writing the repo carries only the GitHub
defaults, so `documentation`, `enhancement` and `bug` cover most cases.

## Board status

**Leave the issue's board Status at its default.** Maintainers handle board
placement, priority and sizing. Only a dedicated workflow tool or an explicit
request from the maintainer may move an issue's Status.

## Dates

Use absolute dates in issue bodies, never relative ones. Write "15 Aug 2026",
not "last Tuesday". This matches the rule Daikenja applies to its own generated
output, and it is the only form that survives being read months later from
another time zone.

## Worked example

Issue #2 ("Remove the non-overridable em dash / en dash ban from the default
voice") follows this format end to end. Read it before writing your first one.
