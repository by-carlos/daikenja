# tests/

Fixtures the skills are exercised against, plus one script. Nothing here is
read at runtime, and no skill points at this directory -- it exists so a
stage's acceptance checks can be re-run later against the same inputs.

- [`check-invariants.py`](check-invariants.py) -- enforces the invariants
  every v2 build stage checked by hand: `claude plugin validate .` exits
  clean, and every `skills/*/SKILL.md` frontmatter block parses as YAML with
  a `name` matching its directory and a `description`. Requires `pyyaml`
  (`pip install pyyaml`) and the `claude` CLI on `PATH`. Run it with
  `python tests/check-invariants.py`; CI runs it on every push and pull
  request via `.github/workflows/ci.yml`.

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
- [`fixtures/broken-supersession.md`](fixtures/broken-supersession.md) -- a
  ledger with two mismatched supersession pairs (a body claiming `Supersedes`
  with no matching tail, and a tail with no matching claim), plus a correctly
  matched pair as a control. Exercises `decisions`' tail-is-authoritative
  handling: it must report both mismatches, naming both IDs, and never repair
  the ledger.

Every fixture is synthetic: invented project, invented people, `example.com`
links. Nothing in this directory may contain real work content, personal data or
organization data.
