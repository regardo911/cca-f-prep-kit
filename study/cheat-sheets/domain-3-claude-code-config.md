<!-- Appendix A, Domain 3 cheat sheet, verbatim. Tape it to the wall. -->

### Domain 3 (20%) — Claude Code Configuration and Workflows

- CRITICAL: CLAUDE.md has FOUR scopes, NOT three. Managed policy → Project → User → Local. There is NO "plugin" scope. The "3-Level project/user/plugin" framing is a YouTuber simplification and is wrong.
- Operationally meaningful three: Project (`./CLAUDE.md`) → User (`~/.claude/CLAUDE.md`) → Local (`./CLAUDE.local.md`, gitignored).
- Precedence: Local > User > Project > Managed. Files concatenated, not overridden; later-loaded scopes win on contradictions.
- CRITICAL: Claude Code has more than 30 built-in tools, NOT six. The "six tools" framing is also a YouTuber simplification.
- The eight tools you reach for daily: Read, Write, Edit, Bash, Grep, Glob, Agent (for delegation), WebFetch.
- User-defined slash commands: `.claude/commands/<name>.md` (project) or `~/.claude/commands/<name>.md` (user). `/recap` is NOT a built-in.
- Hooks in `.claude/settings.json`: events `PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `InstructionsLoaded`. Run as shell commands.
- Skills at `.claude/skills/<name>/SKILL.md`. AI-invoked. Distinct from slash commands (user-invoked).
- Path-scoped rules at `.claude/rules/<name>.md` with `paths:` frontmatter for glob-matched scoping.
- Custom subagent definitions at `.claude/agents/<name>.md` with frontmatter declaring `tools` and `model`.
