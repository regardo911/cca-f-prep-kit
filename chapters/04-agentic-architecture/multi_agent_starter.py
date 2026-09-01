#!/usr/bin/env python3
"""Coordinator plus two subagents — Chapter 4, upgraded by Chapter 5.

Without "Agent" in the coordinator's allowed_tools the coordinator cannot
delegate at all. ch04:25 calls that the single most exam-relevant detail in the
chapter, and `--no-agent-tool` below lets you watch it break without editing
this file.

Two run modes, because Chapter 5 Step 3 tells you to replace the Researcher
call site and it is worth seeing both:

    --mode agent   Chapter 4's streaming query() coordinator (default)
    --mode typed   Chapter 5's typed Researcher call, schema-bound and
                   wrapped in the fallback loop

Needs your own ANTHROPIC_API_KEY. Every run is real Claude traffic on your own
credit. Nothing here is stubbed or replayed.

    pip install claude-agent-sdk anthropic pydantic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python3 multi_agent_starter.py
    python3 multi_agent_starter.py --query "How do we roll back?" --project ../..
    python3 multi_agent_starter.py --no-agent-tool     # the Step 6 break test

This file is deliberately self-contained so you can copy it straight into your
own cca-f-prep repo. `shared/fallback_wrapper.py` is the standalone
build-project form of the same retry wrapper.
"""

import argparse
import asyncio
import sys
from pathlib import Path

# --- Chapter 4, the two subagent system prompts, verbatim -------------------

RESEARCHER_PROMPT = """
Find evidence in the project files relevant to the user's question.
Return a JSON object with a "citations" array of {file, snippet, line_start, line_end}
and a "confidence" field of "low", "medium", or "high".
If you cannot find relevant evidence, return citations: [] and confidence: "low".
"""

SYNTHESIZER_PROMPT = """
Compose a final answer that cites only the material the researcher returned.
For every claim in your answer, cite the file and line range from the researcher's citations.
If a claim cannot be cited from the researcher's output, remove it.
"""

# Published per-million-token rates from ch04:246. Used only to label an
# estimate. This script never reads your bill.
RATES = {
    "claude-opus-4-7": (5.0, 25.0),
    "claude-haiku-4-5": (1.0, 5.0),
}

DEFAULT_QUERY = "What does our README say about deployment?"
DEFAULT_PROJECT = Path(__file__).parent / "sample-project"


def build_options(coordinator_model, subagent_model, with_agent_tool=True):
    """The coordinator's own tool budget, plus the two subagents.

    A subagent's tool list cannot exceed the coordinator's, but it can be
    narrower (ch04:84). Researcher is read-only; Synthesizer is narrower still,
    which is why it cannot invent.
    """
    from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions

    allowed = ["Read", "Glob", "Grep", "Agent"]
    if not with_agent_tool:
        # ch04:244's Step 6 "break it" exercise, as a flag instead of a source
        # edit. Expect the coordinator to either answer without subagent help
        # or to error about delegation not being authorized — the book says
        # "either... or", so watch which one you actually get.
        allowed = ["Read", "Glob", "Grep"]

    return ClaudeAgentOptions(
        model=coordinator_model,
        allowed_tools=allowed,
        agents={
            "researcher": AgentDefinition(
                description="Searches project files and returns structured citations.",
                prompt=RESEARCHER_PROMPT,
                tools=["Read", "Glob", "Grep"],
                model=subagent_model,
            ),
            "synthesizer": AgentDefinition(
                description="Composes a cited final answer from researcher output.",
                prompt=SYNTHESIZER_PROMPT,
                tools=["Read"],
                model=subagent_model,
            ),
        },
    )


def researcher_task(user_query, project):
    """Structured context passing — ch04:152-160.

    The coordinator delegates a task, not the user's question. The subagent
    gets a contractual interface instead of a conversational one.
    """
    return {
        "objective": "Find evidence about deployment in the project files.",
        "search_scope": ["README.md", "docs/**/*.md", ".github/workflows/*.yml"],
        "must_cite": True,
        "max_citations": 6,
        "user_query_for_context_only": user_query,
        "project_root": str(project),
    }


def _usage(message):
    """Token counts, if this message carries any. Never guesses."""
    u = getattr(message, "usage", None)
    if u is None:
        return None
    got = {}
    for name in ("input_tokens", "output_tokens",
                 "cache_creation_input_tokens", "cache_read_input_tokens"):
        value = getattr(u, name, None)
        if value is None and isinstance(u, dict):
            value = u.get(name)
        if isinstance(value, int):
            got[name] = value
    return got or None


def report_usage(totals, model):
    """Print what the SDK actually returned, and nothing it did not."""
    if not totals:
        print("\ntoken usage: this stream did not carry a usage field. "
              "Read the real numbers on your Anthropic console.")
        return
    print("\ntoken usage, as returned by the SDK:")
    for name in sorted(totals):
        print(f"  {name}: {totals[name]:,}")
    rate = RATES.get(model)
    if rate and ("input_tokens" in totals or "output_tokens" in totals):
        est = (totals.get("input_tokens", 0) / 1e6 * rate[0]
               + totals.get("output_tokens", 0) / 1e6 * rate[1])
        print(f"  estimate: ${est:.4f} if every one of those tokens billed at "
              f"{model}'s published ${rate[0]}/${rate[1]} per million.")
        print("  Subagent tokens bill at their own model's rate, so treat that "
              "as a ceiling, not a receipt. Your console has the real figure.")


async def run_agent_mode(args):
    from claude_agent_sdk import query

    options = build_options(args.model, args.subagent_model,
                            with_agent_tool=not args.no_agent_tool)
    task = researcher_task(args.query, args.project)
    prompt = (
        f"Execute the task in researcher_task. Return citations matching the "
        f"schema. Do not respond to the user_query directly; that field is "
        f"context only.\n\nresearcher_task = {task}"
    )
    totals = {}
    async for message in query(prompt=prompt, options=options):
        print(message)
        got = _usage(message)
        if got:
            for k, v in got.items():
                totals[k] = totals.get(k, 0) + v
    report_usage(totals, args.model)


def run_typed_mode(args):
    """Chapter 5 Steps 2-4: schema-bound Researcher, wrapped in the retry."""
    import time

    import anthropic
    from pydantic import BaseModel
    from typing import Literal

    class Citation(BaseModel):
        file: str
        snippet: str
        line_start: int
        line_end: int

    class ResearcherOutput(BaseModel):
        citations: list[Citation]
        confidence: Literal["low", "medium", "high"]
        refusal_reason: str | None = None

    client = anthropic.Anthropic()

    def with_fallback(call, max_attempts=3, base_delay=1.0):
        """ch05:176-185, made synchronous.

        The printed wrapper is `async` and does `await call()`, but every call
        site the book gives you is a sync client, and awaiting a sync SDK
        return raises TypeError. Same three attempts, same 1s/2s/4s backoff.
        """
        last_exc = None
        for attempt in range(max_attempts):
            try:
                return call()
            except (anthropic.RateLimitError, anthropic.APITimeoutError) as exc:
                last_exc = exc
                time.sleep(base_delay * (2 ** attempt))
        raise last_exc

    def call_researcher(user_query: str) -> ResearcherOutput:
        response = with_fallback(lambda: client.messages.parse(
            model=args.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": user_query}],
            output_format=ResearcherOutput,
        ))
        return response.parsed_output

    task = researcher_task(args.query, args.project)
    out = call_researcher(str(task))
    print(f"confidence: {out.confidence}")
    if out.refusal_reason:
        print(f"refusal:    {out.refusal_reason}")
    for c in out.citations:
        print(f"  {c.file}:{c.line_start}-{c.line_end}  {c.snippet[:70]!r}")
    if not out.citations:
        print("  no citations returned — this is the refusal path, "
              "and it is the correct behavior when there is no evidence.")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--query", default=DEFAULT_QUERY,
                    help=f"the user's question (default: {DEFAULT_QUERY!r})")
    ap.add_argument("--project", type=Path, default=DEFAULT_PROJECT,
                    help="directory the Researcher searches (default: the "
                         "sample-project fixture next to this file)")
    ap.add_argument("--mode", choices=("agent", "typed"), default="agent",
                    help="agent = Chapter 4's streaming coordinator; "
                         "typed = Chapter 5's schema-bound Researcher call")
    ap.add_argument("--model", default="claude-opus-4-7",
                    help="coordinator model (default: claude-opus-4-7)")
    ap.add_argument("--subagent-model", default="claude-haiku-4-5",
                    help="subagent model (default: claude-haiku-4-5)")
    ap.add_argument("--no-agent-tool", action="store_true",
                    help='drop "Agent" from the coordinator allow-list — '
                         "ch04:244's break test, without editing this file")
    args = ap.parse_args()

    if not args.project.exists():
        sys.exit(f"--project {args.project} does not exist")
    if args.mode == "typed" and args.no_agent_tool:
        sys.exit("--no-agent-tool only means something in --mode agent; the "
                 "typed path does not delegate.")

    if args.mode == "agent":
        asyncio.run(run_agent_mode(args))
    else:
        run_typed_mode(args)


if __name__ == "__main__":
    main()
