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
-->

## Decisions

<!-- - YYYY-MM-DD -- D-001 -- @owner -- What was decided. [label](url) -->

## Open items

<!-- - [ ] YYYY-MM-DD -- O-001 -- @owner -- What is unresolved. [label](url) -->
<!-- Resolve by flipping the box and appending: -> resolved YYYY-MM-DD[, see D-nnn] -->

## Context links

<!-- - Label -- https://example.com -->

## Changelog

<!-- - YYYY-MM-DDThh:mmZ -- project-log -- +D-001, +O-001, resolved O-002 -->
<!-- Verbs: +created, ~edited, resolved, superseded, -deleted. Every change gets a line. -->
