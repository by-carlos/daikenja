# docs/

Specifications the skills agree on. A skill implements a contract; it never
redefines one. When a contract changes, it changes here and the skills follow.

- [`ledger-format.md`](ledger-format.md) -- the ledger file layout, the entry
  line shape, and how skills read it.
- [`config-contract.md`](config-contract.md) -- the `daikenja.yaml` schema, the
  lookup order, how the `writing_style` and `personas` pointers resolve,
  precedence, and failure behavior.
- [`upgrading.md`](upgrading.md) -- what a user has to do when a release changes
  something already on their disk. One section per version that needs action,
  newest first, written by the change and promoted by the release. The only
  document here written for the user rather than for a skill.
- [`reading.md`](reading.md) -- the shared read mechanism for `project-catchup`,
  `project-summary`, `project-decisions` and `project-gaps`: take an optional
  project key, resolve config, find the ledger, parse it.
- [`voice.md`](voice.md) -- the default writing voice, in two tiers: `Fixed`,
  which a user cannot switch off, and `Defaults`, which a user's own
  `writing-style.md` layers on top of. The layering contract is fixed in
  `config-contract.md`.
- [`response-format.md`](response-format.md) -- how a skill reports to the
  user in the conversation: answer first, findings itemised, entries named
  topic-first with the ID in parentheses, `profile.tone` scaling narration,
  and a one-line report for a clean result.
- [`substance-checks.md`](substance-checks.md) -- the six checks a request has
  to pass, shared by `compose` and `preflight`.
- [`rewrite-rules.md`](rewrite-rules.md) -- the rules that bound any rewrite
  of a user's message. Applied by `compose` and by `preflight`.
- [`reviewer-personas.md`](reviewer-personas.md) -- the reviewer archetypes
  `preflight` dispatches, the two checks it always runs itself, and the
  contract every finding comes back in.
- [`future-work.md`](future-work.md) -- what the shipped design does not do.
  Limitations of current behaviour, not a roadmap.
