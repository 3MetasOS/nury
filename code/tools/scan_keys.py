"""Fail if any tracked file holds a key-like string. Used by CI; run it yourself before a push.

    python3 code/tools/scan_keys.py          # scans `git ls-files` from the repository root; exit 1 on a hit

It looks for: an `sk-` style secret; GLOO_API_KEY, JEV_API_KEY or YVP_APP_KEY (and the other YVP names) assigned a literal
value; and a Bearer token. Obvious placeholders (test, not-real, example, your, xxx, KEY123, <...>) are allowed. It prints the
file, the line number and the KIND of hit, never the value. A hit in a file that is not tracked (.env) is not its business:
.env is gitignored.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSIGN = re.compile(r"""(?ix)\b(GLOO_API_KEY|JEV_API_KEY|YVP_APP_KEY)\b['"\]]?\s*[:=]\s*(?:f?['"])?([A-Za-z0-9._\-]{12,})""")
SK = re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b")
BEARER = re.compile(r"\bBearer\s+([A-Za-z0-9._\-]{24,})\b")
PLACEHOLDER = re.compile(r"(?i)test|not-real|not_real|example|your|xxx|placeholder|dummy|redacted|key123|fake|\.\.\.|<|\$\{|environ|getenv|os\.environ")
# Known fixtures: a made-up secret that a test feeds to a detector. Exact file and kind only, each with its reason.
ALLOW = {("evaluations/tests/test_casefile.py", "a Bearer token"): "a made-up header used to test the case-file Bearer detector"}
BINARY = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg", ".pdf", ".mp3", ".wav", ".mp4", ".mov", ".woff", ".woff2", ".ttf", ".zip", ".gz", ".pyc"}


def tracked(root=ROOT):
    out = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, text=True, check=True).stdout
    return [p for p in out.split("\0") if p]


def scan_text(text):
    """[(line number, kind)] for one file's text."""
    hits = []
    for n, line in enumerate(text.splitlines(), 1):
        for m in ASSIGN.finditer(line):
            if not PLACEHOLDER.search(m.group(2)):
                hits.append((n, "a key name assigned a literal value"))
        for m in SK.finditer(line):
            if not PLACEHOLDER.search(m.group(0)):
                hits.append((n, "an sk- style secret"))
        for m in BEARER.finditer(line):
            if not PLACEHOLDER.search(m.group(1)):
                hits.append((n, "a Bearer token"))
    return hits


def scan(root=ROOT):
    bad = []
    for rel in tracked(root):
        p = Path(root) / rel
        if p.suffix.lower() in BINARY or not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        bad += [(rel, n, kind) for n, kind in scan_text(text) if (rel, kind) not in ALLOW]
    return bad


if __name__ == "__main__":
    bad = scan()
    for rel, n, kind in bad:
        print(f"{rel}:{n}: {kind}")
    print(f"scanned {len(tracked())} tracked files: {len(bad)} hit(s)")
    sys.exit(1 if bad else 0)
