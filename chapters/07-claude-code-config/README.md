# Chapter 7: Claude Code Configuration

Domain 3 is 20% of the exam, and half of those questions probe whether you
understand the hierarchy you have to architect inside or memorized a misshapen
version of it from a video.

Two corrections the exam has distractor answers written for:

- CLAUDE.md has **four** scopes (Managed policy, Project, User, Local) and
  precedence runs **Local > User > Project > Managed**. There is no plugin
  scope.
- Claude Code has **more than thirty** built-in tools, not six.

## What you build

`claude_config_starter/`: a three-scope CLAUDE.md hierarchy that you prove by
making two scopes contradict each other, a `/recap` slash command, and one
`PostToolUse` hook on `Bash` matched to `git commit.*`.

Five files, and where each one goes is the whole lesson:

| File | Copy to | Ships with the repo? |
|---|---|---|
| `CLAUDE.project.md` | `./CLAUDE.md` | yes |
| `CLAUDE.user.md` | `~/.claude/CLAUDE.md` | no |
| `CLAUDE.local.md.example` | `./CLAUDE.local.md` | no, gitignored |
| `recap.command.md` | `.claude/commands/recap.md` | yes |
| `settings.hooks.json` | `.claude/settings.json` | yes |

## The one command

There isn't one, and that is the honest answer for this chapter. Config files do
not run. What they do is change how a live session behaves, and the only way to
see that is to open a session and look.

[`claude_config_starter/VERIFY.md`](claude_config_starter/VERIFY.md) is the
four-check procedure. It needs Claude Code installed; it does not need an
Anthropic API key beyond whatever your Claude Code session already uses.

The alternative would have been a script that printed "precedence verified",
which would be a claim about a session it never opened. Chapter 9 is about
exactly that failure mode, so it would be a strange thing to ship in Chapter 7.

## What success looks like

1. `/recap` runs in a fresh session and returns five bullets in under ten
   seconds.
2. Project says 4-space, Local says 2-space, and the agent says **2-space**.
3. The agent commits, and the hook has run `ruff` against the project
   afterward.
4. You can answer the teammate question cold: clone this repo with default
   settings and *which* of these five files' rules survive? (Three of them.)

## How to run it on your own project

Install the five files into a repo you actually work in. That is the transfer
step, and it is the same five `cp` commands from `VERIFY.md`. Then do the audit:
open your existing `~/.claude/CLAUDE.md` and read it for anything your *team*
depends on. Every line that belongs to the project rather than to you is a rule
your new hire's session is silently missing. Move those into `./CLAUDE.md`.

Copy `claude_config_starter/` into your own `cca-f-prep` and tag the commit
`ch07-config-complete`.

## Why the names are odd here

The hook in `settings.hooks.json` is real. It matches `git commit.*` and runs
`ruff check . --fix --silent`, which rewrites source files. If this repo shipped
it at `.claude/settings.json`, it would be a live hook in *this* repo rather
than a sample of one, and it would edit files behind you. Same reason
`CLAUDE.local.md.example` carries the suffix. Nothing about the contents
changed: the files are the book's, byte for byte, under names that stay inert
until you deliberately install them.
