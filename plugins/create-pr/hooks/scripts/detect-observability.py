#!/usr/bin/env python3
"""
SessionStart hook:
1. Detect if docs/observability/ exists — signal Claude if missing.
2. Save transcript_path to CLAUDE_ENV_FILE so the skill can read it later.
"""

import json
import os
import sys


def main():
    hook_input = json.loads(sys.stdin.read())

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", hook_input.get("cwd", os.getcwd()))
    env_file = os.environ.get("CLAUDE_ENV_FILE")
    transcript_path = hook_input.get("transcript_path", "")

    obs_dir = os.path.join(project_dir, "docs", "observability")
    docs_missing = not os.path.isdir(obs_dir)

    if env_file:
        try:
            with open(env_file, "a") as f:
                if docs_missing:
                    f.write("export OBSERVABILITY_DOCS_MISSING=1\n")
                if transcript_path:
                    f.write(f"export TRANSCRIPT_PATH={transcript_path}\n")
        except (IOError, OSError):
            pass

    output = {
        "continue": True,
        "suppressOutput": True,
    }

    if docs_missing:
        output["systemMessage"] = (
            "This project has no docs/observability/ directory. "
            "When creating a PR, generate observability documentation first."
        )

    print(json.dumps(output))


if __name__ == "__main__":
    main()
