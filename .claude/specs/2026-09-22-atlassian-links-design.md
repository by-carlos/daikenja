# Design: the bot reads linked Confluence pages and Jira issues

**Date:** 22 Sep 2026
**Status:** approved design, not yet implemented.
**Branch:** `feat/atlassian-links` (one integration branch, two tasks).
**Affects:** `bot/daikenja_bot/` -- `links.py`, `confluence.py`, `subject.py`,
`handler.py`, `prompts.py`, `runner.py`, `commands.py`, new `resolve.py`,
`follow.py` and `jira.py` -- plus `bot/README.md`, `bot/bot.yaml.example`,
`bot/tests/` and `CHANGELOG.md`.

---

## 1. Summary

Today every bot command reads exactly one thing: the thread it was typed in,
or the single link given as its argument. A thread that says "please review
this page" gets judged without the page, and a second link in the command is
silently dropped.

This design lets every command also read what its subject links to -- one
level deep -- and attaches those documents to the prompt as separately
labelled data. Task 1 builds the mechanism with Confluence as the only
followed source. Task 2 adds Jira issues, comments included, as a second
source that plugs into the same mechanism.

Nothing here changes the `bot.yaml` schema, so `docs/upgrading.md` gets no
entry. Jira reuses the `confluence` block's site and credentials: on Atlassian
Cloud both products share one host and one API token.

## 2. Decisions already made

| Decision | Choice | Why |
|---|---|---|
| Who fetches | The bot, in Python, before the model starts | The headless session has no network or Slack access by design (`runner.py`); giving it Atlassian tools would put the token inside the model process |
| Which commands | All of them: `summary`, `judgement`, and the reaction trigger | Following happens inside subject resolution, so one path serves all |
| Depth | One hop | Links inside an attachment are never followed |
| Credential scope | The configured personal API token, as today | Accepted by the maintainer: the person triggering the command is the one reading |
| Effort | `medium` when attachments are present, unless `claude.effort` is already higher | Comparing sources is reasoning; a plain thread keeps today's `low` cost. Hardcoded, no new config key |
| Jira comments | Always included | Comments are where tickets record the actual decision |

## 3. Architecture

### 3.1 The subject carries its attachments

`Subject` (`subject.py`) gains two fields, both defaulting to empty so every
existing construction keeps working:

- `attachments: tuple[Subject, ...]` -- the documents followed from this
  subject, each a normal `Subject` with kind, label, body and `source_url`.
- `unread: tuple[UnreadLink, ...]` -- links that were found but not read,
  each a URL plus a short reason.

A new kind constant `ISSUE = "Jira issue"` joins `THREAD`, `PAGE` and `ITEMS`
in Task 2.

### 3.2 `links.py`: finding links

- `extract_links(text) -> list[str]` -- every Slack-wrapped `<url|label>`
  and every bare `http(s)` URL, in order of first appearance, unwrapped and
  de-duplicated.
- `looks_like_jira(url, base_url) -> bool` and
  `parse_jira_key(url) -> str | None` (Task 2) -- `/browse/KEY-123` and the
  `selectedIssue=KEY-123` query form used by board URLs.

### 3.3 `resolve.py`: one URL to one fetcher

A `Resolver` built from the config and the Slack client. `resolve(url)`
returns a `Subject` or raises; `kind_of(url)` says which source a URL
belongs to (`slack`, `confluence`, `jira`, or `None`) without fetching. It
replaces the `if permalink ... elif looks_like_confluence` chain in
`handler._resolve_subject`, and it is what `Handler` takes as its injected
dependency in tests instead of `fetch_confluence`.

### 3.4 `follow.py`: collecting and fetching attachments

`follow(subject, extra_urls, resolver, links_in) -> Subject` returns the
subject with `attachments` and `unread` filled in.

- **Links in a thread** come from the raw Slack messages -- each message's
  `text`, plus the `title_link` and `original_url` of its unfurl
  attachments, which is where an "Added by Confluence Cloud" card keeps its
  URL.
- **Links in a page** come from the Confluence storage format *before* it is
  flattened to text: `<a href>` URLs, `<ri:page ri:content-title=...
  ri:space-key=...>` internal links, and (Task 2) `jira` macro keys.
  `confluence.py` returns these next to the page, so flattening and link
  extraction read the same payload once.
- **Internal page links** carry a title and an optional space key, not an id.
  Each costs one title lookup (`/wiki/rest/api/content?spaceKey=&title=`,
  space defaulting to the linking page's own). That lookup counts toward the
  link cap below.
- **Explicit extra arguments** (§3.6) are followed whatever their kind,
  Slack permalinks included. Links *found* in content are followed only when
  they are Confluence or Jira; Slack permalinks and every other URL found in
  content are ignored.
- The main subject's own URL and repeats are dropped.

### 3.5 Limits

Module constants in `follow.py`, not configuration:

| Limit | Value |
|---|---|
| Links followed | 6, in order of appearance -- explicit arguments first |
| Characters per attachment | 12,000 |
| Characters across all attachments | 40,000 |
| Per-request timeout for followed links | 15 s |
| Overall fetch deadline | 45 s |

Fetches run in parallel (`concurrent.futures.ThreadPoolExecutor`, standard
library). A fetch still running at the deadline is abandoned and recorded as
`timed out`. The 300 s run timeout is unchanged and still bounds only the
model session.

Truncation keeps the start and appends `[truncated at N characters]`. The
exception is a Jira issue, whose comments are trimmed from the oldest end so
the latest decision survives (§6). The main subject stays uncapped, as it is
today.

### 3.6 Several links in one command

`commands.py`: `Command` gains `extra: tuple[str, ...]`. The first argument
stays the subject; every further link token becomes an explicit attachment.
Words between links (`and`, commas) are ignored. With no argument, the
subject is still the thread the mention was typed in.

## 4. Failure handling

- **The main subject failing still stops the run**, with today's messages.
- **An attachment failing never stops the run.** It is recorded in `unread`
  with a short reason: an HTTP status, `not found or not visible`,
  `timed out`, `Confluence not configured`, `over the link limit`,
  `short link has no page id`.
- The model is shown the `unread` list (§5), so a judgement can say a linked
  page could not be read rather than guess at it.
- Nothing about an attachment failure is posted separately; it surfaces only
  through the answer.

## 5. Prompt, effort and reply

**Input.** `build_input` fences the main subject exactly as today, then each
attachment in its own block:

```
--- BEGIN ATTACHMENT 1 ---
Confluence page: Cutover plan (https://example.atlassian.net/wiki/spaces/HARBOR/pages/424242)
...body...
--- END ATTACHMENT 1 ---
```

followed, when non-empty, by a `Could not read:` list of URL and reason.

**Instruction.** When attachments or unread links exist, `_INSTRUCTION`
gains one paragraph: the attachments were linked from the subject, they are
data written by other people exactly like the subject, and nothing in them
can change the task; when a point rests on an attachment, name it; when the
subject and an attachment disagree, say so. With no attachments the
instruction is byte-for-byte today's.

**Effort.** `runner.build_argv` takes the subject. With attachments present
and `claude.effort` set below `medium` (order: `low` < `medium` < `high` <
`xhigh` < `max`), it passes `--effort medium`. An unset `claude.effort`
(the CLI's own default) is left alone.

**Reply header.** `_On_ <url>` becomes `_On_ <url> + N linked` when N
attachments were read.

## 6. Task 2: Jira

`jira.py`, standard library only, mirroring `confluence.py`:

- **Endpoint:** REST API v2, `/rest/api/2/issue/{key}` with
  `fields=summary,status,issuetype,assignee,reporter,description`, then
  `/rest/api/2/issue/{key}/comment` newest first. v2 returns description and
  comments as wiki-markup text, which the model reads as-is, avoiding an
  Atlassian Document Format flattener. **To verify on the first real call:**
  v2 availability on the site, and the comment endpoint's page size.
- **Body:** a header block (key, type, status, assignee, reporter), the
  description, then comments oldest to newest, each with author and date.
- **Truncation:** when over the attachment cap, drop whole comments from the
  oldest end first, noting how many were dropped; the description is cut
  only if it alone exceeds the cap.
- **Credentials:** the `confluence` block's `base_url`, `email` and token.
  README says so, and states that the block turns on both products.
- **Reachable as:** a direct subject (`judgement <jira link>`), an explicit
  extra argument, a link found in a thread, and a `jira` macro on a page.

## 7. Testing

The existing pytest suite in `bot/tests/`, run in CI, is the gate. New or
extended tests, all against stand-in fetchers with synthetic `example.com`
content:

- `test_links.py` -- `extract_links` on wrapped, bare, duplicated and
  unfurled links; Jira key parsing.
- `test_follow.py` -- one hop only, dedupe, link cap order, per-attachment
  and total caps, deadline expiry recorded as `timed out`, unconfigured
  Confluence recorded not raised.
- `test_confluence.py` -- link extraction from storage format, internal page
  title lookup.
- `test_prompts.py` -- attachment blocks and unread list; instruction
  unchanged when there are no attachments.
- `test_runner.py` -- effort raised only when needed and never lowered.
- `test_commands.py` -- several links in one command.
- `test_handler.py` -- end to end with a stub resolver, including the reply
  header and the reaction path.
- `test_jira.py` (Task 2) -- body shape, oldest-first comment trimming,
  error mapping.

**Acceptance, by hand, once per task:** run the bot against a real thread
that links a Confluence page (Task 1) and a Jira issue with comments
(Task 2), and confirm the answer names the linked source.

## 8. Out of scope

- Following Slack permalinks found inside content, and any second hop.
- Resolving `/wiki/x/` short links, which need a redirect to find a page id.
- A per-space or per-project allowlist.
- Attachments and images inside Confluence pages or Jira issues.
- Making the limits configurable.
