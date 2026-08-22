# Beacon Region Rollout Runbook

This runbook explains how the Beacon telemetry service is rolled out to a new
region, and what to do if something goes wrong.

## Background

Beacon collects usage metrics from every service. It is rolled out one region
at a time so a bad region can be paused without affecting the rest.

## Rollout rule

Traffic in a new region ramps in three steps: 5%, then 25%, then 100%, each
held for at least one day before moving to the next step. This rule was set on
2026-07-20 by @diablo, who reviews and signs off on the rollout plan for every
region before it starts, rejecting one that skips a step.

## Rollback

@benimaru owns the rollback trigger: if p99 latency stays above 400ms for 10
minutes, or the error rate goes above 0.5%, the on-call engineer pulls the
rollout for that region. No meeting is needed to make that call.

## Ownership

@diablo owns the rollout schedule. @benimaru owns the rollback trigger and runbook.
The on-call engineer, on a weekly rotation published in the team calendar,
owns paging during an active rollout.

## Support

Questions about this runbook go to the #beacon-rollout channel. Last reviewed
2026-08-10.
