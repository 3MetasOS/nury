"""Build the worked example of the learning loop on SYNTHETIC data. No real pastor is involved anywhere in it.

    cd code && python3 tools/learning_example.py            # writes documents/product/learning_example/

It invents 30 sessions with fictional families and scripted 'pastor' behavior, in the spirit of scenario 16 (pastor edits a
stage) and the revision scenarios, passes them through the real capture code (nury.feedback) with the real Pseudonymizer, then
runs the learning report on what was captured. Deterministic: the same seed gives the same files.
"""
import os
import random
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

OUT = HERE.parents[1] / "documents" / "product" / "learning_example"
NAMES = [("Zorana Quimbley", "Thaddeus"), ("Brunhilda Vandersloot", "Ottilie"), ("Marguerite Ostrowski", "Leopold"),
         ("Placida Wetherby", "Casimir"), ("Odalys Fernwood", "Barnaby")]
PAST = [
    "{n}, sabemos que esta noche es muy difícil.",
    "Es normal sentir miedo, y no tienen que pretender que no lo sienten.",
    "La iglesia está con ustedes y los tenemos en el corazón.",
    "En este paquete hay una lista de pasos para esta noche y una lista de personas a quienes pueden llamar.",
    "Si quieren orar juntos o necesitan hablar, pueden llamarme.",
    "No están solos.",
]
CHECK = ["DO TONIGHT", "1. Busque los papeles de {c}.", "DO NOT DO", "1. No firme nada.", "GATHER THESE DOCUMENTS", "1. Identificación."]


def build(seed=16):
    from nury import feedback as fb
    from nury.privacy import PrivacyClient
    rnd = random.Random(seed)
    fb_dir = OUT / "feedback"
    shutil.rmtree(OUT, ignore_errors=True)
    fb_dir.mkdir(parents=True)
    os.environ["NURY_FEEDBACK"] = "on"
    os.environ["NURY_FEEDBACK_DIR"] = str(fb_dir)
    n_lines = 0
    for i in range(30):
        pb = "detention" if i < 20 else "hospital"
        name, other = NAMES[i % len(NAMES)]
        pc = PrivacyClient(None, [name, other])
        first = name.split()[0]
        events = [{"kind": "jev_gate", "stage": "pastoral", "attempt": 1, "question": "promises_action", "probability": round(rnd.uniform(0.1, 0.45), 2), "decision": "pass"}]
        if rnd.random() < 0.3:
            events.append({"kind": "draft_rejected", "stage": "pastoral", "attempt": 1, "visible_to_pastor": False, "reason_categories": ["jev_promises_action"]})
        draft = "\n".join(PAST).replace("{n}", first)
        # pastoral stage: the scripted pastor shortens in 15 of 20 detention sessions and in 2 of 10 hospital sessions
        shorten = rnd.random() < (0.75 if pb == "detention" else 0.2)
        voice = rnd.random() < 0.3
        final = draft
        chip = None
        if shorten:
            final = "\n".join(PAST[:3] + PAST[4:]).replace("{n}", first)
            final = final.replace(" y los tenemos en el corazón", "")
            chip = "too_long" if rnd.random() < 0.7 else None
        if voice:
            final = final.replace("No están solos.", f"{first}, Dios los acompaña.").replace("no tienen que pretender que no lo sienten", "es natural sentir miedo")
            chip = "not_my_voice" if rnd.random() < 0.6 else chip
        action = "edit" if final != draft else "approve"
        fb.record_gate("pastoral", action, draft, final, pc, events, playbook=pb, language="es", run_id=f"syn{i:03d}",
                       reason_chip=chip or ("good_as_is" if action == "approve" and rnd.random() < 0.5 else None), outcome_label=None, root=str(fb_dir))
        n_lines += 1
        # checklist stage: one pastor adds a sentence sometimes
        cdraft = "\n".join(CHECK).replace("{c}", other)
        cfinal = cdraft + (f"\n2. Pregunte por {other} en la oficina." if rnd.random() < 0.15 else "")
        fb.record_gate("checklist", "edit" if cfinal != cdraft else "approve", cdraft, cfinal, pc, [], playbook=pb, language="es", run_id=f"syn{i:03d}", root=str(fb_dir))
        n_lines += 1
        # the revision flow: 'Something changed' answers
        if i % 3 == 0:
            res = rnd.choices(["went as hoped", "did not go as hoped", "unknown"], [0.35, 0.4 if pb == "detention" else 0.1, 0.25])[0]
            fb.record_outcome(pb, res, language="es", root=str(fb_dir))
            n_lines += 1
    os.environ.pop("NURY_FEEDBACK", None)
    os.environ.pop("NURY_FEEDBACK_DIR", None)
    return fb_dir, n_lines


if __name__ == "__main__":
    import learning_report as lr
    fb_dir, n = build()
    an, cs = lr.main(["--feedback", str(fb_dir), "--ledger", str(OUT / "no-ledger"), "--out", str(OUT / "LEARNING_REPORT_EXAMPLE.md"),
                      "--candidates", str(OUT / "candidates"), "--synthetic", "--today", "2026-10-07"])
    print("synthetic lines:", n, "| candidates:", [c[0]["id"] for c in cs])
