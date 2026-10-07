"""'Our network' API: the pastor's own vetted contacts, saved by the app on the server (no sign-in yet).

Separate from server.py so the two never collide. To mount it, server.py needs these lines:

    from app import network_api
    # in do_GET / do_POST / do_PUT / do_DELETE, before the other routes:
    if self.path.split("?")[0].startswith("/api/network"):
        status, ctype, body = network_api.handle(self.command, self.path, self._body_bytes())
        ... send status, ctype, body ...
    if path == "/network":  serve app/static/network.html

Run it alone to try it:  cd code && PORT=8120 python3 -m app.network_api
"""
import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from nury import network as net  # noqa: E402

STATIC = Path(__file__).parent / "static"


def _root():
    return os.environ.get("NURY_NETWORK_DIR", net.DEFAULT_ROOT)


def _out(status, obj):
    return status, "application/json; charset=utf-8", json.dumps(obj, ensure_ascii=False).encode("utf-8")


def snapshot():
    n = net.load_network(_root())
    city, state = n.home
    return {"fictional": n.fictional, "readonly": n.demo, "home": {"city": city, "state": state}, "kinds": list(net.KINDS),
            "entries": n.list()}


def handle(method, path, body=b""):
    """(status, content_type, bytes). Never raises: a bad request is a 400 with a plain message."""
    p = path.split("?")[0].rstrip("/")
    try:
        data = json.loads(body.decode("utf-8")) if body else {}
    except ValueError:
        return _out(400, {"error": "that was not valid JSON"})
    if not isinstance(data, dict):
        return _out(400, {"error": "the request must be a JSON object"})
    try:
        n = net.load_network(_root())
    except (ValueError, OSError):
        return _out(500, {"error": "the church network file could not be read"})
    try:
        if method == "GET" and p == "/api/network":
            return _out(200, snapshot())
        if method == "GET" and p == "/api/network/export":
            return _out(200, {"entries": n.list()})
        if method in ("POST", "PUT", "DELETE") and n.demo:
            return _out(403, {"error": "These are fictional demo contacts. They are read only."})
        if method == "POST" and p == "/api/network":
            return _out(201, n.add(data))
        if method == "POST" and p == "/api/network/home":
            n.set_home(data.get("city", ""), data.get("state", ""))
            return _out(200, snapshot())
        if method == "POST" and p == "/api/network/import":
            tmp = Path(_root()) / ".import.json"
            Path(_root()).mkdir(parents=True, exist_ok=True)
            tmp.write_text(json.dumps({"entries": data.get("entries", [])}), encoding="utf-8")
            try:
                added = n.import_json(tmp)
            finally:
                tmp.unlink(missing_ok=True)
            return _out(200, {"added": added, **snapshot()})
        m = re.fullmatch(r"/api/network/([\w\-]+)(/used)?", p)
        if m:
            eid, used = m.group(1), m.group(2)
            if method == "PUT" and not used:
                return _out(200, n.update(eid, data))
            if method == "POST" and used:
                return _out(200, n.mark_used(eid))
            if method == "DELETE" and not used:
                n.delete(eid)
                return _out(200, {"deleted": eid})
        return _out(404, {"error": "not found"})
    except net.NetworkError as e:
        return _out(400, {"error": str(e)})
    except (ValueError, OSError):            # a damaged or unreadable network file: the pastor's request was fine
        return _out(500, {"error": "the church network file could not be read or written"})
    except (KeyError, TypeError, AttributeError):         # a field of the wrong kind: a plain answer, never a dropped connection
        return _out(400, {"error": "that request could not be used"})


class _H(BaseHTTPRequestHandler):
    def _send(self, status, ctype, body):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _go(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else b""
        if self.path.split("?")[0] in ("/", "/network", "/network.html") and self.command == "GET":
            return self._send(200, "text/html; charset=utf-8", (STATIC / "network.html").read_bytes())
        self._send(*handle(self.command, self.path, body))

    do_GET = do_POST = do_PUT = do_DELETE = _go

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8120"))
    print(f"Our network on http://127.0.0.1:{port}/  (dir {_root()}, demo={net.demo_enabled()})")
    ThreadingHTTPServer(("127.0.0.1", port), _H).serve_forever()
