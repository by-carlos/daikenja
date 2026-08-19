# Writing style

How you want your own messages to sound. Daikenja reads this when it composes or
rewrites anything on your behalf.

Copy this file to `~/.claude/daikenja/writing-style.md` and fill it in. Point at
it from `daikenja.yaml` with `profile.writing_style`. Nothing here ships with
the plugin -- it is yours, and it stays on your machine.

**One skill writes this file, and only with your approval.** If you would rather
not start from a blank page, `/daikenja:learn-voice` works out how you write
from writing samples you supply and proposes the whole file. It shows you the
complete content first, diffs it against anything already here, and writes only
what you approve. Nothing else edits this file.

**This layers on top of the Daikenja default voice, it does not replace it.**
The default applies except where you say otherwise, so you only need to write
down what is specific to you.

Part of the default voice you cannot override. It is the part marked `## Fixed`,
and it covers absolute dates, the rules that keep a message readable for someone
whose first language is not English, and a short list of things Daikenja will
not write at all. Everything marked `## Defaults` -- message length, humor, how
far to push a plain-word substitution -- is yours to change. Anything you write
below that contradicts a Fixed rule has no effect.

Write in prose or bullets, whichever you prefer. Useful things to pin down:

- Greetings and sign-offs you use, and ones you never use.
- How long a message should get before you would rather send a summary.
- Words and phrases you avoid, and ones you reach for.
- How you soften or sharpen a request.
- Whether you use bullets or paragraphs by default.
- Anything you have been told about your writing, good or bad.
- Which spelling variant you write in -- Commonwealth/British is the shipped
  default; say so here if you want US spelling instead.
- Whether a soft deadline to a reader in your own time zone may go relative
  ("ideally by end of day") instead of an absolute date -- absolute stays the
  default until you say so here, and a hard deadline or a reader in another
  time zone always gets an absolute date regardless.

Delete everything below this line once you have written your own.

---

## Openings and closings

## Length and structure

## Words to avoid

## Words and phrasings I use

## Tone
