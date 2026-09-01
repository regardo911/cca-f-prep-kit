# The Five Judgment Patterns

The exam grades whether you can name one of five scenario archetypes inside the
first ten seconds of reading a stem. Name the archetype and the wrong answers
fall away on their own. Miss it and every option looks defensible while the
clock runs.

These five are the book's synthesis, not Anthropic's taxonomy. Anthropic does
not publish archetypes. They came out of drilling scenario stems.

## The card

Cues and templates below are Chapter 3's, condensed to the five rows Chapter 3
asks you to write. Print this side; drill against the blank on the next page.

| # | Pattern | Three stem cues | Answer template |
|---|---|---|---|
| 1 | Scale Failure | *at scale* · *p95 / latency / timeout* · *cost spike* | Batch, then schema, then fallback loop |
| 2 | Wrong-Tool Routing | *calls the wrong tool* · *hits the wrong endpoint* · *fired create when the user said update* | Tighten descriptions, narrow subagent `tools` |
| 3 | Silent Failure | *no exception thrown* · *passes JSON validation* · *user complains days later* | Assertions, golden set, LLM-as-judge |
| 4 | Cross-Machine Portability | *works on my machine* · *teammate clones the repo* · *CI misses the tools* | Move the config to the scope that matches its intent |
| 5 | Trust-Boundary Edge Case | *user requests an override* · *prompt-injection attempt* · *operator policy conflicts with the user* | Name blast radius, then least-privilege scope |

## The traps, one per pattern

Each of these is the answer candidates reach for first. Each is a knob-turn
where the exam wants an architectural change.

**Pattern 1.** "Switch to Haiku" when the stem mentions cost. Haiku is cheaper
per token, but the Batch discount is fifty percent and applies across every
model. Route to Batch, then choose the model independently.

**Pattern 2.** "Fine-tune the system prompt to nudge Claude toward the right
tool." Prompt nudges are knob-turns. Tool-description tightening and subagent
scoping are the architectural fixes.

**Pattern 3.** "Increase log verbosity." It does not detect and it does not fix.
Neither does lowering temperature, and neither does a more capable model.

**Pattern 4.** "The teammate has a different Claude Code version." Version skew
is real and it is almost never the root cause. When the stem says *one config
file in the wrong place*, the answer is the file and its scope.

**Pattern 5.** "Anthropic's terms of service prohibit it." The exam grades
architecture, not policy. Even if it were prohibited, the architectural answer
would still be the architectural answer.

## Two more things worth holding

Patterns overlap on purpose, and the harder questions carry two at once. Pick
the dominant one, apply the template, validate against the wrong-answer cues,
move on.

Each domain also has a canonical opener the exam writers reuse. Domain 1's is
the hallucinating customer chatbot. Domain 2's is the agent that works on your
laptop and dies on your teammate's. Domain 3's is the rules in the wrong
CLAUDE.md scope. Domain 4's is the JSON extractor that is ninety-three percent
valid. Domain 5's is the agent that returns a clean-looking answer that is
quietly, completely wrong.

---

## Now write it from memory

Chapter 3's deliverable is *you* writing this card, not reading mine. The
recognition rep is the writing. Cover the table above and fill this in; then
diff it against the card.

```
# | Pattern name                | Three stem cues              | Answer template
--+-----------------------------+------------------------------+------------------
1 |                             |                              |
2 |                             |                              |
3 |                             |                              |
4 |                             |                              |
5 |                             |                              |
```

Then run the five classification stems in
[rehearsal-stems.md](rehearsal-stems.md). Five out of five and you move on.
Three or fewer and you read Chapter 3 again from "Pattern 1."
