# Fixture: thread with no channel

Synthetic. Invented project, invented people, invented links. Nothing here
comes from real work. Used by the `thread` skill's acceptance checks.

Built to exercise the no-channel case in `thread` § Step 2: summarize it -- a
pasted block of three messages between two named people, with no channel
named anywhere and no link. The `🧵 **Thread**` line must still name the
subject and the people, without describing how the block arrived and without
stating that a channel is unknown.

**Acceptance criterion:** the `🧵 **Thread**` line names what the messages are
about and who is in them. It does not contain the words `pasted`, `block`,
`link`, `channel not stated` or any other statement that a channel is
unknown.

Depends on: thread "Step 2: summarize it"

---

**milim** (2026-09-10 11:02)
> Quick one -- are we still cutting the lantern-lite trial over to the new
> pricing tier this week, or has that slipped?

**veldora** (2026-09-10 11:06)
> Slipped. Finance flagged that the tier mapping is wrong for annual
> contracts, so I am holding it until that is fixed.

**milim** (2026-09-10 11:09)
> Fair enough. Ping me when it is unblocked -- I need to tell the trial
> customer something today.

**The failure this catches:** a `🧵 **Thread**` line that reads "Pasted block,
2 people, 3 messages" or "Thread (channel not stated)" instead of naming the
lantern-lite pricing-tier cutover and the two people discussing it.
