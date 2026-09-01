# Day 1 Diagnostic: Five Questions, One Per Domain

Chapter 1's diagnostic. Five scenarios, one per domain. The point is not to pass. It is to find out which of the five domains you are weakest in, so you know which chapter to read twice.

> **Why the letters differ from the printed book.** Chapter 1 prints "The answers are B, B, B, B, B." The options are reordered here so the diagnostic can actually measure something. The stems and the reasoning are the book's, verbatim.

Answer all five before you scroll. Then:

```
python3 study/score_mock.py --diagnostic
```

**Question 1 (Domain 1, Agentic Architecture).** Your customer's chatbot is hallucinating confidently. It invents return policies, cites canceled flight numbers, sends shipments to wrong cities. You are the architect. The fix is:

A. Replace the system prompt with a more explicit refusal instruction.
B. Increase the temperature parameter to make the answers more cautious.
C. Add a coordinator that routes high-stakes questions to a structured-output subagent with a JSON schema, plus a fallback loop and a logged refusal path on schema violations.
D. Move from Sonnet 4.6 to Opus 4.7 for higher accuracy.

**Question 2 (Domain 2, Tool Design and MCP).** Your Claude agent works on your machine. Your teammate clones the repo. The MCP tools are gone. The agent runs but does nothing. The most likely cause is:

A. Your `.mcp.json` references absolute paths or env vars the teammate's machine doesn't have, or the file is in `.claude/` instead of the project root.
B. The teammate's Claude Code version is older than yours.
C. The MCP protocol is not portable across operating systems.
D. MCP requires a paid Claude subscription and the teammate has the free tier.

**Question 3 (Domain 3, Claude Code Configuration).** Your team has rules in `~/.claude/CLAUDE.md`. A new hire opens the project, runs `claude`, and her session ignores half the rules. The fix is:

A. Add the rules as a custom plugin in the plugin scope.
B. Put team-wide rules in `./CLAUDE.md` at the project root so they ship with the repo, and reserve `~/.claude/CLAUDE.md` for personal preferences.
C. Move the rules to a server-shared location that all teammates auto-mount.
D. Tell the new hire to copy your `~/.claude/CLAUDE.md` to her machine.

**Question 4 (Domain 4, Prompt Engineering and Structured Output).** Your extractor returns valid JSON ninety-three percent of the time. Seven percent of the time it returns malformed output. You need one hundred percent. The architectural fix is:

A. Post-process the malformed output with a regex.
B. Train a custom Claude model on your schema.
C. Lower the temperature to zero and rerun the failures.
D. Use `output_config.format` with a JSON schema so the API guarantees schema-valid output, then wrap the call in a fallback loop for upstream content failures.

**Question 5 (Domain 5, Safety and Reliability).** Your manager asks you to give the agent full read-write access to the production database to "let it just figure things out." You say no. The reason you give is:

A. The Claude Agent SDK doesn't support database connections.
B. Blast radius. A jailbroken or hallucinating agent with full database access can drop tables, leak rows across tenants, or write garbage that propagates to every downstream consumer. The architectural answer is a least-privilege MCP server that scopes the agent to read-only on the tables it actually needs, with query whitelisting and audit logging.
C. Anthropic's terms of service prohibit it.
D. Database access slows the agent down.

---

## Answers

**Question 1: C.** Because the exam is asking for an architectural fix, and the only architectural option in the four is the coordinator with structured outputs and a fallback loop. Switching models (A), tweaking the system prompt (C), and changing temperature (D) are knob-turns that may help at the margin but do not change the system's shape. The hallucinating-chatbot scenario will reappear in Chapter 4 (the coordinator), Chapter 8 (the schema), and Chapter 9 (the silent-failure trap that punishes the architects who skip step three). *(printed book: B)*

**Question 2: A.** Because MCP portability fails at exactly two layers: the config file's location, and the references inside it. Absolute paths and ungrounded env vars are how you break a teammate's clone in five seconds. The other three answers are red herrings the exam loves: A and C are factually wrong (MCP works across versions and pricing tiers), and D is a category error. Chapter 6 walks the full portability anatomy. *(printed book: B)*

**Question 3: B.** Because the four CLAUDE.md scopes go Managed, Project, User, Local, and only Project ships with the repo. There is no plugin scope. If you have ever seen a YouTuber teach a "3-Level CLAUDE.md hierarchy of project / user / plugin," that creator was guessing. Chapter 7 corrects the record and walks the actual hierarchy. *(printed book: B)*

**Question 4: D.** Because Anthropic's structured-output feature, `output_config.format` with a JSON schema, guarantees schema-valid JSON through constrained sampling. The other three options buy you a percentage point or two and leave you below one hundred. Chapter 8 walks the twenty-trial proof. *(printed book: B)*

**Question 5: B.** Because the architectural answer always names blast radius first. Least-privilege scoping, query whitelisting, audit logging, and a tightly scoped MCP server are the layers the exam grades. The other three answers are technically wrong (A and C) or beside the point (D). Chapter 10 walks the full trust hierarchy and the database-access scenario the exam wants you to be able to argue out loud. *(printed book: B)*

## Your baseline page

Chapter 1's deliverable is one page you keep: the date you started, your diagnostic score, and the domain you got wrong most. Write it now. You reference it at the end of Chapter 12 to decide whether to book the exam.

```
Started:            ____________________
Diagnostic score:   ____ / 5
Weakest domain:     ____________________
Target exam date:   ____________________
```

Put the weakest domain on a sticky note on your monitor. You look at it again on Day 28.
