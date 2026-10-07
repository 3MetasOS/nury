"""Stand-in agent so the harness can be tested before the real core lands.
Produces trajectories in the documented shape. Not part of the product."""
import time

DIS_ES = "No soy abogado y esto no es asesoramiento legal. Soy un asistente de IA."
DIS_EN = "I am not a lawyer and this is not legal advice. I am an AI assistant."
NAMES = {1: "triage", 2: "rights_brief", 3: "attorney_resources", 4: "family_checklist", 5: "pastoral_message"}
BANNED_FOR_MOCK = ["you should plead", "your case will", "you will win", "guaranteed"]


def _text(n, lang, ctx):
    d = DIS_ES if lang == "es" else DIS_EN
    es = {2: "Tiene derecho a guardar silencio y no debe firmar nada sin hablar con un abogado. Fuente: ACLU Know Your Rights. Consulte a un abogado de inmigración.",
          3: "Directorio nacional: Immigration Advocates Network https://www.immigrationadvocates.org/nonprofit/legaldirectory/ y AILA https://www.ailalawyer.com/ para encontrar un abogado.",
          4: "HAGA ESTA NOCHE: llame a un abogado. NO HAGA: no firme nada. REÚNA: pasaporte y actas de nacimiento de los niños.",
          5: "Querida familia, no están solos. Estamos con ustedes esta noche y la iglesia los acompaña. Hablen con un abogado pronto."}
    en = {2: "You have the right to remain silent and should not sign anything without a lawyer. Source: ACLU Know Your Rights. Please consult an immigration attorney.",
          3: "National directory: Immigration Advocates Network https://www.immigrationadvocates.org/nonprofit/legaldirectory/ and AILA https://www.ailalawyer.com/ to find a lawyer.",
          4: "DO TONIGHT: call an attorney. DO NOT DO: do not sign anything. GATHER THESE DOCUMENTS: passport and the children's birth certificates.",
          5: "Dear family, you are not alone. We are with you tonight and the church walks with you. Please speak with an attorney soon."}
    if n == 1:
        return "Situation: detention reported. People: spouse and two children. Urgency: high, the detainee's location is unknown. Missing: location, agency, any documents signed. " + DIS_EN
    return (es if lang == "es" else en)[n] + " " + d + (" " + ctx if ctx else "")


def run(sc):
    t0 = time.time()
    lang, actions, fi = sc["output_language"], sc["pastor_actions"], sc.get("fault_injection")
    audit, stages, ctx, halted, hstage, escalated = [], [], "", False, None, False
    for n in range(1, 6):
        base = _text(n, lang, ctx)
        attempts = []
        bad_times = fi["times"] if fi and fi["stage"] == n else 0
        for i in range(4):
            if i < bad_times:
                text = base + fi["draft_suffix"]
            else:
                text = base
            viol = [p for p in BANNED_FOR_MOCK if p in text.lower()]
            attempts.append({"text": text, "violations": viol})
            audit.append({"ts": time.time(), "event": "guardrail", "stage": n, "try": i + 1, "violations": viol})
            if not viol or i == 3:
                break
        esc = bool(attempts[-1]["violations"]) or len(attempts) > 3
        if len(attempts) > 3:
            attempts = attempts[:3]; esc = bool(attempts[-1]["violations"])
        s = {"n": n, "name": NAMES[n], "attempts": attempts, "retries": len(attempts) - 1, "escalated": esc,
             "input_context": ctx, "latency_s": 0.01, "tokens_in": 100, "tokens_out": 150, "cost_usd": 0.0}
        if esc:
            s["shown_text"] = None; s["final_text"] = None; escalated = True; halted = True; hstage = n
            stages.append(s); break
        s["final_text"] = s["shown_text"] = attempts[-1]["text"]
        act = actions.get(n, actions.get(str(n), "approve"))
        if isinstance(act, dict) and "edit" in act:
            s["gate"] = {"action": "edit", "edited_text": act["edit"]}; s["shown_text"] = s["final_text"] = act["edit"] + " " + (DIS_ES if lang == "es" else DIS_EN)  # gate re-appends disclaimer
            ctx = s["final_text"]
        else:
            s["gate"] = {"action": act}
        audit.append({"ts": time.time(), "event": "gate", "stage": n, "action": s["gate"]["action"]})
        stages.append(s)
        if act in ("reject", "stop"):
            halted = True; hstage = n; break
    pkg = None if halted else {str(s["n"]): s["final_text"] for s in stages}
    return {"scenario_id": sc["id"], "stages": stages, "halted": halted, "halt_stage": hstage, "escalated": escalated,
            "audit_log": audit, "package": pkg, "ui_strings": ["Approve", "Edit", "Stop"], "latency_s": time.time() - t0}
