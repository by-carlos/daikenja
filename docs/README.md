# docs/

Specifications the skills agree on. A skill implements a contract; it never
redefines one. When a contract changes, it changes here and the skills follow.

- [`ledger-format.md`](ledger-format.md) -- the ledger file layout, the entry
  line shape, and how skills read it.
- [`config-contract.md`](config-contract.md) -- the `daikenja.yaml` schema, the
  lookup order, precedence, and failure behavior.

Still to land:

- `voice.md` -- the default writing voice shipped with Daikenja, which a user's
  own `writing-style.md` layers on top of. The layering contract is fixed in
  `config-contract.md`; the file itself is written by the `compose` stage.
