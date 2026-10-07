"""The Build log page refreshes itself at server start when BUILD_LOG.md is newer. Offline. Run: python3 -m pytest evaluations/tests -q"""
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "code"
sys.path.insert(0, str(ROOT))
from app import build_docs, server  # noqa: E402

LOG = "# Build log\n\n## 1. 2026-10-07 07:00 MDT — first entry\n\nbody one\n\n## 2. 2026-10-07 08:00 MDT — NEWEST-ENTRY-TEXT-xyz\n\nbody two\n"


def _setup(tmp_path, monkeypatch, text=LOG):
    src, out = tmp_path / "BUILD_LOG.md", tmp_path / "build-log.html"
    src.write_text(text, encoding="utf-8")
    monkeypatch.setattr(build_docs, "LOG_SRC", src)
    monkeypatch.setattr(build_docs, "LOG_OUT", out)
    return src, out


def test_a_newer_log_regenerates_the_page(tmp_path, monkeypatch):
    src, out = _setup(tmp_path, monkeypatch)
    out.write_text("old page", encoding="utf-8")
    os.utime(out, (time.time() - 100, time.time() - 100))
    os.utime(src, (time.time(), time.time()))          # touch BUILD_LOG.md
    assert server.refresh_build_log_if_stale() == "rebuilt"
    assert "NEWEST-ENTRY-TEXT-xyz" in out.read_text(encoding="utf-8")


def test_a_current_page_is_left_alone(tmp_path, monkeypatch):
    src, out = _setup(tmp_path, monkeypatch)
    out.write_text("current page", encoding="utf-8")
    os.utime(src, (time.time() - 100, time.time() - 100))
    assert server.refresh_build_log_if_stale() == "current"
    assert out.read_text(encoding="utf-8") == "current page"


def test_a_failed_secret_scan_keeps_the_old_page_and_warns(tmp_path, monkeypatch, capsys):
    src, out = _setup(tmp_path, monkeypatch, LOG + "\nGLOO_API_KEY=abcdef123456\n")
    out.write_text("old page", encoding="utf-8")
    os.utime(out, (time.time() - 100, time.time() - 100))
    assert server.refresh_build_log_if_stale() == "scan-failed"
    assert out.read_text(encoding="utf-8") == "old page"
    assert "WARNING" in capsys.readouterr().out
