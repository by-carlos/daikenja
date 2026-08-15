# tests/

Fixtures the skills are exercised against. Nothing here is read at runtime, and
no skill points at this directory -- it exists so a stage's acceptance checks
can be re-run later against the same inputs.

- [`fixtures/sample-thread.md`](fixtures/sample-thread.md) -- a thread with one
  agreed decision, one proposal nobody agreed to, and two unresolved items.
  Exercises the `log` classifier, including its refusal to log a parked
  suggestion as a decision.
- [`fixtures/sample-thread-followup.md`](fixtures/sample-thread-followup.md) --
  the same conversation with two later messages. Logging it after the first
  fixture must update entries in place instead of appending near copies.
- [`fixtures/malformed-ledger.md`](fixtures/malformed-ledger.md) -- a ledger with
  a misspelled section heading and an entry missing its owner field, plus a legal
  continuation line as a control. A skill must report all of it and write
  nothing.

Every fixture is synthetic: invented project, invented people, `example.com`
links. Nothing in this directory may contain real work content, personal data or
organization data.
