# Tensei

[Home](../../README.md) · [Install](install.md) · [Commands](commands.md) · [Writing](writing.md) · [Ledger](ledger.md) · [Reviewing](reviewing.md) · **Tensei** · [Your data](your-data.md) · [Slack bot](slack-bot.md) · [FAQ](faq.md) · [Why](why.md)

> **In short:** optional. Tensei is the Daikenja way of working, for every
> Claude Code session on your computer -- not only Daikenja's. Answers lead
> with the finding, push back on a wrong premise and say how sure they are;
> design advice lists every option, ranked; and nothing others can see goes
> out without your yes. `/daikenja:tensei` shows what will change and asks
> once.

## The difference, side by side

The same request, made twice. Both answers are illustrations written for this
page, not captured sessions; the first is a deliberately familiar shape:
long, confident, one plan -- and it keeps growing.

> *Our website has got slow. Let's move it to a bigger server.*

<details>
<summary><b>Without Tensei</b> -- long, certain, escalating, no questions (click to expand)</summary>

> Great idea! Moving to a bigger server is a solid way to speed up your site
> and prepare for growth. Here's a step-by-step plan:
>
> 1. **Choose a larger machine** -- for example, go from 2 CPUs and 4 GB of
>    memory to 8 CPUs and 32 GB.
> 2. **Snapshot the current server** so you can roll back.
> 3. **Create the new server** from the snapshot and test it.
> 4. **Point your domain at the new server** and wait for DNS to update.
> 5. **Shut down the old one** once traffic has moved.
>
> For future scale, you should also put a **load balancer** in front of two
> or more servers, so traffic is shared and one failure does not take the
> site down. And as you grow, consider moving to **Kubernetes**, so the site
> scales up and down automatically:
>
> ```yaml
> apiVersion: autoscaling/v2
> kind: HorizontalPodAutoscaler
> spec:
>   minReplicas: 2
>   maxReplicas: 10
> ```
>
> With this in place, your website will be much faster and ready for any
> amount of traffic. Want me to start the migration?

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
> ❓ **Query:** slow all the time, or only at busy hours? Busy hours points at
> the server.

</details>

What changed: the risk is labelled before anything else; the request was
checked before it was followed; each option says whether it is checked or
assumed, and the constraints are named; the move you asked for is still on
the list, ranked against cheaper fixes; and the one question that separates a
page problem from a server problem comes last. (In a real session that
question comes as buttons.) Nothing escalated to Kubernetes.

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
- **A big design is reviewed before you see it.** When the advice is a
  lasting decision -- architecture, an interface, a contract, a process --
  helper models check it first from the angles a plan gets checked from:
  simplicity always, plus architecture, security or operations when the
  design touches them. You see one line when nothing changes
  (`Lenses: Simplicity, Architect -- no change`), a finding only when it
  changes the advice, and a warning when the design cannot work. Routine
  choices get no review.

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
