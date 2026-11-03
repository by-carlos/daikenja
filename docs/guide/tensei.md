# Tensei

[Home](../../README.md) · [Install](install.md) · [Commands](commands.md) · [Writing](writing.md) · [Ledger](ledger.md) · [Reviewing](reviewing.md) · **Tensei** · [Your data](your-data.md) · [Slack bot](slack-bot.md) · [FAQ](faq.md) · [Why](why.md)

> **In short:** optional. Tensei is the Daikenja way of working, for every
> Claude Code session on your computer -- not only Daikenja's. Answers lead
> with the finding, push back on a wrong premise and say how sure they are;
> design advice lists every option, ranked; and nothing others can see goes
> out without your yes. `/daikenja:tensei` shows what will change and asks
> once.

## The difference, side by side

The same question, asked twice. Both answers are illustrations written for
this page, not captured sessions; the first is a deliberately familiar shape:
long, confident, one plan.

> *Our dashboard has got slow. Should I put Redis in front of Postgres?*

<details>
<summary><b>Without Tensei</b> -- long, certain, one plan, no questions (click to expand)</summary>

> Great question! Adding a Redis cache in front of PostgreSQL is an excellent
> way to speed up a slow dashboard. Redis is an in-memory data store, so reads
> are dramatically faster than hitting the database every time.
>
> Here's a step-by-step plan:
>
> 1. **Install Redis** with Docker: `docker run -d -p 6379:6379 redis:7`.
> 2. **Add a client library**, such as `redis-py` for Python.
> 3. **Wrap your dashboard queries** in a cache-aside pattern: check Redis
>    first, and on a miss, query Postgres and store the result with a TTL.
> 4. **Choose TTLs** -- 60 to 300 seconds works well for most dashboards.
> 5. **Handle invalidation** by deleting keys when the underlying data
>    changes.
> 6. **Monitor your hit rate** with `INFO stats`.
>
> ```python
> def get_dashboard_data(user_id):
>     key = f"dashboard:{user_id}"
>     cached = r.get(key)
>     if cached:
>         return json.loads(cached)
>     data = run_dashboard_query(user_id)
>     r.setex(key, 300, json.dumps(data))
>     return data
> ```
>
> With this in place, your dashboard should load significantly faster, and
> you'll reduce the load on your database as well. Let me know if you'd like
> help with any of these steps!

</details>

<details open>
<summary><b>With Tensei</b> -- finding first, premise checked, options ranked</summary>

> ℹ️ **Notice:** measure before you cache. A slow dashboard is usually one
> slow query, and a cache hides that query instead of fixing it.
>
> 💬 **Answer:** not yet. Run `EXPLAIN ANALYZE` on the dashboard's slowest
> query first. If it shows a sequential scan on a large table, an index is
> likely the whole fix -- *likely*, not certain: I have not seen your schema.
> Then choose:
>
> 1. **Index the slow query** -- cheapest, no new service to run.
>    *Assumed* until the query plan confirms it.
> 2. **A materialized view, refreshed every few minutes** -- fits if the data
>    can be a few minutes old. *Assumed.*
> 3. **Redis in front of Postgres** -- adds a service to run, cache
>    invalidation, and stale-data bugs. Worth it only if the index and the
>    view both fall short. *Assumed.*
>
> Constraints: Postgres stays the store (a fixed fact); how fresh the
> dashboard must be is unknown, and probably a setting someone picked rather
> than a requirement.
>
> ❓ **Query:** if the index is not enough, how fresh does the dashboard need
> to be? That decides between the view and Redis.

</details>

What changed: the premise was checked before the how-to; the answer says what
is certain and what is assumed; the option you asked about is still on the
list, ranked against the alternatives; and the one question that decides
between the last two comes last.

## What it changes

Tensei shapes **how Claude talks to you and how it works**. What it writes for
others -- messages, documents, ledger lines, commit text -- keeps following its
own rules, with one exception: anything a person will read must make sense
without the earlier conversation.

**Answers**

- **Headline first, then stop.** The first line carries the finding,
  complete enough to act on; the default answer is that line plus a few
  sentences. Ask for more and you get full depth.
- **The premise is checked first.** If the question rests on something wrong,
  that is the answer.
- **Certain, likely or guessing** -- it says which, and checks rather than
  stating a guess as fact.
- **The cold-read test.** Every message makes sense to someone who read none
  of the earlier ones: things are named in words, not "item 3" or "the point
  above".
- **Long output goes to a file**, with a short summary in the reply; a
  revision shows only the paragraph that changed.
- **Labelled parts.** Notices, reports, suggestions and warnings are always
  labelled; the answer and the question are labelled when a response has
  several parts. A risk is never buried under an answer:

  ```
  💬 Answer:  the direct response
  ℹ️ Notice:  the premise is off, or something outranks the ask
  📋 Report:  what was done
  💡 Suggestion:  unprompted advice, offered once
  ⚠️ Warning:  a risk, always shown, never cut for brevity
  ❓ Query:  a question whose answer changes what happens next
  ```

  An action against live systems or data outside your project folder opens
  with a **SAFE / RISKY / DESTRUCTIVE** label, above the command.

**Design advice**

- **Every option weighed is shown, rejected ones included**, numbered and
  ranked best-first, so "go with 2" works.
- **Each reason is marked *verified* or *assumed***, and the constraints are
  named as fixed facts or as settings someone could change.

**Working practice**

- **Anything others can see needs your explicit yes, every time** --
  comments, issues, pull requests, messages.
- **It reads before it works elsewhere:** another repository's `CLAUDE.md`
  first, large files and logs through a search or a script rather than whole.
- **Big reading jobs go to a cheaper helper model**, which hands back a
  short digest.
- **A fix you would have to repeat next week is treated as a symptom**, and
  it keeps looking for what actually broke.

Your own `CLAUDE.md` still wins wherever the two differ. The full text is
[`templates/tensei.md`](../../templates/tensei.md).

## Adopt, update, remove

Run `/daikenja:tensei`. It needs no other Daikenja setup, and
`/daikenja:setup-user` mentions it once, at the end, if you do not have it.

**One acknowledgement.** It shows five to eight plain lines on what the agent
will do differently, then asks *"Adopt this way of working?"*. Your answer is
recorded only on your computer, as the time you adopted it and a fingerprint
of the version.

**What it changes on your computer.** It saves Tensei as `tensei.md` in your
Daikenja folder (`~/.claude/daikenja/`), and adds one line to the end of your
personal Claude instructions file, `~/.claude/CLAUDE.md` (skipped if it is
already there), so every session from the next one loads it.

**Your edits are safe.** Tensei is content the plugin keeps improving.
Running the skill again shows only what changed and asks *"Adopt the updated
way of working?"*:

- a copy you have not edited can be updated to the new one;
- a copy you **have** edited is never overwritten without asking;
- anything replaced is backed up first, under `~/.claude/backups/`.

**Removing it.** Run `/daikenja:tensei` and ask to remove it. It backs up
Tensei and your `CLAUDE.md`, offers to delete Tensei, and takes out the line
it added -- a line you wrote by hand is left alone.

It runs only when you type the command: a skill that edits the instructions
file every session reads should never start on its own.
