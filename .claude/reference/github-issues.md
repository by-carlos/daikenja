# Filing issues on this repo

Read this before opening a GitHub issue on `by-carlos/daikenja`. The one-line
trigger lives in the repo `CLAUDE.md`; the detail is here so it costs nothing
until you actually need it.

Everything about *how* to file -- the floor test, when to file versus just
fix it, the four-section body format, provenance, typed relationships,
labels, and board fields -- lives in the shared `carlos:file-issue` skill
(`by-carlos/claude-lab`, `plugins/carlos/skills/file-issue/`). Invoke it to
file. Starting work on an already-filed issue -- the session-announcement
comment, board `Status` moves -- is covered by `carlos:work-issue` (same
plugin). This page covers only what is genuinely specific to this repo.

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

## The issue form is the authority on body shape

`.github/ISSUE_TEMPLATE/follow-up.yml` defines the sections and the
constraint on each one for this repo, and wins wherever it disagrees with the
shared skill's body format. Read it before filing and fill every field it
names, whether you are filing through the web form or building a body by
hand.

**`gh issue create` does not apply the form.** GitHub enforces templates only
in the web UI, so `--body`, `--body-file`, or the shared skill's `ghpost.py`
bypass it silently. Reproduce the form's sections by hand, as `### <label>`
headings matching the form's own labels, so a CLI-filed issue reads the same
as a web-filed one.

## Dates

Use absolute dates in issue bodies, never relative ones. Write "15 Aug 2026",
not "last Tuesday". This matches the rule Daikenja applies to its own
generated output, and it is the only form that survives being read months
later from another time zone.
