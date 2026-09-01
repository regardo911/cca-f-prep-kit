#!/usr/bin/env python3
"""Five-field contract extractor with a twenty-trial test — Chapter 8.

The four-layer anti-hallucination stack, in one file:

  Layer 1  the prompt              — sets the task and names the five fields
  Layer 2  the schema              — output_format=ContractInfo, schema-valid
                                     JSON by construction
  Layer 3  the validators          — @field_validator catches what the schema
                                     cannot express
  Layer 4  the repair loop         — retry with 1s/2s/4s backoff

Needs your own ANTHROPIC_API_KEY. Twenty trials is twenty Opus calls at 2,048
max tokens on your own credit. `--limit 3` if you just want to watch it work.

    pip install anthropic pydantic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python3 extractor.py                       # the 20 committed samples
    python3 extractor.py --limit 3
    python3 extractor.py --samples ~/contracts --out ~/results.json
    python3 extractor.py --document one.txt    # a single file, printed

One correction to the printed listing. ch08:167 declares
`parties: list[str] = Field(min_length=2)` and passes the model straight to
`output_format`. Pydantic v2 compiles that to `minItems` in the emitted JSON
Schema, and ch08:71 says in the book's own words that length constraints are
not supported — it is the answer to the book's own exam question at ch08:73.
The constraint moved to a `@field_validator`, which is the architecture ch08:73
and ch08:250-252 actually teach. Same rule, enforced at Layer 3 where it works,
instead of Layer 2 where the endpoint rejects it.
"""

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

import anthropic
from pydantic import BaseModel, field_validator

DEFAULT_SAMPLES = Path(__file__).parent / "samples"
DEFAULT_OUT = Path("results.json")


class ContractInfo(BaseModel):
    """The five fields. ch08:166-183, with the Field() constraint relocated."""

    parties: list[str]
    effective_date: date
    termination_clause: str
    payment_terms: str
    governing_law: str

    @field_validator("termination_clause")
    def must_mention_duration(cls, v):
        assert any(unit in v.lower() for unit in ["day", "month", "year"]), \
            "termination_clause must reference a duration unit"
        return v

    @field_validator("parties")
    def parties_are_named_entities(cls, v):
        for p in v:
            assert len(p) >= 3, f"party name too short: {p}"
        return v

    @field_validator("parties")
    def at_least_two_parties(cls, v):
        # ch08:167 wrote this as Field(min_length=2). Length constraints are on
        # the endpoint's unsupported list (ch08:71), so it lives here instead.
        assert len(v) >= 2, f"a contract needs at least two parties, got {len(v)}"
        return v


client = anthropic.Anthropic()


def with_fallback(call, max_attempts=3, base_delay=1.0):
    """Layer 4. ch05:176-185, made synchronous.

    The printed wrapper awaits a sync client call, which raises TypeError. Same
    three attempts, same 1s/2s/4s backoff.
    """
    last_exc = None
    for attempt in range(max_attempts):
        try:
            return call()
        except (anthropic.RateLimitError, anthropic.APITimeoutError) as exc:
            last_exc = exc
            time.sleep(base_delay * (2 ** attempt))
    raise last_exc


def extract(document_text: str, model="claude-opus-4-7") -> ContractInfo:
    response = with_fallback(lambda: client.messages.parse(
        model=model,
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": f"""Extract the contract metadata from this document:

{document_text}

Return all five fields in the schema."""
            }
        ],
        output_format=ContractInfo,
    ))
    return response.parsed_output


def run_trials(paths, model, out_path):
    results = []
    for sample_path in paths:
        text = sample_path.read_text()
        try:
            info = extract(text, model=model)
            results.append({"file": sample_path.name, "status": "valid",
                            "data": info.model_dump(mode="json")})
            print(f"  [valid] {sample_path.name}")
        except Exception as e:
            results.append({"file": sample_path.name, "status": "error",
                            "error": str(e)})
            print(f"  [error] {sample_path.name}: {e}")
    out_path.write_text(json.dumps(results, indent=2, default=str))
    return results


def summarize(results, out_path):
    valid = sum(1 for r in results if r["status"] == "valid")
    errors = [r for r in results if r["status"] == "error"]
    print(f"\n{valid} of {len(results)} passed every layer. "
          f"Full log in {out_path}.\n")
    if not errors:
        print("No validator rejections in this batch. That is a clean run, not")
        print("a proof — a batch with zero semantic failures means the samples")
        print("were easy, and the next thing to do is write a harder one.")
        return
    print("Validator rejections — these are the wins. The schema could not have")
    print("caught any of them, because every one is shape-valid and")
    print("meaning-wrong:\n")
    for r in errors:
        print(f"  {r['file']}: {r['error']}")
    print("\nWrite one line per rejection into failure_modes.md. That file is")
    print("the regression set Chapter 9's detector earns its reps against.\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES,
                    help="directory of .txt documents (default: ./samples)")
    ap.add_argument("--document", type=Path,
                    help="extract one document and print it, no result log")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help="where the result log goes (default: ./results.json)")
    ap.add_argument("--limit", type=int,
                    help="stop after N documents — each one is a paid call")
    ap.add_argument("--model", default="claude-opus-4-7")
    args = ap.parse_args()

    if args.document:
        info = extract(args.document.read_text(), model=args.model)
        print(json.dumps(info.model_dump(mode="json"), indent=2, default=str))
        return 0

    if not args.samples.is_dir():
        sys.exit(f"--samples {args.samples} is not a directory")
    paths = sorted(args.samples.glob("*.txt"))
    if not paths:
        sys.exit(f"no .txt documents in {args.samples}")
    if args.limit:
        paths = paths[:args.limit]

    print(f"\n{len(paths)} document(s) through {args.model}, "
          f"four layers each:\n")
    results = run_trials(paths, args.model, args.out)
    summarize(results, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
