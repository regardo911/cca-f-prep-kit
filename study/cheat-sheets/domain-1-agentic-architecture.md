<!-- Appendix A, Domain 1 cheat sheet, verbatim. Tape it to the wall. -->

### Domain 1 (27%) — Agentic Architecture and Orchestration

- Hub-and-Spoke skeleton: User → Coordinator → Researcher subagent + Synthesizer subagent → structured final answer.
- Coordinator's `allowed_tools` MUST include `"Agent"` for delegation. This is the most exam-relevant single detail in the domain.
- `AgentDefinition(description, prompt, tools)`. Subagent's `tools` cannot exceed coordinator's; can be narrower.
- Four multi-agent failure modes (the book's taxonomy, not Anthropic's): deadlock, hallucinated handoff, silent retry storm, budget blow-out.
- Batch API discount: 50% off both input and output tokens, uniformly across every active model. Not 30%.
- Endpoint: `https://api.anthropic.com/v1/messages/batches`. SDK call: `client.messages.batches.create(requests=[...])`.
- Prompt caching: 90% read discount; minimum 4,096 cacheable tokens on Opus 4.7 / 4.6 / 4.5 / Haiku 4.5. Syntax: `cache_control={"type": "ephemeral"}` (5-min) or `{"type": "ephemeral", "ttl": "1h"}`.
- Models: `claude-opus-4-7` for coordinators, `claude-haiku-4-5` for retrieval-shaped subagents. Cost: Opus $5/$25 per million tokens (input/output), Haiku $1/$5.
