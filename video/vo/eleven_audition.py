"""ElevenLabs auditions for VO lines 01-03 (locked text, English). Key comes from the environment or repo-root .env; never printed or logged.
Usage: python3 vo/eleven_audition.py list            # premade voices in the account
       python3 vo/eleven_audition.py render [names]   # render lines 01-03 to vo/auditions/eleven_<Name>_<NN>.mp3 and log characters"""
import json, os, sys, urllib.request, urllib.error
from pathlib import Path
here = Path(__file__).resolve().parent
def key():
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k:
        for l in open(here.parent.parent / ".env"):
            if l.startswith("ELEVENLABS_API_KEY="): k = l.split("=", 1)[1].strip().strip('"\'')
    assert k, "ELEVENLABS_API_KEY missing"; return k
def call(path, body=None, method=None, raw=False):
    req = urllib.request.Request("https://api.elevenlabs.io" + path, data=json.dumps(body).encode() if body is not None else None,
        headers={"xi-api-key": key(), "Content-Type": "application/json", "Accept": "audio/mpeg" if raw else "application/json"}, method=method)
    with urllib.request.urlopen(req, timeout=120) as r: d = r.read(); return d if raw else json.loads(d)
SETTINGS = {"stability": 0.5, "similarity_boost": 0.75, "style": 0.2, "use_speaker_boost": True}
lines = dict(l.strip().split("|", 1) for l in open(here / "lines.txt") if l.strip())
SHARED = {"qqab7XtemzUr6wYwGSrQ": "Jerome", "Wb1wmVQjMx9g2QSIOTPI": "Juan Esteban", "kNiBmBMHnRB4vitKoqQt": "Jose Dominguez", "M64I64ENmO2dliUo0xY7": "AD-berto",
          "I6l6HMSXnLBBXnb2W3fB": "Nayla", "IP2syKL31S2JthzSSfZH": "Ivan Rodriguez", "4ISzXkLY6aTZQsrFLVme": "Kevo"}
PREMADE = {"nPczCjzI2devNBz1zQrb": "Brian", "JBFqnCBsd6RMkjVDRZzb": "George", "hpp4J3VqNfWAUOO0d1Us": "Bella", "cjVigY5qzO86Huf0OWal": "Eric", "EXAVITQu4vr4xnSDxMaL": "Sarah"}
import urllib.parse
FOUND = here / "auditions" / "shared_found.json"
def shared():
    found = {}
    for vid, name in SHARED.items():
        r = call("/v1/shared-voices?page_size=30&search=" + urllib.parse.quote("Velvety" if name == "AD-berto" else name.split()[0]))
        for v in r.get("voices", []):
            if v["voice_id"] == vid:
                found[vid] = {"owner": v["public_owner_id"], "name": v["name"], "accent": v.get("accent"), "free_users_allowed": v.get("free_users_allowed"),
                              "category": v.get("category"), "language": v.get("language"), "description": (v.get("description") or "")[:140]}
        print(name, "found" if vid in found else "NOT FOUND", found.get(vid, {}).get("accent"), found.get(vid, {}).get("free_users_allowed"))
    json.dump(found, open(FOUND, "w"), indent=1)
def add():
    for vid, v in json.load(open(FOUND)).items():
        try: call(f"/v1/voices/add/{v['owner']}/{vid}", {"new_name": v["name"]}); print("added", v["name"])
        except urllib.error.HTTPError as e: print("add failed", v["name"], e.code, e.read()[:160])
def render(names):
    log = here / "auditions" / "LOG.md"
    voices = dict(PREMADE); voices.update({vid: SHARED[vid] for vid in SHARED})
    for vid, name in voices.items():
        if names and name not in names: continue
        extra = {"03b": lines["03"].replace("Nury", "Noory"), "names": "Maria and Jose called from Aurora."}  # 03b: phonetic respelling in the request only; names: pronunciation check
        for k in ["01", "02", "03", "03b", "names"]:
            text = extra.get(k) or lines[k]
            out = here / "auditions" / f"eleven_{name.replace(' ', '')}_{k}.mp3"
            try: audio = call(f"/v1/text-to-speech/{vid}?output_format=mp3_44100_128", {"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": SETTINGS}, raw=True)
            except urllib.error.HTTPError as e: print("FAILED", name, k, e.code, e.read()[:200]); continue
            out.write_bytes(audio)
            with open(log, "a") as f: f.write(f"- {name} line {k}: {len(text)} characters\n")
            print(name, k, "ok", len(text))
if __name__ == "__main__":
    c = sys.argv[1]
    if c == "list":
        for v in call("/v1/voices")["voices"]: print(v["voice_id"], v["name"], "|", v.get("category"), "|", (v.get("labels") or {}).get("accent"))
    elif c == "shared": shared()
    elif c == "add": add()
    elif c == "render": render(sys.argv[2:])
