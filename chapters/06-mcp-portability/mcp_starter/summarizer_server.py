"""Third MCP tool: a repo summarizer — Chapter 6.

The listing below is the book's, byte for byte (ch06:196-221). Registered in
.mcp.json under the `summarizer` key alongside the filesystem and github
servers.

`pip install mcp` is the runtime dependency. No Anthropic key: this is a local
stdio server that shells out to `git ls-files` and reads a README.

    pip install mcp
    python3 summarizer_server.py      # runs as a stdio MCP server

The tool description is deliberately narrow — "does not search file contents;
use the filesystem server for content reads" — because an overlapping
description is what makes a coordinator break a routing tie by coin flip.
"""

# summarizer_server.py
from mcp.server.fastmcp import FastMCP
import os
import subprocess

mcp = FastMCP("summarizer")

@mcp.tool()
def summarize_repo(path: str = ".") -> str:
    """Summarize the repository's README and top-level file structure.

    Returns a concatenated digest. Does not search file contents;
    use the filesystem server for content reads.
    """
    files = subprocess.check_output(
        ["git", "-C", path, "ls-files"], text=True
    ).splitlines()[:50]
    readme = ""
    readme_path = os.path.join(path, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path) as f:
            readme = f.read()[:2000]
    return "Files (first 50):\n" + "\n".join(files) + f"\n\nREADME excerpt:\n{readme}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
