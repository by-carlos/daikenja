# `ledger:` resolution -- configuration fixtures

<!--
Fixture: four synthetic `daikenja.yaml` project entries plus the walks each is
for. Everything here is invented -- invented projects, invented people,
`example.com` links. Nothing is read at runtime.

There is no test runner. Walk `project-log` and the four read skills
(`project-catchup`, `project-summary`, `project-decisions`, `project-gaps`) by
hand against each configuration below, run from the directory named in each
walk, and compare against the expected result stated under it.
-->

## Config A -- no `ledger:` key

The common case, and unchanged by this fixture's subject.

```yaml
profile:
  name: rimuru

projects:
  tempest-guild:
    path: C:/GitHub/tempest-guild
```

**Expected walk**, run from `C:/GitHub/tempest-guild`.

1. `docs/config-resolution.md` § Finding the ledger, step 2 applies: no
   `ledger:` key, so the ledger is `C:/GitHub/tempest-guild/.daikenja/ledger.md`.
2. `Ledger: C:/GitHub/tempest-guild/.daikenja/ledger.md` -- the fully resolved
   absolute path, per `docs/reading.md` § Step B.
3. If no file exists there, a read skill reports "No ledger at
   C:/GitHub/tempest-guild/.daikenja/ledger.md. Run /daikenja:project-log to
   create one." and stops. `project-log` instead offers to scaffold it, per
   its Step 3.

**The failure this catches:** treating the default path as anything other than
what step 2 already meant before this change -- this config must resolve
identically to how it always has.

## Config B -- relative `ledger:` key

```yaml
profile:
  name: rimuru

projects:
  quill-gateway:
    path: C:/GitHub/quill-gateway
    ledger: records/decisions.md
```

**Expected walk**, run from `C:/GitHub/quill-gateway/services/auth`.

1. Longest-prefix match is `quill-gateway` (`C:/GitHub/quill-gateway`).
2. Step 1 of Finding the ledger applies: the project has a `ledger:` key, so
   it is resolved relative to `path` --
   `C:/GitHub/quill-gateway/records/decisions.md`. The default
   `.daikenja/ledger.md` is **not** also checked.
3. `Ledger: C:/GitHub/quill-gateway/records/decisions.md`.

**The failure this catches:** resolving a relative `ledger:` against the
current directory instead of the project's `path` -- the two differ here
because the skill is running from a subdirectory.

## Config C -- absolute `ledger:` key, outside the project root

The repository-less convention this issue adds.

```yaml
profile:
  name: rimuru

projects:
  vendor-onboarding-programme:
    path: C:/Users/rimuru/daikenja-projects/vendor-onboarding-programme
    ledger: C:/Users/rimuru/.claude/daikenja/ledgers/vendor-onboarding-programme.md
```

**Expected walk**, run from
`C:/Users/rimuru/daikenja-projects/vendor-onboarding-programme`.

1. Exact match on `vendor-onboarding-programme`.
2. The project has a `ledger:` key and it is an absolute path, so it resolves
   to itself, verbatim:
   `C:/Users/rimuru/.claude/daikenja/ledgers/vendor-onboarding-programme.md`.
   This is outside `path` entirely, which is legal -- the pointer form does
   not require the resolved path to sit under the project.
3. `Ledger: C:/Users/rimuru/.claude/daikenja/ledgers/vendor-onboarding-programme.md`.
4. `project-log` scaffolds this file from `templates/ledger.md` on the same
   Step 3 approval it always needs -- but the "doesn't look like a project"
   question does **not** fire here, because `vendor-onboarding-programme` is
   already registered in `daikenja.yaml`. Registration is itself the
   confirmation, per Step 3's registered-project branch; the project's own
   directory need not hold `.git` or `.daikenja/` for that to hold, which is
   exactly the case for a project with no repository of its own.

**The failure this catches:** a skill that assumes the ledger always sits
under the matched project's `path` and either refuses an outside path or
silently rewrites it to something under `path`.

## Config D -- absolute `ledger:` key that does not exist

```yaml
profile:
  name: rimuru

projects:
  harbor-rollout:
    path: C:/GitHub/harbor
    ledger: D:/Backups/old-machine/harbor-ledger.md
```

**Expected walk**, run from `C:/GitHub/harbor`, where `D:/Backups/old-machine/`
does not exist on this machine (a stale pointer carried over from another
machine's configuration, for instance).

1. The project has a `ledger:` key, absolute, resolving to
   `D:/Backups/old-machine/harbor-ledger.md`. This is still the resolved
   ledger path -- the key is authoritative, so the default
   `C:/GitHub/harbor/.daikenja/ledger.md` is not consulted as a fallback, even
   though a file might happen to exist there too.
2. `Ledger: D:/Backups/old-machine/harbor-ledger.md`.
3. A read skill reports "No ledger at D:/Backups/old-machine/harbor-ledger.md.
   Run /daikenja:project-log to create one." and stops, per
   `docs/reading.md` § Step B -- the same notice an unconfigured project with
   a missing default file would get. There is nothing distinct about a broken
   absolute pointer; a missing local path is a fact you can establish just as
   plainly as a missing relative one.
4. `project-log` treats this the same as any other missing ledger. `harbor` is
   already registered, so Step 3's "doesn't look like a project" question does
   not fire regardless of what `C:/GitHub/harbor` itself contains -- that
   check is about the current directory's registration status, not about the
   resolved ledger path. Scaffolding proceeds: create the missing
   `D:/Backups/old-machine/` parent directory and write the template there,
   folded into the same Step 5 approval as the rest of the write.

**The failure this catches:** silently falling back to
`C:/GitHub/harbor/.daikenja/ledger.md` because the configured absolute path
did not resolve -- per `docs/config-resolution.md` § Finding the ledger, an
explicit `ledger:` key is authoritative and never degrades to the default.
That degrade would also violate "a ledger found on disk wins over the
config", which is scoped to an *unmatched* project, not to second-guessing a
matched one's explicit key.
