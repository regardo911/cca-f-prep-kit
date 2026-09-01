# The 30-Day Map

Chapter 1's day map, with the folder in this repo that serves each block. Six
pages of reading a day, plus one buildable thing every two or three days.

Days 4 through 9 are the longest block because Domain 1 is 27% of the exam.
Days 20 through 22 are the shortest because Domain 5 is 15%. That is the whole
pacing argument: read in chapter order and your time budget self-balances.

| Days | Chapter | What you do | Where it lives here |
|---|---|---|---|
| 1 | 1 | Take the diagnostic. Write your weakest domain on a sticky note. | [diagnostic.md](diagnostic.md) |
| 2-3 | 2, 3 | Pick your access path. Learn to name the five judgment patterns cold. | [access-path-worksheet.md](access-path-worksheet.md) · [five-judgment-patterns.md](five-judgment-patterns.md) |
| 4-9 | 4, 5 | Domain 1, 27%. A working coordinator with two subagents, structured-output schemas, fallback loops, and a Batch call. | [chapters/04-agentic-architecture](../chapters/04-agentic-architecture) · [chapters/05-orchestration](../chapters/05-orchestration) |
| 10-12 | 6 | Domain 2, 18%. An MCP server that survives `git clone` on a fresh machine. | [chapters/06-mcp-portability](../chapters/06-mcp-portability) |
| 13-15 | 7 | Domain 3, 20%. The CLAUDE.md hierarchy, the slash command, the hook. | [chapters/07-claude-code-config](../chapters/07-claude-code-config) |
| 16-19 | 8 | Domain 4, 20%. Anti-hallucination architecture and the twenty-trial test set. | [chapters/08-structured-output](../chapters/08-structured-output) |
| 20-22 | 9 | Domain 5, 15%. The smallest weight and the killer. | [chapters/09-silent-failures](../chapters/09-silent-failures) |
| 23-25 | 10 | Safety. Trust hierarchy. The database access question. | [chapters/10-trust-and-safety](../chapters/10-trust-and-safety) |
| 26-27 | 11 | Honest math on the $99 fee. LinkedIn and five outreach DMs. | [chapters/11-cert-positioning](../chapters/11-cert-positioning) |
| 28-30 | 12 | Sixty mock questions, scored by domain against the Day 1 diagnostic. Book the exam or push it seven days. | [mock-exam.md](mock-exam.md) · [scoresheet.md](scoresheet.md) |

## What "one buildable thing" means on the code days

Days 4 through 25 each end with a file you can point at. Eight of them, in the
book's own order:

1. `multi_agent_starter.py`, Chapters 4 and 5
2. `mcp_starter/`, Chapter 6
3. `claude_config_starter/`, Chapter 7
4. `extractor.py`, Chapter 8
5. `silent_failure_detector.py`, Chapter 9
6. `trust_enforcement_middleware.py`, Chapter 10
7. `harmlessness_screen.py`, Chapter 6, shipped standalone
8. `fallback_wrapper.py`, Chapter 5, shipped standalone

Running any of them spends your own Anthropic credit. The study files on this
page do not.

## The two ends of the loop

Day 1 and Day 28 are the same measurement taken twice. Write the baseline page
at the bottom of [diagnostic.md](diagnostic.md) on Day 1 (start date,
diagnostic score, weakest domain) and compare it to the mock scoresheet on Day
28. If the weakest domain is the same one, that chapter has not landed and you
re-read it in full.
