# templates/

Files Daikenja copies into a user's own directories. Nothing here is read at
runtime from this location -- `setup-user` copies a template out to
`~/.claude/daikenja/`, and `project-log` scaffolds the ledger into a project's
`.daikenja/` directory. The copies are the live files; these are only the
starting points.

- [`daikenja.yaml`](daikenja.yaml) -- the config template `setup-user` copies to
  `~/.claude/daikenja/`. Schema: [`../docs/config-schema.md`](../docs/config-schema.md).
- [`ledger.md`](ledger.md) -- the empty ledger `project-log` scaffolds into a
  project's `.daikenja/`, with `{{PROJECT}}` replaced by the project name. Format:
  [`../docs/ledger-format.md`](../docs/ledger-format.md).
- [`personas.md`](personas.md) and [`writing-style.md`](writing-style.md) -- the
  prose templates a user fills in and points at from `daikenja.yaml`. The
  pointer may name a local file or a Google Drive file; `setup-user` writes the
  same template into whichever the user chose. See
  [`../docs/config-resolution.md`](../docs/config-resolution.md) § Resolving
  `writing_style` and `personas`.
- [`tensei.md`](tensei.md) -- the conversational persona `/daikenja:tensei`
  installs to `~/.claude/daikenja/tensei.md`, imported from `~/.claude/CLAUDE.md`.
  Unlike the two templates above, this one is not a blank starting point the
  user fills in: it is maintained content, and the skill can update an
  installed copy the user has not edited by hand. See
  [`../skills/tensei/SKILL.md`](../skills/tensei/SKILL.md).

Nothing in this directory may contain personal or organization data.
