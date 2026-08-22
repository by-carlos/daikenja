Synthetic drafts for `preflight` acceptance. Invented people and project.
Not real work content.

Depends on: preflight "Step 3: cycle 0 -- the substance checks", substance-checks.md "The six checks"

## Draft 1 -- should pass

To: diablo
"Hey diablo -- the events-table migration script I ran this morning against
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

To: diablo
"Hey diablo, quick one -- should we hold off on schema changes to the events
table until after the beacon rollout finishes, or is it fine to land them
now?"

Check 6 fails by finding an answer, not by missing one: `sample-ledger.md`'s
`D-003` already settled this. The report must name it topic-first -- "the
events-table schema freeze (D-003)" -- and ask only whether the draft should
defer to it, not add a "you have not stated X" item to the questions list.
