#!/usr/bin/env python3
"""The five MCP portability gotchas, as assertions — Chapter 6.

Standard library only. No key, no network, no Claude. This is the single best
keyless demonstration in the book: the whole Domain 2 skill is "why does the
same repo behave differently on two machines", and four of the five causes are
visible in the files without running anything.

    python3 check_portability.py                 # checks this directory
    python3 check_portability.py ~/code/your-repo

Exit code is 0 when every check passes, 1 when any fails, so CI can run it.

Gotcha 5 (missing npm package or node binary) is the one this cannot fully
settle from the files — it checks whether `node` and `npx` are on *your* PATH,
which says nothing about your teammate's. It reports what it can see and says
so.
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ENV_VAR = re.compile(r"\$\{(\w+)\}")


class Result:
    def __init__(self):
        self.rows = []

    def add(self, gotcha, name, ok, detail):
        self.rows.append((gotcha, name, ok, detail))

    @property
    def failed(self):
        return [r for r in self.rows if r[2] is False]

    def report(self):
        for gotcha, name, ok, detail in self.rows:
            mark = "PASS" if ok else ("FAIL" if ok is False else "----")
            print(f"  [{mark}] Gotcha {gotcha}: {name}")
            if detail:
                print(f"         {detail}")
        print()
        failed = len(self.failed)
        if failed:
            print(f"  {failed} of {len(self.rows)} checks failed. A teammate "
                  f"cloning this repo would hit them in that order.")
        else:
            print(f"  All {len(self.rows)} checks pass. Nothing here depends on "
                  f"one machine's filesystem or one shell's environment.")
        return 1 if failed else 0


def check(root: Path) -> int:
    print(f"\nMCP portability check: {root}\n")
    res = Result()

    config = root / ".mcp.json"
    stray = root / ".claude" / ".mcp.json"

    # --- Gotcha 3: .mcp.json in the wrong directory -----------------------
    if config.is_file():
        res.add(3, ".mcp.json sits at the project root", True, str(config))
    elif stray.is_file():
        res.add(3, ".mcp.json sits at the project root", False,
                f"found it at {stray} instead. The loader reads the project "
                f"root. Move it up one level.")
        return res.report()
    else:
        res.add(3, ".mcp.json sits at the project root", False,
                "no .mcp.json found at all. Nothing else to check.")
        return res.report()

    try:
        data = json.loads(config.read_text())
    except json.JSONDecodeError as exc:
        res.add(3, ".mcp.json parses", False, f"{exc}")
        return res.report()

    servers = data.get("mcpServers", {})
    if not servers:
        res.add(3, ".mcp.json declares at least one server", False,
                "mcpServers is empty or missing")
        return res.report()

    # --- Gotcha 1: hardcoded absolute paths in args ------------------------
    offenders = []
    for name, server in servers.items():
        for arg in server.get("args", []):
            if isinstance(arg, str) and (arg.startswith("/") or
                                         re.match(r"^[A-Za-z]:\\", arg)):
                offenders.append(f"{name}: {arg!r}")
    res.add(1, "no absolute paths in any server's args",
            not offenders,
            "; ".join(offenders) if offenders else
            f"{len(servers)} server(s) checked")

    # --- Gotcha 2: every ${VAR} is documented in .env.example -------------
    referenced = set()
    for server in servers.values():
        for value in list(server.get("env", {}).values()) + server.get("args", []):
            if isinstance(value, str):
                referenced |= set(ENV_VAR.findall(value))
    example = root / ".env.example"
    documented = set()
    if example.is_file():
        for line in example.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                documented.add(line.split("=", 1)[0].strip())
    undocumented = referenced - documented
    if not referenced:
        res.add(2, "every ${VAR} is documented in .env.example", True,
                "no environment variables referenced")
    elif not example.is_file():
        res.add(2, "every ${VAR} is documented in .env.example", False,
                f"no .env.example; {sorted(referenced)} would be undefined on "
                f"a teammate's machine")
    else:
        res.add(2, "every ${VAR} is documented in .env.example",
                not undocumented,
                f"undocumented: {sorted(undocumented)}" if undocumented
                else f"documented: {sorted(referenced)}")

    # --- Gotcha 4: settingSources includes "project" -----------------------
    settings = root / ".claude" / "settings.json"
    if settings.is_file():
        try:
            sources = json.loads(settings.read_text()).get("settingSources")
        except json.JSONDecodeError as exc:
            res.add(4, 'settingSources includes "project"', False, str(exc))
        else:
            if sources is None:
                res.add(4, 'settingSources includes "project"', True,
                        "not overridden, so the default loads project settings")
            else:
                res.add(4, 'settingSources includes "project"',
                        "project" in sources,
                        f"settingSources = {sources}")
    else:
        res.add(4, 'settingSources includes "project"', True,
                "no .claude/settings.json override, so the default applies")

    # --- Gotcha 5: node / npx on PATH --------------------------------------
    needs_npx = any(s.get("command") in ("npx", "npm")
                    for s in servers.values())
    if not needs_npx:
        res.add(5, "node and npx available", True, "no server invokes npx")
    else:
        found = {tool: shutil.which(tool) for tool in ("node", "npx")}
        missing = [t for t, p in found.items() if p is None]
        res.add(5, "node and npx available", not missing,
                (f"missing from this PATH: {missing}." if missing else
                 f"node={found['node']}") +
                " This one is about *your* machine only — it cannot tell you "
                "anything about a teammate's.")

    # --- pinning, which is Gotcha 5's own fix (ch06:39) --------------------
    unpinned = []
    for name, server in servers.items():
        for arg in server.get("args", []):
            if isinstance(arg, str) and arg.startswith("@") and "@" not in arg[1:]:
                unpinned.append(f"{name}: {arg}")
    code = res.report()
    if needs_npx:
        print(f"\n  note: unpinned npm packages: "
              f"{unpinned if unpinned else 'none'}.")
        print("        ch06:39 prefers pinned versions in args so version skew "
              "does not surprise you.")
        print("        Not a failure — the book ships the github server "
              "unpinned too — but it is the fix for Gotcha 5.")
    print()
    return code


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", nargs="?", default=str(Path(__file__).parent),
                    help="project root to check (default: this directory)")
    args = ap.parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"{root} is not a directory")
    return check(root)


if __name__ == "__main__":
    raise SystemExit(main())
