# pr-roast-mcp

MCP server that roasts your pull requests. Brutally honest code review with humor.

## Install

```bash
claude mcp add pr-roast -- uv run --directory /path/to/pr-roast-mcp pr-roast-mcp
```

Or add to your MCP config:

```json
{
  "mcpServers": {
    "pr-roast": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/pr-roast-mcp", "pr-roast-mcp"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-..."
      }
    }
  }
}
```

Requires: `gh` CLI authenticated, `ANTHROPIC_API_KEY` env var.

## Usage

Ask Claude:

- "Roast my latest PR"
- "Roast PR #89"
- "Roast https://github.com/owner/repo/pull/123"
- "List my open PRs so I can pick one to roast"

## Tools

### `roast_pr`

Roast a specific pull request.

| Parameter | Type | Description |
|-----------|------|-------------|
| `pr` | string | PR number, `owner/repo#123`, or full GitHub URL |

### `roast_my_prs`

List your PRs to pick one for roasting.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `repo` | string | current repo | Repository in `owner/repo` format |
| `state` | string | "open" | PR state: "open", "closed", or "merged" |

## What it does

1. Fetches PR metadata and diff via `gh` CLI
2. Sends to Claude Haiku for a roast
3. Returns a brutally honest review with severity rating (🔥 to 🔥🔥🔥🔥🔥)
4. Always ends with one genuine compliment

## Example output

> **🔥🔥🔥 CODE REVIEW: "Initiative Bonus"**
>
> Your tests are *thorough*. Like, suspiciously thorough. 156 lines for a POST endpoint? You're basically writing a dissertation on HTTP status codes.
>
> That `selectChain` helper is magical incantation — nobody knows why `.select()` returns itself. Add a comment explaining the Supabase API you're mimicking.
>
> 849 lines added, 7 removed. That's 121:1 ratio. For a "bonus feature," this sprawls.
>
> **Severity: 🔥🔥🔥 (Ship after fixing migration description, simplifying mocks)**
