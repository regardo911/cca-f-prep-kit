#!/usr/bin/env python3
"""Wrong-tool-routing test — Chapter 6, Step 6.

Three queries, three servers, three for three (ch06:228). The fixture is
routing-fixture.json, not a constant in this file, so you can add your own
cases without touching code.

**Needs your own ANTHROPIC_API_KEY, Node, and the MCP servers running.** Each
case is a real agent turn on your own credit.

    export ANTHROPIC_API_KEY="sk-ant-..."
    export GITHUB_TOKEN="ghp_..."
    python3 tests/routing_test.py
    python3 tests/routing_test.py --case "summarize the repo:summarizer"

How it decides which server fired: it scans the streamed messages for an
`mcp__<server>__` name. That is a crude read of the stream rather than a
structured tool-call inspection, and it will call a case ambiguous if two
server names show up in one turn. When a case comes back ambiguous, read the
transcript yourself — the printed messages are right there.
"""

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER_MENTION = re.compile(r"mcp__(\w+)__(\w+)")


async def run_case(query, expect, model, verbose):
    from claude_agent_sdk import ClaudeAgentOptions, query as agent_query

    config = json.loads((ROOT / ".mcp.json").read_text())
    servers = list(config.get("mcpServers", {}))
    options = ClaudeAgentOptions(
        model=model,
        allowed_tools=[f"mcp__{name}__*" for name in servers],
    )

    seen = set()
    async for message in agent_query(prompt=query, options=options):
        if verbose:
            print(f"    {message}")
        for server, tool in SERVER_MENTION.findall(str(message)):
            seen.add((server, tool))

    servers_hit = {s for s, _ in seen}
    if not servers_hit:
        return "none", seen
    if len(servers_hit) > 1:
        return "ambiguous", seen
    return servers_hit.pop(), seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fixture", default=str(ROOT / "routing-fixture.json"))
    ap.add_argument("--case", action="append",
                    help='extra case as "query:expected_server", repeatable')
    ap.add_argument("--model", default="claude-opus-4-7")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every streamed message")
    args = ap.parse_args()

    cases = json.loads(Path(args.fixture).read_text())["cases"]
    for extra in args.case or []:
        query, _, server = extra.rpartition(":")
        if not query or not server:
            sys.exit(f'--case wants "query:expected_server", got {extra!r}')
        cases.append({"query": query, "expect_server": server})

    print(f"\nrouting test: {len(cases)} case(s) on {args.model}\n")
    passed = 0
    for case in cases:
        got, seen = asyncio.run(
            run_case(case["query"], case["expect_server"], args.model,
                     args.verbose))
        ok = got == case["expect_server"]
        passed += ok
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {case['query']!r}")
        print(f"         expected {case['expect_server']}, routed to {got}")
        if seen:
            print(f"         tools seen: "
                  f"{', '.join(sorted(f'mcp__{s}__{t}' for s, t in seen))}")

    print(f"\n{passed} of {len(cases)}.")
    if passed != len(cases):
        print("Tighten the tool descriptions on the servers that collided, "
              "then rerun. Overlapping descriptions make the coordinator break "
              "the tie by itself, which is the whole failure mode.\n")
        return 1
    print("Three for three. The tool surface is unambiguous.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
