"""Audit log: every call, check, retry, gate decision, with a timestamp.

Events live in memory and, if a path is given, append to a JSONL file.
Rejected drafts are logged here for evaluation. The pastor UI never reads them.
Never log secrets. Nothing here touches headers or env.

Each event carries `ts` (wall clock, UTC) and `t_ms` (milliseconds on a monotonic clock since this log was created).
Subtract `t_ms` values to get a duration that does not depend on the wall clock changing.

subscribe(fn) calls fn(event) after each event is recorded, so a ledger, an ops stream or a progress bar can hang off the
log instead of re-reading it. A subscriber that raises is ignored: it can never break a run. fn gets the event itself;
do not change it.
"""

import json
import threading
import time
from datetime import datetime, timezone
from . import log


class AuditLog:
    def __init__(self, path=None):
        self.path = path
        self.events = []
        self._lock = threading.Lock()
        self._t0 = time.monotonic()
        self._subs = []

    def subscribe(self, fn):
        """Returns a function that removes the subscription."""
        with self._lock:
            self._subs.append(fn)

        def unsubscribe():
            with self._lock:
                if fn in self._subs:
                    self._subs.remove(fn)
        return unsubscribe

    def log(self, kind, **fields):
        event = {"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                 "t_ms": round((time.monotonic() - self._t0) * 1000, 1),
                 "kind": kind, **fields}
        with self._lock:
            self.events.append(event)
            subs = list(self._subs)
            if self.path:
                with open(self.path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(event, ensure_ascii=False) + "\n")
        for fn in subs:                      # outside the lock: a slow subscriber must not block the log
            try:
                fn(event)
            except Exception as e:
                log.note("audit.subscriber", e)
        return event

    def of_kind(self, kind):
        return [e for e in self.events if e["kind"] == kind]
