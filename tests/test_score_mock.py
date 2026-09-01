#!/usr/bin/env python3
"""Scoring maths, and the shuffle's round-trip against the book's key.

Standard library only. No key, no network. Plain `python3 tests/test_score_mock.py`
— the book's own CI runs `python tests/*.py` and teaches no test runner, so
neither does this.
"""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STUDY = ROOT / "study"
LETTERS = "ABCD"

spec = importlib.util.spec_from_file_location(
    "score_mock", STUDY / "score_mock.py")
score_mock = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score_mock)

KEY = json.loads((STUDY / "answer-key.json").read_text())

checks = 0
failures = []


def check(name, condition, detail=""):
    global checks
    checks += 1
    if condition:
        print(f"  [ ok ] {name}")
    else:
        print(f"  [FAIL] {name}  {detail}")
        failures.append(name)


print("\nscoring and shuffle\n")

# --- the key itself --------------------------------------------------------
check("mock has 60 questions", len(KEY["mock"]) == 60, len(KEY["mock"]))
check("diagnostic has 5 questions", len(KEY["diagnostic"]) == 5)

counts = {}
for entry in KEY["mock"].values():
    counts[entry["domain"]] = counts.get(entry["domain"], 0) + 1
check("domain allocation is 16/11/12/12/9",
      counts == {1: 16, 2: 11, 3: 12, 4: 12, 5: 9}, counts)

# --- the shuffle round-trips to the book's own key ------------------------
bad = []
for section in ("mock", "diagnostic"):
    for n, entry in KEY[section].items():
        order = entry["order"]
        if sorted(order) != list(LETTERS):
            bad.append(f"{section} Q{n}: order {order} is not a permutation")
            continue
        # order[i] is the book's letter now printed in slot i, so mapping this
        # repo's answer through order must land on the book's answer.
        if order[LETTERS.index(entry["answer"])] != entry["book_answer"]:
            bad.append(f"{section} Q{n}: {entry['answer']} maps to "
                       f"{order[LETTERS.index(entry['answer'])]}, book says "
                       f"{entry['book_answer']}")
check("every reordering round-trips to the printed book's answer",
      not bad, "; ".join(bad[:3]))

# --- the reorder is what earns its place ----------------------------------
book_dist = {L: 0 for L in LETTERS}
repo_dist = {L: 0 for L in LETTERS}
for entry in KEY["mock"].values():
    book_dist[entry["book_answer"]] += 1
    repo_dist[entry["answer"]] += 1
check("the printed book's answers really are lopsided",
      book_dist["B"] == 47 and book_dist["D"] == 0, book_dist)
check("this repo's answers are flat across A/B/C/D",
      set(repo_dist.values()) == {15}, repo_dist)

# --- the scorer's arithmetic ----------------------------------------------
perfect = {int(n): e["answer"] for n, e in KEY["mock"].items()}
per_domain, wrong = score_mock.score(KEY["mock"], perfect)
check("a perfect sheet scores 60/60",
      sum(v[0] for v in per_domain.values()) == 60 and not wrong)

blank = {}
per_domain, wrong = score_mock.score(KEY["mock"], blank)
check("an empty sheet scores 0/60 and reports 60 missed",
      sum(v[0] for v in per_domain.values()) == 0 and len(wrong) == 60)

one_wrong = dict(perfect)
first = min(one_wrong)
one_wrong[first] = "A" if perfect[first] != "A" else "B"
per_domain, wrong = score_mock.score(KEY["mock"], one_wrong)
check("one wrong answer scores 59/60",
      sum(v[0] for v in per_domain.values()) == 59 and len(wrong) == 1)

all_b = {n: "B" for n in range(1, 61)}
per_domain, _ = score_mock.score(KEY["mock"], all_b)
blind = sum(v[0] for v in per_domain.values())
check("blind-picking B no longer clears the book's 70% band",
      blind <= 20, f"scored {blind}/60")

check("pct() handles an empty domain without dividing by zero",
      score_mock.pct(0, 0) == 0.0)

# --- the answer-file parser ------------------------------------------------
parsed = score_mock.parse_answers("1. A\n2) b\n3 C\n4:D\n", 60)
check("parses '1. A', '2) b', '3 C' and '4:D'",
      parsed == {1: "A", 2: "B", 3: "C", 4: "D"}, parsed)

parsed = score_mock.parse_answers("A\nB\nC\n", 60)
check("bare letters fill in question order",
      parsed == {1: "A", 2: "B", 3: "C"}, parsed)

parsed = score_mock.parse_answers("# a comment\n\n1. A\n2.\n3. C\n", 60)
check("comments and a blank numbered line are skipped",
      parsed == {1: "A", 3: "C"}, parsed)

parsed = score_mock.parse_answers("1. A\n99. B\n", 60)
check("answers past the last question are dropped",
      parsed == {1: "A"}, parsed)

# --- the decision rule, both instruments ----------------------------------
report = score_mock.report({1: [16, 16], 2: [11, 11], 3: [12, 12],
                            4: [12, 12], 5: [9, 9]}, [], 60, 60, "mock", "k")
check("80%+ tells you to schedule the exam",
      "ready to schedule" in report)

report = score_mock.report({1: [8, 16], 2: [5, 11], 3: [6, 12],
                            4: [6, 12], 5: [4, 9]}, [], 29, 60, "mock", "k")
check("below 70% sends you back to Chapters 4 through 9",
      "redo Chapters 4 through 9" in report)

report = score_mock.report({1: [1, 1], 2: [1, 1], 3: [1, 1], 4: [1, 1],
                            5: [1, 1]}, [], 5, 5, "diagnostic", "k")
check("5/5 on the diagnostic uses Chapter 1's wording",
      "not as far from ready" in report)

report = score_mock.report({1: [0, 16], 2: [11, 11], 3: [12, 12],
                            4: [12, 12], 5: [9, 9]}, [], 44, 60, "mock", "k")
check("the weakest domain is named, with its exam weight",
      "Weakest domain: 1" in report and "27%" in report)

print(f"\n{checks - len(failures)} of {checks} checks passed.\n")
sys.exit(1 if failures else 0)
