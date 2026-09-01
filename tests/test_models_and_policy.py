#!/usr/bin/env python3
"""The Pydantic models and the operator policy, offline.

Two halves:

  * the schemas import and their validators fire on the values the book says
    they should — needs `pydantic`, and skips cleanly with a non-zero-visible
    message if you do not have it
  * the operator policy loads and enforces both tiers the printed middleware
    only half-implemented — needs `pyyaml`, same deal

Neither half calls Claude. Constructing a Pydantic model is local work; that is
the whole reason Mechanism 1 is the cheap layer.
"""

import importlib.util
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
checks = 0
failures = []
skipped = []


def check(name, condition, detail=""):
    global checks
    checks += 1
    if condition:
        print(f"  [ ok ] {name}")
    else:
        print(f"  [FAIL] {name}  {detail}")
        failures.append(name)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def raises(fn):
    try:
        fn()
    except Exception:
        return True
    return False


print("\nmodels and policy\n")

# --- Chapter 9's assertion validators -------------------------------------
try:
    import pydantic  # noqa: F401
except ImportError:
    skipped.append("pydantic models (pydantic not installed)")
    print("  [skip] Chapter 9 validators — pydantic not installed")
else:
    det = load(ROOT / "chapters" / "09-silent-failures" /
               "silent_failure_detector.py", "silent_failure_detector")

    ok = det.ContractInfo(payment_terms="USD 18,000 per month, net 30",
                          effective_date=date(2026, 1, 15))
    check("a clean contract validates", ok.payment_terms.startswith("USD"))

    check("must_name_currency rejects a term with no currency",
          raises(lambda: det.ContractInfo(
              payment_terms="eighteen thousand a month",
              effective_date=date(2026, 1, 15))))

    check("must_be_within_decade rejects a date eleven years out",
          raises(lambda: det.ContractInfo(
              payment_terms="EUR 4,200 per month",
              effective_date=date.today() + timedelta(days=365 * 11))))

    check("a date nine years out is accepted",
          det.ContractInfo(payment_terms="GBP 31,500 per quarter",
                           effective_date=date.today()
                           + timedelta(days=365 * 9)) is not None)

    check("JudgeVerdict pins quality to the three the book names",
          raises(lambda: det.JudgeVerdict(quality="excellent", reason="x",
                                          confidence=0.9)))

    check("the detector's thresholds are the book's 0.7 and 0.5",
          det.SilentFailureDetector(None, "a", "b").judge_threshold == 0.7
          and det.SilentFailureDetector(None, "a", "b").refuse_threshold == 0.5)

    # --- Mechanism 2 end to end, no model anywhere ------------------------
    samples = ROOT / "chapters" / "09-silent-failures" / "samples"
    clean = det._DriftingAgent(drift_on=set())
    drifting = det._DriftingAgent(drift_on={2, 5})
    check("golden-set regression is empty when nothing drifted",
          det.golden_set_regression(
              clean, samples / "golden_set.json",
              samples / "golden_set_expected.json") == [])
    found = det.golden_set_regression(
        drifting, samples / "golden_set.json",
        samples / "golden_set_expected.json")
    check("golden-set regression finds exactly the two planted drifts",
          [f["id"] for f in found] == ["gs-02", "gs-05"], found)

# --- Chapter 10's operator policy -----------------------------------------
try:
    import yaml  # noqa: F401
except ImportError:
    skipped.append("operator policy (pyyaml not installed)")
    print("  [skip] Chapter 10 policy — pyyaml not installed")
else:
    mw = load(ROOT / "chapters" / "10-trust-and-safety" /
              "trust_enforcement_middleware.py", "trust_enforcement_middleware")
    policy = mw.OperatorPolicy()

    check("the policy carries the book's six allowed tools",
          policy.allowed_tools == [
              "Read", "Glob", "Grep", "mcp__filesystem__read_file",
              "mcp__filesystem__list_directory", "mcp__github__list_issues"],
          policy.allowed_tools)
    check("the policy carries all three forbidden patterns",
          policy.forbidden_command_patterns ==
          ["rm -rf", "DROP TABLE", "TRUNCATE"])
    check("read_only_database_role is on", policy.read_only_database_role)

    check("a listed tool is allowed",
          policy.tool_allowed("mcp__filesystem__read_file"))
    check("an unlisted tool is refused — this is Scenario A",
          not policy.tool_allowed("mcp__filesystem__delete_file"))
    check("Bash is refused; it is not on the list",
          not policy.tool_allowed("Bash"))

    check("rm -rf trips its pattern",
          policy.command_forbidden("rm -rf /var/data") == "rm -rf")
    check("matching is case-insensitive",
          policy.command_forbidden("drop table customers") == "DROP TABLE")
    check("an ordinary command passes",
          policy.command_forbidden("ls -la") is None)
    check("enforce_tool raises on a refusal",
          raises(lambda: policy.enforce_tool("mcp__filesystem__delete_file")))
    check("enforce_command raises on a forbidden pattern",
          raises(lambda: policy.enforce_command("TRUNCATE events")))

    check("the policy is frozen — allowed_tools hands back a copy",
          (lambda got: (got.append("Bash"),
                        policy.tool_allowed("Bash") is False)[1])(
              policy.allowed_tools))

print(f"\n{checks - len(failures)} of {checks} checks passed.")
if skipped:
    print(f"{len(skipped)} group(s) skipped: {'; '.join(skipped)}")
    print("Install them and rerun — CI does.")
print()
sys.exit(1 if failures else 0)
