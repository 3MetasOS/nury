#!/usr/bin/env bash
# LIVE capture + cut 4, in one go. ONE Gloo run (about 0.1 dollar). Run ONLY after hack-sensei says "key free".
# 1 fresh worktree of origin/main  2 own copy of the app on port 8766, key from the repo-root .env in the ENVIRONMENT (never printed, never copied), replay OFF
# 3 record.py (one session)  4 stop the app  5 cut.sh  Output: capture/raw_live/, remotion/out/nuryA_cut4.mp4
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; VIDEO="$ROOT/video"; WT=/private/tmp/claude-501/nury-live-worktree; PORT=8766
git -C "$ROOT" fetch -q origin main
[ -d "$WT" ] && git -C "$ROOT" worktree remove --force "$WT"
git -C "$ROOT" worktree add -q --detach "$WT" origin/main; echo "capturing build $(git -C "$WT" rev-parse --short HEAD)"
( set -a; . "$ROOT/.env"; set +a; unset NURY_REPLAY; cd "$WT/code" && PORT=$PORT exec python3 -m app.server ) >/private/tmp/claude-501/nury-live-server.log 2>&1 &
SRV=$!; trap 'kill $SRV 2>/dev/null || true; git -C "$ROOT" worktree remove --force "$WT" 2>/dev/null || true' EXIT
for i in $(seq 1 20); do curl -s -o /dev/null http://127.0.0.1:$PORT/ && break; sleep 0.5; done
curl -s http://127.0.0.1:$PORT/api/playbooks | head -c 200 >/dev/null || { echo "app not up"; exit 1; }
rm -rf "$VIDEO/capture/raw_live"
PY=/private/tmp/claude-501/-Users-juanpelaez-workspace-gloo-hackathon-hackathon-repo-agents-hack-video/acca94cf-8eae-4ede-bc97-eaa97d91c0c8/scratchpad/venv/bin/python
"$PY" "$VIDEO/capture/record.py" http://127.0.0.1:$PORT/ "$VIDEO/capture/raw_live"
kill $SRV 2>/dev/null || true
cat "$VIDEO/capture/raw_live/marks.txt"
grep -q "^ *[0-9.]* reject" "$VIDEO/capture/raw_live/marks.txt" || echo "WARNING: no reject mark: the forced rejection did not show"
"$VIDEO/remotion/cut.sh" "$VIDEO/capture/raw_live" out/nuryA_cut4.mp4
