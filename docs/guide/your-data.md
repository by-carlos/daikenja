# Where your data lives


Nothing personal is stored in this repository, and nothing personal should ever
be written into the installed plugin directory -- plugin directories are managed
and get overwritten on update.

| What | Where | Written by |
|---|---|---|
| Profile, per-project settings, checkpoints | `~/.claude/daikenja/daikenja.yaml` | `setup-user` for your profile, `setup-project` for a project's entry, and `project-catchup` for the `last_checkpoint` key only |
| Your notes on the people you work with | `~/.claude/daikenja/personas.md`, or `daikenja/personas.md` in your Google Drive | you, plus `remember-persona` for people you describe to it |
| How you write | `~/.claude/daikenja/writing-style.md`, or `daikenja/writing-style.md` in your Google Drive | you, plus `learn-voice`, which backs up the file before replacing it |
| Your domain glossary -- one line per term you have had to explain | `~/.claude/daikenja/glossary.md` | you, plus any skill that glosses a term you defined for it, one dated line at a time |
| A project's decision ledger | `<project root>/.daikenja/ledger.md`, or wherever that project's `ledger:` key points -- including outside the project. For a project spanning several directories the root is the first one registered | `project-log` only |

The plugin ships blank starting points in `templates/`. Those get copied out to
your directories; the copies are the live files.

**Local files are the default, and Google Drive is opt-in.** If you want your
persona notes or your writing style reachable from another machine, either one
can live in Google Drive instead -- `setup-user` offers this once, works fine
without it, and never asks you to sign up for anything. Drive is reached through
Google's own connector, under your own account, so nothing goes through the
plugin author. The two settings are independent: keeping personal notes on
colleagues local while sharing a writing style is a normal setup. The ledger
does not move -- it stays in the project, where git already versions it.

Everything Daikenja puts in Drive goes in **one `daikenja` folder** it creates
for you, mirroring `~/.claude/daikenja/` on your machine. Nothing is left loose
at the top level of your Drive.

Two things are worth knowing before you choose Drive. **`setup-user` has to
create the file**: the connector only shows Claude the files it created itself,
so a document already in your Drive cannot be pointed at, however you share it.
And **a Drive file that Daikenja cannot read stops the skill** rather than
quietly carrying on, because an unreadable file and an empty one look identical
from here -- the alternative is drafting in the default voice while you think
your own style was applied.

Two rules the skills follow:

- **One writer for the ledger.** Only the `project-log` skill writes ledger
  content. `project-catchup` writes one config key, `last_checkpoint`, because
  reporting a delta and moving the checkpoint is its job -- it never touches
  the ledger itself. `setup-project` can propose a whole ledger's worth of
  entries when it seeds one, and every last line still goes through
  `project-log` for your approval. Every other skill only reads.
- **You approve first.** A skill proposes a ledger entry, you confirm, then it
  writes.
