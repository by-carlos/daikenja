# Fixture: self-review thread

Synthetic. Invented project, invented people, invented links, invented
incident. Nothing here comes from real work, and no participant is a real
person. Used by the `self-review` skill's acceptance checks.

Built so the invoker (`carlos`) makes identifiable mistakes at all three
severity tiers, including one that misled others into acting on a wrong fact,
and enough of them in total to exercise the findings cap and the parked
remainder.

---

**#quill-search** -- 14 messages, 2026-08-11 09-14 to 2026-08-11 18-02

**mina** (2026-08-11 09:14)
> Morning. The quill reindex finished overnight but the result counts look
> about double what they were last week. Is that expected?

**carlos** (2026-08-11 09:21)
> The reindex is idempotent, re-running it is free. Counts should settle once
> the cache expires. Nothing to worry about.

**mina** (2026-08-11 09:26)
> Ok. I will re-run it on the staging index then, that one still looks stale.

**priya** (2026-08-11 09:40)
> Before anyone re-runs anything -- who signs off the rollback if the counts
> are actually wrong? I want a name.

**carlos** (2026-08-11 09:44)
> The rollback script is in the runbook, it is a single command.
> https://example.com/quill/runbook

**priya** (2026-08-11 09:47)
> That is not what I asked. Who makes the call to run it?

**carlos** (2026-08-11 09:52)
> It has been tested twice, it works fine.

**mina** (2026-08-11 11:38)
> Staging is now showing triple counts. I re-ran it twice because the first run
> did not look like it did anything. This is not idempotent.

**carlos** (2026-08-11 11:55)
> Looking.

**priya** (2026-08-11 12:10)
> @carlos we need a decision on whether the freeze window still starts
> 2026-08-12. Blocking on you.

*(no reply from carlos between 12:10 and 17:05)*

**priya** (2026-08-11 16:58)
> @carlos still waiting on the freeze window call. Anyone home?

**carlos** (2026-08-11 17:05)
> Ok so I have been through the ingest path. The reindex appends into the
> document table instead of upserting, which is why every run adds another
> copy of every document. It has probably been doing this since the schema
> change on 2026-08-04, which also explains the odd relevance scores people
> were seeing last week and the disk growth alert that fired on Saturday. I
> have pulled the job from the scheduler so nothing else runs against it. The
> counts on staging will need a truncate and a single clean run, which I can
> do tonight if nobody objects, and the production index is going to need the
> same treatment but I would rather do that one with someone watching. If
> anyone had actually read the runbook before re-running things we would not
> be cleaning up three copies of staging right now. Anyway, does the freeze
> window still start tomorrow or not?

**dev** (2026-08-11 17:22)
> That is a lot to unpack. What do you need from us?

**carlos** (2026-08-11 17:31)
> The platform team can have the new cluster ready by Thursday, so we could
> just reindex onto that instead and leave this one alone.

**priya** (2026-08-11 18:02)
> Have platform agreed to Thursday? Also I still do not have an answer on the
> freeze window.

*(thread ends here -- no further replies)*
