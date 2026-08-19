# Fixture: sample thread

Synthetic. Invented project, invented people, invented links. Nothing here comes
from real work. Used by the `project-log` skill's acceptance checks.

The thread is built to exercise the classification rules: one clear decision, one
proposal nobody agreed to, one open question, one task with no owner, and one
link worth keeping.

---

**#harbor-rollout** -- 7 messages

**diablo** (2026-08-14 09:02)
> Rate limiter rollout. We have been going back and forth on the cutover shape
> for a week and I want to close it today. Two options on the table: flip all
> tenants at once behind a flag, or ramp 5% / 25% / 100% over three days.

**benimaru** (2026-08-14 09:06)
> Ramp. The flag flip gives us one blast radius and no signal until it is too
> late. Three days is cheap.

**diablo** (2026-08-14 09:09)
> Agreed, we ramp. 5 / 25 / 100 starting Monday 2026-08-17. I will own the
> rollout.

**souei** (2026-08-14 09:14)
> Works for me. Runbook is here if anyone needs it:
> https://example.com/harbor/runbook

**benimaru** (2026-08-14 09:21)
> While we are here -- we should probably move the limiter config out of env
> vars and into the config service. Not for this rollout, but soon.

**diablo** (2026-08-14 09:23)
> Maybe. Park it.

**souei** (2026-08-14 09:30)
> One thing nobody has answered: what is the rollback trigger? If p99 goes up at
> 25%, who decides to pull it and on what number? Also somebody needs to write
> the customer comms before Monday, I do not think that is assigned.
