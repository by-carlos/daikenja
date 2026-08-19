# Fixture: sample meeting transcript

Synthetic. Invented project, invented people, invented links. Nothing here comes
from real work. Used by the `meeting-review` skill's acceptance checks.

It continues the Harbor rate limiter story used by the `project-log` fixtures,
and it is built to exercise the classification rules and the transcript mess
at the same time:

- one real decision, closed out loud (the start date moves to 2026-08-19)
- one decision the meeting only restates, which is not a new decision (the
  5 / 25 / 100 ramp shape, already settled in `sample-thread.md`)
- one suggestion nobody agreed to (the per-tenant override switch)
- one action item with a clear owner and a date (dan, customer comms)
- one action item nobody picked up (the runbook dates)
- one unresolved question (who pulls the ramp at 100%)
- one vague "we should probably" line that is discussion, not an action item
- the mess: three speaker labels for one person, the same point made three
  times, a side conversation, and an inaudible passage

---

**Harbor rate limiter -- rollout sync**
2026-08-14, 09:00, 22 minutes, 4 attendees

```
[00:00:04] Benimaru: can you see my screen?
[00:00:07] Souei: not yet
[00:00:11] Benimaru: how about now
[00:00:13] Souei: yep

[00:00:31] Diablo: Ok, we are all here. One thing to close today, which is
whether we still start Monday. Everything else is status.

[00:00:52] Diablo: To recap where we landed last week, we are ramping
5 / 25 / 100 over three days rather than flipping the flag for everyone at
once. That part is settled, I am not reopening it.

[00:01:20] Souei: On Monday. The customer comms are not written. I have not
started them and I am not going to have them by Monday morning.

[00:01:38] Diablo: How long do you need?

[00:01:44] Souei: If I do them tomorrow and Friday, they are ready Monday
end of day. So Tuesday at the earliest for a send.

[00:02:03] Shuna: Ops would rather not start a ramp on a Monday anyway.
Monday morning is when everything else lands.

[00:02:19] Diablo: Then we move it. We start Wednesday the 19th, same
5 / 25 / 100 shape, same three days. That is the call.

[00:02:34] Benimaru: fine by me

[00:02:36] Souei: works

[00:02:51] Diablo: Souei, the comms are yours then. Can you have them by
Monday the 18th so we have a day of slack?

[00:03:02] Souei: Yes. I will have the customer comms done by the 18th.

[00:03:30] Benimaru: While we are here. I keep coming back to the idea of a
per-tenant override switch, so we can hold one noisy tenant at 5% while
everyone else goes to 25%. It is maybe half a day of work.

[00:03:58] Shuna: That is a nice-to-have and it is new code in the path we
are about to ramp.

[00:04:11] Diablo: Not today. Park it. If the ramp goes badly we will talk
about it again.

[00:04:22] Benimaru: I still think it is worth it.

[00:04:26] Diablo: Noted, but not for this rollout.

[00:05:40] Shuna: Something nobody has answered. At 5% and 25% it is
obvious, on-call pulls it if p99 goes bad. At 100% the limiter is just how the
service behaves. Who makes the call to pull it at that point, us or ops?

[00:06:02] Benimaru: Good question.

[00:06:09] Diablo: We should come back to that.

[00:07:15] Souei: Also the runbook still says Monday the 17th in three
places, and it has the old step ordering from before the ramp.

[00:07:28] Diablo: Right, somebody needs to update the runbook with the new
dates before Wednesday.

[00:07:36] Benimaru: mm

[00:07:41] Souei: I have the comms.

[00:07:44] Diablo: Ok.

[00:09:02] Benimaru: On the dashboards. We should probably be watching the
limiter panels more often than we do, in general.

[00:09:14] Shuna: Sure.

[00:10:30] Benimaru: The other thing about the [inaudible] is that it only
shows up under load, so we would not see it in staging anyway.

[00:10:47] Diablo: Can you say that again, you cut out.

[00:10:50] Benimaru: It is not important, I will write it up.

[00:12:05] Souei: Are we doing the offsite thing on the 27th? I never got
an invite.

[00:12:12] Shuna: I think Ranga is sending them this week.

[00:12:18] diablo: Different meeting.

[00:15:44] diablo: So to be clear, because I do not want this wrong in the notes.
We start Wednesday the 19th. Not Monday. 5 / 25 / 100, one step per day.

[00:15:58] Shuna: Wednesday the 19th, got it.

[00:19:03] Benimaru: Do we need to tell the tenants about the date change or
is that part of the comms?

[00:19:12] Souei: Part of the comms.

[00:21:30] D: Ok. Ramp starts the 19th, Souei has the comms by the 18th, the
runbook needs fixing, and we still owe an answer on who pulls it at 100%. That
is everything.

[00:21:49] Shuna: thanks all
```
