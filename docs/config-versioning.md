# Version marker and upgrades

Depends-on (reverse index -- hand-maintained, checked against SKILL.md
headings by tests/check-invariants.py):
- § Version marker and upgrades -- setup-project "Step 0: the preconditions", setup-user "Step 2: the upgrade branch"

The `daikenja_version` key in `daikenja.yaml`, what makes a skill notice it is
behind, and what `upgrading.md` is for. Companion to
[`config-resolution.md`](config-resolution.md), which holds where the file
lives and how everything else in it resolves; see
[`config-schema.md`](config-schema.md) § Field notes for the key's shape.

A release can change something that already exists on a user's disk -- the shape
of a key here, the grammar of a ledger entry, the name of a skill. Nothing on
the user's side records which version wrote what they have, so without a marker
there is no way to tell an affected install from an unaffected one. That is what
`daikenja_version` is for, and this section is the whole rule.

**Two versions are compared.** The **recorded** version is `daikenja_version` in
`daikenja.yaml`. The **installed** version is the `version` field of
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`, which ships with the plugin
and is therefore always the version currently running.

**Compare them as semver, field by field, numerically** -- never as strings.
`0.10.0` is later than `0.9.0`, and string order says the opposite.

## The mismatch notice

**Every skill that reads `daikenja.yaml` emits one notice line when the recorded
version is out of date, then continues.** This is what makes the upgrade path
get reached at all: nobody re-runs setup after an upgrade unless something tells
them to.

That is binding on all of them, and most do not restate it -- a rule copied into
a dozen skills is a rule that drifts a dozen ways. The three places it is named
again say something the contract does not: [`reading.md`](reading.md) § Step A
places it in the read recipe's order, and `project-log` and `setup-project` also
*write* to this file, so each states that it still does not migrate.

A skill emits the notice when **both** of these hold:

1. The recorded version differs from the installed one, or is absent or empty.
2. [`upgrading.md`](upgrading.md) names at least one version **later than the
   recorded one**. An absent recorded version makes every section later than it.
   Sections under an `## [Unreleased]` heading do not count -- an unreleased
   note is not a version anyone can be on.

The second condition is what stops the line becoming noise. Most releases change
nothing on disk and add no section, and a notice that fires on every patch bump
teaches the user to ignore the one that matters. If `upgrading.md` cannot be
read at all, fall back to noticing on any difference -- erring toward telling the
user is the safe direction.

The wording is one line, and it names both versions and the skill:

```
daikenja.yaml was written by Daikenja 0.4.0; 0.6.0 is installed -- run /daikenja:setup-user.
daikenja.yaml predates version tracking; 0.6.0 is installed -- run /daikenja:setup-user.
```

**A skill never migrates anything and never edits configuration because it saw a
mismatch.** The notice is the whole of a reading skill's part in this. Migration
happens in `setup-user`, on the user's deliberate say-so, and nowhere else.

**Malformed YAML outranks all of the above.** A file that does not parse is a
hard stop naming the first unparsing line, per
[Failure behavior](config-resolution.md#failure-behavior). Never attempt to read
a version out of a file you could not parse, and never migrate one.

## What `upgrading.md` is for

[`upgrading.md`](upgrading.md) holds one section per version that requires user
action: what changed on disk, what happens if the user does nothing, the exact
edit, whether `setup-user` can make it, and whether it is reversible. A release
that changes nothing on a user's disk adds nothing to it.

It does not duplicate `CHANGELOG.md`. The changelog records *what changed*; this
records *what you must do about it*. Two files holding the same fact drift; two
files holding different facts do not.
