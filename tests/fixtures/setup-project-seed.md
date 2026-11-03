# Fixture: setup-project registration and seeding

Synthetic. Invented project, invented people, `example.com` links only. Nothing
here comes from real work content, and no path below exists on any machine.

Exercises `setup-project` in six walks against one starting state: a first
registration of a code repository, a re-registration of the same path, a seed
run whose proposed entries are partially rejected, a project spanning two
repositories (home asked and written first), a plain folder for non-code work
(`git init` offered), and a repository that already has a `DECISIONS.md`. The
seed sources deliberately include a decision register the project already
keeps, a superseded record, a source with no recoverable date, a proposal
nobody agreed to, a standing policy that reads like one of the project
decisions without being the same fact, and a source no connector can reach.

Every ledger line is written by `project-log`; `setup-project` writes only the
`daikenja.yaml` entry, the card, and `git init` on a yes. Nothing is committed.

Depends on: setup-project "Step 2: register the project", setup-project "Step 4a: look for a register the project already keeps", setup-project "Step 4c: propose in tranches, through `project-log`"

---

## The starting `daikenja.yaml`

Copy this to `~/.claude/daikenja/daikenja.yaml` for the walk, or hold it in the
conversation. One project is already registered and it is not this one.

```yaml
profile:
  name: Carlos
  role: Solutions Architect
  tone: standard
  writing_style: ./writing-style.md
  personas: ./personas.md
  stale_after_days: 21

projects:
  beacon:
    path: C:/GitHub/beacon
    last_checkpoint:
      C:/GitHub/beacon: 4f1c2ab
```

## The project on disk

Walks A to C run from `C:/GitHub/quill-gateway`. It is a git repository, it
has no `DECISIONS.md` and no `.daikenja/` directory, and it already keeps its
own decision records:

```
C:/GitHub/quill-gateway
  .git/
  README.md
  docs/
    adr/
      0001-gateway-replaces-edge-proxy.md
      0002-tls-terminates-at-the-gateway.md
      0003-schema-changes-go-through-the-pipeline.md
      0004-tls-terminates-at-the-load-balancer.md
    open-questions.md
  src/
```

Note the directory name is `quill-gateway`. Walk A registers it under a key the
user chooses instead, which is what Walk B then has to leave alone.

---

## Walk A -- first registration

No `projects:` entry matches `C:/GitHub/quill-gateway`, so a new one is
proposed. The user answers the key question and the per-project keys:

> **Key?** Call it `gateway`, not `quill-gateway`. Just this repository.
>
> **`stale_after_days`?** 30 for this one.
>
> **`norms_doc`?** `https://example.com/quill/ways-of-working`

Then declines seeding for now:

> Not yet, I will seed it later.

**Expected.** One entry, the only path being home, and no `ledger:` key:

```yaml
  gateway:
    paths:
      - C:/GitHub/quill-gateway
    stale_after_days: 30
    norms_doc: https://example.com/quill/ways-of-working
```

The card, if accepted, is `C:/GitHub/quill-gateway/.daikenja/project.md`. No
`DECISIONS.md` or `open.md` is created: seeding was declined, and only
`project-log` scaffolds them.

## Walk B -- re-registration of the same path

Run again from `C:/GitHub/quill-gateway`, with Walk A's write in place. Nothing
about the directory has changed. The user says only:

> I want to seed it now.

The registration step has nothing to do, and the run is here for Step 4 alone.

---

## The seed sources

The user names these when Walk C asks, one category at a time.

### Source 1 -- the decision records in `docs/adr/`

Four records. `ADR-0004` supersedes `ADR-0002`. The columns below are the
whole of what each record's summary says; the detail stays in the record.
`ADR-0003` states no revisit condition.

| Record | Date decided | Summary | Why | Revisit |
|---|---|---|---|---|
| `ADR-0001` | 2026-05-04 | The Quill gateway replaces the edge proxy. No dual-run period. | Two proxies doubled the on-call surface. | Never. |
| `ADR-0002` | 2026-05-19 | TLS terminates at the gateway. | One place to manage certificates. | -- |
| `ADR-0003` | 2026-06-08 | Schema changes reach production through the migration pipeline, never a hand-run script. | A hand-run script skipped the review step. | (not stated) |
| `ADR-0004` | 2026-07-13 | TLS terminates at the load balancer instead. Supersedes `ADR-0002`. | The load balancer already holds the certificates. | If the load balancer is replaced. |

Index at `https://example.com/quill/adr`.

### Source 2 -- the question register at `docs/open-questions.md`

Three numbered questions. One is already answered and closed.

| Question | Date raised | Owner | Status | Summary |
|---|---|---|---|---|
| `Q-01` | 2026-05-21 | sam | open | Who owns gateway certificate rotation after cutover? |
| `Q-02` | 2026-06-02 | (nobody named) | open | Agree what "gateway is done" means before the next planning round. |
| `Q-03` | 2026-06-30 | priya | closed 2026-07-13 | Where does TLS terminate? Answered by `ADR-0004`. |

### Source 3 -- a pasted Slack excerpt from `#quill-gateway`

Pasted, not linked, so it carries no URL.

> **sam** (2026-08-11) -- We agreed on the call this morning to hold the
> gateway cutover until the certificate rotation runbook exists, so nobody is
> rotating by hand on day one. Nobody objected.
>
> **jordan** (2026-08-11) -- We could also move the whole thing behind a
> feature flag while we are at it. Just an idea, I have not thought it
> through.
>
> **priya** -- Somebody still needs to work out what happens to in-flight
> connections during the switch. I do not remember when that first came up.

Three candidates, and they are not the same kind. One is a decision. One is a
suggestion nobody agreed to. One is a real open item whose date is nowhere in
the material and which the user, when asked, cannot pin down either.

### Source 4 -- a Confluence space nobody can reach

> The gateway design space is at
> `https://example.com/wiki/spaces/QUILL/gateway-design`. Pull the decisions
> out of that too.

Walk this with no Confluence connector in the session.

### Source 5 -- a standing team rule the user pastes

Offered unprompted while the documents are being named:

> One more thing that should be in there. Quill's standing rule, it predates
> this project and holds across all of them: nothing is ever run by hand
> against production, whatever it is.

Same subject as `ADR-0003`, different kind. Merging the two loses which one a
later reader is bound by.

---

## Walk C -- seeding, partially rejected

Continues from Walk B. The user's replies to the tranches, in order:

**Decisions tranche.** `ADR-0002` is not in it: `ADR-0004` replaced it, and
`DECISIONS.md` is current-only. The proposal creates
`C:/GitHub/quill-gateway/DECISIONS.md` from the template with
`ADRs: docs/adr/` under the title, and asks one question: the revisit
condition for `ADR-0003`.

> Yes to all of them, revisit the schema one never. And put the old TLS one
> in too, for the record.

The answered tranche is written. The old TLS record is not: the run says the
file holds decisions in force only, and that `docs/adr/0002-...` and git
already keep it. Nothing marked superseded is ever written.

**Open items tranche.**

The user replies about something else entirely:

> By the way, can you also check whether beacon still has that schema freeze
> in its decisions?

Nothing here approves anything. The next thing the run says has to restate what
is still unwritten before proposing anything further.

Then, once asked again:

> Yes to those, except drop the in-flight connections one -- I really cannot
> tell you when that was raised.

**Context links tranche.**

> No links, I will add those myself later.

## What the fixture is built to catch

Walked by hand, since this repo has no test runner. The seed run has to reach
the end of Walk C having written, through `project-log` and nothing else:

1. Nothing at all until a tranche is approved, and nothing from the tranche the
   user replied around.
2. No entry for jordan's feature-flag idea, which nobody agreed to.
3. No entry for priya's in-flight connections item, because no date for it
   exists in the material or in the user's head, and no date may be invented.
4. No entry for `ADR-0002`, even when the user asks for it: the TLS entry names
   `ADR-0004` only. No open item for `Q-03`: the `ADR-0004` entry is what
   answered it.
5. `ADR-0003` and the standing rule in Source 5 kept as two entries, not merged
   into one, even though both are about running things by hand.
6. Decisions in `C:/GitHub/quill-gateway/DECISIONS.md` with no date and no
   owner; `Q-01` and `Q-02` in `C:/GitHub/quill-gateway/.daikenja/open.md`,
   dated when raised (`Q-02` as `@unassigned`), which makes both older than
   this project's 30-day staleness threshold on the day they land. The run has
   to say so before the user runs `/daikenja:project-gaps` and finds it out.
7. No IDs anywhere, and the confirmation says the files are not committed.

---

## Walk D -- a project spanning two repositories

Run from `C:/GitHub/harbor-api`, a git repository root, with Walk A's entry in
place. `C:/GitHub/harbor-docs` is also a git repository. Neither is
registered.

> **New or existing?** New. Call it `harbor`. It also covers
> `C:/GitHub/harbor-docs`, and that one is home -- the docs repo is where the
> team works.

**Expected.** Home is written first, though the run started in the other
repository:

```yaml
  harbor:
    paths:
      - C:/GitHub/harbor-docs
      - C:/GitHub/harbor-api
```

The card is offered at `C:/GitHub/harbor-docs/.daikenja/project.md`. A later
seed puts each decision in the `DECISIONS.md` of the repository whose code it
constrains, project-wide ones and every open item in `harbor-docs`.

**Variant D2.** Later, run from `C:/GitHub/quill-web` (a git repository),
answered "another repository of `gateway`". The path is appended after
`C:/GitHub/quill-gateway`, which the run names as staying home; the list is
never reordered.

## Walk E -- a plain folder for non-code work

Run from `C:/Work/vendor-onboarding`, a folder of meeting notes and contract
drafts with no `.git`. Not registered.

> **New or existing?** New, key `vendor-onboarding`.

**Expected.** Before writing anything, the run offers `git init` in
`C:/Work/vendor-onboarding`, saying the ledger's history lives in git.

- **Yes:** `git init` runs there, then the entry is written with that one path
  and no `ledger:` key.
- **No:** nothing is written, and the run says so. The folder is never
  registered as it is.
- **Variant:** "it has no folder, it is a programme across the wiki and Slack"
  gets the offer of a new folder named `vendor-onboarding` with `git init`.
  An entry with no paths is never written.

## Walk F -- a repository that already has a `DECISIONS.md`

Run from `C:/GitHub/lantern`, a git repository root, not registered, with no
`.daikenja/` directory. plan-staged-rollout wrote its `DECISIONS.md`:

```markdown
<!-- decisions-format: 1 -->
# Decisions

Decisions in force. Read the area that covers a path before changing it; add
or edit an entry in the same pull request when a change settles something
future work must respect.

## Release

Paths: `.github/workflows/`, `CHANGELOG.md`

- **Releases are cut from tags only, never from a branch head.** — a branch
  build once shipped unreviewed work. Revisit: never. Source: #12
```

Registered as `lantern`, then seeded from one pasted message:

> **mika** (2026-08-20) -- Settled: the public API is versioned in the path,
> never by header -- clients cache by URL. Revisit if a gateway takes over
> versioning. And as before, releases only from tags. Open question nobody
> owns yet: do we publish the API changelog separately?

**Expected.**

1. Step 4a names the existing `DECISIONS.md`: it is adopted, and seeding adds
   only what it lacks.
2. The decisions tranche, handed to `project-log`, shows one added area at the
   end of `C:/GitHub/lantern/DECISIONS.md` -- `## API` with its `Paths:` line
   and the versioning entry. The tag-only rule is a duplicate of the Release
   entry and is not re-added.
3. The open items tranche creates `C:/GitHub/lantern/.daikenja/open.md` from
   the template inside its own approval, with
   `- 2026-08-20 -- @unassigned -- Decide whether the API changelog is published separately.`
4. After both writes, the title, intro, Release area and its entry are
   byte-identical to the block above. The file is never overwritten,
   re-scaffolded or reformatted.
