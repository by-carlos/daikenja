# Personas

The people and audiences you write to. Daikenja reads this when it composes or
reviews a message, so that a note to your manager does not read like a note to
a vendor.

Copy this file to `~/.claude/daikenja/personas.md` and fill it in. Point at it
from `daikenja.yaml` with `profile.personas`. Nothing here ships with the
plugin -- it is yours and it stays on your machine.

**Daikenja may add to this file.** When you describe someone while working on a
message, `/daikenja:remember-persona` appends a section for them and tells you
afterwards what it wrote. It records only what you actually said, never a guess
at the rest, and every entry it adds carries the date it was recorded so you can
spot it. A section you wrote yourself is never rewritten without the change
being shown to you first. Anything it adds is yours to edit or delete.

**It asks first when the description came in with something you pasted.** A
draft, a thread or a worked example can describe people who do not exist, and
this file is your notes on real colleagues. So a person you told it about
directly is added and reported; a person who turned up inside pasted material is
shown to you and added only if you say yes.

Write in prose. There is no schema. One section per persona works well, and
what matters is what changes how you write to them: what they already know,
what they care about, how much detail they want, and how direct you can be.

**One optional convention: `Known as`.** A ledger entry attributes work to a
short handle -- `@priya` -- and nothing in that line says who `@priya` is. List
the names a person goes by here and the handle has a referent, which is what
lets `/daikenja:project-log` tell a genuinely new colleague apart from a second
spelling of one you already have. Write their full name, then whatever else
picks them out: other handles, a chat ID, an email address. It is a line of
prose like the rest, and leaving it out costs nothing except that check.

**It can hold contact details, so keep the file where private notes belong.**
This was already your own prose about real colleagues; chat IDs and email
addresses make it worth thinking about before you sync or share it anywhere.

Delete everything below this line once you have written your own.

---

## <Name or group>

**Known as.** Their full name, and anything else that means the same person --
the handle you would write in a ledger entry, a chat ID, an email address.

**Who they are.** Their role and how they relate to your work.

**What they already know.** Background you can assume, so Daikenja does not
re-explain it.

**What they want from you.** The decision, the numbers, the risk, the status --
whatever they actually read the message for.

**How to write to them.** Length, formality, and how direct to be. Note
anything that reliably lands badly.

## <Another name or group>

...
