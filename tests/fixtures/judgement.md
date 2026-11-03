# Fixture: judgement -- a thread, a document and a ledger that contradicts them

Synthetic. Invented project, invented people, `example.com` links. Nothing
here comes from real work. Used by the acceptance checks for `judgement`: the
`answer` form on a thread, the `message` form on a document, the no-match
case, the bare invocation with nothing to work on, the `message` form's own
no-match case (its `📒 Ledger` section must be absent, not apologetic), a
subject that quotes a fenced config snippet, which the message form must
never carry a fence out into, and the two unreadable-data states, where the
`message` form gives a fixed token and no verdict.

The project is `ember`, a reporting warehouse for a booking platform. Its
ledger records the storage engine and the load window; the thread and the
document below each run against one of those, and each also carries a claim
the ledger says nothing about, so the general-knowledge label has something
to attach to.

Depends on: judgement "Step 1: get the subject and the form", judgement "Step 3: place the subject", judgement "Step 4: check the claims", judgement "Step 5: report", judgement "Voice in the message form", project-card.md "Resolving a project by content", config-resolution.md "Voice and writing style"

---

## The registry

```yaml
profile:
  name: rimuru
  tone: standard
  writing_style: ./writing-style.md

projects:
  ember:
    path: C:/GitHub/ember

  billing-api:
    path: C:/GitHub/billing-api
```

`billing-api` has a `C:/GitHub/billing-api/DECISIONS.md` but no card. `writing-style.md` exists and asks for a "Hi all," greeting and
US spelling -- it is here so the `message` walk can show it being ignored.

## The card

`C:/GitHub/ember/.daikenja/project.md`:

```markdown
# ember card

## Scope

Ember is the reporting warehouse for the booking platform. It covers the
warehouse store, the nightly load from the booking database and the retention
of loaded data; it does not cover the booking database itself or the
dashboards built on top of the warehouse.

## Owns

- channel: #ember-warehouse
- repo: northwind/ember
- tracker: EMB
- doc: https://example.com/ember/design

## People

- @gabiru -- warehouse lead
- @hakurou -- platform engineer
- @shion -- analytics
```

## The ledger

`C:/GitHub/ember/DECISIONS.md`:

```markdown
<!-- decisions-format: 1 -->
# Decisions

Decisions in force. Read the area that covers a path before changing it; add
or edit an entry in the same pull request when a change settles something
future work must respect.

## Warehouse

Paths: `.`

- **The warehouse store is PostgreSQL 16, not SQL Server.** — the analytics
  team's tooling targets PostgreSQL. Revisit: never. Source: [design](https://example.com/ember/design)
- **The nightly load runs between 02:00 and 04:00 UTC.** — agreed with the
  platform on-call rota. Revisit: if the rota changes. Source: [thread](https://example.com/slack/ember-warehouse/p2)
```

`C:/GitHub/ember/.daikenja/open.md`:

```markdown
<!-- daikenja-open-format: 1 -->
# ember open items

## Open items

- 2026-09-03 -- @unassigned -- Name an owner for the historical backfill of the 2025 bookings.
- 2026-08-20 -- @shion -- Decide the retention period for loaded data: 90 days is proposed, nothing agreed.

## Context links

- Ember design page -- https://example.com/ember/design

## Sources

- Ember design page -- https://example.com/ember/design
  read: 2026-08-20
```

## Subject A: the thread

**#ember-warehouse** -- 4 messages

**gabiru** (2026-09-15 10:02)
> Quick check before I brief the dashboard team: are we going with SQL Server
> for the warehouse in the end? And if so, can we host the old Oracle reporting
> schema inside it so we skip the rewrite?

**hakurou** (2026-09-15 10:07)
> I thought SQL Server was the plan, yes. Not sure about hosting Oracle in it,
> never tried.

**shion** (2026-09-15 10:11)
> Either way the 90-day retention is settled, so the dashboards can assume it.

**gabiru** (2026-09-15 10:14)
> Good. I will tell them 90 days and SQL Server unless someone objects today.

## Subject B: the document

Pasted from `https://example.com/wiki/ember-load-schedule`, titled **Ember
load schedule**:

> The nightly load runs from 01:00 to 03:00 UTC, as agreed with the platform
> team. Loaded data is kept for 90 days, per the company data-retention
> standard. The backfill of 2025 bookings is owned by the analytics team and
> starts once the schedule is confirmed. Loads use `COPY` into partitioned
> tables, which is the fastest bulk path PostgreSQL offers.

## Subject C: a thread with no project

Pasted from `C:/GitHub/scratch`, no channel header:

**ranga** (2026-09-16 15:40)
> The invoice retry queue keeps re-sending the same invoice three times. Is
> that the queue's at-least-once delivery, or a bug on our side?

## Subject D: a document quoting a config snippet

Pasted from `https://example.com/wiki/ember-cron`, titled **Ember load cron
config**:

> The nightly load's cron entry is:
> ```
> 0 1 * * * /opt/ember/run-load.sh
> ```
> which runs the job at 01:00 UTC daily. Retries are configured with
> `max_attempts: 3` and `backoff: exponential`.

---

## Walk 1: the `answer` form on Subject A, from an unrelated directory

`/daikenja:judgement` from `C:/GitHub/scratch`, with Subject A as the most
recent pasted block in the session. No form named, so `answer`.

- No key was named and the directory resolves nothing. Content resolution
  runs: `#ember-warehouse` is owned by exactly one card, `ember`. Decisive.
- Ember's `DECISIONS.md`, its `open.md` and the card are read. Every
  `DECISIONS.md` entry is in force; there are no IDs to cite.
- The ledger check runs first: gabiru's question is answered by the
  storage-engine decision, and shion's "settled" claim is an open item.

Expected reply, and nothing before it:

```
Thread: #ember-warehouse, 4 messages
Asking: gabiru wants to confirm the warehouse engine and whether the Oracle
reporting schema can be hosted inside it, before briefing the dashboard team
today.
Open: whether anyone objects before end of day; nothing else is put to the
group.
Ledger: ember, matched by #ember-warehouse (C:/GitHub/ember/DECISIONS.md, C:/GitHub/ember/.daikenja/open.md)
Card: C:/GitHub/ember/.daikenja/project.md

Verdict: The warehouse is PostgreSQL 16, not SQL Server -- the storage-engine
decision (ember) records PostgreSQL 16, not SQL Server. SQL Server
and Oracle are two different database engines; one cannot host the other's
schema as it stands -- certain, general knowledge. The 90-day retention is not
settled: the retention question (open item) is still open with 90 days proposed.

1. gabiru's and hakurou's assumption that SQL Server is the plan contradicts
   the storage-engine decision (ember) -- certain. Source: ledger.
2. Hosting an Oracle schema inside SQL Server is not possible as asked;
   moving it means a migration of the schema and its objects, which is the
   rewrite gabiru hoped to skip -- certain. Source: general knowledge.
3. shion presents the 90-day retention as settled; the ledger has it as
   proposed and undecided (open item) -- certain. Source: ledger.

Suggested: brief the dashboard team on PostgreSQL 16 and say retention is
still open, rather than 90 days.
Not checked: whether a later thread changed the storage-engine decision; the dashboard team's own
requirements; the ember design page was not re-read.
```

**The failures this catches:** answering "SQL Server" because two people in
the thread said so; stating the Oracle fact without its `general knowledge`
label, so it reads as a ledger fact; and carrying "90 days" forward as
settled because the thread did.

## Walk 2: the `message` form on Subject B

`/daikenja:judgement message` from `C:/GitHub/ember`, with Subject B as the
most recent pasted block.

- The directory resolves `ember`. The content cross-check finds no handle
  pointing elsewhere (the page URL is not on any card; that is not a
  mismatch).
- `writing_style` is **not read**: the form is voice-only, per `judgement`
  § Voice in the message form. The message carries no "Hi all," and uses the
  shipped Commonwealth spelling, whatever `writing-style.md` asks for. No
  notice about `writing-style.md` appears anywhere in the reply.
- The ledger check: the load window contradicts the nightly load window
  decision; the retention claim is presented as settled and is an open item;
  the backfill owner claim is an open item, unassigned.
- The "company data-retention standard" is named by the page but not linked
  by it, and the Sources of `open.md` carry no such link. It is named and marked
  `link needed`, never given a URL.

Expected reply: two report lines, then the message in its own fenced block.
The report lines are conversation and carry whatever register the user has
installed; the fenced block carries none.

Report lines:

```
Ledger: ember (C:/GitHub/ember/DECISIONS.md, C:/GitHub/ember/.daikenja/open.md)
Card: C:/GitHub/ember/.daikenja/project.md
For your judgement: the page names a company data-retention standard that
neither it nor the ledger links. Add the link before sharing if you know it.
```

The message, exactly as handed back, about 150 words:

```
AI review summary
Subject: Ember load schedule (wiki page, pasted 2026-09-16)
- Ledger: the page's load window, 01:00 to 03:00 UTC, contradicts the
  nightly load window decision (ember): 02:00 to 04:00 UTC, agreed with the
  platform on-call rota. Certain.
- Ledger: the page states a 90-day retention as settled. The retention
  question (open item) is still open, with 90 days proposed. Certain.
- The page names the analytics team as backfill owner. The backfill owner
  item (open item) is unassigned. Likely a claim ahead of a decision. Source:
  ledger.
- The page cites a company data-retention standard with no link (link
  needed). Not verified.
- COPY into partitioned tables as PostgreSQL's fastest bulk load path holds
  as stated. Certain. Source: general knowledge.
- Suggested: correct the load window to 02:00 to 04:00 UTC and mark retention
  and backfill ownership as open until the ledger records them.
- Not checked: the on-call rota, the retention standard's text, and whether
  the page changed after it was pasted.
```

**The failures this catches:** a greeting or the user's own phrasing leaking
into a message headed as an AI pass; a constructed URL for the standard; the
backfill line hedged into "may or may not be owned" instead of a stated
confidence plus a labelled source; the load window buried under the two
softer findings instead of leading.

## Walk 3: no project resolves on Subject C

`/daikenja:judgement` from `C:/GitHub/scratch`, with Subject C as the most
recent pasted block.

- No key, no directory match. Content resolution: no handle; ember's Scope
  is a reporting warehouse and does not fit an invoice retry queue;
  `billing-api` has no card and cannot be checked.
- This skill resolves outright, so the non-match is said, and the verdict
  continues on general knowledge alone.

Expected reply:

```
Thread: pasted, 1 message
Asking: ranga wants to know whether an invoice being sent three times is the
queue's delivery guarantee or a bug.
Open: which it is.
No registered project matches this content. billing-api has no card, so it
could not be checked.

Verdict: No ledger was checked. A queue with at-least-once delivery will
redeliver a message the consumer did not acknowledge, so three deliveries of
one invoice is consistent with that guarantee and a consumer that is not
idempotent -- likely, general knowledge. Whether the queue in question is
configured that way is not something this check can tell.

1. The ledger check did not run: no project resolved. Source: none.
2. At-least-once delivery redelivers on a missing acknowledgement; the fix on
   the consumer side is idempotent handling keyed on the invoice -- likely.
   Source: general knowledge.

Suggested: check the queue's delivery setting and the consumer's
acknowledgement path before calling it a bug.
Not checked: the queue's actual configuration; billing-api's ledger, which
could not be matched.
```

**The failures this catches:** reading `billing-api`'s ledger because it is
the only other project, or `C:/GitHub/scratch`'s non-existent one; dropping
the non-match line so the reply looks like a project was checked; and a
verdict that hides behind "it depends" instead of stating a labelled,
confidence-carrying answer.

## Walk 4: bare invocation with nothing to work on

A fresh session, no link and no pasted block, `/daikenja:judgement`.

- Nothing in the session qualifies as a subject. The skill asks for a link, a
  path or a paste, in one line, and stops.

What must not happen: searching Slack or the working tree for something to
judge, or picking the most recent file the user edited.

## Walk 5: the `message` form on Subject C

`/daikenja:judgement message` from `C:/GitHub/scratch`, with Subject C as the
most recent pasted block.

- Same non-match as Walk 3: no key, no directory match, and no handle in the
  content. `billing-api` has no card and cannot be checked.
- This is the `message` form, so the `📒 **Ledger**` section is omitted
  entirely -- not a bullet saying no ledger was checked, absent. Why
  resolution failed goes in the short report around the message, never
  inside it.

Expected report line, then the message in its own fenced block:

Report line:

```
No registered project matches this content. billing-api has no card, so it
could not be checked.
```

The message, exactly as handed back:

```
⚖️ **Verdict**
The invoice retry queue re-sending the same invoice three times is consistent
with at-least-once delivery redelivering an unacknowledged message to a
consumer that is not idempotent -- likely, general knowledge. Whether the
queue is configured that way is not something this check can tell.

🔍 **Basis**
- **At-least-once redelivery** -- a message is redelivered when the consumer
  never acknowledges it; the fix on the consumer side is idempotent handling
  keyed on the invoice, not a change to the queue. _likely · general
  knowledge_

💡 **Suggestion**
- Check the queue's delivery setting and the consumer's acknowledgement path
  before calling it a bug.

🚧 **Not checked**
- The queue's actual configuration, and whether any registered project's
  records cover this repository.
```

**Acceptance criterion:** the message has no `📒 **Ledger**` section at all. It
does not contain the words `no ledger`, `no project resolved` or `could not be
checked`. The reason the project did not resolve appears in the short report
around the message, not in the message.

**The failure this catches:** a `📒 **Ledger**` section that reads "no ledger
was checked" instead of being left out, or a `Not checked` line that repeats
"could not be checked" inside the deliverable a cold reader receives.

## Walk 6: the `message` form on Subject D, a quoted config snippet

`/daikenja:judgement message` from `C:/GitHub/ember`, with Subject D as the
most recent pasted block.

- The directory resolves `ember`. The ledger check runs as in Walk 2: the
  page's cron entry runs the load at 01:00 UTC, which contradicts the load
  window decision (ember: 02:00 to 04:00 UTC).
- The page itself quotes the cron line inside a fenced block. The message
  form never nests a fence inside the deliverable it hands back -- it quotes
  the cron entry as inline code, on one line, with single backticks.

Expected reply: the report lines, then the message in its own fenced block.

Report lines:

```
Ledger: ember (C:/GitHub/ember/DECISIONS.md, C:/GitHub/ember/.daikenja/open.md)
Card: C:/GitHub/ember/.daikenja/project.md
```

The message, exactly as handed back:

```
⚖️ **Verdict**
The page's cron entry runs the nightly load at 01:00 UTC, which contradicts
the load window decision (ember): 02:00 to 04:00 UTC, agreed with the
platform on-call rota. Certain.

🔍 **Basis**
- **Load window** -- the cron entry `0 1 * * * /opt/ember/run-load.sh` starts
  the job an hour before the agreed window opens. _certain · ledger,
  nightly load window (ember)_
- **Retry configuration** -- `max_attempts: 3` with exponential backoff is a
  reasonable retry policy for a scheduled load and is not covered by any
  decision. _likely · general knowledge_

💡 **Suggestion**
- Correct the cron entry to start the job inside the agreed window.

🚧 **Not checked**
- Whether the retry policy has ever triggered, and the platform on-call
  rota's own record of the agreed window.
```

**Acceptance criterion:** the posted message contains no ``` line anywhere,
and the page's cron entry appears in the `🔍 **Basis**` bullet named or
restated inline -- as prose or as inline code -- never inside its own fenced
block, per `judgement` § the `message` form's no-fence rule.

**The failure this catches:** the message copying the page's fenced cron
snippet verbatim into the deliverable, or wrapping its own quoted line in a
fresh triple-backtick block, either of which breaks out of the fence the
message is itself handed back inside.

## Walk 7: the `message` form on a project that needs migration

`/daikenja:judgement message project ember` with Subject B, after ember's
files are replaced by the old single-file ledger:
`C:/GitHub/ember/.daikenja/ledger.md` exists and
`C:/GitHub/ember/.daikenja/open.md` does not.

- The key resolves `ember`. The legacy check of `reading.md` § Step B runs
  first: an old ledger at home with no `open.md` beside it needs migration.
  Nothing is read -- not the old ledger, not a `DECISIONS.md`.
- This is the `message` form, so there is no verdict. The deliverable is the
  fixed token line alone.

Report line:

```
The ledger at C:/GitHub/ember/.daikenja/ledger.md needs migration -- run /daikenja:setup-user.
```

The message, exactly as handed back:

```
DAIKENJA-PROJECT-DATA-UNREADABLE ember needs-migration
```

The same project in the `answer` form gives the report line and stops.

## Walk 8: the `message` form on a newer format version

`/daikenja:judgement message` from `C:/GitHub/ember`, with Subject B, after
the first line of ember's `DECISIONS.md` reads `<!-- decisions-format: 2 -->`.

- The directory resolves `ember`, and the version line is newer than this
  plugin knows, per `open-format.md` § Version line.
- The `message` form gives no verdict over data it may misread.

Report line:

```
C:/GitHub/ember/DECISIONS.md was written by a newer format (version 2); update the Daikenja plugin.
```

The message, exactly as handed back:

```
DAIKENJA-PROJECT-DATA-UNREADABLE ember newer-format
```

The same subject in the `answer` form warns once and gives the Walk 2 verdict.

**The failures these catch:** a normal-looking verdict posted into a channel
for a project whose ledger was never read or could be misread, and a token
written with words around it, which a caller matching the line misses.
