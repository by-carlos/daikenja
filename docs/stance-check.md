# Stance check

Depends-on (reverse index -- hand-maintained, checked against SKILL.md
headings by tests/check-invariants.py):
- § When the check runs -- compose "Step 6c: stance fit (opt-in)", preflight "Step 3b: stance fit (opt-in)"
- § The four cases -- compose "Step 6c: stance fit (opt-in)", preflight "Step 3b: stance fit (opt-in)"
- § How a match is reported -- compose "Step 6c: stance fit (opt-in)", preflight "Step 10: report"

An opt-in check that a message's stance fits the sender's role: that the
sender does not ask permission for what they own, decide what is the reader's,
apologise for someone else's fault, or complain where an expectation would do.
Written once and shared by two consumers, the same way `substance-checks.md`
is:

- **`compose`** runs it silently before it drafts and names a match in its
  `Comment` block.
- **`preflight`** runs it on the draft before the review loop and names a
  match in its report.

Neither skill restates the cases in its own body. Both point here.

**It flags, it never edits.** The stance-kept rule in
[`rewrite-rules.md`](rewrite-rules.md) § Stance prose in the writing style
flags, never edits binds every consumer: a match is reported with a suggested
reframe, and the message keeps the stance the user gave it.

## When the check runs

Only when the user's `writing_style` prose carries the switch line
`stance-check: on`, as defined in [`config-resolution.md`](config-resolution.md)
§ Voice and writing style. No switch, no check, and nothing is said about it:
the consumer's output is exactly what it would be without this document. A
section that talks about stance with no switch does not turn it on.

With the switch on, it runs on every draft, whatever the goal type -- a
request, an announcement and a push-back can each take the wrong stance. It
reads the two lines of the file's `## Role and stance` section -- what the user
owns or decides, and what is usually the reader's -- and checks the **draft as
the user gave it**, never a rewrite of it.

## The four cases

- **Asking permission for something the sender owns.** "Is it OK if I move the
  release to Thursday?" from the person who owns the release schedule.
- **Deciding or directing what is the reader's.** "We are cutting the budget
  line" sent to the person who owns the budget.
- **Apologising for a fault the sender does not hold.** "Sorry the vendor's
  API was down" when the outage was the vendor's.
- **Complaining where an expectation fits.** "Nobody ever updates the ticket"
  where "Please update the ticket when the status changes" states the
  expectation.

Ownership comes from the role lines only, never from a thread or from what the
draft implies. A case the role lines do not settle is not flagged.

## How a match is reported

- **It fits.** Say nothing about it.
- **A case matches.** One entry per match: topic first (`stance fit`), the
  location in parentheses, one line on the mismatch, and one suggested
  reframe. Example: "stance fit (opening line) -- you own the release
  schedule, but the draft asks permission to move it. Reframe: 'I am moving
  the release to Thursday. Tell me if that blocks you.'" The reframe uses only
  what the draft already says; a date, owner or deadline it does not state
  stays out.
- **The switch is on but the role lines are missing or empty.** One entry
  saying the stance check is on with no role lines to check against, and
  naming `## Role and stance` in the writing-style file as where they go.

Where the entry goes is the consumer's call: `compose` puts it in `Comment`,
`preflight` in a `Stance fit` line of its report. In both, the reframe is a
suggestion to the user and never reaches the message.
