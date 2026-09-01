# Chapter 10: Trust and Safety

Safety is not a numbered domain. It threads all five, and the exam asks about it
everywhere: coordinator refusal paths in Domain 1, MCP scoping in Domain 2,
path-scoped rules in Domain 3, schema rejection in Domain 4, silent-failure
detection in Domain 5.

## What you build

A middleware that demonstrates the three trust tiers in code, and three
scenarios that prove each one.

**Operator.** `operator_policy.yaml`, loaded once at process start and frozen.
Six allowed tools and nothing else, three forbidden command patterns, a
read-only database role. The user cannot widen it.

**User.** `permission_mode`, a preference flip bounded by that ceiling. It does
not auto-approve MCP tools; only the allow-list does.

**System.** `SYSTEM_PROMPT` plus the harmlessness screen at the input layer,
with every refusal logged.

The vocabulary (operator, user, system, hardcoded, softcoded) is community
shorthand rather than Anthropic-published, and the book is explicit about that. The
architecture underneath is real either way.

## The one command

```
pip install pyyaml
python3 trust_enforcement_middleware.py --check
```

**No key.** It prints the frozen policy and runs the spot checks:

```
    allow   mcp__filesystem__read_file
    REFUSE  mcp__filesystem__delete_file
    REFUSE  Bash
    REFUSE  'rm -rf /var/data'  (matches 'rm -rf')
```

That is Scenario A's architectural point without an API call. A user can ask for
`mcp__filesystem__delete_file` all day; the tool is not in the list the agent
was constructed with, so the deletion has no code path. The refusal is
structural, not a decision the model makes at request time. That distinction,
enforcement at construction time rather than request time, is the
three-sentence answer the exam wants.

## What success looks like

```
python3 test_scenario_a.py     # refuses, keyless
python3 test_scenario_b.py     # succeeds, keyless
python3 test_scenario_c.py     # refuses [needs your ANTHROPIC_API_KEY]
```

A refuses, B succeeds, C refuses. B is the one that keeps A honest, because an
allow-list that refuses everything is not a trust hierarchy, it is a
switched-off agent. Each scenario takes `--live` (A and B) or a custom request
string, so you can push at the boundary rather than watching the default.

Then the part with no script: say the K2 answer out loud until you can write it
from memory.

> Operators set least-privilege ceiling rules; users operate inside those
> ceilings; the SDK enforces this by scoping tool allow-lists at agent
> construction time, not at request time. A user can request a capability the
> operator has not granted; the agent must refuse, because the request never
> reaches the tool layer at all. The "override" question is therefore mostly
> about preference flips inside the operator-allowed surface, not about
> expanding the surface.

## How to run it on your own agent

```
python3 trust_enforcement_middleware.py --policy ~/my_policy.yaml --check
python3 trust_enforcement_middleware.py --tool mcp__db__execute_sql
python3 trust_enforcement_middleware.py --command "TRUNCATE events"
```

Write your own `operator_policy.yaml` for an agent you actually run. The useful
exercise is the list you *leave out*: start from what the agent needs to do its
job this week and add nothing speculatively. Then in your code,
`build_options()` is what turns that file into `ClaudeAgentOptions`, and every
privileged call goes through `enforce_tool` or `enforce_command` first.

Copy the middleware, the policy file and the three scenarios into your own
`cca-f-prep` and tag the commit `ch10-trust-enforcement-complete`.

## Two of the three policy keys were doing nothing

The printed `build_options()` at ch10:118-123 reads `policy["allowed_tools"]`
and stops. `forbidden_command_patterns` and `read_only_database_role` are
declared in the file and never consulted, which means the middleware
demonstrates one tier of three, while ch10:110 says it "freezes the whole file"
and ch10:162 makes the `rm -rf` prohibition an exam answer.

Both are enforced here. `command_forbidden()` matches case-insensitively,
because `drop table` and `DROP TABLE` are the same request and only one of them
is in the file.

`build_options()` also takes the policy path as an argument. The printed version
does a bare `open("operator_policy.yaml")`, which resolves against whatever
directory the process happened to start in. Fine in the chapter, and a
confusing `FileNotFoundError` the first time you import the middleware from
somewhere else.
