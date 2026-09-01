#!/usr/bin/env python3
"""Scenario B — a within-allow-list action succeeds. Chapter 10, Step 5.

Request: "read the contents of `README.md`" (ch10:142).

Expected: the agent calls `mcp__filesystem__read_file`, which *is* in the
allow-list, and the operation succeeds.

Scenario B is the one that keeps A honest. An allow-list that refuses everything
is not a trust hierarchy, it is a switched-off agent. The tier only means
something if the permitted request goes through.

The keyless half checks that the tool is inside the ceiling. `--live` runs the
request through a real agent and needs your own ANTHROPIC_API_KEY.

    python3 test_scenario_b.py
    python3 test_scenario_b.py --live
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from trust_enforcement_middleware import (  # noqa: E402
    OperatorPolicy, PolicyViolation, DEFAULT_POLICY, build_options,
)

DEFAULT_REQUEST = "read the contents of `README.md`"
TOOL = "mcp__filesystem__read_file"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--request", default=DEFAULT_REQUEST)
    ap.add_argument("--tool", default=TOOL)
    ap.add_argument("--policy", default=str(DEFAULT_POLICY))
    ap.add_argument("--live", action="store_true",
                    help="also run it through a real agent "
                         "[needs your ANTHROPIC_API_KEY]")
    ap.add_argument("--user", default="scenario-b")
    args = ap.parse_args()

    logging.basicConfig(level=logging.WARNING,
                        format="%(levelname)s %(name)s: %(message)s")

    policy = OperatorPolicy(args.policy)
    print(f"\nScenario B: {args.request!r}\n")

    try:
        policy.enforce_tool(args.tool, user=args.user)
    except PolicyViolation as exc:
        print(f"  [FAIL] {exc}")
        print(f"  Scenario B is supposed to succeed. If the read tool is")
        print(f"  outside the ceiling, the ceiling is too tight to be useful.\n")
        ok = False
    else:
        print(f"  [allowed] {args.tool} is inside the operator ceiling.")
        print(f"  The user is operating inside the ceiling, which is exactly")
        print(f"  what the user tier is for.\n")
        ok = True

    if args.live:
        import asyncio
        from claude_agent_sdk import query
        print("  live run:\n")
        options = build_options(policy_path=args.policy)

        async def run():
            async for message in query(prompt=args.request, options=options):
                print(f"    {message}")

        asyncio.run(run())
        print()

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
