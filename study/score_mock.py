#!/usr/bin/env python3
"""Score your own answers to the Chapter 12 mock, or the Chapter 1 diagnostic.

Standard library only. No key, no network, no account. The decision rule at the
bottom is Chapter 12's (ch12:435-439); the diagnostic rule is Chapter 1's
(ch01:126).

    python3 study/score_mock.py --diagnostic          # 5 questions, Chapter 1
    python3 study/score_mock.py --template > mine.txt # blank answer sheet
    python3 study/score_mock.py mine.txt              # 60 questions, Chapter 12
    cat mine.txt | python3 study/score_mock.py        # same, from stdin

Answer-file format is whatever you would scribble on paper: one answer per
line, `12. B` or `12 B` or just `B` in question order. Blanks count as wrong,
which is what the live exam does too.
"""

import argparse
import json
import re
import sys
from pathlib import Path

KEY_PATH = Path(__file__).with_name("answer-key.json")

# ch12:13-20. The mock's 16/11/12/12/9 allocation is these weights x 60.
DOMAINS = {
    1: ("Agentic Architecture and Orchestration", 27, "chapters/04 + 05"),
    2: ("Tool Design and MCP Integration", 18, "chapters/06"),
    3: ("Claude Code Configuration and Workflows", 20, "chapters/07"),
    4: ("Prompt Engineering and Structured Output", 20, "chapters/08"),
    5: ("Context Management and Reliability", 15, "chapters/09"),
}


def load_key(path):
    if not path.exists():
        sys.exit(f"answer key not found at {path}")
    return json.loads(path.read_text())


def parse_answers(text, count):
    """Pull answers out of whatever the reader typed.

    Numbered lines win: `7. C` sets question 7 regardless of position, so a
    half-filled sheet still scores the questions it does have. Bare letters
    fill in question order.
    """
    answers = {}
    position = 0
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^(\d+)\s*[.):\-]?\s*([A-Da-d])\s*$", line)
        if m:
            answers[int(m.group(1))] = m.group(2).upper()
            position = int(m.group(1))
            continue
        m = re.match(r"^([A-Da-d])\s*$", line)
        if m:
            position += 1
            answers[position] = m.group(1).upper()
            continue
        m = re.match(r"^(\d+)\s*[.):\-]?\s*$", line)
        if m:  # a numbered line the reader left blank
            position = int(m.group(1))
            continue
        sys.exit(f"could not read this line as an answer: {raw!r}")
    return {n: a for n, a in answers.items() if 1 <= n <= count}


def ask_interactively(key, labels):
    print("Answer each one. Enter alone skips (and counts as wrong).\n")
    answers = {}
    for n in sorted(key, key=int):
        prompt = labels.get(n, f"Question {n}")
        while True:
            try:
                got = input(f"{prompt} [A/B/C/D]: ").strip().upper()
            except EOFError:
                print()
                return answers
            if got == "":
                break
            if got in "ABCD" and len(got) == 1:
                answers[int(n)] = got
                break
            print("  A, B, C or D, or Enter to skip.")
    print()
    return answers


def score(key, answers):
    per_domain = {d: [0, 0] for d in DOMAINS}  # [right, asked]
    wrong = []
    for n_str, entry in key.items():
        n = int(n_str)
        d = entry["domain"]
        per_domain[d][1] += 1
        if answers.get(n) == entry["answer"]:
            per_domain[d][0] += 1
        else:
            wrong.append((n, answers.get(n), entry["answer"], d))
    per_domain = {d: v for d, v in per_domain.items() if v[1]}
    return per_domain, sorted(wrong)


def pct(right, asked):
    return 100.0 * right / asked if asked else 0.0


def report(per_domain, wrong, total_right, total_asked, mode, key_file):
    out = []
    out.append("")
    out.append(f"  {'Domain':<44} {'Right':>9} {'':>6}")
    out.append("  " + "-" * 61)
    for d in sorted(per_domain):
        right, asked = per_domain[d]
        name, weight, folder = DOMAINS[d]
        out.append(f"  {d}. {name:<41} {right:>3} / {asked:<3} "
                   f"{pct(right, asked):>5.0f}%")
    out.append("  " + "-" * 61)
    out.append(f"  {'TOTAL':<44} {total_right:>3} / {total_asked:<3} "
               f"{pct(total_right, total_asked):>5.0f}%")
    out.append("")

    total_pct = pct(total_right, total_asked)
    ranked = sorted(per_domain, key=lambda d: (pct(*per_domain[d]), -d))
    weakest = ranked[0]
    name, weight, folder = DOMAINS[weakest]
    out.append(f"  Weakest domain: {weakest} — {name}")
    out.append(f"  It is {weight}% of the live exam. Re-read its chapter; "
               f"redo the BUILD STEP in {folder}.")
    out.append("")

    if mode == "diagnostic":
        # ch01:126, the book's own reading of a diagnostic score.
        if total_right == 5:
            verdict = ("Five out of five: you are not as far from ready as you "
                       "think. Work the chapters, drill the mocks, sit the exam.")
        elif total_right >= 3:
            verdict = "Three or four: the chapters are the path."
        else:
            verdict = ("Two or fewer: this book is the right book and the next "
                       "thirty days are the right plan.")
        out.append("  " + verdict)
        out.append("")
        out.append("  Write the weakest domain on a sticky note. You look at it "
                   "again on Day 28,")
        out.append("  when you score the sixty-question mock.")
    else:
        # ch12:435-439, the book's go/no-go rule.
        if total_pct >= 80:
            verdict = ("80% or higher: ready to schedule the live exam this "
                       "week. Your weakest domain above is your one focused "
                       "review area.")
        elif total_pct >= 70:
            verdict = ("70 to 79%: one more week of focused prep. Bottom two "
                       "domains, re-read the chapters, redo the BUILD STEPs, "
                       "retake this mock at the end of the week.")
        else:
            verdict = ("Below 70%: redo Chapters 4 through 9 in their full "
                       "BUILD STEPs, ship every project, retake this mock in "
                       "two weeks.")
        out.append("  " + verdict)
        out.append("")
        out.append("  The pass mark is a scaled 720/1000, not a percentage, so "
                   "this is a calibration")
        out.append("  reading and not a prediction.")

    if wrong:
        missed = ", ".join(str(n) for n, _, _, _ in wrong)
        out.append("")
        out.append(f"  Missed or blank: {missed}")
        out.append(f"  Reasoning for each, with its chapter cite, is in "
                   f"{key_file}.")
    out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(
        description="Score your own CCA-F mock or diagnostic answers.")
    ap.add_argument("answers", nargs="?",
                    help="file of your answers; omit to type them in or pipe "
                         "them on stdin")
    ap.add_argument("--diagnostic", action="store_true",
                    help="score the 5-question Chapter 1 entry diagnostic "
                         "instead of the 60-question mock")
    ap.add_argument("--key", default=str(KEY_PATH),
                    help="answer key JSON (default: study/answer-key.json)")
    ap.add_argument("--template", action="store_true",
                    help="print a blank answer sheet and exit")
    ap.add_argument("--save", metavar="PATH",
                    help="also write the scored result to PATH")
    args = ap.parse_args()

    data = load_key(Path(args.key))
    mode = "diagnostic" if args.diagnostic else "mock"
    key = data[mode]
    count = len(key)
    key_file = ("study/diagnostic.md" if args.diagnostic
                else "study/mock-exam-answer-key.md")

    if args.template:
        title = ("# Chapter 1 diagnostic — 5 answers"
                 if args.diagnostic else "# Chapter 12 mock — 60 answers")
        print(title)
        print("# One per line. Delete nothing; a blank line stays blank.")
        for n in range(1, count + 1):
            print(f"{n}. ")
        return 0

    if args.answers:
        text = Path(args.answers).read_text()
        answers = parse_answers(text, count)
    elif not sys.stdin.isatty():
        answers = parse_answers(sys.stdin.read(), count)
    else:
        labels = {}
        if args.diagnostic:
            for n_str, entry in key.items():
                d = entry["domain"]
                labels[n_str] = f"Q{n_str} (Domain {d}, {DOMAINS[d][0]})"
        answers = ask_interactively(key, labels)
        answers = {int(k): v for k, v in answers.items()}

    if not answers:
        sys.exit("No answers read. `--template` prints a blank sheet to fill "
                 "in, or run it with no arguments to type them in.")

    per_domain, wrong = score(key, answers)
    total_right = sum(v[0] for v in per_domain.values())
    text = report(per_domain, wrong, total_right, count, mode, key_file)
    print(text)

    if args.save:
        Path(args.save).write_text(
            f"# CCA-F {mode} result\n\n```{text}```\n")
        print(f"  Saved to {args.save}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
