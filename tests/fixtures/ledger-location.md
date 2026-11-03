# Ledger location -- configuration fixtures

<!--
Fixture: six synthetic `daikenja.yaml` project entries plus the walks each is
for. Everything here is invented -- invented projects, invented people,
`example.com` links. Nothing is read at runtime.

There is no test runner. Walk `project-log` and the five read skills
(`project-catchup`, `project-summary`, `project-decisions`, `project-gaps`,
`project-sources`) by hand against each configuration below, run from the
directory named in each walk, and compare against the expected result stated
under it.
-->

Depends on: config-resolution.md "Finding `DECISIONS.md` and `open.md`", config-resolution.md "Legacy keys and unmigrated ledgers"

## Config A -- one repository, nothing on disk yet

The common case.

```yaml
profile:
  name: rimuru

projects:
  tempest-guild:
    path: C:/GitHub/tempest-guild
```

**Expected walk**, run from `C:/GitHub/tempest-guild`, with neither file on
disk and no `.daikenja/ledger.md`.

1. `docs/config-resolution.md` § Finding `DECISIONS.md` and `open.md` applies:
   the files are `C:/GitHub/tempest-guild/DECISIONS.md` and, the only path
   being home, `C:/GitHub/tempest-guild/.daikenja/open.md`.
2. The legacy check finds no `.daikenja/ledger.md`, so nothing needs
   migration.
3. A read skill reports "No ledger yet in C:/GitHub/tempest-guild. Run
   /daikenja:project-log to create one." and stops, per `docs/reading.md`
   § Step B. `project-log` instead offers to scaffold both files from
   `templates/DECISIONS.md` and `templates/open.md`.

**The failure this catches:** looking for the ledger anywhere but the two fixed
paths, or scaffolding from a read skill.

## Config B -- three repositories, run from the second

```yaml
profile:
  name: rimuru

projects:
  quill-gateway:
    paths:
      - C:/GitHub/quill-gateway
      - C:/GitHub/quill-web
      - C:/GitHub/quill-infra
```

**Expected walk**, run from `C:/GitHub/quill-web/src/auth`, with a
`DECISIONS.md` in `quill-gateway` and `quill-web`, none in `quill-infra`, and
`open.md` in `quill-gateway`.

1. Longest-prefix match is `quill-web`, the second path of `quill-gateway`.
2. Home is the **first** path, so open items are
   `C:/GitHub/quill-gateway/.daikenja/open.md`, not anything under
   `quill-web`.
3. A read skill reads both existing `DECISIONS.md` files, per §
   Reading several repositories; `quill-infra` has none, which is not a notice.
4. `Ledger: C:/GitHub/quill-gateway/DECISIONS.md, C:/GitHub/quill-web/DECISIONS.md, C:/GitHub/quill-infra/DECISIONS.md (not created yet), C:/GitHub/quill-gateway/.daikenja/open.md`.
5. An entry reported from `quill-gateway`'s file names `quill-gateway`, so the
   reader knows it binds a question asked from `quill-web`.

**The failure this catches:** reading only the `DECISIONS.md` of the repository
the run started in, or looking for `open.md` under the matched path instead of
home.

## Config C -- a leftover relative `ledger:` key

```yaml
profile:
  name: rimuru

projects:
  harbor-rollout:
    path: C:/GitHub/harbor
    ledger: records/decisions.md
```

**Expected walk**, run from `C:/GitHub/harbor`, where
`C:/GitHub/harbor/DECISIONS.md` and `.daikenja/open.md` already exist (the
project was migrated, but the key was hand-restored from an old backup).

1. The `ledger:` key is ignored, per § Legacy keys and unmigrated ledgers. One
   line: "harbor-rollout still has a ledger: key, which is no longer read --
   run /daikenja:setup-user."
2. The read continues with the fixed paths:
   `C:/GitHub/harbor/DECISIONS.md` and `C:/GitHub/harbor/.daikenja/open.md`.
   `records/decisions.md` is never opened.

**The failure this catches:** honouring the old pointer, or stopping on it.
The key is noise once the files are at their fixed paths; it gets one line and
nothing else.

## Config D -- a project with no paths

```yaml
profile:
  name: rimuru

projects:
  vendor-onboarding-programme:
    paths: []
    ledger: C:/Users/rimuru/.claude/daikenja/ledgers/vendor-onboarding-programme.md
```

**Expected walk**, `/daikenja:project-summary vendor-onboarding-programme` run
from anywhere.

1. The key matches. The entry has no paths, so there is no home and no
   repository to read: one line, "vendor-onboarding-programme has no
   repository in daikenja.yaml and needs migration -- run
   /daikenja:setup-user.", and the read stops for that project.
2. The absolute `ledger:` file is not opened, and neither notice is about the
   `ledger:` key: the no-paths line already says what to do.
3. Run without the key, from any directory, directory resolution skips the
   entry; it never matches by accident.

**The failure this catches:** reading the old absolute ledger as if pathless
projects were still supported, or reporting the entry as malformed rather
than as needing migration.

## Config E -- a registered project that resolves to the home directory

It guards the boundary between `project-log`'s two Step 3 checks, which are
easy to collapse into one "is this a project?" test.

```yaml
profile:
  name: rimuru

projects:
  everything:
    path: C:/Users/rimuru
```

**Expected walk of `project-log`**, run from `C:/Users/rimuru` -- the user's
actual home directory -- with no ledger on disk.

1. The entry matches exactly, so this is a **registered** project. The files
   would be `C:/Users/rimuru/DECISIONS.md` and
   `C:/Users/rimuru/.daikenja/open.md`.
2. Step 3's **refuse-outright** check fires anyway and the run **stops**:

   ```
   Won't create a ledger in C:/Users/rimuru -- that's your home directory, not
   a project. Run this from the project you mean to log.
   ```

3. The registered-project exemption does **not** reach this check. It exempts
   only the second one, the `.git`/`.daikenja/` heuristic. Registration is
   evidence about an ordinary directory; it is not evidence that the home
   directory is a project, because `daikenja.yaml` is hand-editable and
   matching takes the longest prefix -- an entry whose `path` is
   `C:/Users` would sweep the home directory in the same way without ever
   naming it.

**The failure this catches:** scoping the registered-project exemption to the
whole of Step 3 rather than to the heuristic alone, which silently disables
the home-directory refusal for exactly the configurations most likely to have
a too-broad `path`. `setup-project` refuses to register `~` or `~/.claude`, so
the only way such an entry exists is a hand edit -- which is precisely the
case a guard should not trust.

## Config F -- an old ledger at the default location

The default-location case: no key points at the old ledger, it simply sits
where every ledger used to.

```yaml
profile:
  name: rimuru

projects:
  shion-kitchen:
    path: C:/GitHub/shion-kitchen
```

**Expected walk**, run from `C:/GitHub/shion-kitchen`, where
`C:/GitHub/shion-kitchen/.daikenja/ledger.md` holds an old-format ledger
(`D-001`-style IDs, a Changelog) and neither `DECISIONS.md` nor
`.daikenja/open.md` exists.

1. § Finding `DECISIONS.md` and `open.md` resolves the two fixed paths; neither
   exists.
2. The legacy check runs before the "no ledger yet" notice: home has
   `.daikenja/ledger.md` and no `open.md` beside it, so the ledger was never
   migrated.
3. A read skill prints one line and stops, reading nothing from the old file:

   ```
   The ledger at C:/GitHub/shion-kitchen/.daikenja/ledger.md needs migration -- run /daikenja:setup-user.
   ```

4. `project-log` refuses to scaffold `DECISIONS.md` or `open.md` over it, with
   the same line, and writes nothing.
5. **Variant:** the repository also has a `DECISIONS.md` that
   plan-staged-rollout wrote. The walk is the same -- the check keys on the old
   ledger with no `open.md` beside it, so an adopted `DECISIONS.md` does not
   hide an unmigrated ledger's open items.

**The failure this catches:** reporting "No ledger yet" and offering to
scaffold a fresh pair beside an old ledger, which would fork the project's
record into two files nobody reconciles.
