"""One place to say that something failed without saying what it held.

Several parts of the app must never stop a pastor's run for a side job (the ledger, the feedback file, a hook). They catch the
error and carry on. This helper records that it happened: the place and the exception CLASS, never the message, because a
message can hold text from a family. The line goes to stderr through the standard logging module (warning level)."""
import logging

_log = logging.getLogger("nury")


def note(where, exc):
    try:
        _log.warning("%s failed: %s", where, type(exc).__name__)
    except Exception:           # logging itself must never break a run
        pass
