---
name: judgement
description: 'Checks a thread or a document against the project ledger and general knowledge and hands back a verdict: what is being claimed or asked, which parts a recorded decision settles, which parts are plain fact, and what is presented as settled without being established. Use when the user says "is this right?", "check this against the ledger", "give me a judgement on this thread", or asks for a quick "AI review summary" of a page or pull request to share with the team. Read-only -- it never drafts a reply, never edits the document and never writes the ledger.'
metadata:
  owner: Carlos
  version: 1
---

# Judgement

One subject, one verdict. The subject is a thread or a document; the verdict
says what it claims or asks, checks that against the project's ledger first
and against general knowledge second, and labels every statement with where
it came from. It comes back in one of two forms: `answer`, a reply to the
user in the conversation, or `message`, a deliverable a cold reader can be
handed as it stands.

`thread` summarises and gathers; `compose` writes a reply; `doc-review` runs
a fixed checklist over a document's own quality. This skill does none of
those. It judges whether what the subject says holds up.

## Hard rule: read-only, and never a reply

**Do not draft a reply, a suggested wording or a message to send back into
the thread.** Not even in the `message` form: that form is an assessment
written as an AI pass, headed as one, and it is never phrased as the user
speaking. A user who wants to answer the thread runs `/daikenja:thread` and
then `/daikenja:compose`.

**Do not write the ledger, the card or `daikenja.yaml`.** A contradiction
this skill finds is reported; it is logged, if at all, by the user through
`/daikenja:project-log` afterwards. A project this skill cannot resolve is
not registered by it and gets no card from it.

**Do not edit the document.** A finding names what is wrong and where. The
human edits.

## Step 0: read the contracts

Read these before the first output:

- `${CLAUDE_PLUGIN_ROOT}/docs/response-format.md` -- the `answer` form is a
  conversational reply and follows it whole: answer first, findings
  itemised, entries topic-first with the ID in parentheses, clean result in
  one line.
  - § The second person belongs to conversation governs the difference
    between the two forms: the `answer` form addresses the user as `you`,
    and the `message` form -- built to leave the session -- names people
    instead.
- `${CLAUDE_PLUGIN_ROOT}/docs/project-card.md` § Resolving a project by
  content and § Reading a card -- how a subject with no key and no directory
  finds its project, and what a card says.
- `${CLAUDE_PLUGIN_ROOT}/docs/reading.md` § Step B: resolve the ledger path
  and § Step C: read and parse -- how the ledger is found and read.
- `${CLAUDE_PLUGIN_ROOT}/docs/voice.md` -- the `message` form is generated
  output and follows it in voice-only mode; see § Voice in the message form.

## The discipline is this skill's own

A user may have installed a conversational register of their own -- labelled
response parts, a brevity rule -- through `/daikenja:tensei` or by hand. It
is per user, may be absent and may be edited, so nothing here depends on it.
The rules below are written into this skill so it behaves the same on every
install:

- **Headline first.** One line naming the subject, then the finding. Never
  an explanatory paragraph before the verdict.
- **Every statement is labelled with its source**: `ledger`, with the
  decision or open item named topic-first and its ID in parentheses, or
  `general knowledge`. A statement with no label is a defect.
- **Every finding carries a confidence**: `certain`, `likely` or `guessing`.
  A recommended action is framed as a suggestion. Confidence and suggestion
  are two different things; neither form blurs them into hedging.
- **Flag what the subject presents as settled but does not establish.** "As
  agreed", "the standard says", "everyone knows" with nothing behind it is a
  finding, not a fact to carry forward.
- **Links only from evidence.** A standard, page or source is linked only
  when the subject itself or the ledger's Sources section already carries
  that link. Otherwise name it by its human-readable title and mark it
  `link needed`. Never construct a URL, and never restate a standard owned by
  another team in place of naming it.
- **Close with one line saying what was not checked.** An unstated scope
  exclusion is a defect of the review.
- **No padding.** A clean result is one line.

The `answer` form still picks up an installed register when one is present,
exactly as any other reply does, per `response-format.md` § A user-side
conversational layer. The `message` form never does: it leaves the session.

## Step 1: get the subject and the form

**The argument rule.** `/daikenja:judgement` with no argument works on the
enclosing context; `/daikenja:judgement <subject>` works on that subject
instead. In Claude Code there is no enclosing thread, so the bare form means
**the most recent link or pasted block in this session**. When nothing in the
session qualifies, ask for one and stop. Never guess, and never go looking for
a thread or a page the user did not give.

Accepted subjects:

- **A Slack thread link.** Fetch the full thread with the connected Slack
  tool, parent message and every reply. Do not work from the permalink text.
- **A Confluence page link, or any other document link.** Fetch it with
  whatever tool is connected for that source. Use the live content.
- **A repository path**, including a pull request or a file in the working
  tree. Read it.
- **Pasted text.** Use it as-is. Do not go looking for more.

If a fetch fails, say what failed and ask for a paste. Do not judge a title or
a summary in place of the content, and do not review a partial document
silently -- say it is partial.

**The form.** `answer` is the default. `message` is chosen when the user asks
for it by name (`/daikenja:judgement message <subject>`), or in plain words asks
for something to share -- "for the team", "as a message", "an AI review
summary", "something I can post". When the wording is ambiguous, produce the
`answer` form; it is one line to ask for the other afterwards.

A caller that has an enclosing thread of its own -- a chat bot, a later
consumer -- passes that thread as the subject and names the form. Nothing in
this skill assumes a working directory or a terminal.

## Step 2: triage the subject

Before checking anything, establish what the subject says. For a thread, the
summary is the same five-line shape `thread` § Step 2: summarize it uses,
and its attribution rules apply unchanged -- name who said what, keep a
question apart from a proposal and both apart from a decision, and call an
ambiguous position ambiguous:

```
🧵 **Thread** -- [what it is about, who is in it, and how many messages]
❓ **Asking** -- [who is asking, and what they actually want]
🔓 **Open** -- [what is still undecided]
⏳ **Waiting on** -- [name: what is theirs]
📒 **Ledger** -- [what the project already has on this -- see Step 2b]
🌡️ **Tone** -- [neutral / tense / urgent -- only if it is not neutral]
```

For a document, the same block with `📄 **Document**` in place of `🧵 **Thread**`
(title and what kind of document it is), `📌 **Claims**` in place of
`❓ **Asking**` (what it states as fact), and `🔓 **Open**` for what it leaves
undecided. `Waiting on` and `Tone` are omitted whenever they would be empty,
for a thread as much as for a document.

Then list, for yourself, every **factual claim** and every **question** the
subject carries, and for each claim whether the subject establishes it or
merely presents it as settled. This list is what Step 4 checks. It is not
shown to the user as a list; the findings are.

**Do not flag ordinary workplace content.** Names, roles, opinions and
disagreements are the subject matter. The one exception is a credential,
token, connection string or password: say so in one line and never copy it
forward.

## Step 3: place the subject

Resolve the project, in the order `${CLAUDE_PLUGIN_ROOT}/docs/config-resolution.md`
§ Finding the project fixes, and stop at the first that resolves:

1. **A key the user named** -- decisive, never falls back. An unknown key is
   reported with the registered keys and the run stops.
2. **The current directory**, per `reading.md` § Step A. A caller with no
   working directory skips this route.
3. **The subject's content**, per `project-card.md` § Resolving a project by
   content. A handle the subject names -- its channel, a tracker key, a
   repository, a document URL -- that exactly one card owns is a match. A
   Scope match is a **candidate**: say `Project: probably <key> -- confirm`
   and wait. Do not read a ledger on the strength of a candidate.

When a key or a directory resolved, still run the content check as a
cross-check and report a decisive handle that points elsewhere as a mismatch,
in one line, without switching project.

**This skill is asked to resolve outright**, so tier 3's non-match is said,
not kept quiet: `No registered project matches this content. <key> has no
card, so it could not be checked.` The verdict then continues on general
knowledge alone, and both forms say plainly that **no ledger was checked**.
It never falls back to an unrelated project's ledger, and it never treats
the current directory's ledger as the subject's when the subject's own
handles point nowhere.

**Read what the project has**, per `reading.md` § Step B: resolve the ledger
path and § Step C: read and parse: the Decisions and Open items sections in
full, the Sources section when there is one (it is where a link may come
from), and the card beside the ledger per `project-card.md` § Reading a
card. Name the resolved ledger path and, when content decided, how the
project was found -- the same line shapes `thread` § Step 2b uses -- and the
card's path on the line after it when a card was read, per `project-card.md`
§ Reading a card:

```
Ledger: <key> (<absolute path>)                            key or directory
Ledger: <key>, matched by #<channel> (<absolute path>)     decisive handle
Ledger: <key>, confirmed by you (<absolute path>)          Scope candidate
Card: <absolute path>
```

A ledger that does not exist is reported with `reading.md`'s own line and the
run continues on general knowledge, saying so. A malformed line is reported
and skipped, never repaired.

## Step 4: check the claims

**The ledger check comes first.** Walk Step 2's list against the entries just
read:

- A claim or proposal that **contradicts a decision in force** -- name the
  decision topic-first with its ID, and quote the decision's own wording where
  the exact words matter. This is the most useful finding the skill can make
  and it leads the verdict.
- A question the ledger **already answers** -- name the decision that answers
  it.
- A claim or question that **bears on an open item** -- name the item, and
  whether the subject appears to resolve it. "Appears to resolve", never
  "resolved": only `project-log` resolves, and only on the user's say-so.
- A claim the subject presents as settled that the ledger records as **still
  open** -- a finding of its own, labelled `ledger`.

**Then general knowledge**, for what the ledger does not cover: a plain
factual error (one database engine cannot host another; a protocol does not
do what the thread says it does), a question with a well-known answer, a
claim that is true as stated. Each carries `general knowledge` and a
confidence. A statement this skill is guessing at says `guessing`; it is not
dropped to look more certain, and it is not padded to look more thorough.

**A superseded decision is not in force.** A subject that agrees with the
superseded wording contradicts the current one; say which is which.

**What was not checked** is decided here and written down in Step 5: a link
in the subject that was not opened, a channel the thread refers to, a
standard named but not read, a project that could not be checked for want of
a card. One line, always present.

## Step 5: report

### Form `answer`

The conversational reply, per `response-format.md`. The summary block from
Step 2 opens it; the conclusion follows; nothing precedes the block.

```
Thread: ...
Asking: ...
Open: ...
Ledger: <key>, matched by #<channel> (<absolute path>)
Card: <absolute path>

Verdict: <one or two sentences that answer what the thread asks or judge
what it claims, each clause labelled>

1. <finding> -- <certain | likely | guessing>. Source: ledger, <topic>
   (D-nnn) | general knowledge.
2. ...

Suggested: <the action, as a suggestion, or omitted>
Not checked: <one line>
```

The worked example from the design: a thread asks "are we going with X, and
can SQL Server host Oracle?". The verdict reads `Z was agreed for this
project (the storage-engine decision, D-003). SQL Server and Oracle are two
different database engines; one cannot host the other -- certain, general
knowledge.` The first clause is cited to the ledger; the second is labelled
as knowledge, not as ledger fact.

`profile.tone` scales the framing around the block and the findings, never
the findings. A clean subject -- nothing contradicted, nothing unestablished,
every question answered by the thread itself -- is one line:
`No findings. <subject> agrees with the ledger and makes no claim that does
not hold.` followed by the `Not checked:` line.

**When no project resolved**, the `Ledger:` line is replaced by the one-line
non-match from Step 3, and the first numbered finding says the ledger check
did not run. The `Verdict:` sentence itself stays on the answer. Nothing
else changes.

### Form `message`

A shareable deliverable for a cold reader with medium knowledge of the
domain: define a non-standard term in the sentence it first appears; do not
explain what a practitioner already knows. **No conversational markers, no
emoji, no register labels**, whatever the user has installed -- a consumer
that cannot render them is the reason this form exists. Bulleted throughout,
about 150 words, written as an AI pass and never as the user. Exactly this
shape:

```
AI review summary
Subject: <one line naming the subject -- channel and date, or document title>
- Ledger: <the finding itself: what the subject says, the decision or open
  item it contradicts or depends on, topic-first with the ID in parentheses,
  and its confidence -- first, before any other finding; or "no project
  resolved, so no ledger was checked">
- <finding> -- <certain | likely | guessing>. Source: ledger (D-nnn) |
  general knowledge.
- <a claim presented as settled but not established, if any>
- Suggested: <the action, as a suggestion>
- Not checked: <one line>
```

The `Ledger:` bullet **is** the ledger finding, complete with its confidence;
it is not a heading that a second bullet then restates. One ledger finding
per bullet; a second contradiction or dependency gets its own `Ledger:`
bullet directly under the first.

Sources named in it follow the links rule: title first, a link only when the
subject or the ledger's Sources already carry it, otherwise `(link needed)`.

The message is handed back inside a fenced block so the user can copy it
whole. **Around it, a short report to the user** -- the `Ledger:` and
`Card:` lines from Step 3, and anything that needs the user's own judgement: a candidate the user confirmed,
a mismatch the cross-check found, a finding the user may not want shared, a
term the reader might not know. That material goes in the report, never in
the message; the message must stand without the conversation it came from.

A clean subject in this form is still a complete message: the header line,
the subject line, `- Ledger: nothing contradicted or depended on`, and the
`Not checked:` line.

## Voice in the message form

The `message` form is generated output and follows
`${CLAUDE_PLUGIN_ROOT}/docs/voice.md` in full -- the `## Fixed` tier and
the `## Defaults` tier as shipped. It runs in **voice-only mode**, defined in
`config-resolution.md` § Voice and writing style: the user's `writing_style`
prose is **not read** -- not resolved, not layered, and its absence is not a
notice -- and `personas` is not read either. The message is an AI pass for
a reader who was not in the conversation; the user's own greetings, turns of
phrase and softening would misattribute it. Voice-only is not a user
setting: this skill names it here, and only this form uses it.

The `answer` form is conversation, not generated output; `voice.md` does not
govern it and `response-format.md` does.

## Failure cases

| Situation | What to do |
|---|---|
| Bare `judgement`, and nothing in the session is a link or a pasted block | Ask for a link, a path or a paste. Do not search for one. |
| Link given but no tool is connected for that source | Say which source and that no tool is connected; ask for a paste. |
| Fetched content is empty or truncated | Say so and ask for a paste. Never judge a partial subject silently. |
| The named project key is not registered | Stop: name the key and list the registered ones. Never fall back to the directory. |
| No project matches, and some registered projects have no card | Say the non-match line naming the cardless projects, continue on general knowledge, and say no ledger was checked -- in both forms. |
| A Scope match, no decisive handle | Name the candidate and wait for confirmation. Do not read its ledger first. |
| The resolved ledger does not exist | `No ledger at <path>. Run /daikenja:project-log to create one.`, then continue on general knowledge, saying so. |
| A ledger line does not parse | Report it per `reading.md` § Notices, shared wording and skip it. Never repair the file. |
| The subject asks for a reply, or the user asks for one | Decline per the hard rule; name `/daikenja:thread` and `/daikenja:compose`. |
| The user asks for the document to be fixed | Decline per the hard rule; the findings say where. `/daikenja:doc-review` is the checklist review if that is what was meant. |
| A credential appears in the subject | One line saying so; never copy it into either form. |

## What this skill does not do

- It does not draft. The hard rule at the top is the whole of it, and the
  `message` form is an assessment, not a reply.
- It does not write the ledger, the card or `daikenja.yaml`, and it does not
  register or scaffold anything. `project-log` and `setup-project` do, on
  the user's approval.
- It does not run `doc-review`'s checklist. Clarity, undefined terms and
  missing owners in the document's own text are that skill's findings; this
  skill judges whether the document's claims hold.
- It does not post anywhere. A consumer that posts the `message` form into a
  chat surface is separate work and is not part of this skill.
