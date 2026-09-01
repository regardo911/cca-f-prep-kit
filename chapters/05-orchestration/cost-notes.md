# The Three Cost Levers, With the Numbers That Are Actually Published

Chapter 5's decision tree, plus the figures the exam grades hardest. Every
number here is one the book prints; nothing on this page is computed for you,
because your token split is yours.

## The tree

Ask one question per call: **does someone need this answer within seconds?**

- **Yes** → synchronous. Full price. Optimize it with caching and a smaller
  model where quality permits, not by trying to force it through Batch. Batch
  latency is minutes to hours.
- **No** → Batch. Fifty percent off input *and* output, uniformly across every
  active model.
- **Either way, is the same long preamble going out on many calls?** → cache it.

The branches compose. A nightly extraction job is batched *and* cached.

## Batch

| | |
|---|---|
| Discount | **50% off input and output**, every active model |
| Endpoint | `https://api.anthropic.com/v1/messages/batches` |
| Max batch | 100,000 requests or 256 MB, whichever comes first |
| Typical latency | under an hour; window expires at 24h; results kept 29 days |
| `max_tokens` | must be at least 1, so no `max_tokens=0` cache pre-warming |

Fifty. Not thirty. Study guides that say thirty guessed, and the exam puts both
numbers in the same option set on purpose.

## Caching

Against Opus 4.7's $5 per million input tokens:

| Operation | Price per million |
|---|---|
| Base input | $5.00 |
| 5-minute cache write | $6.25 |
| 1-hour cache write | $10.00 |
| Cache read | $0.50 |

Cache reads are ninety percent off base. The break-even is two reads; after the
third read on the same block you are saving on every call.

Minimum cacheable size is 4,096 tokens on Opus 4.7 / 4.6 / 4.5 and Haiku 4.5;
2,048 on Sonnet 4.6 and Haiku 3.5; 1,024 on older models. Below the threshold
you cannot cache at all, so the move is to consolidate small prompts into one
canonical preamble that crosses it. Up to four cache breakpoints per request.

Syntax: `cache_control={"type": "ephemeral"}` for five minutes,
`cache_control={"type": "ephemeral", "ttl": "1h"}` for the hour.

## Models

| Model | Input / output per million |
|---|---|
| `claude-opus-4-7` | $5 / $25 |
| `claude-haiku-4-5` | $1 / $5 |

Coordinator on Opus for routing and synthesis judgment, subagents on Haiku for
retrieval. Roughly four times less than an all-Opus stack, with negligible
quality loss on retrieval-shaped subagent work.

## What this page will not give you

A single combined percentage. Batch and caching do compound, but the size of the
compound depends entirely on how your tokens split between the cached preamble
and the rotating content, and only you know that. Two levers, both verified:
**50% on Batch, 90% on cache reads.** Do your own split.

Same reason `multi_agent_batch.py` prints a batch id and then tells you to open
your console. The bill is not a thing this repo can read.
