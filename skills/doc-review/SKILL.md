---
name: doc-review
description: Reviews a document against a fixed checklist before it is published or shared -- clarity, undefined terms, unenforced rules, undated decisions, missing owners, contradictions, and content that is stale on its face. Use when the user says "review this doc", "is this page clear", "check this page before I publish", "does this make sense to someone outside the team", or pastes a document/link and asks for a check before sending it out. Read-only -- this skill reports findings, it never edits or rewrites the document. Not for a message or reply (that is /daikenja:compose) or a pre-send substance check on a draft message (that is /daikenja:preflight) -- this skill is for standalone documents (specs, runbooks, wikis, READMEs), not chat replies.
metadata:
  owner: Carlos
  version: 1
---

# Doc review

A fixed-checklist review of one document. It finds problems and says where
they are and why they matter. It does not fix them.

## Hard rule: never rewrite

This skill reports. It does not edit the document, propose replacement text
for more than a short illustrative phrase, or produce a "fixed" version. The
human edits. Say this up front if there is any risk of the request being read
as "clean this up for me".

## Step 1: get the document

- **A link was given.** Fetch it with whatever tool is connected for that
  source -- Confluence, Google Docs, a web page, a local file path. Use the
  live content, not the link text.
- **Text was pasted.** Use it as-is. Do not go looking for more.
- **Nothing was given.** Ask for a link or a paste. Do not search for it or
  guess which document is meant.

If a fetch fails, say what failed and ask for a paste. Do not review a title
or a summary in place of the real content.

## Step 2: run the checklist

Evaluate the document against each of these. A document can trip any number of
them, including zero.

- **Clarity.** A sentence or section whose meaning takes more than one reading
  to get, or that could mean two different things.
- **Readability for non-native English speakers.** Long sentences, uncommon
  words with a common alternative, idioms, or culturally-specific references.
- **Undefined terms and unexpanded acronyms.** A term or acronym used before
  it is defined, or never defined at all, where a reader new to the subject
  would stumble.
- **Rules with no enforcement or owner.** A "must" or "should" statement with
  nobody named to enforce it and no mechanism that would catch a violation.
- **Decisions with no date.** A decision stated as settled, with no date
  attached, so a reader cannot tell how current it is.
- **Missing owners.** A task, section, or piece of ongoing work with nobody
  named responsible for it.
- **Internal contradictions.** Two parts of the same document that cannot both
  be true, or that give conflicting instructions.
- **Content stale on its face.** A reference to a date, version, tool, or
  event that has clearly passed or changed, judged from the document's own
  content -- not from outside knowledge of what changed.

Do not invent a finding to fill out the list. A clean document produces a
short report, not a padded one.

## Step 3: cap and order

Findings are capped at 5, hardest first, matching the ordering `self-review`
uses -- consistency between the two review skills is worth more than either
skill inventing its own scale. "Hardest" here means most likely to cause real
harm if unfixed: a contradiction or an unenforced rule outranks a wording
nit. Within a tier, order by where the finding sits in the document (earliest
first), since that is the order a reader will hit them.

If there are more than 5, name the count and list the rest by one-line title
only, the same parked-by-title treatment `self-review` uses.

## Step 4: report

One entry per finding, in the order fixed by Step 3:

```
1. [checklist category] -- <one-line title>
   Where: <section heading, or a short quote that locates it>
   Why it matters: <what goes wrong if this ships as-is>
   Fix: <a concrete, specific fix -- not "make this clearer">
```

Close with a one-line summary: how many findings, and whether anything is
parked.

If nothing qualifies, say so plainly rather than omitting the report:

```
No findings. <document name> reads clearly, has no undefined terms, and
nothing on this checklist tripped.
```

## Failure cases

| Situation | What to do |
|---|---|
| Link given but no tool is connected for that source | Say which source and that no tool is connected; ask for a paste instead. |
| Fetched content is empty or clearly truncated | Say so and ask for a paste rather than reviewing a partial document. |
| Document is very long | Review the whole thing. Do not sample or skip sections silently. |
| User asks for the document to be rewritten or fixed | Decline per the hard rule above; offer the findings instead. |
