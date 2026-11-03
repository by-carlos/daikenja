# Tensei

[Home](../../README.md) · [Install](install.md) · [Commands](commands.md) · [Writing](writing.md) · [Ledger](ledger.md) · [Reviewing](reviewing.md) · **Tensei** · [Your data](your-data.md) · [Slack bot](slack-bot.md) · [FAQ](faq.md) · [Why](why.md)

> **In short:** optional. Tensei is the Daikenja way of working, for every
> Claude Code session on your computer -- not only Daikenja's. Answers lead
> with the finding, push back on a wrong premise and say how sure they are;
> design advice lists every option, ranked, and a lasting design is reviewed
> before you see it; advice respects what your project's ledger already
> decided; and nothing others can see goes out without your yes. `/daikenja:tensei` shows what will change and asks
> once.

## The difference, side by side

The same request, made twice. Both answers are illustrations written for this
page, not captured sessions. The first is a familiar shape: nothing in it is
wrong, and the right check is even in there -- buried mid-paragraph, under
everything else the model knows, with the risk mentioned after the commands
that cause it.

> *Our website has got slow. Let's move it to a bigger server.*

<details>
<summary><b>Without Tensei</b> -- everything at once, the key check buried, the risk last (click to expand)</summary>

> Great question, and a very reasonable instinct! Upsizing can definitely
> help, and it's usually the quickest lever to pull, but whether it actually
> fixes things depends a lot on where the slowness is coming from. Websites typically get slow for a handful of reasons: the
> server itself is out of CPU or memory (in which case a bigger instance helps
> directly), the database is struggling with unindexed queries or too many
> connections, large unoptimized images and JavaScript bundles are making
> pages heavy, there's no caching layer so every request is rendered from
> scratch, or a third-party script is blocking the page. It could also be
> network latency if most of your users are far from where the server is
> hosted. A quick way to get a sense of it is to check load on the box:
>
> ```bash
> uptime
> free -h
> top -o %CPU
> ```
>
> If the load average is consistently above the number of cores, the server
> is likely the bottleneck. If not, it's probably something else, though it's
> also worth turning on the slow query log if you're on MySQL:
>
> ```sql
> SET GLOBAL slow_query_log = 'ON';
> SET GLOBAL long_query_time = 1;
> ```
>
> In terms of alternatives, there are a few directions depending on your
> setup and budget. You could scale vertically, which is what you're
> suggesting -- simple, but it has a ceiling. You could scale horizontally
> behind a load balancer, which gives you redundancy too but needs the app to
> be stateless (sessions in Redis rather than on disk, for example). A CDN
> like Cloudflare or CloudFront would offload static assets and could make a
> big difference for far-away users, and Varnish or a Redis object cache
> would help if pages are expensive to generate. If you're on WordPress, a
> caching plugin is often the single biggest win. Longer term, containerizing
> and moving to a managed platform with autoscaling (ECS, Kubernetes, or
> something like Render or Fly.io) would let you absorb spikes without
> overprovisioning, though that's a bigger lift.
>
> Given all that, I'd say the best approach is probably a combination: go
> ahead with the bigger server now since it's low-risk and buys you headroom,
> put a CDN in front for the static assets, and then profile the application
> to find any slow queries or endpoints. Here's what the resize would look
> like on AWS:
>
> ```bash
> aws ec2 stop-instances --instance-ids i-0abc123
> aws ec2 modify-instance-attribute --instance-id i-0abc123 \
>   --instance-type '{"Value": "m5.2xlarge"}'
> aws ec2 start-instances --instance-ids i-0abc123
> ```
>
> Keep in mind that stopping the instance takes the site offline for a few
> minutes, and if you're not using an Elastic IP the public IP will change,
> so you'd need to update DNS. Let me know if you'd like me to go ahead with
> the resize, set up the CDN, or dig into the database first!

</details>

<details open>
<summary><b>With Tensei</b> -- risk labelled, premise checked, options ranked</summary>

> ⚠️ **Warning:** **RISKY** -- moving a live site risks downtime, and the move
> may not fix the slowness. It waits for your yes.
>
> ℹ️ **Notice:** check before you move. A slow site is usually heavy images,
> one slow page or a slow database query -- a bigger server would likely not
> fix those, and costs more every month.
>
> 💬 **Answer:** two quick checks first: run a free speed test on the slowest
> page, and look at the server's CPU and memory use. Then, best first:
>
> 1. **Shrink the images** -- cheapest. *Assumed* until the test confirms it.
> 2. **Fix the one slow page or query.** *Assumed.*
> 3. **Add caching** (ready-made copies of pages) **or a CDN** (copies served
>    from closer to each visitor). *Assumed.*
> 4. **Move to a bigger server** -- helps only if the server runs flat out.
>    *Assumed -- unverified.*
>
> Constraints: the budget is a setting you control; that the site is one
> server you can resize is assumed.
>
> Reviewed for simplicity, architecture and operations -- no change.
>
> ❓ **Query:** slow all the time, or only at busy hours? Busy hours points at
> the server.

</details>

What changed: no opening praise; the downtime risk opens the answer instead of trailing the
commands that cause it, and nothing calls the move "low-risk" first; the
check that was buried mid-paragraph is now the first thing to do; nothing
assumes AWS, MySQL or WordPress you never mentioned; each option says whether
it is checked or assumed, and the constraints are named; the move you asked
for is still on the list, ranked against cheaper fixes instead of bundled
with them; because hosting is a lasting decision, the ranking was reviewed
before you saw it; and the closing menu of three things to do is replaced by
the one question that separates a page problem from a server problem. (In a
real session that question comes as buttons.)

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
- **One question, with its context.** It asks only when the answer changes
  what happens next, says what is being decided and what each choice
  changes, and offers short answers as buttons.
- **Suggestions lead with the idea and are made once.** The first clause
  carries the whole suggestion so you can drop it while skimming; a no
  closes it for the session.

**Design advice**

- **Every option weighed is shown, rejected ones included**, numbered and
  ranked best-first, so "go with 2" works.
- **Each reason is marked *verified* or *assumed***, and the constraints are
  named as fixed facts or as settings someone could change.
- **A big design is reviewed before you see it.** When the advice is a
  lasting decision -- architecture, an interface, a contract, a process --
  helper models check it first from the angles a plan gets checked from:
  simplicity always, plus architecture, security or operations when the
  design touches them. You see one line when nothing changes
  ("Reviewed for simplicity and architecture -- no change"), a finding only when it
  changes the advice, and a warning when the design cannot work. Routine
  choices get no review.

**Your project's record**

- **Advice starts from what is already decided** -- the project's ledger,
  what you said earlier in the session -- and names a recorded decision it
  goes against ("the ledger says schema changes are frozen until the
  rollout completes") instead of quietly overriding it. Nothing the ledger already answers is asked again.
- **Work conversations go to the matching Daikenja skill** -- a pasted
  thread, a meeting transcript, a document up for review -- rather than an
  improvised version of its job, and a decision worth keeping gets one offer
  to log it. In coding, only lasting decisions get that offer.
- Plain questions get none of this, and without a ledger it stays silent.

**Working practice**

- **Anything others can see needs your explicit yes, every time** --
  comments, issues, pull requests, messages.
- **It reads before it works elsewhere:** another repository's `CLAUDE.md`
  first, large files and logs through a search or a script rather than whole.
- **Big reading jobs go to a cheaper helper model**, which hands back a
  short digest.
- **A fix you would have to repeat next week is treated as a symptom**, and
  it keeps looking for what actually broke.
- **The smallest change that works.** A plan in one to three lines before a
  non-trivial edit, then the edit -- no unasked renaming or cleanup.

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
Daikenja folder (`~/.claude/daikenja/`), with `plan-review-lenses.md` beside
it (the review angles the design check reads), and adds one line to the end of your
personal Claude instructions file, `~/.claude/CLAUDE.md` (skipped if it is
already there), so every session from the next one loads it.

**Your edits are safe.** Tensei is content the plugin keeps improving.
Running the skill again shows only what changed and asks *"Adopt the updated
way of working?"*:

- a copy you have not edited can be updated to the new one;
- a copy you **have** edited is never overwritten without asking;
- anything replaced is backed up first, under `~/.claude/backups/`.

**Removing it.** Run `/daikenja:tensei` and ask to remove it. It backs up
Tensei and your `CLAUDE.md`, offers to delete Tensei and its lens file, and
takes out the line
it added -- a line you wrote by hand is left alone.

It runs only when you type the command: a skill that edits the instructions
file every session reads should never start on its own.
