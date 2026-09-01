#!/usr/bin/env python3
"""Assert every expected mcp__<server>__<tool> name is accounted for — Chapter 6.

Standard library only. No key, no network.

What it asserts, from the files alone:
  * every server named in routing-fixture.json is registered in .mcp.json
  * every expected tool name parses as mcp__<server>__<tool> — double
    underscores, no dots (ch06:19)
  * every expected tool's server exists
  * each server's launch command resolves on this PATH

What it does not assert: that the servers actually start and answer. Tool
*reachability* is a live-session observation — you get it by running `claude`
from a fresh worktree, which is Step 5 of the BUILD STEP and which no committed
file can do on your behalf. The command to run is printed at the end.

    python3 tests/verify_mcp_servers.py
    python3 tests/verify_mcp_servers.py ~/code/your-repo
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent
TOOL_NAME = re.compile(r"^mcp__([^_][\w-]*)__([^_][\w-]*)$")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", nargs="?", default=str(DEFAULT_ROOT),
                    help="project root holding .mcp.json and "
                         "routing-fixture.json (default: this starter)")
    args = ap.parse_args()
    root = Path(args.root).expanduser().resolve()
    if not (root / ".mcp.json").is_file():
        sys.exit(f"no .mcp.json at {root}")
    if not (root / "routing-fixture.json").is_file():
        sys.exit(f"no routing-fixture.json at {root}; it names the tools and "
                 f"routing targets this script checks for")

    config = json.loads((root / ".mcp.json").read_text())
    fixture = json.loads((root / "routing-fixture.json").read_text())
    servers = config.get("mcpServers", {})
    expected = fixture["expected_tools"]

    failures = []
    print(f"\n{len(servers)} server(s) registered: {', '.join(sorted(servers))}\n")

    for tool in expected:
        m = TOOL_NAME.match(tool)
        if not m:
            failures.append(f"{tool!r} is not mcp__<server>__<tool>. Double "
                            f"underscores, no dots — ch06:19.")
            print(f"  [FAIL] {tool}")
            continue
        server = m.group(1)
        if server not in servers:
            failures.append(f"{tool!r} names server {server!r}, which is not in "
                            f".mcp.json")
            print(f"  [FAIL] {tool}  (no {server!r} server registered)")
        else:
            print(f"  [ ok ] {tool}")

    print()
    for case in fixture["cases"]:
        server = case["expect_server"]
        if server not in servers:
            failures.append(f"routing fixture expects server {server!r}, "
                            f"which is not registered")
            print(f"  [FAIL] routing target {server!r} not registered")
        else:
            print(f"  [ ok ] routing target {server!r} registered")

    print()
    for name, server in sorted(servers.items()):
        command = server.get("command")
        where = shutil.which(command) if command else None
        if where:
            print(f"  [ ok ] {name}: {command} -> {where}")
        else:
            failures.append(f"{name}: launch command {command!r} is not on "
                            f"this PATH")
            print(f"  [FAIL] {name}: {command!r} not on PATH")

    print()
    if failures:
        for f in failures:
            print(f"  {f}")
        print(f"\n{len(failures)} failure(s).\n")
        return 1

    print("Names, servers and launch commands all check out.\n")
    print("Reachability is the part this cannot answer. Do Step 5 by hand:\n")
    print("    git worktree add ../mcp_starter_clone")
    print("    cd ../mcp_starter_clone && export GITHUB_TOKEN=...")
    print("    claude\n")
    print("Then confirm mcp__filesystem__*, mcp__github__list_issues and")
    print("mcp__summarizer__summarize_repo are all reachable in that session.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
