#!/usr/bin/env bash
# TAKE B (live raw app recording, no audio). NOT RUN until hack-sensei says go (after 17:10 MDT; no browser 16:45 to 17:10).
# Uses hack-sensei's record_app.py --live. Fresh worktree of origin/main; ONE app server with the key from the repo-root .env in the ENVIRONMENT only
# (never printed or copied) and NURY_FORCE_REJECTION='rights:2,checklist:1'; a SECOND server with NURY_DEMO_NETWORK=1 (replay, no key) for the Network page only.
# Output: video/raw_app/live/app_full_live_<n>.mp4 (+3x) with NO audio stream (checked with ffprobe), and the spend from the run ledger.
# Usage: ./take_b.sh [take number]     Budget today: 2.00 dollars for all takes; report the spend after each take.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; N="${1:-1}"; WT=/private/tmp/claude-501/nury-takeb-worktree; P1=8771; P2=8772
OUT="$ROOT/video/raw_app/live/take$N"; mkdir -p "$OUT"
PY=/private/tmp/claude-501/-Users-juanpelaez-workspace-gloo-hackathon-hackathon-repo-agents-hack-video/acca94cf-8eae-4ede-bc97-eaa97d91c0c8/scratchpad/venv/bin/python
git -C "$ROOT" fetch -q origin main; [ -d "$WT" ] && git -C "$ROOT" worktree remove --force "$WT"
git -C "$ROOT" worktree add -q --detach "$WT" origin/main; echo "build $(git -C "$WT" rev-parse --short HEAD)"
LEDGER="$WT/code/data/ledger/ledger.jsonl"; BEFORE=$(wc -l < "$LEDGER" 2>/dev/null || echo 0)
( set -a; . "$ROOT/.env"; set +a; unset NURY_REPLAY; cd "$WT/code" && PORT=$P1 NURY_FORCE_REJECTION='rights:2,checklist:1' exec python3 -m app.server ) >/private/tmp/claude-501/takeb-main.log 2>&1 & S1=$!
( cd "$WT/code" && PORT=$P2 NURY_REPLAY=1 NURY_DEMO_NETWORK=1 exec python3 -m app.server ) >/private/tmp/claude-501/takeb-net.log 2>&1 & S2=$!
trap 'kill $S1 $S2 2>/dev/null || true; git -C "$ROOT" worktree remove --force "$WT" 2>/dev/null || true' EXIT
for i in $(seq 1 30); do curl -s -o /dev/null http://127.0.0.1:$P1/ && curl -s -o /dev/null http://127.0.0.1:$P2/ && break; sleep 0.5; done
"$PY" "$ROOT/video/capture/record_app.py" --base http://127.0.0.1:$P1 --net-base http://127.0.0.1:$P2 --out "$OUT" --live --name "app_full_live_$N"
kill $S1 $S2 2>/dev/null || true
echo "--- ffprobe: audio streams (must print nothing) ---"
for f in "$OUT"/*.mp4; do echo "$f"; ffprobe -v error -select_streams a -show_entries stream=codec_name -of csv=p=0 "$f"; ffprobe -v error -show_entries format=duration -of csv=p=0 "$f" | xargs printf "duration %.1f s\n"; done
echo "--- spend this take (run ledger) ---"
python3 - "$LEDGER" "$BEFORE" <<'PY'
import json,sys
L=open(sys.argv[1]).read().splitlines()[int(sys.argv[2]):]; c=0.0; n=0
for l in L:
    try: r=json.loads(l)
    except ValueError: continue
    if r.get("cost_usd"): c+=r["cost_usd"]; n+=1
print(f"{len(L)} ledger lines, {n} with a cost, total ${c:.3f} (Jev calls are not in this sum if cost is null)")
PY
