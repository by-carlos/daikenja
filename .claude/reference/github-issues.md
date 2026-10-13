# Filing issues on this repo

Read this before opening a GitHub issue on `by-carlos/daikenja`. The one-line
trigger lives in the repo `CLAUDE.md`; the detail is here so it costs nothing
until you actually need it.

Everything about *how* to file -- the floor test, when to file versus just
fix it, the body format, provenance, labels, and board fields -- lives in the
`plan-staged-rollout:create-issue` skill and the maintainer's GitHub ticket
template it resolves. Invoke it to file; never write an issue body by hand or
post one with `gh issue create`. Starting work on an already-filed issue is
`plan-staged-rollout:work-issue`. This page covers only what is genuinely
specific to this repo.

## This repo is public

**An issue body is published the moment it is filed**, and stays indexed even
if it is edited or deleted afterwards. Editing removes it from the rendered
page, not from the record. Treat every filing as one-way.

**Scrub before filing.** No hostnames, LAN IPs or subnets, container or VM
names, personal filesystem paths, email addresses, tokens, or raw log and
console pastes. Redact to generic placeholders -- `<host>`, `10.x.x.x`,
`/path/to/repo` -- and keep the reproduction abstract enough to stand on its
own. Name the repo (`by-carlos/daikenja`), never the checkout directory it
happens to sit in on one machine.

Two things are deliberately *not* covered by this rule, because they are part
of what Daikenja documents rather than facts about anyone's machine: the
plugin's own config paths (`~/.claude/daikenja/…`, a project's `.daikenja/`),
and the invented projects and people in `tests/fixtures/`.

**Show the rendered body and get an explicit OK before filing -- every time.**
This gate is not waived by a general "capture these" from the maintainer, and
not by the filing being obviously routine. Public is a one-way door.

The same rules apply to pull request bodies, review comments and issue
comments.

## The ticket template is the authority on body shape

There is one GitHub issue format, the maintainer's ticket template, and it
applies here as everywhere. `.github/ISSUE_TEMPLATE/follow-up.yml` is only the
web form for people filing in the browser; its field labels mirror the
template's sections so both routes produce the same issue. When the two drift
apart, change the form to match the template, never the other way round.

## Dates

Use absolute dates in issue bodies, never relative ones. Write "15 Aug 2026",
not "last Tuesday". This matches the rule Daikenja applies to its own
generated output, and it is the only form that survives being read months
later from another time zone.
