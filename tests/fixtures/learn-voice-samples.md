# Fixture: learn-voice samples

Synthetic. Invented people, invented projects, `example.com` links only.
Nothing here comes from real work content, and no participant is a real person.
Used by the `learn-voice` skill's acceptance checks.

The invoker is `rimuru`, the same user as the `self-review` fixtures. Everything
below that carries their name is the corpus; everything else is context for what
they were answering and must never reach the output.

Four walks over one corpus:

- **Walk A** -- the whole corpus, against a `writing-style.md` that is still the
  shipped template byte for byte.
- **Walk B** -- a block whose authorship cannot be separated. Must refuse.
- **Walk C** -- the DM block alone. Under the floor, so nothing is derived.
- **Walk D** -- Walk A again, against a `writing-style.md` the user has since
  written a line into. Must diff.

The corpus is deliberately sized between the floor and the bar -- 33 messages of
rimuru's own, 4 sources, 3 audiences, 12 May to 18 August 2026 -- so a run has
to take the middle branch of Step 2 and say the corpus is thin rather than
claiming full confidence.

Traits are seeded so a run can be marked. Six must appear in the file, four
exercise the `Fixed`-rule check in `docs/voice.md`, and two must not be recorded
at all.

Depends on: learn-voice "Step 1: get the samples, and settle authorship", learn-voice "Step 2: check the corpus is enough", learn-voice "Step 3: pass 1 -- evidence", learn-voice "Step 4: pass 2 -- synthesis", learn-voice "Step 5: resolve the file and read what is there", voice.md "Fixed", voice.md "Spelling variant", voice.md "Length"

---

## Source 1 -- `#harbor-rollout`, broad channel, peers

**rimuru** (2026-05-12 09:02)
> Quick one -- the harbor reindex is on the schedule for tomorrow. Anyone
> depending on the old document IDs?

**benimaru** (2026-05-12 09:11)
> The search page still reads them. How long is the window?

**rimuru** (2026-05-12 09:15)
> About forty minutes. I would rather run it tomorrow morning than at the end
> of the week, unless you feel strongly.

**rimuru** (2026-05-14 11:40)
> The reindex finished. Counts are where I expected them. Worth knowing that
> the staging index is still on the old schema, so do not compare the two.

**shion** (2026-05-14 11:52)
> Is that going to bite us at the cutover?

**rimuru** (2026-05-14 11:58)
> Not if we migrate staging first. I will do that Wednesday 20 May.

**rimuru** (2026-06-02 08:30)
> Quick one -- who owns the gateway certificate renewal now? I want a name
> before the expiry, not after.

**rimuru** (2026-06-02 14:22)
> Three things came out of the review, so bullets rather than a paragraph:
>
> - The ingest path retries twice, and nobody knew that.
> - The dashboard reads a cached count, so it lags by an hour.
> - We have no alert on the queue depth at all.
>
> I will take the third one. The other two need an owner.

**rimuru** (2026-06-11 10:05)
> This blocks the release. The schema change has to land before the freeze on
> Monday 15 June or the freeze slips.

**rimuru** (2026-06-11 10:07)
> For what it is worth I think we can still make it, it is one migration.

**rimuru** (2026-06-24 16:41)
> I got that wrong. The retry count is three, not two. Sorry, I read the old
> config.

**rimuru** (2026-07-03 09:12)
> Quick one -- is anyone actually using the legacy export endpoint? I would
> rather delete it than keep testing it.

**rimuru** (2026-07-03 09:44)
> No, I do not think we should postpone it again. We have postponed it twice
> and the reason has not changed. Let me know if that is wrong.

**rimuru** (2026-07-10 15:26)
> Where the migration stands, four things, so bullets again:
>
> - Staging is on the new schema and stable since Wednesday 8 July.
> - Production is not, and will not be until the freeze lifts.
> - The rollback script has been tested once, on staging only.
> - Nobody has claimed the certificate renewal. Still.
>
> None of that is urgent this week except the last one.

**rimuru** (2026-07-28 13:05)
> The staging index is DOWN again and this is the third time this week!! I am
> not spending another afternoon on this one.

**rimuru** (2026-07-29 08:48)
> Quick one -- I am going to put the legacy export endpoint on the back burner
> until next Tuesday. Nobody has claimed it and I would rather finish the
> gateway work first.

## Source 2 -- DMs with `benimaru`, one-to-one, peer

**rimuru** (2026-05-19 17:20)
> Quick one -- did the platform team ever answer on the Thursday slot?

**benimaru** (2026-05-19 17:26)
> Not yet. I will chase them.

**rimuru** (2026-05-19 17:28)
> Thanks. No rush, it only matters if we are still doing the cutover that week.

**rimuru** (2026-06-05 12:03)
> I have been staring at this migration for two hours and the bug was a typo in
> my own config. Not my finest morning.

**rimuru** (2026-06-05 12:04)
> Anyway it works now.

**rimuru** (2026-07-09 08:55)
> Worth knowing before the standup -- the queue alert fired overnight and it was
> a real one. I have the numbers, I will bring them.

**rimuru** (2026-07-09 09:30)
> I would rather you took the ingest half and I took the gateway half, unless
> you would rather swap. Either is fine.

**rimuru** (2026-08-04 14:12)
> That is a fair point and I had not thought about the replica lag. Let me redo
> the estimate.

**rimuru** (2026-08-04 15:47)
> Redone. It is closer to ninety minutes than forty. I will say so in the
> channel rather than quietly changing the number.

**rimuru** (2026-08-04 15:52)
> Done. Same number in the channel, with the reason.

## Source 3 -- `#platform-announce`, announcement, leadership reads this

**rimuru** (2026-06-18 09:00)
> Hi all -- the harbor gateway moves to the new cluster on Tuesday 23 June,
> 08:00 to 10:00 UTC. Search will be read-only for that window. Nothing else is
> affected. Details and the rollback plan are in the runbook,
> https://example.com/harbor/runbook
>
> Thanks,
> rimuru

**rimuru** (2026-06-23 10:14)
> Hi all -- the move is done and search is writable again. We finished forty
> minutes early. No rollback was needed.
>
> Thanks,
> rimuru

**rimuru** (2026-07-21 09:00)
> Hi all -- one change to how we organize the release calendar. From Monday
> 27 July the freeze window starts a day earlier, so the last merge is the
> Friday before. This came out of the June slip, and the reasoning is written up
> at https://example.com/harbor/release-calendar
>
> Thanks,
> rimuru

**rimuru** (2026-08-11 09:00)
> Hi all -- short version first, because this got long. The ingest job
> duplicated documents for a week, the cause is fixed, and nothing was lost. The
> full write-up, including what we are changing so it cannot happen again, is at
> https://example.com/harbor/postmortem-ingest
>
> Thanks,
> rimuru

**rimuru** (2026-08-18 09:00)
> Hi all -- the color scheme on the status dashboard changed this morning. Same
> data, clearer thresholds. No action needed.
>
> Thanks,
> rimuru

## Source 4 -- mail to `souei` at a supplier, cross-organization

**rimuru** (2026-07-15 11:02)
> Hi Souei,
>
> Quick one before I raise a ticket. Our gateway sees a 30-second timeout on
> your bulk endpoint, but only over about 5,000 records. Smaller batches are
> fine.
>
> Is 5,000 a documented limit, or is this something on our side? I would rather
> ask than guess.
>
> Thanks,
> rimuru

**rimuru** (2026-07-15 16:40)
> Hi Souei,
>
> Thanks, that explains it. We will batch at 2,000.
>
> One more thing while I have you. The retry guidance in your documentation says
> to back off exponentially, and the example does not. Worth fixing, it cost me
> an afternoon.
>
> Thanks,
> rimuru

**rimuru** (2026-08-06 09:18)
> Hi Souei,
>
> Following up on the batch limit. We have been at 2,000 for three weeks with no
> timeouts, so this is closed from our side.
>
> Thanks,
> rimuru

**rimuru** (2026-08-06 09:20)
> Hi Souei,
>
> Sorry, ignore the ticket number in my last mail, I pasted the wrong one. It is
> HAR-4471.
>
> Thanks,
> rimuru

**rimuru** (2026-08-14 10:33)
> Hi Souei,
>
> We are planning the next volume increase for Monday 24 August. Nothing needed
> from you unless 4x the current rate is a problem. Say so by Thursday
> 20 August if it is.
>
> Thanks,
> rimuru

## Excluded on sight -- drafted by Daikenja

The user supplies this one with the rest and says Daikenja wrote it. It has to
be left out, and the run has to say so.

**rimuru** (2026-08-12 15:10)
> Hi all -- the ingest job is paused while we confirm the fix. One idea per
> sentence, no action needed from anyone today. I will update this thread by
> 17:00 UTC on Thursday 13 August.

---

## What a Walk A run must produce

Six traits belong in the proposed file:

1. **Openers.** `Quick one --` opens 5 of the 14 chat messages that start a
   thread, and one mail carries the same opener without the dash
   (2026-07-15 11:02). It never appears in an announcement. Stable enough to
   write, and register-specific enough to be marked as such.
2. **Greetings and sign-offs split by register.** No greeting at all in chat, and
   `Hi all --` / `Hi <name>,` with `Thanks,` in announcements and mail. The
   general rule is the split, not either half.
3. **Bullets past three items, prose below.** Both messages that list more than
   three things use bullets and say so as they do it (2026-06-02 14:22,
   2026-07-10 15:26). Every shorter message is prose. Two instances is a
   conditional frequency, not a habit counted against the whole corpus, and the
   file has to say which.
4. **Softening and sharpening.** Softens with `I would rather X, unless you feel
   strongly` and `Let me know if that is wrong`. Sharpens by stating the
   consequence first and flat -- `This blocks the release.`
5. **US spelling** (`organize`, `color`), held consistently. A real override of
   the Commonwealth default in `docs/voice.md` § Spelling variant.
6. **Summary-first past roughly 120 words**, then a link
   (2026-08-11 09:00). A replaceable override of § Length.

Two more are legitimate extra sections if the evidence is stated honestly:

- **Humor.** Two instances in 33 messages, both self-deprecating, both in DM. A
  run that describes this user as funny has over-read the corpus.
- **Habits to watch.** `Sorry` opens two mails that do not need it, and
  `For what it is worth I think` hedges a sentence that was already correct.

## What a Walk A run must observe and leave out

These are seeded in the corpus above. Each must be reported in the chat summary
as seen but not written, because `docs/voice.md` fixes it:

| Seeded where | Why it stays out |
|---|---|
| `is DOWN again` and `this week!!` (2026-07-28 13:05) | `Fixed` -- no shouting. Capitals and stacked exclamation marks for emphasis are the clearest habit in the corpus and the file cannot carry it |
| `until next Tuesday` (2026-07-29 08:48), `that week`, `the Friday before` | `Fixed` -- absolute dates. The corpus carries plenty of absolute ones too, and only those may be described |
| `on the back burner` (2026-07-29 08:48) | `Fixed` -- an idiom a reader cannot decode from its words, and `docs/voice.md` names this one |
| `it cost me an afternoon`, `not my finest morning` | Neither is a finding. They sit inside the substitution floor, so a run must not report them as habits to remove either |

## What must not be recorded at all

- **`harbor`, `quill`, `gateway`, `reindex`, `ingest`.** They recur in nearly
  every message and they are the user's work, not their voice. A run that lists
  them under `## Words and phrasings I use` has recorded facts about a project.
- **Anything about `benimaru`, `shion` or `souei`.** They are context for what
  the user was answering. No observation about any of them belongs in the file
  or in the chat report, including that the user writes differently to them.

---

## Walk B -- authorship cannot be separated

Supplied as "our rollout notes, I wrote most of this". Three people edited it
over two weeks and no line carries an author. The run must refuse, name what
would make it usable, and derive nothing:

> Rollout notes -- harbor
>
> Cutover is Tuesday. Search read-only for the window. Rollback is one command,
> see the runbook. Decided we would not do this on a Friday again.
> Still open -- who owns the certificate renewal? Nobody has answered.
> Batch limit is 2,000, confirmed with the supplier.
> Freeze starts a day earlier from now on.

## Walk C -- under the floor

Supplied alone, with nothing else. Nine messages, one source, one audience, and
only five of them longer than a line -- the DM block above. The run must stop
before proposing a file, say what was seen, and say what would be enough. A file
written from this describes how the user talks to one person.

## Walk D -- an existing file

Walk A again, but `~/.claude/daikenja/writing-style.md` is no longer the shipped
template. The user has written one line into it by hand:

```markdown
## Words to avoid

Never "circle back". I have never used it and I never will.
```

The run must show a diff rather than the whole file, must not drop that line,
and must not silently reword it. The corpus supports keeping it -- `circle
back`, `sync up` and `touch base` appear nowhere in 33 messages -- so the
proposal extends the line rather than replacing it.
