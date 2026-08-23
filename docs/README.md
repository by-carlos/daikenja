# docs/

Specifications the skills agree on. A skill implements a contract; it never
redefines one. When a contract changes, it changes here and the skills follow.

One file here is a different kind. `project-log-reference.md` belongs to a
single skill rather than to an agreement between several: it holds the sections
of `project-log/SKILL.md` that a run reaches only on some branches, kept out of
line so a run that never reaches one never pays to read it. It is that skill's
own instructions and binds exactly as if it sat in its `SKILL.md`; no other
skill reads it.

- [`ledger-format.md`](ledger-format.md) -- the ledger file layout, the entry
  line shape, and how skills read it.
- [`project-log-reference.md`](project-log-reference.md) -- `project-log`'s own
  branch-only sections: scaffolding a missing ledger, an imposed decision, a
  relationship marker, a source, a backfill, a meeting date handed over by
  `meeting-review`, the failure cases, and what that skill does not do. Read at
  the point of use, never on every run.
- [`config-resolution.md`](config-resolution.md) -- the resolution core: where
  `daikenja.yaml` lives, the lookup order, how the `writing_style` and
  `personas` pointers resolve, precedence, and failure behavior.
- [`config-schema.md`](config-schema.md) -- the `daikenja.yaml` schema, key by
  key, and two worked examples.
- [`config-writers.md`](config-writers.md) -- which skill writes which key or
  file.
- [`config-drive.md`](config-drive.md) -- the Google Drive-specific mechanics
  for a `drive:` pointer.
- [`config-versioning.md`](config-versioning.md) -- the `daikenja_version`
  marker and what `upgrading.md` is for.
- [`upgrading.md`](upgrading.md) -- what a user has to do when a release changes
  something already on their disk. One section per version that needs action,
  newest first, written by the change and promoted by the release. The only
  document here written for the user rather than for a skill.
- [`reading.md`](reading.md) -- the shared read mechanism for `project-catchup`,
  `project-summary`, `project-decisions`, `project-gaps` and
  `project-sources`: take an optional project key, resolve config, find the
  ledger, parse it.
- [`voice.md`](voice.md) -- the default writing voice, in two tiers: `Fixed`,
  which a user cannot switch off, and `Defaults`, which a user's own
  `writing-style.md` layers on top of. The layering contract is fixed in
  `config-resolution.md` § Voice and writing style.
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
