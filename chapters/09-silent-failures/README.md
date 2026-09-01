# Chapter 9: Silent Failures

Domain 5 is 15% of the exam: the smallest weight, nine questions, and where
close-fail candidates lose. Most people study it least because the weight is
lowest. That is the trap, and the exam writers know it.

## What you build

A drop-in detector that wraps any Claude agent with three mechanisms:

| | Mechanism | Catches | Needs a key? |
|---|---|---|---|
| 1 | Assertion validators | rules the schema cannot express, like a payment term with no currency or a date ten years out | no |
| 2 | Golden-set regression | drift: a change that broke something a previous version got right | no |
| 3 | LLM-as-judge | a fluent, correctly-cited answer that summarises the wrong paragraph | yes |

Use one and you fail the stem that grades the other two.

## The one command

```
python3 silent_failure_detector.py --demo-regression
```

**No key. No network.** It runs Mechanism 2 against a local stand-in that
mislabels two of eight cases, and you watch the diff fire:

```
  [drift] gs-02
          expected 'outage', got 'billing'
  [drift] gs-05
          expected 'outage', got 'billing'

  2 of 8 drifted.
```

The stand-in is three lines of Python and it says so. Nothing is calling
Claude here, and nothing pretends to. What it demonstrates is that the runner
catches drift, which is a property of the runner.

Then:

```
export ANTHROPIC_API_KEY="sk-ant-..."
python3 silent_failure_detector.py --judge "When does the lease break?" "The lease has no break clause."
```

That one is a real Haiku 4.5 call on your own credit. Cheap at 512 max tokens,
but yours.

## What success looks like

1. `--demo-regression` shows exactly two drifts and exits 0.
2. `--scenarios` lists five planted failures, each one schema-valid and wrong.
3. You point your own agent at those five and **at least four trip a flag**,
   through an assertion, a low judge confidence, or a golden-set diff.
4. The fifth probably slips through. Write it down in `failure_modes.md` as a
   known false negative rather than rounding it to zero. The residual rate is
   real and pretending otherwise is itself a silent failure.

Thresholds are the book's: below 0.7 flags for human review, below 0.5 refuses
and takes the fallback path.

## How to run it on your own agent

```python
from silent_failure_detector import SilentFailureDetector

detector = SilentFailureDetector(
    agent=your_agent,                       # anything with .run(input)
    samples_path="samples/golden_set.json",
    expected_path="samples/golden_set_expected.json",
)

result = detector.check(question, answer)   # Mechanism 3
if result["flag"]:
    log(result); surface_with_reviewer_tag(answer)

drift = detector.regression()               # Mechanism 2, keyless, run in CI
```

The real transfer step is the golden set, not the code. Pin eight to ten inputs
from your own system whose correct outputs you are certain of, commit them, and
run the regression on every change. It grows every time you find a new failure
mode, and that is what makes it an architecture rather than a test suite.

Copy `silent_failure_detector.py` and `samples/` into your own `cca-f-prep` and
tag the commit `ch09-silent-failure-complete`.

## One thing assembled that the book prints in pieces

ch09:160-178 shows the detector class on its own. As printed it has a
`validated = answer` line that is assigned and never used, and it calls
`judge()` and `golden_set_regression()` without importing them. Both are
defined earlier in the chapter, so the class is correct in context and not
standalone. This file is the whole module with the three mechanisms in it,
which is what "drop-in" has to mean. The dead assignment became a comment
explaining what it was pointing at: by the time `check()` runs, Mechanism 1 has
already had its say, because constructing the Pydantic model is what raises.
