#!/usr/bin/env bash
set -euo pipefail
frontend_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$frontend_dir/../.." && pwd)"
cd -- "$frontend_dir"
argos_node_dir="$repo_root/.argos/frontend-tooling/node_modules/node/bin"
if [[ -x "$argos_node_dir/node" ]]; then
  export PATH="$argos_node_dir:$PATH"
fi
node -e 'const [major, minor] = process.versions.node.split(".").map(Number); if (major < 24 || (major === 24 && minor < 15)) { console.error("Node.js 24.15 or newer is required."); process.exit(1); }'
if [[ ! -d node_modules ]]; then
  npm ci --no-audit --no-fund
fi
exec npm run dev -- --port "${ARGOS_FRONTEND_PORT:-8013}"
