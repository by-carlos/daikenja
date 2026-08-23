Synthetic draft for `preflight` acceptance. Invented people and project.
Not real work content.

Exercises the re-run rule: a second run on a revised draft must not re-ask
what the user already answered between runs, and must say whether what
remains is finite. Only meaningful under `claude --plugin-dir .`, like the
other loop fixtures in this directory -- a normal session loads the last
released copy of the skill.

Depends on: preflight-reference.md "Re-running on the same draft", preflight-reference.md "Reporting a re-run"

## Run 1 -- the original draft, two gaps

To: Diablo
cc: #tempest-ops

"Hi Diablo -- I want to run the certificate rotation on `tempest-gateway`
before Friday's release. I tested the rotation script against staging last
week and it completed cleanly.

There will be a short window where the gateway drops connections while it
runs, so I want your sign-off before I schedule it. Can you approve?"

The window's length and what happens to connections while it runs exist
nowhere in this draft. `preflight` run 1 must report `needs 2 facts`: the
window's length, and what "drops connections" means for callers mid-request.

## Directions given between runs

The user answers both, in the conversation, not by editing the draft yet:

- The window is 12 minutes.
- In-flight requests fail and must be retried by the caller; nothing queues.

## Run 2 -- the revised draft, one new gap

"Hi Diablo -- I want to run the certificate rotation on `tempest-gateway`
before Friday's release. I tested the rotation script against staging last
week and it completed cleanly.

The rotation takes 12 minutes. In-flight requests during that window fail and
must be retried by the caller; nothing queues. I want to run it Thursday
evening, so I want your sign-off before Benimaru's on-call shift starts.

Can you approve?"

The window and the failure mode are now stated in the draft. Run 2 must
report both as **settled since the last run**, in one line, and must not
re-ask either one. What run 2 still needs is when Benimaru's on-call shift
starts, which the draft assumes the reader already knows and never states --
the one new fact. Because this is a second consecutive run still ending
`needs facts`, the report must say the remaining set is exactly this one fact
and name it, not report a bare count.
