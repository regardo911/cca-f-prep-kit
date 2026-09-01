# Chapter 8: Structured Output

Domain 4 is 20% of the exam, and the right answer is almost never "write a
better prompt."

## What you build

An extractor that pins a five-field schema, runs against twenty trial
documents, and produces a result log. Four layers, and the exam grades whether
you can put a fix at the right one:

| Layer | What it is | What it catches | What it misses |
|---|---|---|---|
| 1. Prompt | the task and the field names | the easy cases | everything hard |
| 2. Schema | `output_format=ContractInfo` | malformed JSON, missing fields, wrong types, impossible by construction | anything about meaning |
| 3. Validator | `@field_validator` | business rules: a termination clause with no duration, a party name two characters long | a fluent, plausible, wrong value that satisfies every rule |
| 4. Repair loop | retry, 1s/2s/4s | refusals, rate limits, network | nothing about the content |

## The one command

```
pip install anthropic pydantic
export ANTHROPIC_API_KEY="sk-ant-..."
python3 extractor.py
```

**Twenty Opus calls on your own credit.** At 2,048 max tokens against
one-page documents that is well under a dollar at the published rates, but run
`--limit 3` first if you want to see the shape before you spend the rest.

It prints `[valid]` or `[error]` per document and writes the full log to
`results.json`.

## What success looks like

Every call that reaches the model comes back schema-valid. That is not an
achievement, it is the API contract. Anthropic guarantees it when the output
format is set, through constrained sampling at decode time. If you see a
malformed-JSON error, something is wrong with your setup, not with the model.

The interesting number is the other one. Five of the twenty samples were
written with a specific hole in them, and a `[error]` line on those is the
validator doing its job: catching what the schema structurally cannot express.
Those rejections are the wins.

So: read `results.json`, then write one line per rejection into
[failure_modes.md](failure_modes.md). It starts nearly empty because the entries
are your observations of your run. That file is the regression set Chapter 9
tests against.

One sample is a deliberate argument. `15-short-party-name` has a party called
"IQ" and the validator rejects any name under three characters. The extraction
is correct and the rule is wrong. Decide what you would do about it, because a
validator that cries wolf is a validator someone switches off, and that is a
Domain 5 failure waiting to happen.

## How to run it on your own documents

```
python3 extractor.py --samples ~/contracts --out ~/results.json
python3 extractor.py --document ~/contracts/one.txt
```

Any directory of `.txt` files works. The transfer step that matters is not the
path though. It is the schema. Open `extractor.py`, replace `ContractInfo`
with the five fields *your* documents actually have, and write two validators
that encode a rule you know from the domain and the model does not. That pair,
a schema for shape and an assertion for meaning, is the whole architecture, and
it ports to invoices, tickets, resumes, lab reports, anything.

Copy `extractor.py`, `samples/` and `failure_modes.md` into your own
`cca-f-prep` and tag the commit `ch08-structured-extractor`.

## One correction to the printed listing

ch08:167 writes `parties: list[str] = Field(min_length=2)` and hands the model
straight to `output_format`. Pydantic v2 compiles that constraint to `minItems`
in the emitted JSON Schema, and length constraints are on the endpoint's
unsupported list, which the book says itself at ch08:71 and then asks about at
ch08:73. The rule moved into `at_least_two_parties`, a `@field_validator`. Same
rule, Layer 3 instead of Layer 2, which is the architecture the exam question
is testing you on.
