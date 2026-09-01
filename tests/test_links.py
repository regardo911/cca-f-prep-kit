#!/usr/bin/env python3
"""Every relative link in every markdown file points at a file that exists.

Also asserts the two directions of the README's copy table: every path the table
names exists, and every artifact the repo ships is named somewhere in the
README.

Standard library only. No key, no network — external URLs are listed, never
fetched.
"""

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urldefrag

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
BACKTICKED = re.compile(r"`([^`\n]+)`")

checks = 0
failures = []


def check(name, condition, detail=""):
    global checks
    checks += 1
    if condition:
        print(f"  [ ok ] {name}")
    else:
        print(f"  [FAIL] {name}  {detail}")
        failures.append(name)


docs = sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts)
print(f"\nlinks across {len(docs)} markdown file(s)\n")
check("there are markdown files to check", len(docs) > 10, len(docs))

broken = []
external = 0
for doc in docs:
    for target in LINK.findall(doc.read_text()):
        target = target.strip()
        if target.startswith(("http://", "https://", "mailto:")):
            external += 1
            continue
        if target.startswith("#"):
            continue
        path, _ = urldefrag(target)
        if not path:
            continue
        resolved = (doc.parent / unquote(path)).resolve()
        if not resolved.exists():
            broken.append(f"{doc.relative_to(ROOT)} -> {target}")

check("no broken relative links", not broken, "; ".join(broken[:5]))
print(f"         ({external} external URL(s) listed, none fetched)")

# --- the copy table, both directions --------------------------------------
readme = (ROOT / "README.md").read_text()

# The copy table is the row a reader follows to get their own repo started, so
# both directions of it get asserted: every source path it names exists, and
# below, every artifact this repo ships is named in the README somewhere.
start = readme.index("## The copy table")
copy_table = readme[start:readme.index("\n## ", start + 1)]
table_rows = [line for line in copy_table.splitlines()
              if line.startswith("| ") and line.count("|") >= 4]
sources = []
for row in table_rows:
    cell = row.split("|")[2].strip()
    if "`" not in cell:
        continue
    paths = [p.strip() for p in BACKTICKED.findall(cell)]
    if not paths or "/" not in paths[0]:
        continue
    base = ROOT / paths[0]
    for i, p in enumerate(paths):
        # later paths in a cell are relative to the first one's directory,
        # the way "extractor.py + samples/" reads on the page
        target = ROOT / p if i == 0 else base.parent / p
        sources.append((p, target))

check("the copy table has rows to check", len(sources) >= 12, len(sources))
missing_from_disk = [p for p, target in sources if not target.exists()]
check("every source path in the copy table exists on disk",
      not missing_from_disk, "; ".join(missing_from_disk[:5]))

SHIPPED = [
    "study/diagnostic.md", "study/mock-exam.md", "study/score_mock.py",
    "study/30-day-plan.md", "study/cheat-sheets", "study/glossary.md",
    "chapters/04-agentic-architecture", "chapters/05-orchestration",
    "chapters/06-mcp-portability", "chapters/07-claude-code-config",
    "chapters/08-structured-output", "chapters/09-silent-failures",
    "chapters/10-trust-and-safety", "chapters/11-cert-positioning",
    "shared/harmlessness_screen.py", "shared/fallback_wrapper.py",
]
unnamed = [s for s in SHIPPED if s not in readme]
check("every shipped artifact is named in the README",
      not unnamed, "; ".join(unnamed))

# --- the five images ------------------------------------------------------
images = sorted((ROOT / "docs" / "images").glob("*.png"))
check("all five images are present and are real PNGs",
      len(images) == 5 and all(
          p.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n" for p in images),
      [p.name for p in images])

embedded = [p.name for p in images if p.name in readme]
check("every image is embedded in the README",
      len(embedded) == len(images),
      f"missing: {set(p.name for p in images) - set(embedded)}")

# images are <img> tags so the README can constrain how big they render;
# accept the markdown form too, in case one gets written back that way.
alt_text = (re.findall(r"!\[([^\]]*)\]\(docs/images/", readme)
            + re.findall(r'<img src="docs/images/[^"]+"[^>]*\salt="([^"]*)"', readme))
check("every image carries descriptive alt text",
      len(alt_text) == 5 and all(len(a) > 40 for a in alt_text),
      [len(a) for a in alt_text])

# --- the nesting hazard, asserted rather than remembered ------------------
hazards = [p.relative_to(ROOT) for p in ROOT.rglob("*")
           if ".git" not in p.parts
           and (p.name in ("CLAUDE.md", "CLAUDE.local.md")
                or (p.is_dir() and p.name == ".claude"))]
check("no CLAUDE.md, CLAUDE.local.md or .claude/ anywhere in the tree",
      not hazards, hazards)

print(f"\n{checks - len(failures)} of {checks} checks passed.\n")
sys.exit(1 if failures else 0)
