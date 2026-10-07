"""Audit log: every call, check, retry, gate decision, with a timestamp.

Events live in memory and, if a path is given, append to a JSONL file.
Rejected drafts are logged here for evaluation. The pastor UI never reads them.
Never log secrets. Nothing here touches headers or env.
"""

import json
import threading
from datetime import datetime, timezone


class AuditLog:
    def __init__(self, path=None):
        self.path = path
        self.events = []
        self._lock = threading.Lock()

    def log(self, kind, **fields):
        event = {"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                 "kind": kind, **fields}
        with self._lock:
            self.events.append(event)
            if self.path:
                with open(self.path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event

    def of_kind(self, kind):
        return [e for e in self.events if e["kind"] == kind]
