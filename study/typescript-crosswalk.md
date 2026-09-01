<!-- Appendix A, TypeScript Crosswalk, verbatim. Six canonical SDK calls. -->

## TypeScript Crosswalk

The book teaches in Python because Anthropic Academy leads in Python and the question-bank evidence (Group C, Reddit and X) is framed entirely in Python anxiety. The Claude Agent SDK ships in both Python and TypeScript. The exam is platform-agnostic on language. This crosswalk maps the six canonical SDK calls the exam grades, side by side. TypeScript signatures follow the SDK's camelCase convention for client options; payload fields that match Anthropic's API wire format (like `cache_control`) stay snake_case in both languages. Cross-check the canonical form in `@anthropic-ai/claude-agent-sdk` before shipping production code.

### 1. Basic `query()` plus tool allow-list (Chapter 4)

Python:

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="Find and fix the bug in auth.py",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Edit", "Bash"]),
    ):
        print(message)

asyncio.run(main())
```

TypeScript:

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Find and fix the bug in auth.ts",
  options: { allowedTools: ["Read", "Edit", "Bash"] },
})) {
  console.log(message);
}
```

### 2. Coordinator with subagent definitions (Chapter 4)

Python:

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep", "Agent"],
    agents={
        "researcher": AgentDefinition(
            description="Searches the codebase.",
            prompt="Find evidence.",
            tools=["Read", "Glob", "Grep"],
        ),
    },
)
```

TypeScript:

```typescript
const options = {
  allowedTools: ["Read", "Glob", "Grep", "Agent"],
  agents: {
    researcher: {
      description: "Searches the codebase.",
      prompt: "Find evidence.",
      tools: ["Read", "Glob", "Grep"],
    },
  },
};
```

### 3. Batch API request (Chapter 5)

Python:

```python
import anthropic
client = anthropic.Anthropic()

batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": "q-001",
            "params": {
                "model": "claude-opus-4-7",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": "..."}],
            },
        },
    ]
)
```

TypeScript:

```typescript
import Anthropic from "@anthropic-ai/sdk";
const anthropic = new Anthropic();

const batch = await anthropic.messages.batches.create({
  requests: [
    {
      custom_id: "q-001",
      params: {
        model: "claude-opus-4-7",
        max_tokens: 1024,
        messages: [{ role: "user", content: "..." }],
      },
    },
  ],
});
```

### 4. Prompt caching (Chapter 5)

Python:

```python
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=2048,
    system=[
        {
            "type": "text",
            "text": LONG_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }
    ],
    messages=[{"role": "user", "content": user_query}],
)
```

TypeScript:

```typescript
const response = await anthropic.messages.create({
  model: "claude-opus-4-7",
  max_tokens: 2048,
  system: [
    {
      type: "text",
      text: LONG_SYSTEM_PROMPT,
      cache_control: { type: "ephemeral" },
    },
  ],
  messages: [{ role: "user", content: userQuery }],
});
```

Note: `cache_control` keeps snake_case in TypeScript because it lives in the message-block payload and matches the API wire format on this specific field. Client-side options (`allowedTools`, `permissionMode`) use camelCase; payload-side fields preserve the API field name.

### 5. Structured outputs via `messages.parse` (Chapter 8)

Python:

```python
from pydantic import BaseModel

class ContactInfo(BaseModel):
    name: str
    email: str

response = client.messages.parse(
    model="claude-opus-4-7",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Extract contact info."}],
    output_format=ContactInfo,
)
```

TypeScript (Zod schema):

```typescript
import { z } from "zod";

const ContactInfo = z.object({
  name: z.string(),
  email: z.string().email(),
});

const response = await anthropic.messages.parse({
  model: "claude-opus-4-7",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Extract contact info." }],
  output_format: ContactInfo,
});
```

### 6. MCP server registration (Chapter 6)

Python:

```python
from claude_agent_sdk import ClaudeAgentOptions
import os

options = ClaudeAgentOptions(
    mcp_servers={
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_TOKEN": os.environ["GITHUB_TOKEN"]},
        }
    },
    allowed_tools=["mcp__github__list_issues"],
)
```

TypeScript:

```typescript
const options = {
  mcpServers: {
    github: {
      command: "npx",
      args: ["-y", "@modelcontextprotocol/server-github"],
      env: { GITHUB_TOKEN: process.env.GITHUB_TOKEN },
    },
  },
  allowedTools: ["mcp__github__list_issues"],
};
```

### What stays the same across both SDKs

- MCP tool naming: `mcp__<server>__<tool>`. Double underscores. No dots in either language.
- `.mcp.json` config file format and project-root location. Both SDKs load it identically.
- Tool allow-list semantics. `permissionMode` (TS) and `permission_mode` (Py) do not auto-approve MCP tools; only the allow-list does.
- The four-layer prompt-injection defense (Chapter 6). Same architecture, same model choices, same exam answer.
- Domain weights, exam format, retake policy. The exam grades architecture, not syntax.

If you are a TypeScript-only candidate, read the book in Python and write the BUILD STEP code in TypeScript using the mappings above. The exam will not ask you to write code; it will ask you to recognize the architectural primitive. Recognition transfers across languages.
