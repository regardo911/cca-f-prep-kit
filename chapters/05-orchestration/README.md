# Chapter 5: Orchestration

The second half of Domain 1, overlapping Domain 4. Cost, validity, resilience,
in that order.

## What you build

A batch companion to the Chapter 4 coordinator, plus the two upgrades that go
back into `multi_agent_starter.py` itself: a Pydantic schema on the Researcher's
response, and a retry wrapper around every Claude call.

The Chapter 5 upgrades to the starter live in
[`../04-agentic-architecture/multi_agent_starter.py`](../04-agentic-architecture/multi_agent_starter.py)
under `--mode typed`, because that is where the book puts them. Step 1 says
"open the `multi_agent_starter.py` from Chapter 4." Both paths ship so you can
run each and see what changes.

## The one command

```
export ANTHROPIC_API_KEY="sk-ant-..."
python3 multi_agent_batch.py
```

**Spends your own credit.** Three Opus requests at 2,048 max tokens, submitted
as one batch. It prints the batch id and the three queries it sent, then stops.

It does not print what the batch cost. That number lives in Anthropic's billing
console, and a script that printed one here would be making it up.

## What success looks like

1. A batch id comes back. That is the whole synchronous part of the exercise.
2. The batch completes, usually inside an hour. Three queries is fast.
3. On your Anthropic console, the batch's cost is **half** what the same three
   queries would have cost synchronously. That is the fifty-percent figure, and
   confirming it yourself is worth more than reading it again here.
4. You can say out loud why it is fifty and not thirty, and why it applies to
   Haiku exactly as much as to Opus.

Read [cost-notes.md](cost-notes.md) before the mock. Domain 1 and Domain 4
together are 47% of the exam and the cost-lever questions sit right in the
middle of them.

## How to run it on your own work

```
python3 multi_agent_batch.py my-queries.txt
```

One query per line. The real exercise is picking the file: go through a workload
you actually run and split it into the calls where somebody is waiting and the
calls where nobody is. The second list is your batch list, and routing it is a
fifty-percent cut with no code change beyond the endpoint and the `custom_id`
plumbing.

Copy `multi_agent_batch.py` into your own `cca-f-prep` beside the starter, and
tag the commit `ch05-orchestration-complete`.
