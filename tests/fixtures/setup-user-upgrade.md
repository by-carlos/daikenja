# setup-user upgrade branch -- configuration fixtures

<!--
Fixture: six synthetic `daikenja.yaml` files plus the walks each one is for.
Everything here is invented -- invented projects, invented people,
`example.com` links. Nothing is read at runtime.

Every walk below assumes:

- The **installed** version -- `version` in `.claude-plugin/plugin.json` --
  reads `0.6.0`.
- `docs/upgrading.md` holds two version sections, `## [0.6.0]` (the version
  marker itself, promoted from `## [Unreleased]` at release) and
  `## [0.3.0]` (the five renamed project skills), newest first.

There is no test runner. Walk `setup-user` by hand against each configuration
and compare against the expected result stated under it.
-->

Depends on: setup-user "Step 2: the upgrade branch", setup-user "Proposing the upgrade", config-versioning.md "The mismatch notice", ledger-migration.md "Which projects need migration"

## Config A -- no version key

The file every user who installed before the key existed will have. This is the
common case, not an edge one.

```yaml
profile:
  name: rimuru
  role: Platform Lead
  org: Tempest
  tone: standard
  writing_style: ./writing-style.md
  personas: ./personas.md
  stale_after_days: 21

projects:
  harbor-rollout:
    path: C:/GitHub/harbor
    last_checkpoint: 2026-08-14T09:12Z
```

**Expected walk of `setup-user`.**

1. Step 1 reads the file. It parses, so nothing stops. No `daikenja_version`.
2. Step 2 compares. Recorded is absent, installed is `0.6.0`. Absent means
   "written before the key existed", which is legal and is **not** an error and
   **not** a stop.
3. Every section in `docs/upgrading.md` is later than an absent version, so both
   apply. They are shown **oldest first** -- `0.3.0`, then `0.6.0`.
4. `0.3.0` is reported, not proposed: the five renamed commands are not an edit
   this skill can make, and there is nothing on disk to change. `0.6.0` is
   proposed as a concrete edit -- add `daikenja_version: 0.6.0` at the top level.
5. One question covering both. On approval the key is written above `profile:`
   and stamped `0.6.0`.

**The failure this catches:** stopping, erroring, or treating the absent key as
malformed. Any of those makes every pre-0.6.0 install unusable until the user
hand-edits a file they were never told about.

**Second walk -- the user declines.** Nothing is written and
`daikenja_version` is **not** stamped. The skill says the notice will keep
appearing until the upgrade is accepted. Stamping a declined upgrade would
silence the only thing still telling the user it is outstanding, and is the
single most tempting wrong move in this branch.

## Config B -- an older version

```yaml
daikenja_version: 0.2.0

profile:
  name: benimaru
  role: Reliability
  tone: direct
  writing_style: ./writing-style.md
  personas: ./personas.md

projects:
  quill-gateway:
    path: C:/GitHub/quill-gateway
    stale_after_days: 30
```

**Expected walk of `setup-user`.** Both `0.3.0` and `0.6.0` are later than
`0.2.0`, so this behaves exactly as Config A from step 3 onwards. The one
difference is that Step 2 has a recorded version to name in its notice.

**Expected walk of a read skill** -- `project-catchup`, `project-summary`,
`project-decisions` or `project-gaps`, run from `C:/GitHub/quill-gateway`. After
`reading.md` § Step A resolves the config and before the answer, exactly one
line:

```
daikenja.yaml was written by Daikenja 0.2.0; 0.6.0 is installed -- run /daikenja:setup-user.
```

Then the read continues and produces its normal output. The notice never blocks
it, never repeats, and the skill migrates nothing.

**Expected walk of `project-log`**, same directory. The same one line at Step 2,
then the write proceeds normally. `project-log` writes `daikenja.yaml` for
nothing here: it does not stamp `daikenja_version` and does not migrate, even
though it is a writer of that file.

**The failure this catches:** a read or write skill that "helpfully" stamps the
version or applies the migration itself. Only `setup-user` may, and only with
the user's say-so.

## Config C -- current

```yaml
daikenja_version: 0.6.0

profile:
  name: shion
  tone: guided
  writing_style: ./writing-style.md
  personas: ./personas.md

projects: {}
```

**Expected walk of `setup-user`.** Step 2 compares `0.6.0` against `0.6.0`, they
match, and it says **nothing at all**. Not "no upgrade needed", not "you are up
to date" -- nothing. Step 4 restamps `0.6.0`, which changes no bytes. The run
reads exactly as it did before the branch existed.

**Expected walk of any other skill.** No version line anywhere in the output.

**The failure this catches:** a branch that announces itself on every ordinary
re-run. `setup-user` is re-run often and its idempotency is the reason it is
safe to; a line of noise per run erodes that.

## Config D -- does not parse

The `tone` line has an unquoted colon in its value, and `projects:` is indented
under a key that has already closed.

```yaml
daikenja_version: 0.2.0

profile:
  name: gobta
  tone: standard: the default
   writing_style: ./writing-style.md

projects:
  harbor-rollout:
    path: C:/GitHub/harbor
```

**Expected walk of `setup-user`.** Step 1 **stops** and names the first line that
does not parse. Step 2 never runs.

This is the ordering the branch's position exists to guarantee: a recorded
version of `0.2.0` is visible on the first line and would look like a perfectly
good reason to migrate. It is not. Reading a version out of a file that does not
parse means trusting a parse that failed, and migrating one means editing a file
whose shape is unknown. **Malformed YAML outranks the upgrade branch**, and
nothing is written.

**The failure this catches:** a migration that runs on an unparsable file and
"repairs" it, destroying hand-written content the user cannot get back.

## Config E -- recorded version ahead of installed

Beyond the four the issue asked for. It covers a real case: a user who installed
a newer Daikenja on one machine and an older one on another, with the
configuration shared between them.

```yaml
daikenja_version: 0.7.0

profile:
  name: hakurou
  tone: standard
  writing_style: drive:writing-style.md
  personas: ./personas.md

projects:
  harbor-rollout:
    path: C:/GitHub/harbor
```

**Expected walk of `setup-user`.** Step 2 finds recorded `0.7.0` ahead of
installed `0.6.0`. It does not migrate -- there is nothing in `docs/upgrading.md`
later than `0.7.0`, because this install has never seen `0.7.0`. It says one line
and continues with the rest of setup.

**`daikenja_version` is left at `0.7.0`.** Step 4 does not restamp it. Writing
`0.6.0` over it would destroy the only record that a newer version had been here,
and the next run on the newer machine would then see a false gap and offer to
"upgrade" a file that is already ahead.

**The failure this catches:** stamping unconditionally on every run. That is the
obvious reading of "written on every run" and it is wrong in exactly this case.

## Config F -- old ledgers waiting to migrate

Its own assumptions, unlike A to E: the installed version reads `0.13.0`, and
`docs/upgrading.md`'s top section is `## [0.13.0]`, promoted from the
`## [Unreleased]` notes that moved the ledger to `DECISIONS.md` and `open.md`
-- the config section and the ledger-migration section.

```yaml
daikenja_version: 0.12.0

profile:
  name: rimuru
  tone: standard
  writing_style: ./writing-style.md
  personas: ./personas.md

projects:
  atlas:
    path: C:/GitHub/atlas
    last_checkpoint: 2026-08-20T09:12Z
  q4-planning:
    paths: []
    ledger: ~/.claude/daikenja/ledgers/q4-planning.md
  lantern:
    path: C:/GitHub/lantern
```

`C:/GitHub/atlas/.daikenja/ledger.md` exists with no `open.md` beside it.
`C:/GitHub/lantern` has a `DECISIONS.md` and an `open.md`, and no old ledger.

**Expected walk of `setup-user`.**

1. Step 2 selects `0.13.0` and both of its change notes, oldest first.
2. Neither is proposed as an edit here. The run lists the projects that need
   migration, per `ledger-migration.md` § Which projects need migration, with
   the command for each, and nothing else about them:

   ```
   Two projects still keep the old single-file ledger. Migrate each when you are
   ready -- it shows everything before writing:
   - atlas -- /daikenja:setup-project atlas
   - q4-planning (no folder yet) -- /daikenja:setup-project q4-planning
   ```

   `lantern` is not listed: it already has `open.md` and no old ledger.
3. On approval, `daikenja_version` is stamped `0.13.0`. **`projects:` is not
   touched**: atlas keeps its timestamp `last_checkpoint`, q4-planning keeps
   `paths: []` and its `ledger:` key. Those go in each project's own migration.
4. Afterwards, every skill that reaches atlas or q4-planning still says it
   needs migration, until `setup-project` migrates it.

**The failure this catches:** `setup-user` removing the `ledger:` key or
`paths: []` itself, which leaves the config naming no ledger while the old file
still holds the only copy of the project's record -- or migrating a ledger
itself, when `project-log` is the only writer of ledger content.
