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

## Labels

Apply the existing repo labels that fit. Check with `gh label list` first and do
not invent new ones. At the time of writing the repo carries only the GitHub
defaults, so `documentation`, `enhancement` and `bug` cover most cases.

## Board fields

**Leave the issue's board Status at its default.** Only a dedicated workflow
tool, or an explicit request from the maintainer, may move an issue's Status.

The remaining board fields (priority, size, effort) are set by whoever files
with board access, under the maintainer's own filing contract. That contract is
deliberately not reproduced here, because it covers repos beyond this one.

**If you are filing without board access, file the issue and stop there.** A
body that stands on its own is the deliverable; the board fields are not your
problem.

## Dates

Use absolute dates in issue bodies, never relative ones. Write "15 Aug 2026",
not "last Tuesday". This matches the rule Daikenja applies to its own generated
output, and it is the only form that survives being read months later from
another time zone.

## Worked example

Issue #2 ("Remove the non-overridable em dash / en dash ban from the default
voice") follows this format end to end. Read it before writing your first one.
