#!/usr/bin/env python3
"""Run every test file. No key, no network, no test framework.

The book's own CI runs `python tests/*.py` and teaches no test runner, so this
is a loop and not a dependency.

    python3 tests/run_all.py
    python3 tests/run_all.py -v      # show each file's output

Nothing here exercises the eight build projects. Those make live Claude calls
and need your own key, so they are not tested — writing a test that pretended
to call the API would be testing the pretence.
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COUNT = 0


def main():
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    files = sorted(p for p in HERE.glob("test_*.py"))
    if not files:
        print("no test files found — that is itself a failure")
        return 1

    results = []
    total_checks = 0
    for path in files:
        proc = subprocess.run([sys.executable, str(path)],
                              capture_output=True, text=True)
        ok = proc.returncode == 0
        results.append((path.name, ok))
        for line in proc.stdout.splitlines():
            if line.strip().endswith("checks passed."):
                total_checks += int(line.strip().split()[2])
        if verbose or not ok:
            print(proc.stdout)
            if proc.stderr.strip():
                print(proc.stderr, file=sys.stderr)

    print()
    for name, ok in results:
        print(f"  {'pass' if ok else 'FAIL'}  {name}")

    failed = [n for n, ok in results if not ok]
    print(f"\n{len(files) - len(failed)} of {len(files)} files, "
          f"{total_checks} individual checks.\n")

    if total_checks == 0:
        print("Zero checks ran. A green run with no assertions is not a green "
              "run.\n")
        return 1
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
