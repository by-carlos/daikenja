# Fixture: sample thread, second pass

Synthetic, same invented project as `sample-thread.md`. Used by the
`project-log` skill's idempotence check.

This is the same conversation re-pasted with two later messages appended. Logging
it after `sample-thread.md` must update the existing entries rather than append
near copies: the rollback trigger question gets answered (resolving an open item)
and the ramp decision is narrowed, not repeated.

Starting ledger: the one `sample-thread.md` produces. No new handles appear in
this pass, so the proposal carries no `New owner handles:` block.

---

**#harbor-rollout** -- 9 messages

**diablo** (2026-08-14 09:09)
> Agreed, we ramp. 5 / 25 / 100 starting Monday 2026-08-17. I will own the
> rollout.

**souei** (2026-08-14 09:30)
> One thing nobody has answered: what is the rollback trigger? If p99 goes up at
> 25%, who decides to pull it and on what number? Also somebody needs to write
> the customer comms before Monday, I do not think that is assigned.

**benimaru** (2026-08-14 14:40)
> Rollback trigger: p99 over 400ms sustained for 10 minutes at any step, or any
> 5xx rate above 0.5%. On-call pulls it, no meeting needed. Settled.

**diablo** (2026-08-14 14:52)
> Good. And I am taking the customer comms, I will have a draft tomorrow.
