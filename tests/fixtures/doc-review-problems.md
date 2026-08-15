# Harbor Rollout Runbook

This runbook covers the Harbor rate limiter rollout.

## Background

Harbor replaces the old GKR pipeline. All services must migrate before the
freeze.

## Rollout rule

Traffic must ramp gradually. Nobody should flip the flag for all tenants at
once, whatever the circumstances.

## Rollback

We decided the rollback trigger is p99 latency above 400ms for 10 minutes.

## Ownership

The on-call engineer handles paging during the rollout. The customer comms
task is still being worked out.

## Fast path

If staging looks clean, flip the flag for all tenants at once to save time.

## Support

This runbook was written for the initial GKR cutover in 2024 and still
applies today for any future service migration.
