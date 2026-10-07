"""Print-ready copies of a case: a family copy and a pastor copy as PDF, and the export zip that holds them.

The PDFs are made by rendering a self-contained print page (the same final-page code the app shows, a print stylesheet,
the self-hosted fonts) with headless Chrome or Chromium. No Python dependency is added. If no browser is found the
export falls back to the print-ready HTML files, and the page says plainly: PDF needs Chrome or Chromium.

Nothing here changes the case files. The token map (privacy-map.json) is never read."""
import html
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATIC = HERE / "static"
NO_BROWSER = "PDF needs Chrome or Chromium; use Print > Save as PDF"
MAC_PATHS = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             "/Applications/Chromium.app/Contents/MacOS/Chromium",
             "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
NAMES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "microsoft-edge"]


def find_chrome():
    """CHROME_BIN first, then a browser on PATH, then the macOS app paths. None when there is none."""
    env = os.environ.get("CHROME_BIN", "")
    if env and os.access(env, os.X_OK):
        return env
    for n in NAMES:
        p = shutil.which(n)
        if p:
            return p
    for p in MAC_PATHS:
        if os.access(p, os.X_OK):
            return p
    return None


def _inline(s):
    """Text that goes inside a <script> or <style> must not close it."""
    return s.replace("</", "<\\/")


def print_html(kind, data, copy, title, date_iso, fonts_base="/fonts", screen_note=True, extras=None):
    """One self-contained HTML file. kind: 'case' (a saved case: pages, meta) or 'session' (a finished run).
    copy: 'family' (the family's language) or 'pastor' (English headings plus the audit summary)."""
    tpl = (STATIC / "case-print.html").read_text(encoding="utf-8")
    css = (STATIC / "case-print.css").read_text(encoding="utf-8").replace("__FONTS__", fonts_base)
    js = (STATIC / "final.js").read_text(encoding="utf-8") + "\n" + (STATIC / "case-print.js").read_text(encoding="utf-8")
    mark = re.search(r'<symbol id="i-mark"[^>]*>(.*?)</symbol>', (STATIC / "icons.svg").read_text(encoding="utf-8"), re.S)
    payload = {"kind": kind, "copy": copy, "data": data, "title": title, "date": date_iso, "note": NO_BROWSER if screen_note else "", **(extras or {})}
    out = tpl.replace("/*@CSS@*/", _inline(css)).replace("/*@JS@*/", _inline(js))
    out = out.replace("/*@DATA@*/", "window.__PRINT__=" + _inline(json.dumps(payload, ensure_ascii=False)) + ";")
    out = out.replace("<!--@MARK@-->", mark.group(1) if mark else "")
    out = out.replace("@@TITLE@@", html.escape(f"{title}, {'family copy' if copy == 'family' else 'pastor copy'}"))
    return out


def render_pdf(page_html, timeout=90):
    """PDF bytes from a print page, or None when there is no browser or it fails."""
    chrome = find_chrome()
    if not chrome:
        return None
    with tempfile.TemporaryDirectory(prefix="nury_pdf_", ignore_cleanup_errors=True) as d:
        d = Path(d)
        page = d / "page.html"
        out = d / "out.pdf"
        page.write_text(page_html, encoding="utf-8")
        cmd = [chrome, "--headless", "--disable-gpu", "--no-first-run", "--no-default-browser-check", "--hide-scrollbars",
               f"--user-data-dir={d / 'profile'}", "--no-pdf-header-footer", f"--print-to-pdf={out}", page.as_uri()]
        proc = None
        try:
            # Chrome can keep its helper processes (and any pipe) open after it has written the file: do not wait on it.
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, start_new_session=True)
            end, last = time.time() + timeout, -1
            while time.time() < end:
                time.sleep(0.4)
                size = out.stat().st_size if out.is_file() else -1
                if size > 800 and size == last:        # written and no longer growing
                    break
                last = size
        except Exception:
            return None
        finally:
            if proc is not None:
                try:
                    os.killpg(proc.pid, 15)
                except Exception:
                    pass
                try:
                    proc.wait(timeout=4)
                except Exception:
                    try:
                        os.killpg(proc.pid, 9)
                    except Exception:
                        pass
        return out.read_bytes() if out.is_file() and out.stat().st_size > 800 else None


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower() or "case"


def playbook_extras(playbook_id, playbooks_dir):
    """Title and disclaimer in each language, read from the playbook's own data (text only)."""
    try:
        pj = json.loads((Path(playbooks_dir) / playbook_id / "playbook.json").read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {"disc": pj.get("disclaimer") or {}, "title_loc": {k[6:]: v for k, v in pj.items() if k.startswith("title_") and isinstance(v, str)}}


def case_payload(case, title):
    """What the print page needs from a saved case, without the token map and without the map image."""
    meta = case.get("meta", {})
    pages = {k: v for k, v in case.get("pages", {}).items() if re.match(r"0\d-[a-z]+\.md$", k) or k in ("index.md", "log.md", "intake.md")}
    return {"meta": {k: meta.get(k) for k in ("id", "playbook", "created", "language", "status", "edited")}, "pages": pages, "playbook_title": title}


def export_zip_bytes(case_id, case, title, date_iso, extras=None):
    """The export zip: the family copy and the pastor copy as PDF (or print-ready HTML when there is no browser),
    and one records/case.json. No .md files, no privacy-map.json."""
    import io
    data = case_payload(case, title)
    fam = print_html("case", data, "family", title, date_iso, fonts_base=STATIC.as_uri() + "/fonts", screen_note=False, extras=extras)
    pas = print_html("case", data, "pastor", title, date_iso, fonts_base=STATIC.as_uri() + "/fonts", screen_note=False, extras=extras)
    fam_pdf, pas_pdf = render_pdf(fam), render_pdf(pas)
    buf = io.BytesIO()
    root = case_id
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        if fam_pdf and pas_pdf:
            z.writestr(f"{root}/Family copy.pdf", fam_pdf)
            z.writestr(f"{root}/Pastor copy.pdf", pas_pdf)
        else:
            z.writestr(f"{root}/Family copy (print me).html", print_html("case", data, "family", title, date_iso, screen_note=True, extras=extras).replace('src="/', 'src="'))
            z.writestr(f"{root}/Pastor copy (print me).html", print_html("case", data, "pastor", title, date_iso, screen_note=True, extras=extras))
            z.writestr(f"{root}/READ ME.txt", NO_BROWSER + ".\nOpen a copy in a browser and print it to PDF.\n")
        z.writestr(f"{root}/records/case.json", json.dumps({"meta": data["meta"], "pages": data["pages"]}, ensure_ascii=False, indent=1))
    return buf.getvalue(), bool(fam_pdf and pas_pdf)


def session_zip_bytes(view, title, date_iso, extras=None):
    """Both PDFs for a finished run that is not saved yet (no records folder: there is no case)."""
    import io
    fam = print_html("session", view, "family", title, date_iso, fonts_base=STATIC.as_uri() + "/fonts", screen_note=False, extras=extras)
    pas = print_html("session", view, "pastor", title, date_iso, fonts_base=STATIC.as_uri() + "/fonts", screen_note=False, extras=extras)
    fp, pp = render_pdf(fam), render_pdf(pas)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        if fp and pp:
            z.writestr("Family copy.pdf", fp)
            z.writestr("Pastor copy.pdf", pp)
        else:
            z.writestr("Family copy (print me).html", print_html("session", view, "family", title, date_iso, extras=extras))
            z.writestr("Pastor copy (print me).html", print_html("session", view, "pastor", title, date_iso, extras=extras))
            z.writestr("READ ME.txt", NO_BROWSER + ".\nOpen a copy in a browser and print it to PDF.\n")
    return buf.getvalue(), bool(fp and pp)
