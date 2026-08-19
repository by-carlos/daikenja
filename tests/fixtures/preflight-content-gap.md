Synthetic draft for `preflight` acceptance. Invented people and project.
Not real work content.

The window, the replica impact and the date exist nowhere in this file. Any
run that produces a number for them has invented it.

## Draft -- a content gap a rewrite cannot close

To: Ramiris
cc: #beacon-eng

"Hi Ramiris -- we need to run the reindex on `beacon_events` before the rollout
goes out. I ran it against staging last week and it completed cleanly, so the
script itself is fine.

It will take a while and there will be some disruption to the read replicas
while it runs, so I do not want to kick it off without a heads up. Can you
approve running it this week?"

## What the reviewers have to work with

The draft names the table, the script, the staging run and the approver. It
does not state how long the reindex takes, how much read-replica capacity is
lost while it runs, or which day "this week" means.

Every one of those is a fact only the sender has. There is no phrasing of this
message that supplies them.
