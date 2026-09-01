#!/usr/bin/env python3
"""Batch companion to multi_agent_starter.py — Chapter 5.

Takes a list of queries instead of one and submits them as a batch. Fifty
percent off both input and output tokens, uniformly across every active model
(ch05:3, ch05:15). Not thirty. Fifty.

Needs your own ANTHROPIC_API_KEY. Submitting a batch spends your own credit.

    python3 multi_agent_batch.py                      # the book's three queries
    python3 multi_agent_batch.py queries.txt          # one query per line
    python3 multi_agent_batch.py -q "..." -q "..."    # queries on the command line
    cat queries.txt | python3 multi_agent_batch.py

What it will not do is tell you what the run cost. ch05:264 sends you to your
Anthropic console for that, and it is right to: the batch's price lives in
Anthropic's billing system, not in this process. Printing a dollar figure here
would be inventing a receipt.
"""

import argparse
import sys
from pathlib import Path

# ch05:239-243, the book's three, kept as the default so a reader who types
# nothing sees the book's behavior.
DEFAULT_QUERIES = [
    "What does our README say about deployment?",
    "What does our README say about rollback?",
    "What does our docs/architecture.md describe about the coordinator?",
]

MAX_BATCH_SIZE = 100_000  # ch05:48, or 256 MB, whichever you hit first


def read_queries(args):
    if args.query:
        return list(args.query)
    if args.file:
        text = Path(args.file).read_text()
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        return list(DEFAULT_QUERIES)
    queries = [line.strip() for line in text.splitlines()
               if line.strip() and not line.startswith("#")]
    if not queries:
        sys.exit("no queries found in that input")
    return queries


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file", nargs="?",
                    help="file of queries, one per line; omit for the book's "
                         "three or pipe them on stdin")
    ap.add_argument("-q", "--query", action="append",
                    help="a query, repeatable")
    ap.add_argument("--model", default="claude-opus-4-7")
    ap.add_argument("--max-tokens", type=int, default=2048,
                    help="per request; must be at least 1 — the batch endpoint "
                         "will not do max_tokens=0 cache pre-warming (ch05:50)")
    args = ap.parse_args()

    queries = read_queries(args)
    if len(queries) > MAX_BATCH_SIZE:
        sys.exit(f"{len(queries):,} queries exceeds the {MAX_BATCH_SIZE:,} "
                 f"per-batch maximum. Split it into "
                 f"{-(-len(queries) // MAX_BATCH_SIZE)} batches and keep the "
                 f"custom_id plumbing so you can match responses back.")
    if args.max_tokens < 1:
        sys.exit("--max-tokens must be at least 1 (ch05:50)")

    import anthropic
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    client = anthropic.Anthropic()

    batch = client.messages.batches.create(
        requests=[
            Request(
                custom_id=f"q-{i:03d}",
                params=MessageCreateParamsNonStreaming(
                    model=args.model,
                    max_tokens=args.max_tokens,
                    messages=[{"role": "user", "content": q}],
                ),
            )
            for i, q in enumerate(queries)
        ]
    )

    print(f"batch id: {batch.id}")
    print(f"submitted {len(queries)} request(s) on {args.model}")
    for i, q in enumerate(queries):
        print(f"  q-{i:03d}  {q}")
    print()
    print("Most batches finish inside an hour; the processing window closes at "
          "24 hours and results stay available for 29 days (ch05:48). Poll the "
          "batch by its id.")
    print("Cost: check your Anthropic console. It should land at half the "
          "equivalent synchronous run — that is the thing to verify, and this "
          "script cannot verify it for you.")


if __name__ == "__main__":
    main()
