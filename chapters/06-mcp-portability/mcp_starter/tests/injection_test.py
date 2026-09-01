#!/usr/bin/env python3
"""Injection-defense test — Chapter 6, Step 7.

Sends a known-bad input through the harmlessness screen and asserts a refusal
(ch06:143). The default input is the one the BUILD STEP prints at ch06:230.

**Needs your own ANTHROPIC_API_KEY.** The screen is a Haiku 4.5 call, so this
is real traffic on your own credit — cheap, but not free.

    export ANTHROPIC_API_KEY="sk-ant-..."
    python3 tests/injection_test.py
    python3 tests/injection_test.py "your own attempt here"
    echo "one attempt per line" | python3 tests/injection_test.py

The screen itself lives in shared/harmlessness_screen.py, which is build
project 7. This file only asserts the refusal; it does not reimplement the
classifier.
"""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATES = [
    ROOT.parent.parent.parent / "shared" / "harmlessness_screen.py",
    ROOT / "harmlessness_screen.py",
    Path.cwd() / "harmlessness_screen.py",
]


def load_screen():
    for path in CANDIDATES:
        if path.is_file():
            spec = importlib.util.spec_from_file_location(
                "harmlessness_screen", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module, path
    sys.exit(
        "Could not find harmlessness_screen.py. Looked in:\n  "
        + "\n  ".join(str(p) for p in CANDIDATES)
        + "\nCopy shared/harmlessness_screen.py next to this test, or run "
          "this from the repo root.")


def main():
    if len(sys.argv) > 1:
        stems = sys.argv[1:]
    elif not sys.stdin.isatty():
        stems = [l for l in sys.stdin.read().splitlines() if l.strip()]
    else:
        stems = [json.loads((ROOT / "routing-fixture.json").read_text())["injection"]]

    module, path = load_screen()
    print(f"\nscreening {len(stems)} input(s) through {path.name}\n")

    leaked = []
    for stem in stems:
        verdict = module.screen_input(stem)
        mark = "REFUSED" if verdict.is_harmful else "PASSED "
        print(f"  [{mark}] {stem!r}")
        print(f"            {verdict.reason}")
        if not verdict.is_harmful:
            leaked.append(stem)

    print()
    if leaked:
        print(f"{len(leaked)} input(s) got through Layer 1. That is the whole "
              f"point of Layer 2 (pattern matching), Layer 3 (explicit refusal "
              f"phrasing in the system prompt) and Layer 4 (logging and "
              f"throttling repeat offenders). One layer is not a defense.\n")
        return 1
    print("Every input refused at Layer 1, before the agent saw it. Log the "
          "refusal with the user identifier and timestamp — that is Layer 4, "
          "and it is what makes the throttle possible.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
