<!-- decisions-format: 1 -->
# Decisions

Decisions in force. Read the area that covers a path before changing it; add
or edit an entry in the same pull request when a change settles something
future work must respect.

## Ledger files

Paths: `docs/decisions-format.md`, `docs/open-format.md`, `templates/DECISIONS.md`, `templates/open.md`, `skills/project-log/`, `docs/project-log-reference.md`

- **`docs/decisions-format.md` is a byte-identical copy of plan-staged-rollout's
  spec: change it upstream, then copy it.** — it is the contract between the
  two plugins. Revisit: never. Source: #292
- **Daikenja's own rules — the `open.md` grammar, the version rule for both
  files — live in `docs/open-format.md`, never in the spec copy.** — the copy
  must stay identical. Revisit: never. Source: #292
- **On a newer format version, reading skills read and warn once; `project-log`
  refuses to write.** — reading is safe, writing could corrupt the file.
  Revisit: never. Source: #292
- **"Ledger" names `DECISIONS.md` plus `.daikenja/open.md` to users.** — skill
  triggers, bot prompts and the guide keep working. Revisit: if users stop
  calling it the ledger. Source: #292
- **No IDs and no markers; the one exception is `Blocked by:` on `open.md` item
  lines, naming the other item in words.** — the file is current-only and git
  keeps the history. Revisit: never. Source: #292
- **`project-log` never commits; `project-catchup` lists uncommitted changes to
  the two files.** — no skill commits on whatever branch the user is on.
  Revisit: never. Source: #292
- **`project-log <key>` writes to a project with paths from any directory, with
  no branch warning; the proposal names each file by absolute path.** — fixed
  paths settle where a write lands, so the old refusal guarded nothing.
  Revisit: if a ledger file's location stops following from the entry alone.
  Source: #320

## Projects and configuration

Paths: `docs/config-*.md`, `templates/daikenja.yaml`, `docs/reading.md`, `skills/setup-project/`, `skills/project-catchup/`

- **Every project lives in a git repository; projects without a folder are not
  supported.** — git is the ledger's history. Revisit: never. Source: #292
- **The files sit at fixed paths, `<repo>/DECISIONS.md` and
  `<home>/.daikenja/open.md`, home being the first entry of `paths`; there is no
  `ledger:` key.** — reuses the first-path rule. Revisit: never. Source: #292
- **`last_checkpoint` maps each repository path to a commit SHA; an unresolvable
  SHA is a first run, and the report says so.** — a silent first run reads like
  "nothing changed". Revisit: never. Source: #292
- **Legacy config is reported, never repaired in place: `paths: []`, or an old
  `.daikenja/ledger.md` with no `open.md` beside it, means "needs migration".**
  — keyed on `open.md`, so another tool's `DECISIONS.md` cannot hide an
  unmigrated ledger. Revisit: after the first real upgrade. Source: #292, #322

## Migration from the old ledger

Paths: `docs/ledger-migration.md`, `skills/setup-project/`, `skills/setup-user/`

- **The procedure lives in `docs/ledger-migration.md`; `setup-project` runs it
  and `setup-user` hands off to it.** — keeps `setup-project` under the skill
  size trigger. Revisit: if the procedure shrinks enough. Source: #292
- **Migration drops superseded entries, writes through `project-log` in one
  approval and keeps `<name>.<YYYY-MM-DD>.bak.md` beside the old ledger.** —
  the stem stops two backups in one folder colliding. Revisit: never. Source: #292
- **A no-folder project's new home defaults to a new folder outside any
  repository, with `git init`; a target inside a repository is asked about.**
  — private notes never land in a repository unannounced. Revisit: never. Source: #292

## Stance and the writing style

Paths: `skills/compose/`, `skills/preflight/`, `docs/stance-check.md`, `docs/rewrite-rules.md`, `docs/config-resolution.md`

- **Stance prose in `writing-style.md` triggers flags, never edits; the
  stance-kept rule outranks it, in any section of the file.** — the sender
  keeps their position and decides on any reframe. Revisit: never. Source: #331
- **The stance check is opt-in through a `stance-check: on` line in
  `writing-style.md`, with role facts in its `## Role and stance` section; no
  `daikenja.yaml` key.** — the switch travels with the prose wherever the
  pointer resolves. Revisit: if a second setting needs the same switch.
  Source: #331
- **`compose` and `preflight` both run the stance check, from one shared
  `docs/stance-check.md`; neither restates the four cases.** — one set of
  cases cannot drift between the rewrite and the review, as with
  `substance-checks.md`. Revisit: if a third consumer needs different cases.
  Source: #335
- **In `preflight` the stance check is reported only, never fixed in the
  rewrite and never put to a reviewer.** — the stance is the sender's call,
  and a reviewer that saw the flag would anchor on it. Revisit: never.
  Source: #335

## Persona notes and what is derived from them

Paths: `templates/personas.md`, `skills/remember-persona/`, `docs/reviewer-personas.md`, `skills/preflight/`, `templates/tensei.md`

- **Anything derived from `personas.md` is written only to the session's
  scratch folder, and its first line is `<!-- daikenja:private -->`; that
  includes every `preflight` reviewer's output.** — persona-derived files
  predict real colleagues' reactions and once nearly landed in a repository
  about to be shared with the team; the marker lets a git guard refuse them.
  Revisit: never. Source: PR_PENDING
- **`personas.md` starts with the same marker, and `remember-persona` restores
  it only alongside a write it is already making.** — the template covers new
  files; existing files are fixed without an unasked write of their own.
  Revisit: if a second skill gains write access to the file. Source: PR_PENDING

## Skill invocation

Paths: `skills/compose/`, `docs/guide/commands.md`

- **`compose` is model-invocable on a narrow trigger: the words "compose",
  "run compose on" or "polish this message", or a message Claude will post or
  send for the user.** — Claude drafting a message to post must be able to run
  it without a retyped slash command; a one-sentence description keeps the
  listing cost low and stray phrases out. Revisit: if it fires on asks that
  were not about a message. Source: #337
- **`compose` never posts or sends; posting stays with the caller, after the
  user's explicit yes to the final text.** — a model-invoked draft must not
  become a send path. Revisit: never. Source: #337

## Slack bot

Paths: `bot/`

- **The bot reads current files only, never git history, and adds no
  dependency.** — it runs headless with Read, Glob and Grep. Revisit: never.
  Source: #292
