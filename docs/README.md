# docs/

Specifications the skills agree on. A skill implements a contract; it never
redefines one. When a contract changes, it changes here and the skills follow.

- [`ledger-format.md`](ledger-format.md) -- the ledger file layout, the entry
  line shape, and how skills read it.
- [`config-contract.md`](config-contract.md) -- the `daikenja.yaml` schema, the
  lookup order, precedence, and failure behavior.
- [`reading.md`](reading.md) -- the shared read mechanism for `catchup`,
  `summary`, `decisions` and `gaps`: resolve config, find the ledger, parse it.
- [`voice.md`](voice.md) -- the default writing voice, which a user's own
  `writing-style.md` layers on top of. The layering contract is fixed in
  `config-contract.md`.
- [`substance-checks.md`](substance-checks.md) -- the six checks a request has
  to pass, shared by `compose` and `preflight`.
- [`rewrite-rules.md`](rewrite-rules.md) -- the rules that bound any rewrite of
  a user's message, shared by `compose` and `preflight`.
