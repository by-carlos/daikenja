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

Write in prose. There is no schema. One section per persona works well, and
what matters is what changes how you write to them: what they already know,
what they care about, how much detail they want, and how direct you can be.

Delete everything below this line once you have written your own.

---

## <Name or group>

**Who they are.** Their role and how they relate to your work.

**What they already know.** Background you can assume, so Daikenja does not
re-explain it.

**What they want from you.** The decision, the numbers, the risk, the status --
whatever they actually read the message for.

**How to write to them.** Length, formality, and how direct to be. Note
anything that reliably lands badly.

## <Another name or group>

...
