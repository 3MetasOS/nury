"""GET /api/ops: read-only totals from the run ledger. No text, no names, no case ids.

Separate from server.py. To mount it, server.py needs these lines:

    from app import ops_api
    # in do_GET (and a refusal for other methods), before the other routes:
    if self.path.split("?")[0] == "/api/ops":
        status, ctype, body = ops_api.handle(self.command, self.path)
        ... send status, ctype, body ...

Query: /api/ops?since=3600  (seconds back; omit for everything)  or  ?since=2026-10-07T00:00:00+00:00
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from nury import ledger  # noqa: E402


def _out(status, obj):
    return status, "application/json; charset=utf-8", json.dumps(obj, ensure_ascii=False).encode("utf-8")


def handle(method, path):
    if method != "GET":
        return _out(405, {"error": "read only"})
    q = parse_qs(urlparse(path).query)
    since = None
    if "since" in q:
        v = q["since"][0]
        if re.fullmatch(r"\d{1,9}", v):
            since = int(v)
        elif re.fullmatch(r"\d{4}-\d\d-\d\dT[\d:.]+\+00:00", v):
            since = v
        else:
            return _out(400, {"error": "since must be seconds or an ISO UTC time"})
    return _out(200, ledger.summarize(since))
