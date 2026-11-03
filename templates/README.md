# templates/

Files Daikenja copies into a user's own directories. Nothing here is read at
runtime from this location -- `setup-user` copies a template out to
`~/.claude/daikenja/`, `project-log` scaffolds the ledger -- `DECISIONS.md` at a
repository's root and `.daikenja/open.md` in the home repository -- and
`setup-project` scaffolds the project card beside `open.md`. The copies are the
live files; these are only the starting points.

- [`daikenja.yaml`](daikenja.yaml) -- the config template `setup-user` copies to
  `~/.claude/daikenja/`. Schema: [`../docs/config-schema.md`](../docs/config-schema.md).
- [`ledger.md`](ledger.md) -- the old single-file ledger, no longer scaffolded
  by any skill. Kept until its format document is retired. Format:
  [`../docs/ledger-format.md`](../docs/ledger-format.md).
- [`DECISIONS.md`](DECISIONS.md) -- the empty decisions file `project-log`
  scaffolds at a repository's root, copied as it stands. Format:
  [`../docs/decisions-format.md`](../docs/decisions-format.md).
- [`open.md`](open.md) -- the empty open-items file `project-log` scaffolds
  into the home repository's `.daikenja/`, with `{{PROJECT}}` replaced by the
  project name. Format: [`../docs/open-format.md`](../docs/open-format.md).
- [`project.md`](project.md) -- the empty project card `setup-project`
  scaffolds at `.daikenja/project.md` in the home repository, beside `open.md`,
  with `{{PROJECT}}` replaced by the project name. Format: [`../docs/project-card.md`](../docs/project-card.md).
- [`personas.md`](personas.md) and [`writing-style.md`](writing-style.md) -- the
  prose templates a user fills in and points at from `daikenja.yaml`. The
  pointer may name a local file or a Google Drive file; `setup-user` writes the
  same template into whichever the user chose. See
  [`../docs/config-resolution.md`](../docs/config-resolution.md) § Resolving
  `writing_style` and `personas`.
- [`glossary.md`](glossary.md) -- the empty domain glossary `setup-user` copies
  to `~/.claude/daikenja/glossary.md` if absent: one line per term, ten words
  of gloss at most, with project, date and source. Always local, never a
  pointer or a Drive file. Manual-only: no skill reads or writes it after
  `setup-user` creates it, so the user keeps it by hand.
- [`tensei.md`](tensei.md) -- the way of working (answer shape, design
  recommendations, working practice) that `/daikenja:tensei` installs to
  `~/.claude/daikenja/tensei.md`, imported from `~/.claude/CLAUDE.md`.
  Unlike `personas.md`, `writing-style.md` and `glossary.md`, this one is
  not a blank starting point the user fills in: it is maintained content, and
  the skill can update an installed copy the user has not edited by hand. See
  [`../skills/tensei/SKILL.md`](../skills/tensei/SKILL.md).

Nothing in this directory may contain personal or organization data.
