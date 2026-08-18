# Security Policy

## Reporting a vulnerability

**Do not open a public issue or pull request for a security problem.** This
repository is public, and an issue body stays indexed even after it is edited or
deleted.

Report privately through GitHub:
[**Report a vulnerability**](https://github.com/by-carlos/daikenja/security/advisories/new).
That opens a draft advisory visible only to you and the maintainer.

If that form is unavailable, contact the maintainer,
[Carlos Eng](https://github.com/by-carlos), through his GitHub profile and ask
for a private channel before sending any detail.

Include what you can: the affected skill or document, the version from
`.claude-plugin/plugin.json`, the steps to reproduce, and what an attacker gains.
Scrub the report the same way an issue would be scrubbed -- placeholders instead
of real hostnames, paths, addresses or credentials.

Expect an acknowledgement within a week. This is a single-maintainer project
worked on in spare time, so a fix may take longer than that; you will be told
where it stands. Please give the maintainer a reasonable window to ship a fix
before disclosing publicly.

## Supported versions

Only the most recent release is supported. Releases are distributed from the
`release` branch, which the marketplace entry in
[`by-carlos/claude-plugins`](https://github.com/by-carlos/claude-plugins) points
at; `main` is the working branch and is not a distribution channel.

## What is in scope

Daikenja is a Claude Code plugin: markdown skills and the documents that
constrain them. There is no server, no service and no code that runs outside
your own Claude Code session. In scope:

- A skill that can be induced to write, send or publish something without the
  approval step its contract requires.
- A skill that reads or exfiltrates data outside the paths its contract names
  (`~/.claude/daikenja/`, the project's `.daikenja/` ledger, and a Google Drive
  `daikenja` folder when the user has opted in).
- Instructions embedded in content a skill ingests -- a thread, a transcript, a
  document -- that redirect the skill's behaviour.
- Secrets or personal data committed to this repository, including in history
  and in test fixtures.
- A weakness in the release path: the tag, the `release` branch, or the CI
  workflows.

## What is out of scope

- Vulnerabilities in Claude Code, the Claude API, or the Google Drive connector.
  Report those to their own maintainers.
- The fact that a skill reads files on your machine or writes a ledger into your
  project. That is the documented purpose, gated on your approval.
- Anything requiring an attacker who already controls your machine or your
  Claude Code configuration.
