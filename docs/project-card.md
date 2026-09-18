# Project card

Depends-on (reverse index -- hand-maintained, checked against SKILL.md
headings by tests/check-invariants.py):
- § Location -- project-summary "Step 0: read the contracts", setup-project "Step 3b: offer the project card", thread "Step 2b: place the thread", digest "Step 0: read the contracts"
- § Format -- project-summary "Step 0: read the contracts", setup-project "Step 3b: offer the project card", digest "Step 0: read the contracts"
- § Reading a card -- project-summary "Step 0: read the contracts", thread "Step 2b: place the thread", judgement "Step 3: place the subject", digest "Step 0: read the contracts"
- § Resolving a project by content -- thread "Step 2b: place the thread", judgement "Step 3: place the subject", digest "Step 0: read the contracts"

A project card says what a project **is about**. The registry entry in
`daikenja.yaml` says where a project is; the ledger says what was decided in
it. Neither says what the project covers, which channels and repositories
belong to it, or who is on it -- and without that, a thread, a report or a
conversation can only be checked against a project the user has already named
or is already standing in. The card is that missing surface: one short file
per project, beside the ledger, that a skill can match content against.

Three things it is not. It is not registry content -- `daikenja.yaml` stays a
file of pointers and short settings, per `config-schema.md` § Field notes, and
a paragraph of scope does not belong in it. It is not ledger content -- the
ledger's grammar in `ledger-format.md` is a frozen parsing contract, and a
card does not add a section to it. And it is not a second decision log --
nothing dated, nothing with an ID, nothing that changes when a decision lands
belongs here.

## Location

**The card sits in the ledger's directory, and its name is derived from the
ledger's.** There is no `card:` key in `daikenja.yaml` and no separate
resolution: whatever `config-resolution.md` § Finding the ledger resolves the
ledger path to, the card is beside it.

| The resolved ledger | The card |
|---|---|
| `<dir>/ledger.md` -- the default name, wherever the directory is | `<dir>/project.md` |
| `<dir>/<name>.md` -- any other file name | `<dir>/<name>.project.md` |

So a project with the default ledger keeps its card at
`.daikenja/project.md`, and a pathless project whose absolute `ledger:` is
`~/.claude/daikenja/ledgers/q4-planning.md` keeps its card at
`~/.claude/daikenja/ledgers/q4-planning.project.md`. Two projects sharing one
ledgers directory therefore never share a card, which is why the second rule
exists at all.

A project with no ledger location -- no paths and no absolute `ledger:` --
has no card location either. The skills report that per
`config-resolution.md` § Failure behavior, and nothing here changes it.

**The card is optional.** A project without one resolves, reads and logs
exactly as before. What it loses is content matching: a project with no card
cannot be found by what a thread is about, only by key or by directory. Every
skill that reads a card says when there is none, in one line, and continues.

## Format

The file is Markdown with exactly three H2 sections, in this order, all three
always present even when empty. The template is
[`../templates/project.md`](../templates/project.md).

```markdown
# harbor card

## Scope

One paragraph: what the project is about, what it delivers, what it does not
cover.

## Owns

- channel: #harbor-rollout
- repo: northwind/harbor
- tracker: HARB
- doc: https://example.com/wiki/harbor

## People

- @diablo -- rollout owner
- @benimaru -- platform lead
```

### Section: Scope

One paragraph of prose. It is what a skill compares a thread's subject against,
so it should say what the project covers **and what it does not** -- the
exclusion is what separates two projects on neighbouring ground. No bullet
list, no headings inside it, no dates.

### Section: Owns

One line per handle, `- <kind>: <handle>`. `<kind>` is one of `channel`,
`repo`, `tracker`, `doc` or `other`; `<handle>` is the name exactly as it
appears in the source system -- the `#channel` name, the `owner/repository`
slug, the tracker's project key (`HARB`), a document or space URL. These are
the **decisive** matching handles: a thread from `#harbor-rollout` belongs to
the project that owns `#harbor-rollout`, whatever its Scope says. Keep them
exact, and keep them to what this project genuinely owns -- a shared channel
listed on three cards decides nothing.

### Section: People

One line per person, `- @handle -- role`. The handle is the same `@name` the
ledger uses as an owner, so a person named on the card and a person owning an
entry are recognisably the same. People are a **supporting** match, never a
decisive one: the same people sit on several projects.

### Reading rules

1. Locate each section by its exact H2 heading. A card missing one of the
   three is reported -- name the heading -- and read for what it has.
2. HTML comments and blank lines are ignored. The template ships its guidance
   in comments so a fresh card reads as empty, not as filled.
3. An `Owns` or `People` line that does not match its shape is reported and
   skipped, never guessed at.
4. **Nothing rewrites the card.** The user edits it by hand; `setup-project`
   creates it, on approval, and never touches an existing one. A read skill
   that finds a malformed line reports it and moves on. See
   `config-writers.md` § Who writes what.

## Reading a card

A skill that has resolved a ledger path per `reading.md` § Step B resolves the
card path from it by the table above and reads the file if it exists. It is
one extra read on the same directory; no config lookup and no second
resolution.

- **Card exists.** Parse it per the reading rules. Where the skill shows it,
  the Scope paragraph leads and the Owns handles follow -- People only when
  the skill's own report has a use for them.
- **No card.** One line, then continue:

  ```
  No project card at <path>. Run /daikenja:setup-project to add one.
  ```

  A read skill never scaffolds it, for the same reason it never scaffolds a
  ledger.

The `Ledger:` line every read skill already prints is unchanged. When a card
was read, a `Card:` line with its absolute path follows it, so the user can
tell which file the scope came from.

## Resolving a project by content

`config-resolution.md` § Finding the project gives two routes: by key, and by
directory. Both start from something the user already knows. This section is
the third route, for a caller that starts from **content** -- a thread, a
report, a pasted conversation -- and has no key and no useful directory. It
is what lets `thread` place a Slack thread against the right project from any
directory, and it is designed so that a caller with no working directory at
all can use it on its own.

**It is a scan over every registered project's card**, shaped like
`project-list` § Step 2: walk the `projects:` entries in file order, resolve
each entry's ledger path per `config-resolution.md` § Finding the ledger and
its card path per § Location above, and read every card that exists. There is
no index file to maintain, and nothing is cached between runs -- the cards are
few and short, and a stale index would be a worse failure than a slow scan.
An entry with no card, or no ledger location, is simply not a candidate; the
report names it so the user knows why it could not match.

Then match the content against the cards, in this order, and stop at the
first tier that decides:

1. **Owns handles, decisive.** The content names a channel, a repository, a
   tracker key or a document that exactly one card owns -- the thread's
   channel, a `HARB-123` ticket, a repository link. That card's project is
   the match, stated as `Project: <key> (matched by #harbor-rollout)` -- or,
   in a skill whose report already carries a project line, on that line
   (`thread` says it on its `Ledger:` line). Two cards owning the same
   handle is a card problem, not a tie to break: report both keys and treat
   it as undecided.
2. **Scope and People, suggestive.** No handle decided. Compare the content's
   subject against each card's Scope paragraph, with People as a tiebreaker.
   The best fit is a **candidate**, never a match: state it as
   `Project: probably <key> -- confirm`, and let the user confirm or name
   another. A skill that goes on to read a ledger on the strength of a
   candidate says so on the `Ledger:` line.

   **A caller with no reader never asks.** A chat bot, a headless run, any
   consumer whose output lands where nobody can answer: there a candidate is
   taken as no match. No ledger is read, tier 3 below is the outcome, and the
   candidate is **offered rather than asked** -- named in the deliverable
   alongside the command that would check it, for the person to run if they
   want it. Waiting on a confirmation that cannot arrive does not produce a
   cautious answer; it produces no answer at all, and whatever the run happened
   to say while stopping is what the consumer posts in place of one.
3. **Nothing fits.** Continue without a project. It is a normal outcome --
   most conversations are not project work -- and never a stop. Whether it
   is said is the caller's call: a skill asked to resolve says so in one
   line, naming any registered project that could not be checked for want of
   a card (`No registered project matches this content. billing-api has no
   card, so it could not be checked.`); a skill that only consults this route
   on the way to something else (`thread`) stays silent, because narrating a
   non-match in the middle of another job is noise.

**Content resolution never overrides a key or a directory.** A key the user
named is decisive per `config-resolution.md`, and a directory that resolves
is the project the user is standing in. Content resolution runs only when
neither applies, or when a skill explicitly asks whether the content agrees
with the project it already has -- and in that second use a decisive handle
that points elsewhere is reported as a mismatch (`This thread is from
#atlas-dev, which belongs to atlas-migration, not to harbor`), not silently
acted on.

**It is read-only, like every read.** Resolving by content opens cards and
nothing else; it writes no config, no card and no ledger, and it never
registers a project it could not find.
