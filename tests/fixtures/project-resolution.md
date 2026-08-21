# Project resolution -- configuration fixtures

<!--
Fixture: one synthetic `daikenja.yaml` plus seven walks over it. Everything
here is invented -- invented projects, invented people, `example.com` links.
Nothing is read at runtime.

There is no test runner. Walk the four read skills, `project-log`,
`setup-project` and `project-list` by hand against the configuration below and
compare against the expected result stated under each walk.

Every walk assumes the **installed** version -- `version` in
`.claude-plugin/plugin.json` -- matches `daikenja_version` below, so no version
notice fires and the walks stay about resolution alone.
-->

## The configuration

Four projects, one of each legal shape: a single-value `path` written before
`paths` existed, a `paths` list of three repositories, a project with no
directory at all, and a nested project inside one of the others.

```yaml
daikenja_version: 0.5.1

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

  quill-programme:
    paths:
      - C:/GitHub/quill-gateway
      - C:/GitHub/quill-web
      - C:/GitHub/quill-infra
    stale_after_days: 30

  beacon-charter:
    paths: []

  harbor-migrator:
    path: C:/GitHub/harbor/tools/migrator
```

Assume on disk: `C:/GitHub/harbor/.daikenja/ledger.md` exists,
`C:/GitHub/quill-gateway/.daikenja/ledger.md` exists, and
`C:/GitHub/quill-web/.daikenja/ledger.md` does **not**.

## Walk 1 -- a single-value `path`, resolved by directory

Run `/daikenja:project-summary` from `C:\GitHub\harbor\services\ingest`.

1. No key was given, so `reading.md` § Step A0 falls through to § Step A.
2. Normalized, the directory is `c:/github/harbor/services/ingest`.
   `c:/github/harbor` is a prefix; `c:/github/harbor/tools/migrator` is not.
3. Longest match is `harbor-rollout`. Its root is its only path.
4. `Ledger: C:/GitHub/harbor/.daikenja/ledger.md`, and the overview follows.

**The failure this catches:** a `path` scalar that stopped resolving once
`paths` existed. Every configuration written before this change has this shape,
and it must behave exactly as it did.

## Walk 2 -- several paths, reached from the second one

Run `/daikenja:project-gaps` from `C:\GitHub\quill-web\src`.

1. `c:/github/quill-web` matches, and it is the **second** path of
   `quill-programme`.
2. The project is `quill-programme`. Its root is the **first** path,
   `C:/GitHub/quill-gateway`.
3. `Ledger: C:/GitHub/quill-gateway/.daikenja/ledger.md` -- not
   `C:/GitHub/quill-web/.daikenja/ledger.md`, which does not exist and must
   never be scaffolded or reported as the project's ledger.
4. The 30-day threshold is this project's own, so the run says so.

**The failure this catches:** resolving the ledger against the path that
matched. That gives a three-repository project three ledgers, so a decision
logged from `quill-infra` cannot be found from `quill-gateway`, and neither run
has any way to notice.

## Walk 3 -- a pathless project, by key

Run `/daikenja:project-summary beacon-charter` from anywhere -- the directory
is irrelevant and that is the point.

1. Step A0 matches the key `beacon-charter`. Directory resolution never runs.
2. The entry has no paths, so there is no root and no ledger location.
3. The run stops with one line and reads nothing:

   ```
   beacon-charter has no path in daikenja.yaml, so its ledger has no location yet.
   ```

**The failure this catches:** treating `paths: []` as malformed, or falling
back to `.daikenja/ledger.md` under the current directory -- which would answer
about whatever repository the user happened to be in, under the name of the
project they asked for.

## Walk 4 -- a key that resolves, from the wrong directory

Run `/daikenja:project-decisions quill-programme` from `C:\GitHub\harbor`.

1. Step A0 matches. `harbor-rollout` would have matched by directory, and is
   not consulted.
2. `Project: quill-programme` and
   `Ledger: C:/GitHub/quill-gateway/.daikenja/ledger.md`.
3. The decisions reported are quill's.

**The failure this catches:** the original bug. A person who moved a ledger, or
who is simply in the wrong window, gets answered about the project they named
rather than the folder they are standing in -- and the reply says which project
it is about, so a mistake is visible.

## Walk 5 -- a key that does not resolve

Run `/daikenja:project-catchup quil-programme` -- one letter short.

1. Step A0 finds no entry under that key.
2. The run stops, names the key and lists the registered ones:

   ```
   No project called quil-programme in daikenja.yaml. Registered:
   harbor-rollout, quill-programme, beacon-charter, harbor-migrator.
   ```

3. Nothing is read and no checkpoint is written.

**The failure this catches:** falling back to the current directory on an
unknown key. That answers confidently about a different project, and there is
nothing in the reply to tell the user it happened.

## Walk 6 -- a nested project still wins on the longest prefix

Run `/daikenja:project-log` from `C:\GitHub\harbor\tools\migrator\src`.

1. Two paths are prefixes: `c:/github/harbor` and
   `c:/github/harbor/tools/migrator`.
2. The longest wins, so the project is `harbor-migrator` and the ledger is
   `C:/GitHub/harbor/tools/migrator/.daikenja/ledger.md`.
3. `project-log` takes no key argument, so there is no way to redirect this
   from the command line -- and it says nothing about keys.

**The failure this catches:** letting the multi-path change disturb nesting.
Longest-prefix-wins now runs across every path of every entry, and an entry's
own paths cannot compete with each other, but a genuinely nested project is
still the innermost match.

## Walk 7 -- `project-list` over the whole file

Run `/daikenja:project-list` from `C:\GitHub\quill-web`.

Expected, in this order:

1. A count and the current project: four projects, `quill-programme` marked.
2. `harbor-rollout` -- one path, ledger exists.
3. `quill-programme` -- three paths with the first marked as the root, ledger
   exists at `C:/GitHub/quill-gateway/.daikenja/ledger.md`.
4. `beacon-charter` -- no paths, reachable by name only, no ledger location.
5. `harbor-migrator` -- one path, and its ledger reported as not existing, with
   `/daikenja:project-log` named as what creates one.
6. The bounded scan under `C:/GitHub/quill-web`, and what it found or did not.

**The failure this catches:** a report that hides the two states a person
actually needs -- a project whose ledger is missing, and a project that has
nowhere to put one. Everything else on the list is a line of confirmation.
