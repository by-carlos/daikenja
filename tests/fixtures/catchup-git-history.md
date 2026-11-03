# Catchup over git history

<!--
Fixture: a two-repository project whose ledger has a short git history, plus
five `last_checkpoint` values to walk `project-catchup` against. Synthetic
content: an invented project and people, `example.com` links.

It exercises the paths a catchup run can take: changes reported since a
checkpoint SHA, an unresolvable SHA reported as a first run, a repository with
no checkpoint entry, a scalar timestamp left over from the old layout, a SHA
holding shell metacharacters that must be rejected before git sees it, and an
uncommitted edit listed as "not committed yet" in every walk.

Build the two repositories from the commits below in a scratch folder, in
order, then leave the last edit uncommitted. `<C1>` to `<C3>` and `<I1>` stand
for the SHAs your build produced; the walks never depend on their exact value.
-->

Depends on: project-catchup "Step 2: read and check each checkpoint", project-catchup "Step 3: compute the delta", project-catchup "Step 4: report the delta", project-catchup "Step 5: propose and write the checkpoint", config-schema.md "Field notes"

## The project

```yaml
projects:
  lumen-launch:
    paths:
      - C:/GitHub/lumen-app      # home: holds .daikenja/open.md
      - C:/GitHub/lumen-infra
```

Each walk below adds one `last_checkpoint` to this entry. The walks run from
`C:/GitHub/lumen-app`.

## History of `lumen-app`

**`<C1>` -- "Start the lumen ledger"** (2026-09-03, Noor). `DECISIONS.md`:

```markdown
<!-- decisions-format: 1 -->
# Decisions

Decisions in force. Read the area that covers a path before changing it; add
or edit an entry in the same pull request when a change settles something
future work must respect.

## Delivery

Paths: `web/`, `cdn.config.json`

- **Static assets are served from one CDN, with no origin fallback.** — a
  fallback doubled the cache-miss cost in the trial. Revisit: if the CDN misses
  its uptime target. Source: https://example.com/lumen/issues/12
```

`.daikenja/open.md`:

```markdown
<!-- daikenja-open-format: 1 -->
# lumen-launch open items

## Open items

- 2026-09-02 -- @noor -- Confirm the CDN contract renews before launch.
- 2026-09-03 -- @unassigned -- Pick the launch date.

## Context links

- Launch plan -- https://example.com/lumen/launch-plan

## Sources
```

**`<C2>` -- "Log the launch date"** (2026-09-10, Tomas). Appends to
`DECISIONS.md`:

```markdown

## Launch

Paths: `release/`

- **Launch on Tuesday 2026-10-06, not the Monday before.** — the support rota
  is thin on Mondays. Revisit: if the support rota changes. Source:
  https://example.com/lumen/issues/19
```

In `open.md`, deletes the "Pick the launch date." line (closed) and adds, under
`## Open items`:

```markdown
- 2026-09-10 -- @unassigned -- Decide who announces the launch on the status page.
```

**`<C3>` -- "Keep an origin fallback for launch month"** (2026-09-12, Noor).
Replaces the Delivery entry in `DECISIONS.md` with:

```markdown
- **Static assets are served from one CDN, with the origin as a fallback for
  the first month.** — launch week cannot risk a CDN-only outage. Revisit:
  after 2026-11-06. Source: https://example.com/lumen/issues/24
```

**Uncommitted** -- `project-log` wrote this and nobody has committed it. Adds to
`open.md`, under `## Open items`:

```markdown
- 2026-09-15 -- @tomas -- Book the launch-day war room.
```

## History of `lumen-infra`

**`<I1>` -- "Record the hosting layout"** (2026-09-04, Noor). `DECISIONS.md`,
the same header as `lumen-app`'s, then:

```markdown
## Hosting

Paths: `infra/`

- **One resource group per environment, named `rg-lumen-<env>`.** — access is
  granted per group. Revisit: if environments share a subscription. Source:
  https://example.com/lumen-infra/issues/3
```

No `open.md`: only the home repository has one.

## Walk 1: changes since a checkpoint

```yaml
    last_checkpoint:
      C:/GitHub/lumen-app: <C1>
      C:/GitHub/lumen-infra: <I1>
```

Expected: both SHAs pass validation and resolve. `lumen-app` reports 2 commits
since `<C1>` and four changes, each by its current wording: the launch-date
decision (new, Launch); the CDN decision (edited, Delivery -- the origin
fallback wording, not the old one); "Pick the launch date" (closed); "Decide
who announces the launch on the status page" (new, called out as unowned).
`lumen-infra` has no commits since `<I1>`. Under **Not committed yet**: "Book
the launch-day war room" (new, `open.md`). The proposal moves `lumen-app` to
`<C3>` and leaves `lumen-infra`, whose HEAD is already `<I1>`.

## Walk 2: an unresolvable SHA, and a repository with no entry

```yaml
    last_checkpoint:
      C:/GitHub/lumen-app: 0123abcd0123abcd
```

Expected: the value passes validation (hexadecimal, 16 characters) but does not
resolve, so `lumen-app` is a first run with the line "The checkpoint for
lumen-app (0123abcd0123abcd) is not in its history any more, so this is a
first run there." `lumen-infra` has no entry: "No checkpoint for lumen-infra
yet." Both report their whole current content -- two decisions, two open items
and one context link in `lumen-app`, one decision in `lumen-infra` -- and the
uncommitted war-room item is listed as not committed yet. The proposal adds
both repositories.

## Walk 3: a scalar timestamp from the old layout

```yaml
    last_checkpoint: 2026-09-01T09:00Z
```

Expected: the scalar is never validated as a SHA or passed to git. One line
says the checkpoint predates the new ledger, names the timestamp, and makes
this a first run for both repositories; the report is Walk 2's content with the
war-room item not committed yet. The proposal replaces the timestamp with a map
holding `<C3>` for `lumen-app` and `<I1>` for `lumen-infra`.

## Walk 4: a SHA carrying shell metacharacters

```yaml
    last_checkpoint:
      C:/GitHub/lumen-app: "c0ffee1; rm -rf ~"
      C:/GitHub/lumen-infra: "--output=/tmp/x"
```

Expected: both values fail `^[0-9a-fA-F]{7,40}$` -- the first for the
semicolon and spaces, the second for the leading dashes -- so neither reaches
any git command. Each repository gets "The checkpoint for <repo> is not a
commit SHA, so it was not used." and a first run, with the war-room item not
committed yet. The proposal replaces both values with real SHAs.
