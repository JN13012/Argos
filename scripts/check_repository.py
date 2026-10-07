#!/usr/bin/env python3
"""Check repository hygiene and syntax without running imported applications."""

import ast
import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
ENGAGEMENTS = "Harness/Harness/engagements/"
LOCAL_FILES = {
    "Harness/Harness/CURRENT_ENGAGEMENT.md",
    "Harness/course-pack/findings.jsonl",
    "Harness/course-pack/notes.md",
    "Harness/course-pack/project/findings.jsonl",
    "Harness/course-pack/project/notes.md",
}


def sensitive_path(name):
    path = Path(name)
    return (
        name in LOCAL_FILES
        or name.startswith("Harness/course-pack/")
        or name.startswith(ENGAGEMENTS)
        and not name.startswith(ENGAGEMENTS + "_template/")
        or path.name.lower().endswith(".identifier")
        or path.name in {"settings.local.json", ".credentials.json", ".env"}
        or path.name.startswith(".env.")
        and path.name not in {".env.example", ".env.sample", ".env.template"}
        or any(part in {"node_modules", "__pycache__", ".venv", "venv"}
               for part in path.parts)
    )


def git_paths(*args):
    result = subprocess.run(
        ["git", "ls-files", "-z", *args], cwd=ROOT,
        check=True, stdout=subprocess.PIPE,
    )
    return result.stdout.decode("utf-8").rstrip("\0").split("\0") if result.stdout else []


def main():
    errors = []
    tracked = git_paths("--cached")
    ignored_tracked = set(git_paths("--cached", "--ignored", "--exclude-standard"))
    for name in tracked:
        if name in ignored_tracked or sensitive_path(name):
            errors.append(f"Publication-sensitive path still tracked: {name}")
    public = set(tracked + git_paths("--others", "--exclude-standard"))
    node = shutil.which("node")
    counts = {"Python": 0, "JSON": 0, "JavaScript": 0}
    for name in sorted(public):
        if sensitive_path(name):
            continue
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            continue
        try:
            if path.suffix == ".py":
                ast.parse(path.read_text(encoding="utf-8"), filename=name)
                counts["Python"] += 1
            elif path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
                counts["JSON"] += 1
            elif path.suffix == ".js" and node:
                result = subprocess.run(
                    [node, "--check", str(path)], cwd=ROOT,
                    capture_output=True, text=True,
                )
                if result.returncode:
                    errors.append(f"Invalid JavaScript syntax: {name}")
                counts["JavaScript"] += 1
        except (OSError, UnicodeError, SyntaxError, ValueError) as exc:
            errors.append(f"Cannot validate {name}: {type(exc).__name__}")
    print("Syntax checked: " + ", ".join(f"{n} {kind}" for kind, n in counts.items()))
    if not node:
        print("JavaScript syntax skipped: Node.js is unavailable.")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Repository hygiene and syntax checks passed (history not checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
