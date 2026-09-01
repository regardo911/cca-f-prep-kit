<!-- Appendix A, Domain 5 cheat sheet, verbatim. Tape it to the wall. -->

### Domain 5 (15%) — Context Management and Reliability

- Silent failure: an output that is valid (schema-passing) and wrong; no exception, no log line.
- Three architectural detection mechanisms: assertion-based output validation (Pydantic `@field_validator`), golden-set regression (CI diff against pinned correct outputs), LLM-as-judge (Haiku 4.5 critique pass).
- Judge confidence thresholds: below 0.7 flag; below 0.5 refuse and trigger fallback.
- Long-context primitives: prompt-cache the system prompt with `cache_control` (one-hour TTL for sessions over 5 minutes); re-inject important instructions at fixed checkpoints; structured handoff state between subagents (no free-form prose handoff); output logging on every call as architectural audit trail.
- `tool_choice` is a real Anthropic API parameter for Messages with tool use. Use it to constrain which tool fires when the model has multiple options.
- Domain 5 is 15% of the exam, the smallest weight. The four-question margin lives here for many close-fail candidates because most candidates underprepare.
