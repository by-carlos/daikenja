# Project resolution -- configuration fixtures

<!--
Fixture: one synthetic `daikenja.yaml` plus twelve walks over it. Everything
here is invented -- invented projects, invented people, `example.com` links.
Nothing is read at runtime.

There is no test runner. Walk the five read skills, `project-log`,
`setup-project` and `project-list` by hand against the configuration below and
compare against the expected result stated under each walk.

Every walk assumes the **installed** version -- `version` in
`.claude-plugin/plugin.json` -- matches `daikenja_version` below, so no version
notice fires and the walks stay about resolution alone.
-->

Depends on: config-resolution.md "Finding the project", config-resolution.md "Finding `DECISIONS.md` and `open.md`", config-resolution.md "Legacy keys and unmigrated ledgers", config-resolution.md "Precedence", project-list "Step 2: resolve every entry", project-list "Step 4: report"

## The configuration

Four projects: a single-value `path` written before `paths` existed, a `paths`
list of three repositories, a nested project inside one of the others, and a
project left over from before every project lived in a repository -- no paths
and an absolute `ledger:` -- which now needs migration.

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
    last_checkpoint:
      C:/GitHub/harbor: 4f9c2e1

  quill-programme:
    paths:
      - C:/GitHub/quill-gateway
      - C:/GitHub/quill-web
      - C:/GitHub/quill-infra
    stale_after_days: 30

  beacon-charter:
    paths: []
    ledger: C:/Users/rimuru/.claude/daikenja/ledgers/beacon-charter.md

  harbor-migrator:
    path: C:/GitHub/harbor/tools/migrator
```

Assume on disk: `C:/GitHub/harbor/DECISIONS.md` and
`C:/GitHub/harbor/.daikenja/open.md` exist; `C:/GitHub/quill-gateway/DECISIONS.md`,
`C:/GitHub/quill-gateway/.daikenja/open.md` and
`C:/GitHub/quill-web/DECISIONS.md` exist; `C:/GitHub/quill-infra` has neither
file; `C:/Users/rimuru/.claude/daikenja/ledgers/beacon-charter.md` exists; and
nothing exists under `C:/GitHub/harbor/tools/migrator`.

## Walk 1 -- a single-value `path`, resolved by directory

Run `/daikenja:project-summary` from `C:\GitHub\harbor\services\ingest`.

1. No key was given, so `reading.md` § Step A0 falls through to § Step A.
2. Normalized, the directory is `c:/github/harbor/services/ingest`.
   `c:/github/harbor` is a prefix; `c:/github/harbor/tools/migrator` is not.
3. Longest match is `harbor-rollout`. Its home is its only path.
4. `Ledger: C:/GitHub/harbor/DECISIONS.md, C:/GitHub/harbor/.daikenja/open.md`,
   and the overview follows.

**The failure this catches:** a `path` scalar that stopped resolving once
`paths` existed. Every configuration written before this change has this shape,
and it must behave exactly as it did.

## Walk 2 -- several paths, reached from the second one

Run `/daikenja:project-gaps` from `C:\GitHub\quill-web\src`.

1. `c:/github/quill-web` matches, and it is the **second** path of
   `quill-programme`.
2. The project is `quill-programme`. Its home is the **first** path,
   `C:/GitHub/quill-gateway`, so open items come from
   `C:/GitHub/quill-gateway/.daikenja/open.md` -- not from anything under
   `quill-web`, which has no `open.md` and must never be scaffolded one.
3. `Ledger:` names all three `DECISIONS.md` paths, `quill-infra`'s marked as
   not created yet, and the home `open.md`.
4. The 30-day threshold is this project's own, so the run says so.

**The failure this catches:** resolving `open.md` against the path that
matched. That gives a three-repository project three lists of open items, so an
item logged from `quill-infra` cannot be found from `quill-gateway`, and neither
run has any way to notice.

## Walk 3 -- a pathless project, by key

Run `/daikenja:project-summary beacon-charter` from anywhere -- the directory
is irrelevant and that is the point.

1. Step A0 matches the key `beacon-charter`. Directory resolution never runs.
2. The entry has no paths, so it needs migration, per
   `config-resolution.md` § Legacy keys and unmigrated ledgers. The run stops
   with one line and reads nothing:

   ```
   beacon-charter has no repository in daikenja.yaml and needs migration -- run /daikenja:setup-user.
   ```

3. The absolute `ledger:` file exists but is not opened.

**The failure this catches:** reading the old absolute ledger as if pathless
projects were still supported, or falling back to the current directory --
which would answer about whatever repository the user happened to be in, under
the name of the project they asked for.

## Walk 3b -- a pathless project, by directory

Run `/daikenja:project-summary` from `C:\Users\rimuru\.claude\daikenja\ledgers`.

1. `beacon-charter` has no paths, so it is never a directory-resolution
   candidate, and no other entry matches. The project is unregistered.
2. The unregistered branch of `reading.md` § Step A runs: one line naming
   `/daikenja:setup-project`, then the current directory stands in as the one
   root. Neither `DECISIONS.md` nor `.daikenja/open.md` exists there, and no
   `.daikenja/ledger.md` either, so the run reports "No ledger yet" and stops.

**The failure this catches:** matching the old ledger's folder to the pathless
project, which would make the old file look like a live ledger again.

## Walk 3c -- `project-log` on a pathless project by key

Run `/daikenja:project-log beacon-charter` from anywhere.

1. Step 2's key check matches `beacon-charter`. The entry has no paths, so it
   needs migration: the same one line as Walk 3, and nothing is written.
2. Neither `DECISIONS.md` nor `open.md` is scaffolded anywhere, and the old
   absolute ledger is not appended to.

**The failure this catches:** writing into the old ledger, or scaffolding the
new pair somewhere arbitrary -- the current directory, or Daikenja's own config
folder -- because a location was missing and a default had to come from
somewhere.

## Walk 3d -- `project-log` refuses a key that has paths

Run `/daikenja:project-log quill-programme` from `C:\GitHub\harbor`.

1. Step 2's key check matches `quill-programme`, but the entry has paths.
   Refused: one line naming the key and saying that logging against it means
   running from one of its own directories.
2. Directory resolution does not run as a fallback. `harbor-rollout` would
   have matched `C:\GitHub\harbor` by directory, and it is not consulted --
   the named key is decisive, per `config-resolution.md` § Finding the
   project, the same as a read skill's Step A0.
3. Nothing is written.

**The failure this catches:** two ways a rooted project could still be
written to the wrong root -- silently falling back to whatever directory the
user happens to be standing in once the named key is refused, or accepting
the key anyway and guessing which of `quill-programme`'s three repositories is
meant. Both are worse than refusing and saying why.

## Walk 4 -- a key that resolves, from the wrong directory

Run `/daikenja:project-decisions quill-programme` from `C:\GitHub\harbor`.

1. Step A0 matches. `harbor-rollout` would have matched by directory, and is
   not consulted.
2. `Project: quill-programme`, and the `Ledger:` line names quill's three
   `DECISIONS.md` paths and its home `open.md`.
3. The decisions reported are quill's, from both files that exist, each naming
   its repository.

**The failure this catches:** the original bug. A person who is simply in the
wrong window gets answered about the project they named rather than the folder
they are standing in -- and the reply says which project it is about, so a
mistake is visible.

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
2. The longest wins, so the project is `harbor-migrator` and its files are
   `C:/GitHub/harbor/tools/migrator/DECISIONS.md` and
   `C:/GitHub/harbor/tools/migrator/.daikenja/open.md`.
3. No key was named here, so this is unaffected by `project-log`'s key rule
   either way. Had one been named, `harbor-migrator` has a path, so
   `/daikenja:project-log harbor-migrator` from anywhere else would refuse
   rather than redirect here -- see Walk 3d.

**The failure this catches:** letting the multi-path change disturb nesting.
Longest-prefix-wins runs across every path of every entry, and an entry's own
paths cannot compete with each other, but a genuinely nested project is still
the innermost match.

## Walk 7 -- `project-list` over the whole file

Run `/daikenja:project-list` from `C:\GitHub\quill-web`.

Expected, in this order:

1. A count and the current project: four projects, `quill-programme` marked.
2. `harbor-rollout` -- one path, both files exist.
3. `quill-programme` -- three paths with the first marked as home; `open.md`
   exists in `quill-gateway`, and `DECISIONS.md` in `quill-gateway` and
   `quill-web` but not `quill-infra`.
4. `beacon-charter` -- no paths: needs migration, with `/daikenja:setup-user`
   named.
5. `harbor-migrator` -- one path, and neither file existing, with
   `/daikenja:project-log` named as what creates them.
6. The bounded scan under `C:/GitHub/quill-web`, and what it found or did not.

**The failure this catches:** a report that hides the two states a person
actually needs -- a project whose ledger is missing, and a project that cannot
be read until it is migrated. Everything else on the list is a line of
confirmation.

## Walk 8 -- `project-list` narrowed by key

Run `/daikenja:project-list harbor-migrator` from `C:\GitHub\quill-web` -- the
directory is irrelevant and that is the point.

1. Step 1a matches the key `harbor-migrator`. Directory resolution never
   runs -- `quill-programme`, which would have matched by directory, is not
   consulted.
2. Step 2 resolves only that entry: one path, `C:/GitHub/harbor/tools/migrator`,
   and neither `DECISIONS.md` nor `.daikenja/open.md` under it.
3. Step 3's scan is rooted at `C:/GitHub/harbor/tools/migrator` -- the entry's
   own path, not `C:/GitHub/quill-web` -- and finds nothing.
4. The report names the project, its one path, and both files as not existing,
   then says the scan under `C:/GitHub/harbor/tools/migrator` found no
   unregistered ledger.

**The failure this catches:** scanning around the current directory for a
keyed lookup, which would report on whatever repository the user happened to
be standing in instead of the project they asked about -- or silently listing
every entry instead of narrowing to the one requested.

## Walk 9 -- `project-list` with a key that does not resolve

Run `/daikenja:project-list quil-programme` -- one letter short.

1. Step 1a finds no entry under that key.
2. The run stops, names the key and lists the registered ones:

   ```
   No project called quil-programme in daikenja.yaml. Registered:
   harbor-rollout, quill-programme, beacon-charter, harbor-migrator.
   ```

3. Nothing is read and no scan runs.

**The failure this catches:** falling back to listing every project, or to the
current directory, on an unknown key -- either answers confidently about
something other than what was asked, with nothing in the reply to say so.
