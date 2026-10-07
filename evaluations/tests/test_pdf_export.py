"""PDF copies and the export zip. Offline: no model call. The PDF checks run only where Chrome or Chromium is installed; the others always run.
Run: python3 -m pytest evaluations/tests -q"""
import io
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2] / "code"
sys.path.insert(0, str(ROOT))
from app import pdf_export as px  # noqa: E402

DISC = "Nury is an AI assistant, not a lawyer, pastor, counselor, or therapist. Esto es información legal general, no asesoramiento legal."
CASE = {"meta": {"id": "detention-20261007-120000-abcd", "playbook": "detention", "title": "Immigration detention or raid", "created": "2026-10-07 12:00 UTC",
                 "language": "es", "status": "complete", "edited": ["checklist"]},
        "pages": {
            "01-triage.md": "# 1. Triage\n\nStatus: approved by the pastor\n\nSITUATION: José fue detenido cerca de su trabajo en Aurora.\n\nPEOPLE: María (esposa).\n\n" + DISC + "\n\n---\n[Index](index.md)",
            "02-rights.md": "# 2. Rights brief\n\nStatus: approved by the pastor\n\n- Tiene derecho a guardar silencio. (ACLU Know Your Rights)\n- No firme ningún documento sin hablar con un abogado. (ACLU Know Your Rights)\n\nPor favor, hable con un abogado de inmigración.\n\n" + DISC,
            "03-attorney.md": "# 3. Attorney resources\n\nStatus: approved by the pastor\n\n**Contactos de la iglesia**\n\n*Son contactos de la iglesia.*\n\n- **Demo Legal Aid**: Consultas gratis. (303) 555-0101 https://demo.example.org/\n\n" + DISC,
            "04-checklist.md": "# 4. Family checklist\n\nStatus: approved by the pastor\n\nDO TONIGHT / HAGA ESTA NOCHE\n\n1. Llame a un abogado de inmigración.\n2. Reúna los documentos.\n\nGATHER THESE DOCUMENTS / REÚNA ESTOS DOCUMENTOS\n\nDocumentos de identidad:\n- Pasaporte o identificación de José\n\n" + DISC,
            "05-pastoral.md": "# 5. Pastoral message\n\nStatus: approved by the pastor\n\nMaría, sabemos que esta noche es difícil. La iglesia está con ustedes.\n\n«Dios es nuestro refugio y fortaleza.»\n— Salmo 46:1, Biblia Libre\n\nUn versículo para esta noche.\n\n" + DISC,
            "index.md": "# Immigration detention or raid\n\nCase x", "log.md": "scripture provider: bank"},
        "svg": None}


def _zip(zbytes):
    return zipfile.ZipFile(io.BytesIO(zbytes))


def test_print_page_is_self_contained_and_carries_the_data():
    data = px.case_payload(CASE, "Immigration matter")
    h = px.print_html("case", data, "family", "Immigration matter", "2026-10-07T12:00:00Z")
    assert "window.__PRINT__" in h and "NuryFinal" in h and "@page" in h and "/*@" not in h
    assert "José" in h and "privacy" not in h.lower().replace("privacy-map", "")
    assert "Letter" in h and "Fraunces" in h and "Inter" in h


def test_case_payload_leaves_out_the_map_and_the_token_map():
    c = dict(CASE, pages=dict(CASE["pages"], **{"privacy-map.json": "{}", "people.md": "x"}))
    data = px.case_payload(c, "Immigration matter")
    assert "privacy-map.json" not in data["pages"] and "people.md" not in data["pages"]
    assert "svg" not in data


def test_export_zip_has_no_markdown_and_no_token_map():
    z, _ = px.export_zip_bytes(CASE["meta"]["id"], CASE, "Immigration matter", "2026-10-07T12:00:00Z")
    names = _zip(z).namelist()
    assert not [n for n in names if n.endswith(".md")], names
    assert not [n for n in names if "privacy-map" in n], names
    assert any(n.endswith("records/case.json") for n in names)
    rec = json.loads(_zip(z).read([n for n in names if n.endswith("records/case.json")][0]))
    assert "privacy-map" not in json.dumps(rec)
    assert [n for n in names if n.endswith(".pdf") or n.endswith(".html")]


@pytest.mark.skipif(px.find_chrome() is None, reason="needs Chrome or Chromium")
def test_pdfs_exist_start_with_pdf_have_pages_text_accents_and_embedded_fonts():
    z, ok = px.export_zip_bytes(CASE["meta"]["id"], CASE, "Immigration matter", "2026-10-07T12:00:00Z")
    assert ok
    zf = _zip(z)
    pdfs = {n.split("/")[-1]: zf.read(n) for n in zf.namelist() if n.endswith(".pdf")}
    assert set(pdfs) == {"Family copy.pdf", "Pastor copy.pdf"}
    for name, b in pdfs.items():
        assert b.startswith(b"%PDF"), name
    if shutil.which("pdfinfo") and shutil.which("pdftotext") and shutil.which("pdffonts"):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            for name, b in pdfs.items():
                p = Path(d) / name.replace(" ", "_")
                p.write_bytes(b)
                info = subprocess.run(["pdfinfo", str(p)], capture_output=True, text=True).stdout
                assert int(re.search(r"Pages:\s+(\d+)", info).group(1)) >= 1
                assert "612 x 792" in info                                   # US Letter
                txt = subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, text=True).stdout
                assert len(txt.strip()) > 200
                fonts = subprocess.run(["pdffonts", str(p)], capture_output=True, text=True).stdout.splitlines()[2:]
                assert fonts and all(" yes " in f for f in fonts), fonts       # every font embedded
                if name.startswith("Family"):
                    assert "José" in txt and "María" in txt and "Página" in txt and "identificación" in txt
                    assert "Lo que está pasando" in txt
                else:
                    assert "Audit summary" in txt and "Edited by the pastor" in txt and "ACLU Know Your Rights" in txt


def test_find_chrome_honours_chrome_bin(monkeypatch, tmp_path):
    fake = tmp_path / "chrome"
    fake.write_text("#!/bin/sh\n")
    fake.chmod(0o755)
    monkeypatch.setenv("CHROME_BIN", str(fake))
    assert px.find_chrome() == str(fake)


def test_without_a_browser_the_zip_falls_back_to_print_ready_html(monkeypatch):
    monkeypatch.setattr(px, "find_chrome", lambda: None)
    z, ok = px.export_zip_bytes(CASE["meta"]["id"], CASE, "Immigration matter", "2026-10-07T12:00:00Z")
    names = _zip(z).namelist()
    assert ok is False and any(n.endswith(".html") for n in names) and not any(n.endswith(".pdf") for n in names)
    assert "Chrome or Chromium" in _zip(z).read([n for n in names if n.endswith("READ ME.txt")][0]).decode()
