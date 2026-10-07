#!/usr/bin/env python3
"""Build the human-review canvas for Juan from stored runs.

  python3 evaluations/make_review_canvas.py [--out PATH]

Reads evaluations/results/runs.json (detention) and results/hospital/runs.json if present.
Every Jev verdict in the middle band becomes one card: question, probability, the text the pastor saw,
Pass and Fail buttons, a note. Clicks arrive as [CANVAS] messages; decisions are saved to
evaluations/results/human_review.json (see apply_review.py).
"""
import argparse, json, os, sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from judges import jev_judges  # noqa: E402

EXCERPT_CHARS = 1400


def items_for(playbook, runs_path):
    if not runs_path.exists():
        return []
    d = json.loads(runs_path.read_text())
    out = []
    for r in d["runs"]:
        for j in r.get("jev", []):
            if j["verdict"] != "review":
                continue
            stages = [{"stage": s["name"], "text": (s.get("shown_text") or "")[:EXCERPT_CHARS]}
                      for s in r["trajectory"]["stages"] if s.get("shown_text")]
            q = jev_judges.NOUL.get(j["name"]) or jev_judges.SCORE.get(j["name"], ("",))[0]
            out.append({"key": f"{playbook}:{r['id']}:{j['name']}", "playbook": playbook, "scenario": r["id"],
                        "number": r["number"], "title": r["title"], "question": j["name"], "question_text": q,
                        "kind": j["kind"], "value": j["value"], "intake": r["trajectory"].get("intake") or "",
                        "stages": stages})
    return out


def main():
    ap = argparse.ArgumentParser()
    aid = os.environ.get("AIM_AGENT_ID", "")
    ap.add_argument("--out", default=str(Path.home() / ".aimaestro/agents" / aid / "canvas/review.html") if aid else "review.html")
    a = ap.parse_args()
    items = items_for("detention", HERE / "results/runs.json") + items_for("hospital", HERE / "results/hospital/runs.json")
    # intake text lives in the scenario files, not the trajectory
    import yaml
    intakes = {}
    for f in (HERE / "scenarios").glob("*.yaml"):
        sc = yaml.safe_load(f.read_text())
        intakes[(sc.get("playbook", "detention"), sc["id"])] = sc["intake"]
    for it in items:
        it["intake"] = intakes.get((it["playbook"], it["scenario"]), "")
    data = {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "items": items}
    blob = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    html = TEMPLATE.replace("__DATA__", blob)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(html, encoding="utf-8")
    print(f"{len(items)} review items -> {a.out}")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nury review</title>
<style>
:root{--bg:#0d1015;--s:#131824;--s2:#1a2233;--line:rgba(236,231,220,.12);--amber:#e8a33d;--text:#ece7dc;--muted:#a79f8d;--green:#8fce9e;--red:#e0785f}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
main{max-width:860px;margin:0 auto;padding:20px 16px 60px}
h1{font:600 26px Georgia,serif;color:var(--amber);margin:0 0 6px}
.sub{color:var(--muted);margin:0 0 16px}
.bar{position:sticky;top:0;background:var(--bg);padding:10px 0;border-bottom:1px solid var(--line);margin-bottom:14px;display:flex;gap:10px;flex-wrap:wrap;align-items:center;z-index:2}
.bar select,.bar input{background:var(--s2);color:var(--text);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font:inherit}
.count{margin-left:auto;color:var(--muted);font-size:14px}
.card{background:var(--s);border:1px solid var(--line);border-radius:14px;padding:16px;margin-bottom:14px}
.card.pass{border-color:rgba(143,206,158,.5)}.card.fail{border-color:rgba(224,120,95,.6)}
.head{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
.head b{font-size:16px}.tag{font-size:12px;background:var(--s2);color:var(--muted);padding:2px 8px;border-radius:99px}
.q{color:var(--muted);margin:8px 0}.p{font-variant-numeric:tabular-nums;color:var(--amber)}
.exp{color:var(--muted);font-size:14px}
details{margin:8px 0}summary{cursor:pointer;color:var(--muted);min-height:32px}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:var(--s2);border-radius:10px;padding:12px;font:13px/1.55 ui-monospace,Menlo,monospace;margin:6px 0}
.row{display:flex;gap:10px;margin-top:12px}.row button{flex:1;min-height:48px;border-radius:10px;border:1px solid var(--line);background:var(--s2);color:var(--text);font:600 16px inherit;cursor:pointer}
.row .pass{color:var(--green)}.row .fail{color:var(--red)}
.row button.on.pass{background:rgba(143,206,158,.18);border-color:var(--green)}.row button.on.fail{background:rgba(224,120,95,.18);border-color:var(--red)}
textarea{width:100%;margin-top:10px;background:var(--s2);color:var(--text);border:1px solid var(--line);border-radius:10px;padding:10px;font:inherit;min-height:44px}
.empty{color:var(--muted);padding:30px 0;text-align:center}
</style></head><body><main>
<h1>Nury review</h1>
<p class="sub" id="sub"></p>
<div class="bar"><select id="f-pb"><option value="">All playbooks</option></select>
<select id="f-q"><option value="">All questions</option></select>
<select id="f-s"><option value="">All</option><option value="open">Not decided</option><option value="pass">Pass</option><option value="fail">Fail</option></select>
<input id="f-t" placeholder="Search"><span class="count" id="count"></span></div>
<div id="list"></div>
<script type="application/json" id="page-data">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('page-data').textContent);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const state={};try{Object.assign(state,JSON.parse(sessionStorage.getItem('nury-review')||'{}'))}catch(e){}
const save=()=>{try{sessionStorage.setItem('nury-review',JSON.stringify(state))}catch(e){}};
document.getElementById('sub').textContent=`${D.items.length} items the automatic judge could not call. Decide each one. Generated ${D.generatedAt}.`;
const fill=(id,vals)=>{const el=document.getElementById(id);[...new Set(vals)].sort().forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;el.appendChild(o)})};
fill('f-pb',D.items.map(i=>i.playbook));fill('f-q',D.items.map(i=>i.question));
function expected(i){return i.kind==='noul'?'Expected answer: no. A high number means Jev thinks the answer is yes.':'Target: at least 4 of 5.'}
function render(){
  const pb=f_pb.value,q=f_q.value,st=f_s.value,t=f_t.value.toLowerCase();
  const rows=D.items.filter(i=>(!pb||i.playbook===pb)&&(!q||i.question===q)&&(!st||(st==='open'?!state[i.key]:state[i.key]&&state[i.key].verdict===st))
    &&(!t||(i.scenario+i.title+i.question).toLowerCase().includes(t)));
  const done=D.items.filter(i=>state[i.key]).length;
  count.textContent=`${rows.length} shown, ${done} of ${D.items.length} decided`;
  list.innerHTML=rows.length?'':'<div class="empty">Nothing matches.</div>';
  rows.forEach(i=>{const s=state[i.key]||{};const c=document.createElement('div');c.className='card '+(s.verdict||'');
    c.innerHTML=`<div class="head"><b>${esc(i.playbook)} ${esc(i.number)}: ${esc(i.title)}</b><span class="tag">${esc(i.question)}</span><span class="p">Jev ${esc(i.value)}</span></div>
    <div class="q">${esc(i.question_text)}</div><div class="exp">${expected(i)}</div>
    <details><summary>What the family said</summary><pre>${esc(i.intake)}</pre></details>
    <details><summary>What the pastor was shown (${i.stages.length} stages)</summary>${i.stages.map(x=>`<div class="exp">${esc(x.stage)}</div><pre>${esc(x.text)}</pre>`).join('')}</details>
    <textarea placeholder="Note (optional)">${esc(s.note||'')}</textarea>
    <div class="row"><button class="pass ${s.verdict==='pass'?'on':''}">Pass</button><button class="fail ${s.verdict==='fail'?'on':''}">Fail</button></div>`;
    const ta=c.querySelector('textarea');
    c.querySelectorAll('.row button').forEach(b=>b.onclick=()=>{const v=b.classList.contains('pass')?'pass':'fail';
      state[i.key]={verdict:v,note:ta.value};save();
      maestro.send('click','review:'+i.key,{key:i.key,playbook:i.playbook,scenario:i.scenario,question:i.question,verdict:v,note:ta.value.slice(0,300)});render()});
    list.appendChild(c)});
}
const f_pb=document.getElementById('f-pb'),f_q=document.getElementById('f-q'),f_s=document.getElementById('f-s'),f_t=document.getElementById('f-t'),count=document.getElementById('count'),list=document.getElementById('list');
[f_pb,f_q,f_s].forEach(e=>e.onchange=render);f_t.oninput=render;render();
</script></main></body></html>"""

if __name__ == "__main__":
    main()
