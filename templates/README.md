# templates/

Files Daikenja copies into a user's own directories. Nothing here is read at
runtime from this location -- `setup-user` copies a template out to
`~/.claude/daikenja/`, and `project-log` scaffolds the ledger into a project's
`.daikenja/` directory. The copies are the live files; these are only the
starting points.

- [`daikenja.yaml`](daikenja.yaml) -- the config template `setup-user` copies to
  `~/.claude/daikenja/`. Schema: [`../docs/config-contract.md`](../docs/config-contract.md).
- [`ledger.md`](ledger.md) -- the empty ledger `project-log` scaffolds into a
  project's `.daikenja/`, with `{{PROJECT}}` replaced by the project name. Format:
  [`../docs/ledger-format.md`](../docs/ledger-format.md).
- [`personas.md`](personas.md) and [`writing-style.md`](writing-style.md) -- the
  prose templates a user fills in and points at from `daikenja.yaml`. The
  pointer may name a local file or a Google Drive file; `setup-user` writes the
  same template into whichever the user chose. See
  [`../docs/config-contract.md`](../docs/config-contract.md) § Resolving
  `writing_style` and `personas`.

Nothing in this directory may contain personal or organization data.
