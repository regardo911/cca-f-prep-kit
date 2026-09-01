# Chapter 4: Agentic Architecture

Domain 1 is 27% of the exam and this is its reference architecture.

## What you build

A coordinator on Opus 4.7 that does not answer the user. It routes. A Researcher
subagent with `["Read", "Glob", "Grep"]` gathers evidence and returns structured
citations. A Synthesizer subagent with `["Read"]`, narrower still, composes an
answer that cites only what the Researcher found. Because the Synthesizer cannot
search, it cannot invent.

The whole thing hangs on one string. `"Agent"` has to be in the coordinator's
`allowed_tools` or it cannot delegate to anything, no matter how many subagents
you define. That is the single most exam-relevant detail in the chapter, and
`--no-agent-tool` lets you watch it fail.

## The one command

```
pip install claude-agent-sdk anthropic pydantic
export ANTHROPIC_API_KEY="sk-ant-..."
python3 multi_agent_starter.py
```

**This spends your own Anthropic credit.** One run is a handful of Opus and
Haiku calls against the two-paragraph README in `sample-project/`. Cents, not
dollars, but your cents. The script prints the token counts the SDK hands back
and, if it gets them, an estimate against the published per-million rates. It
never prints a figure off your bill, because it cannot read your bill.

What comes back is a stream of messages, not a tidy report: the coordinator
delegating, the Researcher grepping, citations coming back, the Synthesizer
composing. Watch the chain, not the formatting.

## What success looks like

Checkable, in this order:

1. Every file the answer cites exists.
2. Every line range maps to real content in `sample-project/README.md`. Open it
   and check one by hand. Zero hallucinated citations is the bar.
3. The answer covers both paragraphs: the Fly.io region-by-region rollout *and*
   the forward-only-migration exception on rollback. A Synthesizer that only
   found one of them found half the evidence.
4. Then run `python3 multi_agent_starter.py --no-agent-tool`. It should stop
   working. The book says you get one of two failures: the coordinator
   answering without subagent help, or an error about delegation not being
   authorized. It does not say which. Note which one you actually got. That is the
   exam question in Q2 of the mock.

## How to run it on your own project

```
python3 multi_agent_starter.py --project ~/code/your-repo \
  --query "How does this service handle rollback?"
```

Point `--project` at a repo you already know well. You are grading the citations,
so you need to be able to tell a real one from a plausible one at a glance. That
is the whole exercise: the citations look identical either way until you check.

`--mode typed` runs Chapter 5's schema-bound version of the same Researcher call
instead. Same evidence, contractual interface, and a `refusal_reason` field
when there is nothing to cite.

Copy `multi_agent_starter.py` and `sample-project/` into your own `cca-f-prep`
and tag the commit when the citations check out. It carries forward into
Chapters 5, 6, 8, 9 and 12. One artifact, six chapters of compounding depth.
