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

    def use_playbook(self, playbook, language):
        p = packs().get(playbook)
        if not p or language != p["language"]:
            raise RuntimeError(REFUSAL)
        self.pack, self.calls = p, {}

    def ask(self, user_input, instructions=None, **kw):
        if self.pack is None:
            raise RuntimeError(REFUSAL)
        line = task_line(instructions)
        for sid, st in self.pack["stages"].items():
            if _norm(st["task"]) == line:
                n = self.calls.get(sid, 0)
                self.calls[sid] = n + 1
                a = st["attempts"][min(n, len(st["attempts"]) - 1)]          # past the last recording: say the last thing again
                return a["text"], {"latency_s": a.get("latency_s", 0.0), "input_tokens": a.get("input_tokens", 0),
                                   "output_tokens": a.get("output_tokens", 0), "model": self.pack.get("model", "recorded"), "http_retries": 0}
        raise RuntimeError("this recorded run has no words for that step")

    def jev_scores(self, stage):
        """The Jev scores recorded for a stage, labelled as recorded: [{attempt, question, probability, decision}]."""
        return list(((self.pack or {}).get("stages", {}).get(stage, {}) or {}).get("jev", []))
