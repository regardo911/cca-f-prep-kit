#!/usr/bin/env python3
"""Three-mechanism silent-failure detector — Chapter 9.

A silent failure is an output that is *valid* and *wrong*. Nothing throws.
Nothing logs. The schema validates, the Pydantic model is happy, the dashboard
is green, and the customer finds it on Monday.

Three mechanisms, and the exam grades whether you name all three:

  1. Assertion-based output validation  — @field_validator, no key
  2. Golden-set regression              — diff against pinned outputs, no key
  3. LLM-as-judge                       — a Haiku 4.5 critique pass, needs a key

Mechanisms 1 and 2 are pure Python. Mechanism 3 is a real Claude call.

    pip install anthropic pydantic
    python3 silent_failure_detector.py --demo-regression   # keyless
    export ANTHROPIC_API_KEY="sk-ant-..."
    python3 silent_failure_detector.py --judge "question" "answer"
    python3 silent_failure_detector.py --scenarios         # the five planted

The chapter prints the detector class in isolation, which leaves it with an
unused `validated` binding and calls to `judge()` and `golden_set_regression()`
that the snippet never imports. This file is the whole module with those pieces
wired together, which is what "drop-in for any Claude agent" needs to mean.
"""

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, field_validator

SAMPLES = Path(__file__).parent / "samples"


# --- Mechanism 1: assertions. Pure Python, no key. -------------------------

class ContractInfo(BaseModel):
    """ch09:37-52. Domain rules the schema cannot express."""

    payment_terms: str
    effective_date: date

    @field_validator("payment_terms")
    def must_name_currency(cls, v):
        currencies = ["USD", "EUR", "GBP", "JPY", "CHF"]
        assert any(c in v for c in currencies), \
            f"payment_terms missing currency: {v}"
        return v

    @field_validator("effective_date")
    def must_be_within_decade(cls, v):
        assert v <= date.today() + timedelta(days=365 * 10), \
            f"effective_date too far in future: {v}"
        return v


# --- Mechanism 2: golden-set regression. Pure Python, no key. --------------

def golden_set_regression(agent, samples_path: Path, expected_path: Path):
    """ch09:65-77, verbatim.

    `agent` is anything with a `.run(input)`. It does not have to be a Claude
    agent — that is the point of the interface.
    """
    samples = json.loads(samples_path.read_text())
    expected = json.loads(expected_path.read_text())
    failures = []
    for sample_id, sample_input in samples.items():
        actual = agent.run(sample_input)
        if actual != expected[sample_id]:
            failures.append({
                "id": sample_id,
                "expected": expected[sample_id],
                "actual": actual,
            })
    return failures


# --- Mechanism 3: LLM-as-judge. Needs the reader's own key. ----------------

class JudgeVerdict(BaseModel):
    quality: Literal["good", "questionable", "bad"]
    reason: str
    confidence: float


def judge(question: str, answer: str) -> JudgeVerdict:
    """ch09:96-114. A real Haiku 4.5 call on your own credit."""
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.parse(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": f"""You are an output critic. Judge whether the answer
is correct, complete, and grounded for the question.

Question: {question}
Answer: {answer}

Rate quality and explain. Return the schema."""
            }
        ],
        output_format=JudgeVerdict,
    )
    return response.parsed_output


# --- The detector: all three, around any agent. ---------------------------

class SilentFailureDetector:
    """ch09:160-178, assembled.

    Thresholds are the book's: below 0.7 flags for human review, below 0.5
    refuses and triggers the fallback path.
    """

    def __init__(self, agent, samples_path, expected_path,
                 judge_threshold=0.7, refuse_threshold=0.5):
        self.agent = agent
        self.samples_path = Path(samples_path)
        self.expected_path = Path(expected_path)
        self.judge_threshold = judge_threshold
        self.refuse_threshold = refuse_threshold

    def check(self, question: str, answer):
        # Mechanism 1 has already run by the time you get here: constructing
        # the Pydantic model raises on validator failure, so an `answer` that
        # reaches this method is one the assertions accepted. That is what the
        # chapter's dead `validated = answer` line was gesturing at.
        verdict = judge(question, str(answer))
        if verdict.confidence < self.refuse_threshold:
            return {"flag": True, "action": "refuse",
                    "reason": verdict.reason, "confidence": verdict.confidence}
        if verdict.confidence < self.judge_threshold:
            return {"flag": True, "action": "review",
                    "reason": verdict.reason, "confidence": verdict.confidence}
        return {"flag": False, "confidence": verdict.confidence}

    def regression(self):
        return golden_set_regression(self.agent, self.samples_path,
                                     self.expected_path)


# --- A keyless demonstration of Mechanism 2 -------------------------------

class _DriftingAgent:
    """Not a model. A three-line local function that gets two answers wrong.

    Nothing here calls Claude, and nothing here pretends to. The point is to
    show that the golden-set runner catches a drift, which is a property of the
    runner, not of any agent.
    """

    def __init__(self, drift_on):
        self.drift_on = set(drift_on)
        self._n = 0

    def run(self, sample_input):
        self._n += 1
        if self._n in self.drift_on:
            return "billing"
        return sample_input["correct_label"]


def demo_regression():
    samples = SAMPLES / "golden_set.json"
    expected = SAMPLES / "golden_set_expected.json"
    agent = _DriftingAgent(drift_on={2, 5})
    failures = golden_set_regression(agent, samples, expected)
    print("\nMechanism 2, run locally. No key, no network, no Claude — the")
    print("'agent' is a three-line stand-in that deliberately mislabels two")
    print("cases so you can watch the diff fire.\n")
    total = len(json.loads(samples.read_text()))
    for f in failures:
        print(f"  [drift] {f['id']}")
        print(f"          expected {f['expected']!r}, got {f['actual']!r}")
    print(f"\n  {len(failures)} of {total} drifted.\n")
    print("In CI this runs on every commit, against outputs you pinned when")
    print("they were right. A non-empty diff means a change broke something a")
    print("previous version got correct — before the customer finds it.\n")
    return 0


def show_scenarios():
    path = SAMPLES / "silent_failures.json"
    data = json.loads(path.read_text())
    print(f"\n{len(data)} planted scenarios in {path.name}. Each one is "
          f"schema-valid\nand wrong, which is the whole definition.\n")
    for sid, case in data.items():
        print(f"  {sid}: {case['planted_failure_mode']}")
        print(f"      in:       {case['input']}")
        print(f"      expected: {case['expected_output']}")
        print()
    print("Run your own agent against these and count how many trip a flag.")
    print("The book's bar is four of five. The fifth is the residual false-")
    print("negative rate — document it rather than pretending it is zero.\n")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--demo-regression", action="store_true",
                    help="run Mechanism 2 against a local stand-in agent "
                         "(keyless)")
    ap.add_argument("--scenarios", action="store_true",
                    help="print the five planted silent-failure scenarios "
                         "(keyless)")
    ap.add_argument("--judge", nargs=2, metavar=("QUESTION", "ANSWER"),
                    help="run Mechanism 3 on one question/answer pair "
                         "[needs your ANTHROPIC_API_KEY]")
    args = ap.parse_args()

    if args.demo_regression:
        return demo_regression()
    if args.scenarios:
        return show_scenarios()
    if args.judge:
        verdict = judge(*args.judge)
        print(f"\nquality:    {verdict.quality}")
        print(f"confidence: {verdict.confidence}")
        print(f"reason:     {verdict.reason}\n")
        if verdict.confidence < 0.5:
            print("Below 0.5 — refuse and take the fallback path.\n")
        elif verdict.confidence < 0.7:
            print("Below 0.7 — flag for human review.\n")
        return 0

    ap.print_help()
    print("\nNothing to do without a mode. --demo-regression needs no key.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
