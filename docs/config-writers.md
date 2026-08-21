# Who writes what

Which skill owns which file, and which part of it. Companion to
[`config-resolution.md`](config-resolution.md), which holds where the files
live and how a pointer resolves to one.

| File | Written by | Notes |
|---|---|---|
| `daikenja.yaml` -- the `profile:` block | `setup-user` | Only on user approval. Never touches `projects:`. |
| `daikenja.yaml` -- `daikenja_version` | `setup-user` | Stamped on every successful run, in the same approved write as whatever else that run changed. No other skill writes it, and no skill writes it because it noticed a mismatch. See [Version marker and upgrades](config-versioning.md#version-marker-and-upgrades). |
| `daikenja.yaml` -- a project's entry under `projects:` | `setup-project` | Only on user approval, and only the entry matching the directory it runs in. Registration is idempotent: an exact normalized-path match leaves the existing entry and its key alone. Never writes `last_checkpoint`. |
| `daikenja.yaml` -- `last_checkpoint` | `project-catchup` | Proposes advancing it after reporting; writes on approval. |
| `personas.md` -- creating the file | `setup-user`, and `remember-persona` on absence | Both copy the blank template if and only if no file exists, and neither inspects or overwrites content. `setup-user` does this proactively on every run; `remember-persona` does it only when it has an entry to write and finds the file missing, folding the scaffold into that write's report. Copying the template twice is idempotent, so the two never conflict. |
| `personas.md` -- content | the user by hand, and `remember-persona` | Appends an entry for a person the user described. Any other skill that needs a persona recorded runs it. The append is silent only where the user described the person with nothing pasted; a description that arrived with pasted material is offered once and written on a yes. Amending prose the user wrote by hand is proposed, never silent. |
| `writing-style.md` -- creating the file | `setup-user` on absence | Copies the blank template if and only if no file exists, and never inspects content. Same rule as `personas.md`. |
| `writing-style.md` -- content | the user by hand, and `learn-voice` on approval | `learn-voice` derives a proposal from writing samples the user supplies, shows the exact content it would write -- as a diff whenever the file already holds anything -- and writes only what the user approves. Nothing else edits it. |
| `<project>/.daikenja/ledger.md` | `project-log`, and only `project-log` | `meeting-review` writes through `project-log`. Every other skill reads. |

**The table names the local defaults, and who may write does not change with
where the prose lives.** When `personas` or `writing_style` points at a Drive
file, the same skill writes the same content to that file instead of to a local
one, through the replacement sequence in
[`config-drive.md`](config-drive.md) § Writing replaces the file. Two rules
follow from the fact that Daikenja can only see Drive files it created itself:

- **`setup-user` is the only skill that creates a Drive file or the `daikenja`
  folder**, and only when the user chooses Drive during setup and the connector
  is present. It creates the folder if it is not already there, writes the blank
  template into a new file inside it, and puts that file's name in the pointer.
  This is not a convention about tidiness. A file Daikenja did not create cannot
  be seen at all, so creating it is the only way one can exist to point at.
- **`remember-persona` does not create Drive files, and never redirects a
  write.** Its scaffold-on-absence rule covers local files only. If `personas`
  is a Drive pointer that does not resolve, it writes nothing, says so, and
  keeps the entry in the conversation. Falling back to the local default would
  split the user's notes across two stores without telling them, which is worse
  than not writing.

**The single-writer rule governs the ledger, not `daikenja.yaml`.** This
distinction matters: `project-catchup`'s job is to report a delta and move the
checkpoint, so it must be able to write that one key. It still never touches
ledger content.

**`personas.md` has two writers doing two different acts, not one job split in
two.** `setup-user` owns *creation* as a standing rule -- existence is its only
test, and a file that is already there is left alone whatever is in it.
`remember-persona` owns every *content* write, and appending an entry is the
only way content reaches the file from Daikenja; because a content write needs
the file to exist, it also scaffolds the same template on absence rather than
stopping to wait for `setup-user`. Creation is now something both skills can
do, but the split that matters is unchanged: `setup-user` never writes
content, and `remember-persona` never inspects or overwrites content on an
existing file. That is the boundary the ledger's stricter single-writer rule
does not transfer here unchanged.

A learned entry is written without asking and reported afterwards, which is
deliberate: an append is additive and reversible, and the report names the file
and shows the exact entry so it can be edited or deleted. That licence covers
new people only. Prose the user wrote by hand is never rewritten silently.

**The licence also stops at the file's own subject: real colleagues.** Where the
description came in with material the user pasted -- a draft, a thread, an
example -- the person may be invented, and nothing in a pasted block has to say
so. `remember-persona` therefore offers those entries and writes them on a yes,
per its Step 1 § Where the description came from. That test lives there and
nowhere else: a skill that routes a description to it reports the outcome and
never re-decides it. **The question never gates the caller** -- a review or a
draft finishes and carries the offer back as one line, the same one line a
silent write would have cost it.

**`writing-style.md` splits the same way, and its content writer asks every
time.** `setup-user` owns creation on the same existence-only test, and
`learn-voice` owns every content write. The two prose files differ only in what
buys the write: an appended persona is additive, so it is silent and reported
afterwards, while a derived writing style replaces the whole file and is
therefore proposed in full, diffed against whatever is already there, and
written only on approval. Neither skill may write the other's file, and
`setup-user`'s never-inspect rule is unchanged -- `learn-voice` reads the file
under its own contract, to show the user what would change.

`setup-user` writes a fresh configuration by asking the user. It does not
import or convert anything from another tool or from any pre-plugin layout.

**It does apply Daikenja's own documented upgrade steps**, and it is the only
skill that does. When the recorded `daikenja_version` is behind the installed
one, its upgrade branch reads [`upgrading.md`](upgrading.md), proposes the exact
edits for the versions in between, and writes them on approval -- the same
propose-then-approve shape as everything else it does. That is a different act
from importing a foreign layout, which it still refuses. See
[Version marker and upgrades](config-versioning.md#version-marker-and-upgrades).

**`setup-project` may propose ledger content but never writes it.** Its optional
seeding step derives candidate decisions and open items from sources the user
names, and hands them to `project-log`, which shows the exact lines and waits.
That keeps the single-writer rule for the ledger intact while letting a project
start with the history it already has.
