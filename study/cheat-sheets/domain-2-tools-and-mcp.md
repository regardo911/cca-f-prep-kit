<!-- Appendix A, Domain 2 cheat sheet, verbatim. Tape it to the wall. -->

### Domain 2 (18%) — Tool Design and MCP Integration

- MCP transports: stdio (local subprocess), HTTP (`type: "http"`, streamable-http alias), SSE (legacy remote).
- Tool naming convention: `mcp__<server>__<tool>`. Double underscores. No dots.
- Allow-list: `allowedTools: ["mcp__<server>__*"]` (wildcard) or explicit per-tool.
- The five MCP portability gotchas: hardcoded absolute paths in `args`; missing env vars; `.mcp.json` placed in `.claude/` instead of project root; `settingSources` excluding `"project"`; missing npm package or node binary on PATH.
- `permissionMode: "acceptEdits"` does NOT auto-approve MCP tools; only `allowedTools` does. Two settings, two surfaces.
- Anthropic's four-layer prompt-injection defense: harmlessness screen (Haiku 4.5 with structured-output classifier `is_harmful: boolean`), input validation, prompt engineering, continuous monitoring with throttle.
- Wrong-tool-routing fix: tighten tool descriptions, scope subagent `tools` lists, run a small routing test set in CI.
