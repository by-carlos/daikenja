# Domain glossary

Terms from the material you work with -- acronyms, rule IDs, team names,
terms of art -- each glossed once, so you have one place to look a term up
instead of asking twice what it means.

This file is yours and it stays on your machine. Nothing here ships with the
plugin, and no skill copies it anywhere. **No skill reads or writes it:**
`setup-user` creates the blank file and nothing touches it afterwards, so you
keep it by hand. If you want Claude to use it in a session, point at it
("check my glossary at `~/.claude/daikenja/glossary.md`").

**One line per term.** Bold term, an em dash, a gloss of ten words or fewer,
then a bracket with the project the term belongs to, the date, and where the
gloss came from. Add `· unverified` inside the bracket for a gloss nobody has
confirmed yet -- an unconfirmed entry is used with a question mark, never as
fact. The two examples below are indented so that a search for real entries,
which start at the left margin, never finds them.

```
    - **DBO** — database owner team, approves schema and pooling changes. [example-db · 2026-09-12 · Alex]
    - **pool mode** — one server connection reused per transaction. [example-db · 2026-09-12 · vendor docs § pooling · unverified]
```

## Entries

