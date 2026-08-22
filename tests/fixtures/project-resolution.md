# Project resolution -- configuration fixtures

<!--
Fixture: one synthetic `daikenja.yaml` plus thirteen walks over it. Everything
here is invented -- invented projects, invented people, `example.com` links.
Nothing is read at runtime.

There is no test runner. Walk the five read skills, `project-log`,
`setup-project` and `project-list` by hand against the configuration below and
compare against the expected result stated under each walk.

Every walk assumes the **installed** version -- `version` in
`.claude-plugin/plugin.json` -- matches `daikenja_version` below, so no version
notice fires and the walks stay about resolution alone.
-->

## The configuration

Five projects: a single-value `path` written before `paths` existed, a `paths`
list of three repositories, a project with no directory at all and an absolute
`ledger:`, a nested project inside one of the others, and a pathless project
with no `ledger:` either -- the one shape that cannot resolve.

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
    ledger: C:/Users/rimuru/.claude/daikenja/ledgers/beacon-charter.md

  harbor-migrator:
    path: C:/GitHub/harbor/tools/migrator

  tempest-charter:
    paths: []
```

Assume on disk: `C:/GitHub/harbor/.daikenja/ledger.md` exists,
`C:/GitHub/quill-gateway/.daikenja/ledger.md` exists,
`C:/Users/rimuru/.claude/daikenja/ledgers/beacon-charter.md` exists, and
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
2. The entry has no paths, so nothing relative could resolve. Its `ledger:` is
   **absolute**, so it resolves verbatim.
3. `Project: beacon-charter` and
   `Ledger: C:/Users/rimuru/.claude/daikenja/ledgers/beacon-charter.md`, and
   the overview follows.

**The failure this catches:** treating `paths: []` as malformed, or falling
back to `.daikenja/ledger.md` under the current directory -- which would answer
about whatever repository the user happened to be in, under the name of the
project they asked for. This is also the shape the two changes only work as a
pair for: `paths: []` makes the project reachable without a directory, and the
absolute `ledger:` gives its record somewhere to live.

## Walk 3b -- a pathless project with no ledger either

Run `/daikenja:project-summary tempest-charter`.

1. The key matches, so the project resolves. That part must succeed:
   `paths: []` is legal, not malformed.
2. There is no root and no absolute `ledger:`, so there is no location at all.
   The run stops with one line and reads nothing:

   ```
   tempest-charter has no path and no absolute ledger in daikenja.yaml, so its ledger has no location.
   ```

**The failure this catches:** confusing "cannot resolve a ledger" with "is not
a project". The entry is valid and `project-list` must list it; only the ledger
lookup fails, and the message has to say which of the two is missing.

## Walk 3c -- `project-log` writes to a pathless project by key

Run `/daikenja:project-log beacon-charter` from anywhere -- again, the
directory is irrelevant.

1. Step 2's key check matches `beacon-charter`, and it has no paths, so the
   key is accepted. Directory resolution never runs.
2. `Ledger: C:/Users/rimuru/.claude/daikenja/ledgers/beacon-charter.md` -- the
   same file Walk 3 read. The file exists, so Step 3's scaffold check never
   runs either.
3. The proposal, wait and write happen exactly as an ordinary run; only how
   the project was found differs.

**The failure this catches:** the original bug. `beacon-charter` could be
created (`setup-project`) and read (Walk 3), but never written to -- Step 2
used to skip any entry with no paths outright and take no key at all, so its
ledger could only ever grow by hand.

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
the key anyway and guessing which of `quill-programme`'s three paths is
meant. Both are worse than refusing and saying why.

## Walk 3e -- `project-log` on a pathless project with no ledger location

Run `/daikenja:project-log tempest-charter`.

1. Step 2's key check matches `tempest-charter`. It has no paths, so the key
   is accepted.
2. Step 3 (ledger resolution) finds no `ledger:` key and no root to resolve a
   relative default against. This is the config error, not a missing
   default: the run stops with one line and writes nothing:

   ```
   tempest-charter has no path and no absolute ledger in daikenja.yaml, so its ledger has no location.
   ```

**The failure this catches:** scaffolding `.daikenja/ledger.md` somewhere
arbitrary -- the current directory, or Daikenja's own config folder --
because a location was missing and a default had to come from somewhere. A
pathless entry has no such fallback; the same message Walk 3b showed for a
read applies unchanged to a write.

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
   harbor-rollout, quill-programme, beacon-charter, harbor-migrator,
   tempest-charter.
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
3. No key was named here, so this is unaffected by `project-log`'s key
   exception either way. Had one been named, `harbor-migrator` has a path, so
   `/daikenja:project-log harbor-migrator` from anywhere else would refuse
   rather than redirect here -- see Walk 3d.

**The failure this catches:** letting the multi-path change disturb nesting.
Longest-prefix-wins now runs across every path of every entry, and an entry's
own paths cannot compete with each other, but a genuinely nested project is
still the innermost match.

## Walk 7 -- `project-list` over the whole file

Run `/daikenja:project-list` from `C:\GitHub\quill-web`.

Expected, in this order:

1. A count and the current project: five projects, `quill-programme` marked.
2. `harbor-rollout` -- one path, ledger exists.
3. `quill-programme` -- three paths with the first marked as the root, ledger
   exists at `C:/GitHub/quill-gateway/.daikenja/ledger.md`.
4. `beacon-charter` -- no paths, reachable by name only, ledger at its absolute
   location, which exists.
5. `harbor-migrator` -- one path, and its ledger reported as not existing, with
   `/daikenja:project-log` named as what creates one.
6. `tempest-charter` -- no paths and no ledger location at all, with
   `/daikenja:setup-project` named as where an absolute `ledger:` is set.
7. The bounded scan under `C:/GitHub/quill-web`, and what it found or did not.

**The failure this catches:** a report that hides the two states a person
actually needs -- a project whose ledger is missing, and a project that has
nowhere to put one. Everything else on the list is a line of confirmation.

## Walk 8 -- `project-list` narrowed by key

Run `/daikenja:project-list harbor-migrator` from `C:\GitHub\quill-web` -- the
directory is irrelevant and that is the point.

1. Step 1a matches the key `harbor-migrator`. Directory resolution never
   runs -- `quill-programme`, which would have matched by directory, is not
   consulted.
2. Step 2 resolves only that entry: one path, `C:/GitHub/harbor/tools/migrator`,
   and a ledger at the default location, which does not exist.
3. Step 3's scan is rooted at `C:/GitHub/harbor/tools/migrator` -- the entry's
   own path, not `C:/GitHub/quill-web` -- and finds nothing.
4. Report:

   ```
   Project: harbor-migrator

   harbor-migrator
     path    C:/GitHub/harbor/tools/migrator
     ledger  C:/GitHub/harbor/tools/migrator/.daikenja/ledger.md    no such file

   no unregistered ledgers under C:/GitHub/harbor/tools/migrator
   ```

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
   harbor-rollout, quill-programme, beacon-charter, harbor-migrator,
   tempest-charter.
   ```

3. Nothing is read and no scan runs.

**The failure this catches:** falling back to listing every project, or to the
current directory, on an unknown key -- either answers confidently about
something other than what was asked, with nothing in the reply to say so.
