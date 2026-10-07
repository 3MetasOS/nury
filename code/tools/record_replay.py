"""Record a replay pack: ONE live run of a playbook's sample intake, with the forced-rejection option on stage 2, so the pack holds
the model's own draft and its own regenerated draft. Needs GLOO_API_KEY (and JEV_API_KEY to record the Jev scores). Costs about 0.1 dollars.

    cd code && python3 tools/record_replay.py detention [--out replay/detention/01-sample.json]

The intake is the playbook's own demo intake (playbook.json, intake.demo): synthetic names only."""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nury import replay  # noqa: E402
from nury.engine import UNSAFE_SUFFIX, get_playbook, run_scripted  # noqa: E402
from nury.privacy import make_client  # noqa: E402


class Recorder:
    def __init__(self, inner):
        self.inner, self.log = inner, []

    def ask(self, user_input, instructions=None, **kw):
        text, meta = self.inner.ask(user_input, instructions=instructions, **kw)
        self.log.append((replay.task_line(instructions), text, meta))
        return text, meta

    def __getattr__(self, name):
        return getattr(self.inner, name)


def main(pid, out=None):
    pb = get_playbook(pid)
    intake = json.loads((Path(__file__).resolve().parents[1] / "playbooks" / pid / "playbook.json").read_text(encoding="utf-8"))["intake"]["demo"]
    lang = pb.default_family_language
    rec = Recorder(make_client(intake=intake))
    fault = {"stage": pb.stages[1].id, "times": 1, "draft_suffix": UNSAFE_SUFFIX}
    st, rs, au = run_scripted(intake, language=lang, client=rec, playbook=pid, fault_injection=fault)
    assert st.outcome["outcome"] == "package_complete", st.outcome
    order = []                                    # the distinct Task lines, in the order the stages asked
    by_task = {}
    for line, text, meta in rec.log:
        if line not in by_task:
            order.append(line)
        by_task.setdefault(line, []).append({"text": text, "input_tokens": meta.get("input_tokens", 0), "output_tokens": meta.get("output_tokens", 0),
                                              "latency_s": meta.get("latency_s", 0.0)})
    if len(order) != len(pb.stages):
        raise SystemExit(f"expected {len(pb.stages)} stages, saw {len(order)} different tasks")
    stages = {}
    for s, line in zip(pb.stages, order):
        jev = [{"attempt": e.get("attempt"), "question": e["question"], "probability": e["probability"], "decision": e["decision"]}
               for e in au.events if e["kind"] == "jev_gate" and e.get("stage") == s.id and e.get("question") not in (None, "*") and e.get("probability") is not None]
        stages[s.id] = {"task": line, "attempts": by_task[line], "jev": jev}
    core = subprocess.run(["git", "log", "-1", "--format=%h", "--", "nury", "playbooks"], cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True).stdout.strip()
    pack = {"playbook": pid, "scenario": "sample", "language": lang, "intake": intake, "model": rec.log[0][2].get("model", ""), "core_commit": core,
            "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "note": "One live run of the playbook's sample intake with the forced-rejection option on stage 2. Synthetic names only. The words are the model's; the checks and gates run live in replay.",
            "stages": stages}
    out = Path(out or Path(__file__).resolve().parents[1] / "replay" / pid / "sample.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(pack, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out}: " + ", ".join(f"{k}={len(v['attempts'])} attempt(s)" for k, v in stages.items()))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None)
