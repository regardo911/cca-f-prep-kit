# Verifying the config starter

Chapter 7's checkpoint is a live-session observation: does `/recap` load, and
does Local actually beat Project when they contradict each other? No committed
file can answer that. A script that claimed to would be lying about a session it
never ran. So this is a procedure you run by hand, and it takes about five
minutes.

## Install the five files

Copy each one to the path in the right column. The paths are the point of the
exercise, because a file in the wrong scope is exactly the Domain 3 failure.

| File here | Copy to | Scope |
|---|---|---|
| `CLAUDE.project.md` | `./CLAUDE.md` | Project, ships with the repo |
| `CLAUDE.user.md` | `~/.claude/CLAUDE.md` | User, rides with you |
| `CLAUDE.local.md.example` | `./CLAUDE.local.md` | Local, gitignored |
| `recap.command.md` | `.claude/commands/recap.md` | Project slash command |
| `settings.hooks.json` | `.claude/settings.json` | Project hooks |

```
cd ~/code/your-prep-repo
cp .../CLAUDE.project.md        ./CLAUDE.md
mkdir -p ~/.claude && cp .../CLAUDE.user.md ~/.claude/CLAUDE.md
cp .../CLAUDE.local.md.example  ./CLAUDE.local.md
mkdir -p .claude/commands
cp .../recap.command.md         .claude/commands/recap.md
cp .../settings.hooks.json      .claude/settings.json
echo "CLAUDE.local.md" >> .gitignore
```

Renaming happens on the way in, not on the way out. `.claude/commands/recap.md`
is what makes the command `/recap`; `recap.command.md` sitting anywhere else is
just a markdown file.

## Check 1: the slash command loads

Open a fresh Claude Code session in the project directory and run `/recap`.

**Pass:** it runs `git log --oneline -20` and comes back with five bullets in
under ten seconds. **Fail:** "unknown command" means the file is not at
`.claude/commands/recap.md`, or you are not in the project directory.

`/recap` is not a built-in. `/init`, `/agents`, `/memory`, `/permissions`,
`/mcp`, `/compact` and friends are. Knowing which side of that line a command
falls on is a Domain 3 question.

## Check 2: precedence, the one that is actually graded

Add a contradiction across two scopes:

```
echo "- Use 4-space indentation in Python." >> ./CLAUDE.md
echo "- Use 2-space indentation in Python." >> ./CLAUDE.local.md
```

Open a fresh session and ask which indentation it will use.

**Pass:** it says 2-space. Local takes precedence over Project.

The full ordering, most specific to least, is **Local > User > Project >
Managed policy**. Four scopes. There is no plugin scope. The "3-level
project / user / plugin" framing circulating on YouTube is wrong, and the exam
has distractor options written to match it.

Undo the contradiction when you are done, or your agent will keep arguing with
itself.

## Check 3: the hook fires

Have the agent make a commit in the project. The `PostToolUse` hook matches
`git commit.*` on the `Bash` tool and runs `ruff check . --fix --silent`
afterward.

**Pass:** the linter has run against the project after the commit. It is
non-blocking, so the commit completes either way. **Fail:** nothing happened.
Check that `ruff` is installed and on PATH, and that the file landed at
`.claude/settings.json`.

**This hook edits your files.** `--fix` rewrites source in place, every time the
agent commits. That is the book's example and it is a fine one, but install it
somewhere you can afford to have rewritten, and read the diff the first time it
fires.

## Check 4: the teammate test

The question that decides every Domain 3 stem: *if a teammate cloned this repo
right now with default settings, which of these rules would they get?*

`./CLAUDE.md` ships. `.claude/commands/recap.md` ships. `.claude/settings.json`
ships. `~/.claude/CLAUDE.md` does not, because it is in your home directory and
not in the repo. `./CLAUDE.local.md` does not either; you gitignored it on
purpose.

So if a rule your whole team depends on is sitting in your User scope, the new
hire's session silently runs without it. That is the entire chapter.
