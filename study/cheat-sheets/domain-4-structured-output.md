<!-- Appendix A, Domain 4 cheat sheet, verbatim. Tape it to the wall. -->

### Domain 4 (20%) — Prompt Engineering and Structured Output

- API syntax: `output_config={"format": {"type": "json_schema", "schema": {...}}}` OR `client.messages.parse(..., output_format=PydanticModel)`.
- Anthropic guarantees schema-valid JSON when `output_config.format` is set. By construction, via constrained sampling.
- Old beta name: `output_format` (still accepted during transition).
- Supported schema features: types, `enum`, `const`, `anyOf`, `allOf`, `$ref`/`$def`, formats (date-time, email, uri, uuid).
- NOT supported: recursive schemas, numerical constraints (`minimum`/`maximum`), string length constraints, regex backreferences, `additionalProperties: true` (must be `false`).
- Up to 4 cache breakpoints per request.
- Models supported: Opus 4.7, Opus 4.6, Opus 4.5, Sonnet 4.6, Sonnet 4.5, Haiku 4.5, plus Mythos Preview.
- Schema solves shape (malformed JSON, missing fields, type mismatches). Pydantic post-validators solve business rules. Fallback loops solve outcomes (refusals, rate limits, low confidence).
- Tool use vs structured outputs: data → structured outputs; action → tool use; both → tool use with structured outputs on each tool's input/output schemas.
