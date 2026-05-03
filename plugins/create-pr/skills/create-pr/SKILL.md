---
name: create-pr
description: Use when the user asks to "create a PR", "open a pull request", "push and create PR", "commit and PR", or wants to finalize their changes into a GitHub pull request. Handles commit, push, observability enforcement, and transcript attachment.
argument-hint: [base-branch]
version: 0.2.0
---

# Create PR with Observability Enforcement

Write a commit message, then create or update a GitHub PR using the `gh` CLI. Enforce observability best practices and attach session context.

## Step 1: Gather Context

Collect current state:

- Git status: !`git status`
- Current branch: !`git branch --show-current`
- Diff summary: !`git diff --stat HEAD`

## Step 2: Worktree Detection

Detect whether we are in a git worktree by comparing:

- `git rev-parse --show-toplevel` (current tree root)
- `git rev-parse --git-common-dir` piped to `dirname` (main repo root)

If these differ, we are in a worktree. Note the main repo root for later use.

## Step 3: Observability Documentation

Check if `docs/observability/` exists in the project root. If it does, skip to Step 4.

If it does NOT exist, generate it:

1. Identify the languages/frameworks in use (look for `go.mod`, `package.json`, `requirements.txt`, `pom.xml`, `Cargo.toml`, etc. — search recursively, not just root).
2. For each language found, search the codebase for existing observability libraries:
   - **Metrics**: Prometheus, OpenTelemetry, Datadog, StatsD, Micrometer, etc.
   - **Logging**: zap, slog, structlog, pino, winston, logrus, SLF4J, etc.
   - **Tracing**: OpenTelemetry, Datadog APM, Jaeger, etc.
3. Find concrete examples of how metrics/logs/traces are created in this repo (grep for counter definitions, logger instantiation, span creation).
4. Write `docs/observability/<language>.md` with:
   - Which libraries are used
   - How to add a new metric (counter, histogram, gauge) with a code snippet from this repo
   - How to add structured logs with a code snippet from this repo
   - How to create a trace span with a code snippet from this repo
   - Required metric tags/labels: `service`, `endpoint`, `method`, `status_code`
5. Stage and commit:

```bash
git add docs/observability/
git commit -m "docs: add observability instrumentation guide"
```

## Step 4: Observability Review

Analyze the impacted code for observability gaps. Read the **full functions and files** that are modified — not just the diff lines.

### How to analyze

1. Get changed files: `git diff --name-only HEAD`
2. For each file (skip generated code like `.pb.go`, test files, protos, constants), read the entire file or at minimum the full functions containing changes.
3. Understand what the code does semantically: endpoint handler? service call? DB query? business logic?
4. Check what instrumentation already exists in the function/file.

### What warrants instrumentation

- **Metrics** (always needed at service boundaries):
  - New/modified endpoint handlers → request count + duration histogram
  - New/modified outgoing calls (HTTP, gRPC, DB, cache) → latency histogram + error counter

- **Traces** (always needed for cross-service work):
  - New outgoing network calls → child span with operation name and attributes
  - New DB queries → span with `db.statement` attribute

- **Logs** (ONLY at error/failure paths — do NOT add logs to every function):
  - Error returns that are surfaced to callers
  - External call failures (timeouts, connection errors)
  - Auth failures
  - NOT for: helpers, data transformations, iterations, routine success paths

### What to skip entirely

- Generated code (`.pb.go`, `_generated.*`, etc.)
- Test files
- Proto/schema definitions
- Constants, config, type definitions
- Functions that already have appropriate instrumentation

### If gaps are found

Add the instrumentation, stage, and commit separately:

```bash
git add -u
git commit -m "observability: add missing metrics/logs/traces"
```

If no gaps, skip this step.

## Step 5: Build Commit Message

**CRITICAL: The commit message MUST end with a `## Release Monitoring` section. Never omit it. CI/CD agents parse this section to set up automated regression checks after deploy.**

To populate it, inspect the **full impacted code** (entire functions affected by ALL commits in this PR, not just the latest diff). Find every metric, log pattern, and trace span that could change behavior as a result of this PR. Include existing signals in modified code paths, not just newly added ones.

The commit message format:

```
<type>: <short description>

<body explaining what and why>

## Release Monitoring

### Metrics to watch
- <metric_name> — expected behavior (e.g., "http_request_duration_seconds{endpoint="/api/relay"} — p99 should stay under 500ms")
- <metric_name> — expected behavior

### Logs to check
- <log pattern> — what to look for (e.g., "level=error msg=\"relay failed\" — should not appear more than 1/min per pod")
- <log pattern> — what to look for

### Traces
- <span_name> — expected behavior (e.g., "webhook.relay — p95 latency should stay under 200ms")
- <span_name> — expected behavior
```

Rules for populating:
- If code touches an endpoint or handler, list its request count/duration metrics.
- If code has error logging, list the log pattern and expected frequency.
- If code makes outgoing calls with spans, list those spans and expected latency.
- If code modifies logic where existing metrics/traces already exist, list those existing signals and note how they might change.
- NEVER write "No new signals introduced" unless the change is truly documentation-only or config-only with zero runtime impact.
- Be specific: include label values, expected thresholds, and what "bad" looks like.

## Step 6: Commit and Push

- Stage only real code changes (do NOT commit `.specstory/`, `.cursor/`, or plan files).
- If a PR already exists for the current branch, create a new commit and push (without `--force`).

```bash
git add -A
git reset -- .specstory/ .cursor/ '*.plan.md'
git commit -m "<commit message from Step 5>"
git push origin HEAD
```

## Step 7: Create or Update PR

Check if a PR exists:

```bash
gh pr view --json number 2>/dev/null
```

If no PR exists, create one. Build the PR body with the same `## Release Monitoring` section from the commit message, plus a summary of changes:

```bash
gh pr create --title "<type>: <short description>" --body "<PR body>"
# or with base branch:
gh pr create --base $ARGUMENTS --title "<type>: <short description>" --body "<PR body>"
```

The PR body should include:
1. A brief description of what the PR does and why.
2. The **same `## Release Monitoring` section** from the commit message (metrics, logs, traces to watch). This makes it visible to reviewers and parseable by CI/CD from the PR API.

If a PR already exists, update its body to include/refresh the Release Monitoring section:

```bash
gh pr edit <PR_NUMBER> --body "<updated PR body with Release Monitoring>"
```

Capture the PR number and URL.

## Step 8: Attach Session Transcript

If `$TRANSCRIPT_PATH` is set (exported by the SessionStart hook), read the transcript file and post it as a PR comment:

1. Read the file at `$TRANSCRIPT_PATH` (it's JSONL — one JSON object per line).
2. Post the full content as a PR comment. If it exceeds GitHub's 65536 char limit, truncate from the beginning (keep the most recent messages).

```bash
gh pr comment <PR_NUMBER> --body-file "$TRANSCRIPT_PATH"
```

If `$TRANSCRIPT_PATH` is not set or the file doesn't exist, skip this step.

## Step 9: Open PR

```bash
open <PR_URL>   # macOS
xdg-open <PR_URL>  # Linux
```

## Important Rules

- NEVER commit `.specstory/`, `.cursor/`, or plan files.
- NEVER force-push.
- **The `## Release Monitoring` section is MANDATORY in both the final commit message AND the PR description.** If you produce a commit without it, amend it immediately. A commit message without this section is considered broken.
- Observability review (Step 4) is best-effort — if unsure about gaps, skip and proceed.
- The Release Monitoring section is NOT best-effort — it must always be present and populated with specific, actionable signals.
- When updating an existing PR, always refresh the Release Monitoring section in the PR body to reflect the latest state of all commits.
