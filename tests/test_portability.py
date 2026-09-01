#!/usr/bin/env python3
"""check_portability.py catches each gotcha it claims to catch.

The checker passing on a correct tree proves nothing on its own — a function
that returns 0 unconditionally would do the same. So this breaks the config
five different ways in a scratch copy and asserts the right check fails each
time.

Standard library only. No key, no network.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STARTER = ROOT / "chapters" / "06-mcp-portability" / "mcp_starter"
CHECKER = STARTER / "check_portability.py"

checks = 0
failures = []


def run(root):
    proc = subprocess.run(
        [sys.executable, str(CHECKER), str(root)],
        capture_output=True, text=True)
    return proc.returncode, proc.stdout


def check(name, condition, detail=""):
    global checks
    checks += 1
    if condition:
        print(f"  [ ok ] {name}")
    else:
        print(f"  [FAIL] {name}  {detail}")
        failures.append(name)


def scratch(mutate=None):
    """A copy of mcp_starter, optionally broken on the way out."""
    tmp = Path(tempfile.mkdtemp())
    dest = tmp / "mcp_starter"
    shutil.copytree(STARTER, dest)
    if mutate:
        mutate(dest)
    return tmp, dest


print("\nMCP portability checks\n")

# --- the shipped config is clean ------------------------------------------
code, out = run(STARTER)
check("the shipped mcp_starter passes all five", code == 0, out)
check("all five gotchas are reported by number",
      all(f"Gotcha {n}" in out for n in (1, 2, 3, 4, 5)))
check("the three servers are all registered",
      "3 server(s) checked" in out, out)


def break_absolute_path(dest):
    config = json.loads((dest / ".mcp.json").read_text())
    config["mcpServers"]["filesystem"]["args"][-1] = "/Users/jane/projects/widgets"
    (dest / ".mcp.json").write_text(json.dumps(config, indent=2))


tmp, dest = scratch(break_absolute_path)
code, out = run(dest)
check("Gotcha 1 fires on an absolute path in args",
      code == 1 and "[FAIL] Gotcha 1" in out, out)
check("Gotcha 1 names the offending path",
      "/Users/jane/projects/widgets" in out)
shutil.rmtree(tmp)

tmp, dest = scratch(lambda d: (d / ".env.example").unlink())
code, out = run(dest)
check("Gotcha 2 fires when .env.example is missing",
      code == 1 and "[FAIL] Gotcha 2" in out, out)
check("Gotcha 2 names the undefined variable",
      "GITHUB_TOKEN" in out)
shutil.rmtree(tmp)


def hide_config(dest):
    (dest / ".claude").mkdir()
    shutil.move(str(dest / ".mcp.json"), str(dest / ".claude" / ".mcp.json"))


tmp, dest = scratch(hide_config)
code, out = run(dest)
check("Gotcha 3 fires when .mcp.json is under .claude/",
      code == 1 and "[FAIL] Gotcha 3" in out, out)
check("Gotcha 3 says where it found it instead",
      ".claude" in out and "Move it up one level" in out)
shutil.rmtree(tmp)


def exclude_project(dest):
    (dest / ".claude").mkdir()
    (dest / ".claude" / "settings.json").write_text(
        json.dumps({"settingSources": ["user"]}))


tmp, dest = scratch(exclude_project)
code, out = run(dest)
check('Gotcha 4 fires when settingSources omits "project"',
      code == 1 and "[FAIL] Gotcha 4" in out, out)
shutil.rmtree(tmp)


def no_npx(dest):
    config = json.loads((dest / ".mcp.json").read_text())
    for name in ("filesystem", "github"):
        config["mcpServers"][name]["command"] = "python3"
        config["mcpServers"][name]["args"] = ["nothing.py"]
    (dest / ".mcp.json").write_text(json.dumps(config, indent=2))


tmp, dest = scratch(no_npx)
code, out = run(dest)
check("Gotcha 5 is skipped when no server invokes npx",
      "no server invokes npx" in out, out)
shutil.rmtree(tmp)

tmp, dest = scratch(lambda d: (d / ".mcp.json").unlink())
code, out = run(dest)
check("a missing .mcp.json fails rather than passing vacuously",
      code == 1 and "no .mcp.json found at all" in out, out)
shutil.rmtree(tmp)

tmp, dest = scratch(lambda d: (d / ".mcp.json").write_text("{not json"))
code, out = run(dest)
check("unparseable JSON fails rather than crashing",
      code == 1 and "parses" in out, out)
shutil.rmtree(tmp)

# --- the tool-name verifier -----------------------------------------------
proc = subprocess.run(
    [sys.executable, str(STARTER / "tests" / "verify_mcp_servers.py")],
    capture_output=True, text=True)
check("verify_mcp_servers.py passes on the shipped config",
      proc.returncode == 0, proc.stdout + proc.stderr)
check("it checks every expected mcp__<server>__<tool> name",
      proc.stdout.count("[ ok ] mcp__") == 4, proc.stdout)
check("it does not claim the servers are reachable",
      "Reachability is the part this cannot answer" in proc.stdout)

print(f"\n{checks - len(failures)} of {checks} checks passed.\n")
sys.exit(1 if failures else 0)
