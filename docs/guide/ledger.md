# The project ledger

## Writing the ledger

- `/daikenja:project-log` -- records decisions and open items in a project's
  ledger. The only skill that writes ledger content; every other skill reads it.

## Reading the ledger

- `/daikenja:project-catchup` -- reports what changed in a project's ledger
  since you last checked, then advances the checkpoint on approval.
- `/daikenja:project-summary` -- gives a full-state overview of a project's
  ledger, written for someone with no prior context.
- `/daikenja:project-decisions` -- looks up what was decided about a specific
  topic, including its supersession history.
- `/daikenja:project-gaps` -- audits a project's ledger for open items with no
  owner or that have sat too long.
- `/daikenja:project-sources` -- reports which of the documents a project is
  tracked from moved since you last read them, by comparing each source's
  stored last-modified value against what its system reports now. The mirror
  image of `project-catchup`: that one reports what Daikenja wrote, this one
  reports what moved outside.
- `/daikenja:project-list` -- lists every project Daikenja knows about, says
  which one you are standing in, and reports whether each ledger actually
  exists. The one to run when a read skill answered about a project you did not
  expect.

All five reading skills take an **optional project name**:
`/daikenja:project-summary atlas-migration` reads that project from anywhere,
without being in its directory. They run only when you type the command: a
phrase such as "catch me up" does not fire them on its own.
