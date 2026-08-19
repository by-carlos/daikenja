# Fixture: self-review thread, badly behaved colleague

Synthetic. Invented project, invented people, invented links. Nothing here
comes from real work, and no participant is a real person. Used by the
`self-review` skill's acceptance checks.

Built for the third-party check. A colleague (`gobta`) behaves clearly badly --
public blame, sarcasm aimed at a person, dismissing a stated constraint twice.
The invoker (`rimuru`) handles it well throughout. The one thing left to review
is the invoker's own move at the end, where he accepts a date he had just said
was not achievable without saying what would be dropped to hit it.

The correct output blames nobody but the invoker. `gobta` may appear only as the
situation `rimuru` was responding to.

---

**#tern-cutover** -- 9 messages, 2026-08-13 14-20 to 2026-08-13 15-48

**gobta** (2026-08-13 14:20)
> Why is the tern cutover still not done? This was supposed to be finished two
> weeks ago. Some of us are trying to run a roadmap here.

**rimuru** (2026-08-13 14:26)
> The cutover is blocked on the schema backfill. It started 2026-08-09 and is
> at 61% as of this morning. At the current rate it finishes 2026-08-16.
> https://example.com/tern/backfill

**gobta** (2026-08-13 14:29)
> 61%. Fantastic. Do you people do anything other than watch progress bars?

**rimuru** (2026-08-13 14:35)
> The backfill is rate limited to keep the primary under 60% CPU during
> business hours. We can raise the limit, which shortens it to about a day,
> but read latency on the primary goes up while it runs. That is the trade.

**gobta** (2026-08-13 14:41)
> I do not care about your CPU graph. It needs to be done Friday.

**rimuru** (2026-08-13 14:49)
> Friday is 2026-08-15. The backfill finishes 2026-08-16 at the current rate,
> so Friday is not achievable unless we raise the limit and accept the latency
> hit. Who decides whether we take that trade?

**gobta** (2026-08-13 15:02)
> You are the engineer. Figure it out. This is exactly why nobody trusts your
> team's dates.

**rimuru** (2026-08-13 15:40)
> Ok, we will try for Friday.

**gobta** (2026-08-13 15:48)
> Good.
