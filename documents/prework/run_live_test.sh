#!/usr/bin/env bash
# run_live_test.sh — first live test of the Gloo hackathon agent.
#
# Loads .env (if present), verifies GLOO_API_KEY is set, does a cheap
# key check against Gloo AI Studio, then runs the live demo scenario
# end to end (--auto-approve so the pastor gates don't pause a smoke test).
#
# Usage:
#   ./run_live_test.sh                 # key from .env or environment
#   GLOO_API_KEY=xxx ./run_live_test.sh # one-off key, nothing written to disk

set -euo pipefail
cd "$(dirname "$0")"

if [ -f .env ]; then
  # shellcheck disable=SC1091
  set -a; source .env; set +a
fi

if [ -z "${GLOO_API_KEY:-}" ]; then
  echo "GLOO_API_KEY is not set."
  echo ""
  echo "Get a key: https://studio.ai.gloo.com -> create account -> add credits"
  echo "(\$10 minimum) -> Dashboard -> API Keys -> Create New Key."
  echo ""
  echo "Then either:"
  echo "  cp .env.example .env   # and paste the key into .env, or"
  echo "  GLOO_API_KEY=<key> ./run_live_test.sh   # single run, nothing saved"
  exit 1
fi

echo "Checking key against Gloo AI Studio (model list, no credits spent)..."
if curl -sf -m 25 -o /dev/null \
    -H "Authorization: Bearer ${GLOO_API_KEY}" \
    "https://platform.ai.gloo.com/platform/v2/models"; then
  echo "Key OK."
else
  echo "WARNING: key check failed (bad key, no credits, or network issue)."
  echo "Continuing to the live run anyway — it will surface the real error."
fi

echo ""
echo "Running live demo scenario (auto-approved)..."
python3 -m demo.demo_scenario --auto-approve
