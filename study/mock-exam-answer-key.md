# Mock Exam: Answer Key

Every reasoning line below is Chapter 12's, verbatim, including its chapter cite. The letters are this repo's, not the book's: the options were reordered, so cross-check by the reasoning.

> **Why the letters differ from the printed book.** Each question's four options are deliberately reordered here. In the printed edition the correct answer is B in 47 of the 60 questions and D in none of them, so the printed order can be gamed without knowing any architecture. The stems, the correct answers and every line of the reasoning are the book's, verbatim; only the order changed. Cross-check by reasoning, not by letter. Reordering fixes the letter tell. It cannot fix the second one: the correct answer is also the longest of the four options in 51 of the 60 questions, because the architectural answer names layers while the three distractors are one-line knob-turns. Do not let option length pick for you.

## Domain 1 (16 questions)

**Q1: C** coordinator + structured citations + refusal Ch 4 + Ch 8. *(printed book: B)*

**Q2: A** `"Agent"` allow-list gotcha Ch 4. *(printed book: B)*

**Q3: A** cap subagent depth + token/turn budgets Ch 4. *(printed book: B)*

**Q4: D** Batch API for non-user-facing Ch 5. *(printed book: B)*

**Q5: B** max batch is 100k requests Ch 5. *(printed book: B)*

**Q6: A** structured-context-passing Ch 4. *(printed book: B)*

**Q7: C** 50% verified Anthropic figure, NOT 30% Ch 5. *(printed book: B)*

**Q8: B** cache_control 90% read discount Ch 5. *(printed book: B)*

**Q9: B** max_turns + tool timeout Ch 4. *(printed book: B)*

**Q10: A** Opus $5/$25 vs Haiku $1/$5 Ch 4 + tech-reference §10. *(printed book: B)*

**Q11: D** Batch the judge calls Ch 5 + Ch 9. *(printed book: B)*

**Q12: B** Agent tool Ch 4. *(printed book: B)*

**Q13: C** subagent-scoped + coordinator widened Ch 4. *(printed book: B)*

**Q14: D** first 5,000 free for partner-network employees Ch 2. *(printed book: B)*

**Q15: B** Anthropic guarantees schema-valid JSON Ch 8. *(printed book: A)*

**Q16: B** LLM-as-judge layer Ch 9. *(printed book: B)*

## Domain 2 (11 questions)

**Q17: B** one of the 5 portability gotchas Ch 6. *(printed book: B)*

**Q18: A** `mcp__<server>__<tool>` strict Ch 6. *(printed book: B)*

**Q19: C** `acceptEdits` does not auto-approve MCP Ch 6. *(printed book: B)*

**Q20: D** Anthropic 4-layer defense Ch 6. *(printed book: A)*

**Q21: C** `.env.example` pattern Ch 6. *(printed book: B)*

**Q22: A** description tightening + subagent scoping Ch 3 + Ch 6. *(printed book: B)*

**Q23: A** stdio + HTTP + SSE Ch 6. *(printed book: A)*

**Q24: B** system prompt is only layer 3; layer 1 missing Ch 6. *(printed book: A)*

**Q25: D** CI fresh-clone validation Ch 6. *(printed book: B)*

**Q26: C** split into separate subagents with scoped tool lists Ch 6 + Ch 10. *(printed book: B)*

**Q27: C** 4-layer defense + monitoring throttle Ch 6 + Ch 10. *(printed book: B)*

## Domain 3 (12 questions)

**Q28: A** 4 scopes: managed, project, user, local Ch 7. *(printed book: B)*

**Q29: C** Local > User > Project > Managed Ch 7. *(printed book: B)*

**Q30: D** project root, committed Ch 7. *(printed book: B)*

**Q31: B** more than 30 Ch 7. *(printed book: B)*

**Q32: C** Local + User > Project on the same machine; the personal file wins on conflicts Ch 7. *(printed book: B)*

**Q33: A** `.claude/commands/<name>.md` Ch 7. *(printed book: A)*

**Q34: B** `.claude/settings.json` PostToolUse + Bash + command pattern Ch 7. *(printed book: A)*

**Q35: A** Plan subagent is read-only Ch 7. *(printed book: A)*

**Q36: D** `.claude/rules/` with `paths:` frontmatter Ch 7. *(printed book: B)*

**Q37: C** AI-invoked at `.claude/skills/` Ch 7. *(printed book: A)*

**Q38: D** `.claude/agents/<name>.md` Ch 7. *(printed book: A)*

**Q39: D** rules in user scope ride with you, not the repo Ch 7. *(printed book: B)*

## Domain 4 (12 questions)

**Q40: A** `output_config.format` Anthropic guarantee Ch 8. *(printed book: B)*

**Q41: C** numerical constraints not supported Ch 8. *(printed book: C)*

**Q42: C** `additionalProperties: false` required Ch 8. *(printed book: B)*

**Q43: D** Pydantic post-validator for business rules Ch 8. *(printed book: B)*

**Q44: A** schema solves shape Ch 8. *(printed book: B)*

**Q45: D** fallback solves outcomes Ch 5 + Ch 8. *(printed book: B)*

**Q46: D** full supported model list Ch 8 + tech-reference §8. *(printed book: A)*

**Q47: D** fallback loop with exponential backoff Ch 5. *(printed book: B)*

**Q48: B** data → structured outputs Ch 8. *(printed book: B)*

**Q49: C** action → tool use Ch 8. *(printed book: B)*

**Q50: C** provenance as architectural primitive Ch 8. *(printed book: A)*

**Q51: C** `output_format` is the old beta name Ch 8 + tech-reference §8. *(printed book: B)*

## Domain 5 (9 questions)

**Q52: B** golden-set regression + assertion validator Ch 9. *(printed book: B)*

**Q53: B** cache + re-injection Ch 9. *(printed book: B)*

**Q54: A** 90% cache-read discount Ch 5. *(printed book: B)*

**Q55: B** assertion + golden set + judge Ch 9. *(printed book: B)*

**Q56: A** valid + wrong + no exception Ch 9. *(printed book: B)*

**Q57: D** Batch the eval workload Ch 5 + Ch 9. *(printed book: B)*

**Q58: A** logs are architecture, not ops Ch 10. *(printed book: A)*

**Q59: B** structured handoff state Ch 4 + Ch 9. *(printed book: B)*

**Q60: D** small weight, candidates underprepare, four-question margin lives here Ch 9. *(printed book: B)*

---

Score it: `python3 study/score_mock.py my-answers.txt`, or by hand with [scoresheet.md](scoresheet.md).
