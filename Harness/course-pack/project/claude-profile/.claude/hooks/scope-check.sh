#!/usr/bin/env bash
# PreToolUse hook. The tool call arrives as JSON on stdin. Exit 0 allows, exit 2 blocks
# and hands stderr back to the model. Exit 1 is non blocking, so it is never used here.
set -euo pipefail
command -v jq >/dev/null || { echo "BLOCKED: jq missing, scope cannot be checked." >&2; exit 2; }
INPUT=$(cat)
CMD=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // ""')
IN_SCOPE_HOST="${ENGAGEMENT_HOST:-localhost:8080}"

# every URL in the command text must point at the engagement host
for url in $(printf '%s' "$CMD" | grep -oE 'https?://[^ "'"'"']+' || true); do
  host=$(printf '%s' "$url" | sed -E 's#https?://([^/]+).*#\1#')
  if [ "$host" != "$IN_SCOPE_HOST" ]; then
    echo "BLOCKED: $host is not in scope. Engagement host is $IN_SCOPE_HOST." >&2
    exit 2
  fi
done
exit 0
