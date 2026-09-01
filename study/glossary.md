<!-- Appendix A, Glossary, verbatim. Eighteen terms. -->

## Glossary

Eighteen canonical technical terms. Each entry is a 25-word definition plus a tech-reference section anchor.

**Agent SDK (Claude Agent SDK).** The Python and TypeScript SDK for orchestrating Claude agents and subagents. Renamed from "Claude Code SDK." Package: `claude-agent-sdk`. Tech-reference §3.

**AgentDefinition.** The dataclass-style spec for a subagent: `description`, `prompt`, `tools`, optional `model`. Used inline in `ClaudeAgentOptions.agents` or filed at `.claude/agents/`. Tech-reference §3.

**Batch API.** Anthropic's asynchronous endpoint at `/v1/messages/batches`. Fifty percent cheaper than synchronous; sub-one-hour typical latency; max 100,000 requests per batch. Tech-reference §6.

**CLAUDE.md hierarchy.** The four-scope memory configuration: Managed policy (org-wide), Project (`./CLAUDE.md`), User (`~/.claude/CLAUDE.md`), Local (`./CLAUDE.local.md`, gitignored). Precedence: Local > User > Project > Managed. Tech-reference §4.

**Claude Code.** Anthropic's CLI / IDE / Desktop / Web client. More than 30 built-in tools. Slash commands user-invoked; skills AI-invoked. Tech-reference §4.

**Coordinator.** The top-level agent in Hub-and-Spoke. Routes work to subagents. Must include `"Agent"` in `allowed_tools` to delegate. Tech-reference §3.

**Fallback loop.** Exponential-backoff retry wrapper for upstream content failures, refusals, rate limits, and timeouts. Cap at three attempts; 1s/2s/4s backoff. Tech-reference §6 + §8.

**Golden-set regression.** A pinned set of inputs with known-correct outputs; CI diffs every change against the set. The architecturally-meaningful silent-failure detection layer. Tech-reference §8 (post-validation pattern).

**Hooks.** `.claude/settings.json` settings that run shell commands on events (`PreToolUse`, `PostToolUse`, `SessionStart`, etc.). Non-interactive. Tech-reference §4.

**Hub-and-Spoke.** Multi-agent reference architecture. User → Coordinator → Subagent fanout → structured final answer. Domain 1's canonical scenario template. Tech-reference §3.

**LLM-as-judge.** A second Claude call (typically Haiku 4.5) that critiques a primary call's output. Returns structured verdict. Engineering term, not Anthropic-canonical. Tech-reference §3 + §9 cross-ref.

**Model Context Protocol (MCP).** Open standard for connecting AI applications to external tools and data. Three transports: stdio, HTTP, SSE. Tech-reference §5.

**Plan mode.** Claude Code feature where the read-only `Plan` subagent produces a plan for approval before code is written. Toggled by `EnterPlanMode` and `ExitPlanMode` tools. Tech-reference §4.

**Prompt caching.** Caches a long shared message block; cache reads cost 90% less than base input. Syntax: `cache_control={"type": "ephemeral"}` (5-min) or `"ttl": "1h"`. Tech-reference §7.

**Silent failure.** An output that is valid and wrong; no exception, no log line goes red. Engineering term, not Anthropic-canonical. Tech-reference §8 + Ch 9 cross-ref.

**Skills.** AI-invoked behaviors at `.claude/skills/<name>/SKILL.md`. Distinct from slash commands (user-invoked). Tech-reference §4.

**Structured outputs.** API feature via `output_config.format` (or `output_format` for the old beta name). Anthropic guarantees schema-valid JSON via constrained sampling. Tech-reference §8.

**Trust hierarchy (operator / user / system).** Community-summarized framing for Anthropic's permissions and harmlessness layers. NOT first-class Anthropic vocabulary; the framing appears in Reddit chatter and test-taker debriefs. Tech-reference Ch 10 cross-ref.
