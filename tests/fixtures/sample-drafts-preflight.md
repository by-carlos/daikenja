Synthetic drafts for `preflight` acceptance. Invented people and project.
Not real work content.

## Draft 1 -- should pass

To: priya
"Hey priya -- the events-table migration script I ran this morning against
staging is failing with a foreign key violation on `beacon_events.region_id`.
I tried re-running it after truncating the staging table and also tried it
against last week's schema snapshot, same error both times. Since you own the
migration, can you confirm by Thursday 2026-08-20 whether the FK constraint on
`region_id` is supposed to be there yet, or whether it shipped early? I do not
want to drop it myself without checking."

## Draft 2 -- missing context and a specific ask

To: #beacon-eng
"can someone look at the migration thing, it's broken again"

## Draft 3 -- already answered in the supplied ledger

To: priya
"Hey priya, quick one -- should we hold off on schema changes to the events
table until after the beacon rollout finishes, or is it fine to land them
now?"
