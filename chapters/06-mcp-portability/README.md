# Chapter 6: MCP Portability

Domain 2 is 18% of the exam and every question in it is a scoping question
wearing MCP clothing. Where does this config live? Whose machine reads it?
Whose machine is missing it?

## What you build

`mcp_starter/`, with three MCP tools registered in one `.mcp.json` at the
project root, a committed `.env.example`, and a custom Python server. Then you clone it
into a sibling worktree and prove it still works over there.

The three servers:

| Server | Where it comes from | Needs |
|---|---|---|
| `filesystem` | `npx @modelcontextprotocol/server-filesystem@1.4.0` | Node |
| `github` | `npx @modelcontextprotocol/server-github` | Node + your `GITHUB_TOKEN` |
| `summarizer` | `summarizer_server.py`, FastMCP, yours | `pip install mcp` |

Chapter 6 prints the first two and describes the third in prose without ever
printing the finished file. The `.mcp.json` here is all three, which is what the
chapter title, the CHECKPOINT and the DELIVERABLE all say you should end up
with.

## The one command

```
cd mcp_starter
python3 check_portability.py
```

**No key. No network. No Claude.** This is the front door of the chapter and it
runs on a bare clone. It reads `.mcp.json` and asserts the five portability
gotchas one by one:

```
  [PASS] Gotcha 3: .mcp.json sits at the project root
  [PASS] Gotcha 1: no absolute paths in any server's args
  [PASS] Gotcha 2: every ${VAR} is documented in .env.example
  [PASS] Gotcha 4: settingSources includes "project"
  [PASS] Gotcha 5: node and npx available
```

Then break it on purpose. Change the filesystem server's last arg from `"."` to
`"/Users/you/projects"` and rerun: Gotcha 1 fails and names the line. Delete
`.env.example` and rerun: Gotcha 2 fails and tells you `GITHUB_TOKEN` would be
undefined on a teammate's machine. Two minutes, and the anatomy stops being a
list you memorized.

Gotcha 5 is the one the checker is honest about being unable to settle. It can
only see your own PATH, which says nothing about your teammate's.

## What success looks like

1. `check_portability.py` exits 0 on a fresh clone with nothing configured.
2. `python3 tests/verify_mcp_servers.py`, also keyless, confirms every
   expected tool name parses as `mcp__<server>__<tool>` and names a registered
   server.
3. The clone test actually clones. `git worktree add ../mcp_starter_clone`, set
   `GITHUB_TOKEN` in that worktree, run `claude` from inside it, and confirm all
   three tool families are reachable. This is the one step no script can do for
   you: reachability is a live-session observation.
4. `python3 tests/routing_test.py` scores three for three.
5. `python3 tests/injection_test.py` refuses at Layer 1.

Steps 4 and 5 **need your own `ANTHROPIC_API_KEY`** and spend your own credit.
Step 5 also wants `shared/harmlessness_screen.py`, which is where the classifier
lives. Steps 1 and 2 need nothing.

## How to run it on your own project

```
python3 mcp_starter/check_portability.py ~/code/your-repo
```

Point it at a repo where you have already set up MCP and see what it says. In
practice the two that fire are Gotcha 1 (an absolute path someone pasted in
while debugging) and Gotcha 2 (an env var that has been in your shell profile so
long you forgot it was not in the repo).

Copy `mcp_starter/` into your own `cca-f-prep`, add `ci-mcp-portability.yml` to
`.github/workflows/`, and tag the commit `ch06-mcp-portable`. The CI job is the
architectural point of the chapter, not a QA nicety: can someone other than the
original author run the validation without manual setup?

**One deliberate change from the printed config.** The book registers the
summarizer with `command: "python"`. This repo says `python3`, because stock
Ubuntu 22.04+ ships no bare `python` and macOS 12.3+ removed
`/usr/bin/python`. A reader who copies `"python"` literally gets
`command not found` from a server that never starts, which reads exactly like
Gotcha 5.
