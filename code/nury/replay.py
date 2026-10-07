"""Replay mode: try the app with no key. Recorded model words, live checks.

A pack (code/replay/<playbook>/<scenario>.json) holds what the model wrote in one real run of the sample intake, stage by
stage and attempt by attempt, with the Jev scores of that run. In replay the engine runs for real: the safety floor, the
named checks, the correction loop, the approval gates, the audit log, the privacy layer, the case file and the Scripture
insertion. Only the model is replaced: ReplayClient hands back the recorded words.

On or off. NURY_REPLAY=1 turns it on, NURY_REPLAY=0 turns it off. Unset: on only when no GLOO_API_KEY exists (the repo-root
.env counts). With a key present and the variable unset, nothing here runs and Nury behaves exactly as before.

What is recorded stays recorded. A pastor's edit at a gate is carried forward as written, but the later stages stay the
recorded ones. A typed intake is refused: only the sample intake is accepted."""
import json
import os
import re
from pathlib import Path

PACKS = Path(__file__).resolve().parents[1] / "replay"
REFUSAL = "This is a recorded run. Add a Gloo key to run your own."
BANNER = "Recorded run. The words were written by the model earlier; the checks run live. Add a Gloo key to run your own."
EDIT_NOTE = "Your edit is carried forward as you wrote it. The later stages are the recorded ones, so they do not react to it."
SPLICE_NOTE = ("The contacts from your church network (or the demo network) were added to the recorded list by the replay layer, copied exactly "
               "as the app gave them, because the recording was made with an empty network.")
_CONTACTS = re.compile(r"CHURCH CONTACTS \(the pastor's own; may be empty\):\n(.*?)\n\n", re.S)
_OFFICIAL = re.compile(r"OFFICIAL LIST \(U\.S\. Department of Justice; may be empty\):\n(.*?)\n\n", re.S)
_PHONE = re.compile(r"\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}")
_HEAD = {"es": ("Personas con quienes nuestra iglesia ha trabajado", "Estos son contactos de nuestra iglesia. No son una recomendación de Nury."),
         "en": ("People our church has worked with", "These are our church's own contacts, not endorsements by Nury.")}


def active(env=None):
    env = os.environ if env is None else env
    v = (env.get("NURY_REPLAY") or "").strip().lower()
    if v in ("1", "true", "on", "yes"):
        return True
    if v in ("0", "false", "off", "no"):
        return False
    if env is os.environ:
        from .gloo_client import load_env
        load_env()
    return not (env.get("GLOO_API_KEY") or "").strip()


def packs():
    """{playbook id: pack} for every pack on disk. A pack that does not parse is skipped."""
    out = {}
    for f in sorted(PACKS.glob("*/*.json")):
        try:
            p = json.loads(f.read_text(encoding="utf-8"))
            out[p["playbook"]] = p
        except (ValueError, KeyError, OSError):
            continue
    return out


def sample_intake(playbook):
    p = packs().get(playbook)
    return p["intake"] if p else None


def _norm(t):
    return " ".join((t or "").split())


def is_sample(playbook, intake, language):
    p = packs().get(playbook)
    return bool(p) and _norm(intake) == _norm(p["intake"]) and language == p["language"]


def task_line(instructions):
    m = re.search(r"(?m)^Task:.*$", instructions or "")
    return _norm(m.group(0)) if m else ""


class ReplayClient:
    """The same ask() the engine uses. It serves the recorded text of the stage whose Task line is in `instructions`."""
    replay = True

    def __init__(self, pack=None):
        self.pack, self.calls, self.model = pack, {}, "recorded"
        self.spliced = []           # stage ids whose recorded text got the church-contacts block (see _splice)

    def use_playbook(self, playbook, language):
        p = packs().get(playbook)
        if not p or language != p["language"]:
            raise RuntimeError(REFUSAL)
        self.pack, self.calls, self.spliced = p, {}, []

    def _splice(self, sid, text, instructions):
        """The recording was made with an empty church network. When this run's network is not empty, the prompt hands the
        stage the contacts to list first, and the checks require every one of them. Put them in the way the prompt asks:
        under the heading, with the note, each entry copied exactly as the app gave it. Nothing else of the text changes."""
        blocks = []
        m = _CONTACTS.search(instructions or "")
        lines = [l for l in (m.group(1).splitlines() if m else []) if l.startswith("- ")]
        if lines and lines[0][2:].split(":")[0].strip() not in text:
            head, note = _HEAD[self.pack["language"] if self.pack["language"] in _HEAD else "en"]
            blocks.append(f"**{head}**\n\n{note}\n\n" + "\n".join(self._entry(l, keep_services=self.pack["language"] == "en") for l in lines))
        o = _OFFICIAL.search(instructions or "")
        official = self.pack["stages"].get(sid, {}).get("official_list_block")
        if o and official and any(l.startswith("- ") for l in o.group(1).splitlines()) and "Departamento de Justicia" not in text:
            blocks.append(official)                                    # the model's own words for these fixed entries (see the pack's note)
        if not blocks:
            return text
        first, _, rest = text.partition("\n\n")
        self.spliced.append(sid)
        return f"{first}\n\n---\n\n" + "\n\n---\n\n".join(blocks) + (f"\n\n---\n\n{rest}" if rest else "")

    @staticmethod
    def _entry(line, keep_services=True):
        """'- name: services phone url' (how the app hands a contact to the prompt) -> '- name — phone — url'. The short description is kept only
        in English: a model would translate it, and the replay layer cannot, so in Spanish the entry is the name, phone and link, copied exactly."""
        m = re.match(r"- (.*?): (.*)$", line)
        if not m:
            return line
        name, rest = m.group(1), m.group(2)
        url = next((w for w in rest.split() if w.startswith("http")), "")
        rest = rest.replace(url, "") if url else rest
        ph = _PHONE.search(rest)
        phone = ph.group(0) if ph else ""
        services = (rest.replace(phone, "") if phone else rest).strip(" ,;")
        return "- " + " — ".join(x for x in (name, services if keep_services else "", phone, url) if x)

    def ask(self, user_input, instructions=None, **kw):
        if self.pack is None:
            raise RuntimeError(REFUSAL)
        line = task_line(instructions)
        for sid, st in self.pack["stages"].items():
            if _norm(st["task"]) == line:
                n = self.calls.get(sid, 0)
                self.calls[sid] = n + 1
                a = st["attempts"][min(n, len(st["attempts"]) - 1)]          # past the last recording: say the last thing again
                text = self._splice(sid, a["text"], instructions)           # only a stage whose prompt hands it church contacts is touched
                return text, {"latency_s": a.get("latency_s", 0.0), "input_tokens": a.get("input_tokens", 0),
                                   "output_tokens": a.get("output_tokens", 0), "model": self.pack.get("model", "recorded"), "http_retries": 0}
        raise RuntimeError("this recorded run has no words for that step")

    def jev_scores(self, stage):
        """The Jev scores recorded for a stage, labelled as recorded: [{attempt, question, probability, decision}]."""
        return list(((self.pack or {}).get("stages", {}).get(stage, {}) or {}).get("jev", []))
