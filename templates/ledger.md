# {{PROJECT}} ledger

<!--
Daikenja ledger. Format spec: docs/ledger-format.md in the Daikenja plugin.

Newest first, in every section. An entry goes directly above the first one
dated the same or older -- for an entry dated today that is under the heading.
Only the `project-log` skill writes this file. Every other Daikenja skill
reads it.

Entry shape, Decisions and Open items:
  <marker><date> -- <id> -- <owner> -- <body>
  Split on " -- " at most three times. The body may contain "--".
  Owner is "@name", or "@unassigned" when there is none.

Two tails may follow a body:
  -> resolved YYYY-MM-DD[, see D-nnn]
  -> superseded by D-nnn

Sources are a head line "- S-001 -- Label -- <url or path>" plus field lines
indented two spaces, one per line, every field optional: "modified:" (as the
source's system reports it), "read:" (YYYY-MM-DD), "covers:",
"does not answer:".
-->

## Decisions

<!-- - YYYY-MM-DD -- D-001 -- @owner -- What was decided. [label](url) -->

## Open items

<!-- - [ ] YYYY-MM-DD -- O-001 -- @owner -- What is unresolved. [label](url) -->
<!-- Resolve by flipping the box and appending: -> resolved YYYY-MM-DD[, see D-nnn] -->

## Context links

<!-- - Label -- https://example.com -->

<!-- ## Sources -->

<!-- - S-001 -- Label -- https://example.com/page -->
<!-- Field lines follow, indented two spaces, one per line, in this order: -->
<!-- modified:, read:, covers:, does not answer:. Absent means unknown. -->

## Changelog

<!-- - YYYY-MM-DDThh:mmZ -- project-log -- +D-001, +O-001, resolved O-002 -->
<!-- Verbs: +created, ~edited, resolved, superseded, -deleted. Every change gets a line. -->
