/* Diagrams drawn from DATA (the playbook's stages, a saved case's pages). A new crisis gets its diagram for free.
   Line drawings in the hand-sketch spirit of the notes: one accent, mono labels, vertical so they read at 390 px.
   Every diagram has a text alternative (aria-label on the figure and the same facts in the page's lists). Server text goes in as textContent. */
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const s = (t, a, x) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); if (x != null) e.textContent = x; return e; };
  const wrap = (t, n) => { const w = (t || "").split(/\s+/), out = []; let l = ""; w.forEach(x => { if ((l + " " + x).trim().length > n) { out.push(l.trim()); l = x; } else l += " " + x; }); if (l.trim()) out.push(l.trim()); return out; };
  const num = t => (t || "").replace(/^\d+\.\s*/, "");

  // The path of a response: intake -> protect names -> stage -> gate -> ... -> package -> case file. Exit at every gate: Stop = I handle it.
  function flow(stages, opts) {
    opts = opts || {};
    const rows = [{ k: "step", t: "Intake", d: "You type what the family told you." }, { k: "step", t: "Protect names", d: "You pick the names to hide. Tokens, not names, go to the model." }];
    stages.forEach((st, i) => { rows.push({ k: "stage", n: i + 1, t: num(st.title), d: st.line || st.summary || "" }); if (i < stages.length) rows.push({ k: "gate" }); });
    rows.push({ k: "step", t: "Package", d: "Every approved stage. You copy it, download it or print it." }, { k: "step", t: "Case file", d: "Optional: save it to open later, with a next-steps map." });
    const W = 600, X = 44; let y = 14; const parts = [], ys = [];
    rows.forEach(r => { const h = r.k === "gate" ? 44 : 70; ys.push([y, h]); y += h; });
    const H = y + 6;
    const svg = s("svg", { viewBox: `0 0 ${W} ${H}`, class: "dgm", role: "img", "aria-label": `The path of a response: intake, protecting names, then ${stages.map(x => num(x.title)).join(", ")}, each followed by your gate (Approve, Edit or Stop), then the package and the case file. Stop at any gate means you handle it yourself.` });
    // the line down the left
    svg.append(s("path", { d: `M${X} 20 V${H - 24}`, class: "dg-line" }));
    rows.forEach((r, i) => {
      const [y0, h] = ys[i], cy = y0 + (r.k === "gate" ? h / 2 : 26);
      if (r.k === "gate") {
        svg.append(s("path", { d: `M${X} ${cy - 9} l9 9 l-9 9 l-9 -9 z`, class: "dg-gate" }));
        const t = s("text", { x: X + 26, y: cy + 4, class: "dg-mono" }, "your gate: Approve · Edit · Stop");
        svg.append(t);
        svg.append(s("path", { d: `M${X + 232} ${cy} C ${X + 300} ${cy - 5}, ${X + 360} ${cy + 5}, ${W - 150} ${cy}`, class: "dg-stop" }));
        svg.append(s("path", { d: `M${W - 158} ${cy - 5} L${W - 150} ${cy} L${W - 159} ${cy + 5}`, class: "dg-stop" }));
        svg.append(s("text", { x: W - 144, y: cy + 4, class: "dg-stoptxt" }, "Stop = I handle it"));
        return;
      }
      if (r.k === "stage") {
        svg.append(s("circle", { cx: X, cy, r: 15, class: "dg-node on" }));
        svg.append(s("text", { x: X, y: cy + 5, "text-anchor": "middle", class: "dg-num" }, String(r.n)));
      } else svg.append(s("circle", { cx: X, cy, r: 9, class: "dg-node" }));
      svg.append(s("text", { x: X + 30, y: cy - 2, class: "dg-title" }, r.t));
      wrap(r.d, 52).slice(0, 2).forEach((ln, k) => svg.append(s("text", { x: X + 30, y: cy + 16 + k * 15, class: "dg-desc" }, ln)));
      if (r.k === "stage") svg.append(s("text", { x: W - 12, y: cy + 4, "text-anchor": "end", class: "dg-mono" }, "named rules · Jev · 3 tries"));
    });
    return svg;
  }

  // A saved case as a progress strip: which stages are approved, edited, stopped or pending.
  function strip(stages, status) {
    const n = stages.length, W = 600, step = (W - 60) / Math.max(1, n - 1), cy = 34;
    const svg = s("svg", { viewBox: `0 0 ${W} 92`, class: "dgm strip", role: "img", "aria-label": "Stages of this case: " + stages.map(x => `${num(x.title)} ${x.state}`).join(", ") });
    svg.append(s("path", { d: `M30 ${cy} H${W - 30}`, class: "dg-line" }));
    stages.forEach((x, i) => {
      const cx = 30 + i * step; const k = x.state;
      svg.append(s("circle", { cx, cy, r: 16, class: "dg-node " + k }));
      svg.append(s("text", { x: cx, y: cy + 5, "text-anchor": "middle", class: "dg-num" }, k === "approved" ? "✓" : k === "edited" ? "✎" : k === "stopped" ? "■" : String(i + 1)));
      svg.append(s("text", { x: cx, y: cy + 38, "text-anchor": "middle", class: "dg-cap" }, num(x.title).split(" ")[0]));
      svg.append(s("text", { x: cx, y: cy + 54, "text-anchor": "middle", class: "dg-mono" }, k));
    });
    return svg;
  }
  window.NuryDiagram = { flow, strip };
})();
