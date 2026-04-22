"""PR Roast MCP Server — brutally honest code review with humor."""

import json
import os
import subprocess
import urllib.request
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pr-roast")

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ROAST_MODEL = "claude-haiku-4-5-20251001"

ROAST_SYSTEM = """You are a senior engineer doing a code review, but you're having a bad day and you're not holding back. Your job is to roast this pull request.

Rules:
- Be brutally honest but technically accurate
- Use humor — sarcasm, dry wit, exaggeration
- Point out real issues: naming, complexity, missing tests, over-engineering, under-engineering
- Call out lazy patterns: "renamed a variable and called it a refactor"
- Give a severity rating: 🔥 (mild roast) to 🔥🔥🔥🔥🔥 (career-ending)
- End with one genuine compliment if you can find anything worth praising
- Keep it under 300 words
- Be funny, not mean. Punch up at the code, not down at the person."""


def _run_gh(args: list[str]) -> str:
    """Run a gh CLI command and return stdout."""
    result = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr[:300]}")
    return result.stdout


def _get_pr_info(pr_ref: str) -> dict[str, Any]:
    """Get PR metadata and diff."""
    # pr_ref can be: "123", "owner/repo#123", or a URL
    pr_args = []
    if "/" in pr_ref and "#" in pr_ref:
        repo, num = pr_ref.rsplit("#", 1)
        pr_args = ["-R", repo, num]
    elif pr_ref.startswith("http"):
        # Extract from URL: https://github.com/owner/repo/pull/123
        parts = pr_ref.rstrip("/").split("/")
        pr_args = ["-R", f"{parts[-4]}/{parts[-3]}", parts[-1]]
    else:
        pr_args = [pr_ref]

    # Get metadata
    meta_json = _run_gh(["pr", "view", *pr_args, "--json",
                          "title,body,additions,deletions,changedFiles,author,baseRefName,headRefName,commits"])
    meta = json.loads(meta_json)

    # Get diff
    diff = _run_gh(["pr", "diff", *pr_args])

    # Truncate diff if huge
    if len(diff) > 15000:
        diff = diff[:15000] + f"\n\n... diff truncated ({len(diff)} chars total)"

    return {
        "title": meta.get("title", ""),
        "body": (meta.get("body") or "")[:500],
        "additions": meta.get("additions", 0),
        "deletions": meta.get("deletions", 0),
        "changed_files": meta.get("changedFiles", 0),
        "author": meta.get("author", {}).get("login", "unknown"),
        "base": meta.get("baseRefName", ""),
        "head": meta.get("headRefName", ""),
        "commits": len(meta.get("commits", [])),
        "diff": diff,
    }


def _call_llm(prompt: str) -> str:
    """Call Anthropic API for the roast."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY required for roasting")

    body = json.dumps({
        "model": ROAST_MODEL,
        "max_tokens": 1024,
        "system": ROAST_SYSTEM,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()

    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())

    return data["content"][0]["text"]


@mcp.tool()
def roast_pr(pr: str) -> str:
    """Roast a pull request. Give it a PR number, owner/repo#number, or URL.

    Args:
        pr: PR reference — "123", "owner/repo#123", or full GitHub URL.
    """
    try:
        info = _get_pr_info(pr)
    except RuntimeError as e:
        return f"Couldn't fetch PR: {e}"
    except Exception as e:
        return f"Error: {e}"

    prompt = f"""Roast this pull request:

**Title:** {info['title']}
**Author:** {info['author']}
**Branch:** {info['head']} → {info['base']}
**Stats:** +{info['additions']}/-{info['deletions']} across {info['changed_files']} files in {info['commits']} commits
**Description:** {info['body'] or '(no description provided)'}

**Diff:**
```
{info['diff']}
```"""

    try:
        return _call_llm(prompt)
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Roast failed (the code was too bad even for me): {e}"


@mcp.tool()
def roast_my_prs(repo: str | None = None, state: str = "open") -> str:
    """List your PRs and pick one to roast.

    Args:
        repo: Repository in owner/repo format. If not set, uses current repo.
        state: PR state — "open", "closed", or "merged" (default: open).
    """
    args = ["pr", "list", "--author", "@me", "--state", state, "--json",
            "number,title,additions,deletions,changedFiles", "--limit", "10"]
    if repo:
        args.extend(["-R", repo])

    try:
        output = _run_gh(args)
    except RuntimeError as e:
        return f"Couldn't list PRs: {e}"

    prs = json.loads(output)
    if not prs:
        return f"No {state} PRs found. Either you're very productive or very lazy."

    lines = [f"Your {state} PRs (pick one to roast):\n"]
    for pr in prs:
        lines.append(
            f"  #{pr['number']}  {pr['title']}  "
            f"(+{pr['additions']}/-{pr['deletions']}, {pr['changedFiles']} files)"
        )
    lines.append(f"\nUse: roast_pr(\"{prs[0]['number']}\") to get roasted.")
    return "\n".join(lines)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
