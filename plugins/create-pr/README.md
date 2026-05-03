# create-pr

A Claude Code plugin that provides an intelligent PR creation workflow with observability enforcement.

## What it does

1. **Creates PRs** — commits, pushes, and opens a GitHub PR via `gh` CLI with worktree support.
2. **Generates observability docs** — detects the repo's existing metrics/logs/traces libraries and generates `docs/observability/<language>.md` guides if they don't exist.
3. **Reviews changes for observability gaps** — Claude reads the full impacted functions (not just diff lines) to find missing metrics at service boundaries, missing trace spans on outgoing calls, and missing error logging on failure paths.
4. **Embeds monitoring guidance** — adds a `## Release Monitoring` section to commit messages listing metrics/logs/traces to watch, parseable by CI/CD agents for automated regression checks.
5. **Attaches chat context** — summarizes the Claude Code session transcript and posts it as a PR comment.

## Requirements

- `gh` (GitHub CLI, authenticated)
- `git`
- `python3` (for the SessionStart hook only)

## Installation

Install as a Claude Code plugin:

```bash
claude plugin add oodle-ai/claude-plugins
```

Or clone locally and add as a local plugin:

```bash
git clone git@github.com:oodle-ai/claude-plugins.git
claude plugin add ./claude-plugins
```

## Usage

Invoke as a slash command:

```
/create-pr
```

Or ask Claude naturally — "create a PR", "push and open a pull request", etc.

## Plugin Structure

```
.claude-plugin/
  plugin.json            # Plugin manifest
skills/
  create-pr/
    SKILL.md             # Main PR creation skill (all logic is here)
hooks/
  hooks.json             # SessionStart hook config
  scripts/
    detect-observability.py  # Lightweight check for docs/observability/
```

## How observability enforcement works

1. On session start, a hook checks if `docs/observability/` exists and signals Claude if missing.
2. When creating a PR, Claude inspects the repo for observability libraries and generates language-specific guides if needed.
3. Claude reads the full impacted functions to find missing metrics/traces/logs (not just diff lines).
4. The commit message includes a structured `## Release Monitoring` section that CI/CD agents can parse.

## Design philosophy

- **Claude does the analysis** — no brittle regex scripts. Claude reads the code and understands it semantically.
- **Logs are not spammy** — only suggested on error/failure paths at service boundaries.
- **Full context, not just diffs** — reads entire impacted functions to understand existing instrumentation.
- **The only script** is a lightweight SessionStart hook that checks for directory existence.

## License

MIT
