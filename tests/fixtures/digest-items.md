# Fixture: a feeder's item list, grouped and enriched

Synthetic. Invented projects, invented people, `example.com` links. Nothing
here comes from real work. Used by the acceptance checks for `digest`: placing
each item against a project, enriching the group from that project's ledger,
and rendering a block that survives the conversion to Slack's dialect.

It reuses the registry and the cards in
[`project-card.md`](project-card.md) rather than inventing a second world --
the same four projects, the same handles, and harbor's ledger exactly as that
fixture leaves it. What this file adds is the atlas ledger, the item list, and
the digest each walk should produce.

Depends on: digest "Step 2: place each item against a project", digest "Step 3: read the ledger of each matched project", digest "Step 4: render the digest", project-card.md "Resolving a project by content", ledger-format.md "Section: Open items"

---

## What the projects look like

From `project-card.md`, unchanged:

| Project | Card | Ledger |
|---|---|---|
| harbor | owns `#harbor-rollout`, `northwind/harbor`, `HARB` | two open items, `O-001` and `O-002` |
| atlas-migration | owns `#atlas-dev`, `northwind/atlas`, `ATL` | below -- no open items |
| q4-planning | owns a wiki doc only | not read by any walk here |
| billing-api | **no card** | exists, never reached |

`C:/GitHub/atlas/.daikenja/ledger.md` -- the second project's ledger, with a
Decisions section and an **empty** Open items section. This is the case that
has to render as `_No open items._` rather than as a missing line:

```markdown
## Decisions

- 2026-09-02 -- D-001 -- @priya -- Keep the legacy read replica online for 30 days after cutover. [thread](https://example.com/slack/atlas-dev/p1)

## Open items

## Context links

- Cutover runbook -- https://example.com/atlas/runbook

## Changelog

- 2026-09-02T09:04Z -- project-log -- +D-001
```

## The item list

What a feeder hands over on standard input. Eight entries: seven with a
summary, one without. Note `score` on the lunch item -- a feeder's own field,
which is dropped rather than refused.

```json
[
  {"ts": "2026-09-18T07:41:00Z", "channel": "#platform-eng", "sender": "@benimaru", "topic": "harbor", "permalink": "https://example.com/slack/platform-eng/p4", "summary": "Moving the limiter config out of env vars is back on the table."},
  {"ts": "2026-09-18T08:02:00Z", "channel": "#atlas-dev", "sender": "@priya", "permalink": "https://example.com/slack/atlas-dev/p8", "summary": "Cutover rehearsal moved to Thursday."},
  {"ts": "2026-09-18T08:14:00Z", "channel": "#harbor-rollout", "sender": "@souei", "bucket": "to:me", "permalink": "https://example.com/slack/harbor-rollout/p11", "summary": "Asked whether the ramp pauses at 25% if p99 doubles."},
  {"ts": "2026-09-18T08:09:00Z", "channel": "#harbor-rollout", "sender": "@diablo", "permalink": "https://example.com/slack/harbor-rollout/p10", "summary": "Customer comms draft is ready for review."},
  {"ts": "2026-09-18T07:55:00Z", "channel": "#payments", "sender": "@sam", "permalink": "https://example.com/slack/payments/p2", "summary": "ATL-214 needs a fallback-window cost before the review."},
  {"ts": "2026-09-18T06:30:00Z", "channel": "#random", "sender": "@shuna", "permalink": "https://example.com/slack/random/p3", "summary": "Friday lunch order.", "score": 0.02},
  {"ts": "2026-09-18T07:12:00Z", "channel": "#billing-questions", "sender": "@gabiru", "permalink": "https://example.com/slack/billing-questions/p6", "summary": "Invoice retry queue failed overnight, retried clean."},
  {"ts": "2026-09-18T08:20:00Z", "channel": "#harbor-rollout", "sender": "@souei"}
]
```

## Walk 1: the whole digest

How each item places, per `digest` Step 2:

| # | Placed on | Why |
|---|---|---|
| 1 | harbor | `topic: harbor` is a registered key. Decisive, and it beats `#platform-eng`, which no card owns. |
| 2 | atlas-migration | `#atlas-dev` is owned by exactly one card. Decisive. |
| 3 | harbor | `#harbor-rollout`. Decisive. |
| 4 | harbor | `#harbor-rollout`. Decisive. |
| 5 | atlas-migration | `ATL-214` carries the tracker key atlas-migration owns. Decisive, though the channel is not its own. |
| 6 | Unmatched | Nothing fits, and nothing should. |
| 7 | Unmatched | billing-api has no card, so it was never a candidate. |
| 8 | dropped | No summary: `Item 8 has no summary. Skipped.` on stderr, before the digest. |

Ledgers read: harbor's and atlas-migration's. q4-planning and billing-api are
never opened -- no item landed on either, and Step 3 opens a ledger only for a
project that got items.

The digest, in the markdown the skill writes:

```markdown
**Digest** -- 7 items, 2 projects, since 2026-09-18T06:30:00Z

**harbor** -- 3 items
- _to:me_ -- #harbor-rollout -- @souei -- [Asked whether the ramp pauses at 25% if p99 doubles](https://example.com/slack/harbor-rollout/p11)
- #harbor-rollout -- @diablo -- [Customer comms draft is ready for review](https://example.com/slack/harbor-rollout/p10)
- #platform-eng -- @benimaru -- [Moving the limiter config out of env vars is back on the table](https://example.com/slack/platform-eng/p4)
_Open items (2):_ Define the rollback trigger for the ramp: who pulls it and on what p99 number (O-001) -- @unassigned · Write the customer comms before Monday 2026-08-17 (O-002) -- @unassigned

**atlas-migration** -- 2 items
- #atlas-dev -- @priya -- [Cutover rehearsal moved to Thursday](https://example.com/slack/atlas-dev/p8)
- #payments -- @sam -- [ATL-214 needs a fallback-window cost before the review](https://example.com/slack/payments/p2)
_No open items._

**Unmatched** -- 2 items
- #billing-questions -- @gabiru -- [Invoice retry queue failed overnight, retried clean](https://example.com/slack/billing-questions/p6)
- #random -- @shuna -- [Friday lunch order](https://example.com/slack/random/p3)
_billing-api has no card, so it could not be checked._
```

And what the bot posts, after `mrkdwn.to_mrkdwn`. This is what the digest
actually looks like in Slack, and the two blocks must stay in step:

```
*Digest* -- 7 items, 2 projects, since 2026-09-18T06:30:00Z

*harbor* -- 3 items
• _to:me_ -- #harbor-rollout -- @souei -- <https://example.com/slack/harbor-rollout/p11|Asked whether the ramp pauses at 25% if p99 doubles>
• #harbor-rollout -- @diablo -- <https://example.com/slack/harbor-rollout/p10|Customer comms draft is ready for review>
• #platform-eng -- @benimaru -- <https://example.com/slack/platform-eng/p4|Moving the limiter config out of env vars is back on the table>
_Open items (2):_ Define the rollback trigger for the ramp: who pulls it and on what p99 number (O-001) -- @unassigned · Write the customer comms before Monday 2026-08-17 (O-002) -- @unassigned

*atlas-migration* -- 2 items
• #atlas-dev -- @priya -- <https://example.com/slack/atlas-dev/p8|Cutover rehearsal moved to Thursday>
• #payments -- @sam -- <https://example.com/slack/payments/p2|ATL-214 needs a fallback-window cost before the review>
_No open items._

*Unmatched* -- 2 items
• #billing-questions -- @gabiru -- <https://example.com/slack/billing-questions/p6|Invoice retry queue failed overnight, retried clean>
• #random -- @shuna -- <https://example.com/slack/random/p3|Friday lunch order>
_billing-api has no card, so it could not be checked._
```

What must not happen:

- **atlas-migration losing its `_No open items._` line.** An empty section is
  information. A project that silently drops the line reads exactly like one
  whose ledger was never opened.
- **harbor's `- [x] ` items appearing.** There are none in this fixture, and
  when there are, Step 3 reads `- [ ] ` only.
- **The Decisions sections appearing.** Both ledgers have one. Neither belongs
  in a digest.
- **billing-api's ledger being read.** It has one, and no card. Reading it
  because the invoice item mentions invoices is the tier-2 mistake Walk 2 is
  about.
- **Any absolute path in the block.** Not `C:/GitHub/harbor/.daikenja/ledger.md`,
  not a shortened form of it.

## Walk 2: a near miss is not a match

Replace item 7 with one that has no channel and no ticket:

```json
{"ts": "2026-09-18T07:12:00Z", "sender": "@gabiru", "permalink": "https://example.com/slack/p6", "summary": "The invoice retry queue backed up again overnight."}
```

No handle decides. billing-api is the project it is *about* -- but billing-api
has no card, so there is nothing to compare against and it is not even a
candidate. The item is unmatched, and the closing line still says why
billing-api could not be checked.

Now give billing-api a card whose Scope names the invoice retry queue. Tier 2
now has a near miss. It still is **not** a match: nobody is reading the digest
live, so per `project-card.md` § Resolving a project by content the candidate
degrades to no match. Expected under Unmatched:

```markdown
- @gabiru -- [The invoice retry queue backed up again overnight](https://example.com/slack/p6)
_billing-api nearly fits the invoice item -- say `@daikenja summary project billing-api` to check it._
```

What must not happen: billing-api's ledger being read, the item appearing under
a `**billing-api**` group, or the digest asking "should I check this against
billing-api?" -- there is nobody there to answer, and the question would be
posted as the digest.

## Walk 3: a topic that names no project

Item 1 again, with `"topic": "harbour-rollout"` -- a plausible typo that
matches no registered key.

The topic decides nothing and is not treated as a project. The item falls
through to the next tier, where `#platform-eng` is owned by no card, and then
to Scope, where harbor's Scope names the limiter configuration -- a near miss,
not a match. So the item is **unmatched**, with the offer line naming harbor.

What must not happen: a `**harbour-rollout**` group appearing in the digest.
A group named after a key that does not exist is worse than no group: it looks
like a project the reader has forgotten about.

## Walk 4: nothing matches at all

Every item is from `#random` and names no handle any card owns.

The digest is still posted: one `**Unmatched**` group with every item, no
project groups, and the header reading `**Digest** -- 5 items, 0 projects,
since ...`. Nothing matching is information, not a failure, and a feeder that
collected five items deserves to see them.

What must not happen: an empty digest, or a run that stops with "no project
matched" and posts nothing.
