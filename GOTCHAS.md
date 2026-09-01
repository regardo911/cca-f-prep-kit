# gotchas

things that actually bit while building this, and every place the printed book
disagrees with itself. not a list of general advice. each one names the file, the
chapter line, or the command output that proves it.

if you are holding the book and something here contradicts it, this file says which
one this repo followed and why.

## the mock's answer key is worse than "mostly B"

i went in expecting a skew and measured it anyway. parsing the printed key gives
B 47/60, A 12, C 1, **D zero times**. then the second one, which i did not
expect: the correct answer is the strictly longest of the four options in 51 of
60, no ties.

so two independent tells, and either one alone beats the pass bar. that is what
turned "shuffle the options" from a nice-to-have into the reason `study/` has a
scorer at all. blind-picking B against `study/answer-key.json` now scores 15/60,
and `tests/test_score_mock.py` asserts it stays under 20 so nobody quietly
un-shuffles this later.

what shuffling cannot fix: the length tell. that lives in the option text and
the text is verbatim. said so out loud at the top of `study/mock-exam.md`
instead of pretending otherwise.

what did *not* change: the stems, the correct answers, and every line of
reasoning in the key, chapter cites and all. only the order of the four options
inside each question, now exactly fifteen A, fifteen B, fifteen C, fifteen D.

the reordering is deterministic and checked in at `study/answer-key.json`, so
retaking in two weeks gives you the same paper and your old scoresheet still
means something. every entry carries `book_answer`, so you can map any question
back to the printed key in one step. if you have the book open beside this,
cross-check by the reasoning, not by the letter.

## `git ls-files` on a tree with no git repo reports success

ran the repo's own quality scan before `git init` and got a clean pass on
checks that read `git ls-files`. of course it did: the command returns nothing
and "nothing" satisfies "no bad files". re-ran after the first commit and it
actually looked at the tree.

anything that greps tracked files is meaningless until the repo exists. order
matters: `git init`, commit, *then* scan.

## codex asked for an OPENAI_API_KEY that was never needed

first image run came back with `OPENAI_API_KEY is not set` and a refusal. the
key is genuinely not required. codex has a built-in image tool and had gone
looking for the CLI path instead. adding one line to the prompt ("use your
built-in image_gen tool, do not use a CLI fallback, do not ask for
OPENAI_API_KEY") fixed all five on the next run.

it also left `tmp/` and `output/` behind in the repo root on the failed attempt.
check what a generator wrote before you commit, not after.

## the first hero image put 15% under the wrong day range

five labels, all spelled right, bars in correct proportion, and one connector
line landing on the tick above "Days 23-25" when it belonged on "Days 20-22". an
exit code would never have caught it, and neither would skimming.

measured it rather than squinting: pulled the amber dot centres and the tick
centres out of the PNG and compared. four dots exact, one off by a hundred-odd
pixels onto the wrong tick. regenerated with the five connections spelled out
one per line; second render has four dots landing exactly on their tick and the
fifth within its own label.

for a diagram whose entire content is a mapping, a wrong line is a wrong fact.

## `.claude/settings.json` is a live hook, not a code sample

chapter 7's artifact is a real `PostToolUse` hook that matches `git commit.*`
and runs `ruff check . --fix --silent`. it rewrites source files. drop it at a
project root and it is not a sample of a hook, it is a hook. including in this
repo, during the build, on the commit that would have installed it.

everything under `chapters/07-claude-code-config/claude_config_starter/` is
therefore named to stay inert: `settings.hooks.json`, `CLAUDE.project.md`,
`CLAUDE.local.md.example`. contents byte-identical to the book, names that do
nothing until you deliberately copy them. `tests/test_links.py` asserts no
`CLAUDE.md`, no `CLAUDE.local.md` and no `.claude/` directory exists anywhere in
the tree, because remembering is not a control.

## a passing checker proves nothing about the checker

`check_portability.py` returned five green checks on the shipped `mcp_starter`
first try. so would `return 0`.

`tests/test_portability.py` now copies the starter to a temp dir and breaks it
five different ways (absolute path into `args`, delete `.env.example`, move
`.mcp.json` under `.claude/`, drop `"project"` from `settingSources`, remove the
npx servers) and asserts the *right* check fails each time, by number. two of
the five assertions were wrong on the first pass and the checker was silently
passing configs it should have refused.

don't ship a validator whose failure path you have never seen.

## the printed `.mcp.json` says `python`, which does not exist

ch06:193 registers the summarizer with `command: "python"`. stock ubuntu 22.04+
ships no bare `python`, and macos 12.3+ removed `/usr/bin/python`. a reader who
copies it gets a server that never starts, which looks exactly like gotcha 5,
"missing node binary", and sends them hunting in the wrong place.

`python3` everywhere in this repo, including inside the config payload and
inside the copied CI job. noted in the chapter README so nobody thinks it is a
transcription slip.

## where the printed code and the printed prose disagree

five of them. in every case the book's worked example won, because that is the
version the chapter actually walks you through.

| where | the problem | here |
|---|---|---|
| ch05:176-185 | `with_fallback` is `async` and does `await call()`, but every call site is a synchronous client. awaiting a sync SDK return raises `TypeError`. | the appendix listing ships verbatim in `shared/fallback_wrapper.py`, with `SyncFallbackWrapper` beside it using `time.sleep`. same three attempts, same 1s/2s/4s. |
| ch08:167 | `Field(min_length=2)` on a structured-output model compiles to `minItems`, which ch08:71 lists as unsupported. | moved to a `@field_validator`, which is what ch08:73 teaches. |
| ch06:165-181 | the printed `.mcp.json` registers two servers; the chapter title, checkpoint and deliverable all say three. | all three registered. `python3` not `python`, for the reason two sections down. |
| ch09:169-178 | the detector class has a dead assignment and calls two functions it never imports. | assembled as one module. |
| ch10:118-123 | `build_options()` reads only `allowed_tools`, leaving `forbidden_command_patterns` declared and unenforced. | both enforced. pattern matching is case-insensitive, because `drop table` and `DROP TABLE` are the same request and only one of them is in the file. |

one number this repo states differently. chapter 5 calls cache writes a "fifty
percent surcharge" and then, ten lines later, prints $6.25 for a five-minute
write and $10 for a one-hour write against a $5 base. those are 25% and 100%.
the dollar figures match anthropic's published rates, so
`chapters/05-orchestration/cost-notes.md` carries $6.25, $10 and $0.50 and
leaves the percentage out.

on proctoring, all this repo will tell you is that the exam is online and
video-proctored. confirm the vendor and the setup requirements in the exam
portal close to your date. that is the kind of detail that moves.

## things this repo deliberately does not do

**no quiz app.** the exam is sixty multiple-choice questions on architecture,
and the reader this book is written for has not written python in years. a
spaced-repetition engine would be a thing to learn before you could study. the
mock is a markdown file and the scorer is one stdlib script.

**nothing under `chapters/` is stubbed to run offline.** faking the model would
simulate the exact architecture the exam grades and hand you a fake. the study
half is genuinely keyless; the code half genuinely needs your key. those are
two different claims and this repo keeps them apart.

**no `results.json`, no recorded transcript, no sample output for the keyed
scripts.** see the last section: nobody here has run them against a live key,
so there is nothing honest to show. the chapter READMEs tell you what to look
for instead of showing you output that was never produced.

## what is not in here

nothing about the eight build projects failing at runtime, because none of them
has been run against a live key from this repo. no key here, so no observations
to report. the study half is a different story: every keyless script in this
repo has been run, and the numbers quoted above came out of those runs.
