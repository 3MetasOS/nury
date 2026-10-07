/* Builds the print copy from the data the server put in window.__PRINT__ and renders it with the same code as the final page.
   Every sentence on the page is a saved stage text, a fixed heading, or the audit facts below. Nothing is invented. */
(function () {
  const P = window.__PRINT__ || {};
  const el = (t, c, x) => { const e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; };
  const IDS = { "01-triage.md": "triage", "02-rights.md": "rights", "03-attorney.md": "attorney", "04-checklist.md": "checklist", "05-pastoral.md": "pastoral" };

  function stageFromPage(name, text, edited) {
    let t = text.replace(/\r/g, "");
    const title = ((t.match(/^#\s*(?:\d+\.\s*)?(.+)$/m) || [])[1] || name).trim();
    t = t.replace(/^#\s.*\n+/, "").replace(/^Status:[^\n]*\n+/, "");
    t = t.replace(/\n---\n[\s\S]*$/, "").trim();                       // the navigation links
    let disclaimer = "";
    const m = t.match(/\n*(Nury is an AI assistant[\s\S]*)$/);
    if (m) { disclaimer = m[1].trim(); t = t.slice(0, m.index).trim(); }
    return { id: IDS[name], title, final: t, disclaimer, status: edited.includes(IDS[name]) ? "edited" : "approved" };
  }

  let s, lang, auditSrc;
  if (P.kind === "session") {
    s = P.data; lang = s.language || "en"; auditSrc = (s.stages || []);
    s.playbook = { id: (s.playbook && s.playbook.id) || "", title: P.title || (s.playbook && s.playbook.title) || "" };
    s.date = P.date;
  } else {
    const c = P.data, meta = c.meta || {}, pages = c.pages || {};
    lang = meta.language || "en";
    const edited = meta.edited || [];
    const stages = Object.keys(pages).filter(k => IDS[k]).sort().map(k => stageFromPage(k, pages[k], edited));
    const log = /youversion/i.test(pages["log.md"] || "") ? [{ kind: "scripture", provider: "youversion" }] : [];
    s = { playbook: { id: meta.playbook, title: c.playbook_title || P.title }, language: lang, stages, log, date: P.date };
    auditSrc = stages;
  }
  const MARK = (document.querySelector(".runhead svg") || { innerHTML: "" }).innerHTML;
  window.NuryShell = { lockup: () => '<div class="lockup"><span class="lk"><svg class="i" viewBox="0 0 64 64" aria-hidden="true">' + MARK + '</svg><b>Nury</b></span><span class="tg">An AI Crisis Response Agent</span></div>' };
  const fam = P.copy === "family";
  const root = document.getElementById("final-root");
  root.dataset.fam = fam && lang !== "en" ? "1" : "0";
  s.language = fam ? lang : "en";
  NuryFinal.render(s);
  // Key facts in the family's own words (the labels already are).
  if (fam && lang !== "en") document.querySelectorAll("#final-head .keyfacts dd").forEach(d => {
    const t = d.textContent.trim();
    if (t === "Spanish") d.textContent = "Espa\u00f1ol"; else if (t === "Portuguese") d.textContent = "Portugu\u00eas"; else if (t === "French") d.textContent = "Fran\u00e7ais";
    else if (/^[A-Z][a-z]+ \d{1,2}, \d{4}$/.test(t)) d.textContent = new Date(P.date).toLocaleDateString(lang + "-US", { year: "numeric", month: "long", day: "numeric" });
  });
  // The final page shows four points and folds the rest; a printed copy gives all of them once.
  { const r = auditSrc.find(x => x.id === "rights" || x.id === "info"); const sec = document.getElementById("fp-1");
    if (r && sec) {
      const all = NuryFinal.parse.bullets(r.final);
      const rest = r.final.split("\n").filter(l => l.trim() && !/^\s*-\s+/.test(l)).map(l => l.trim());
      sec.querySelectorAll("ul.lines, details.full").forEach(n => n.remove());
      if (all.length) { const ul = el("ul", "lines"); all.forEach(b => { const li = el("li"); li.append(el("span", "ltxt", b.text)); if (b.cite) li.append(el("span", "cite mono", b.cite)); ul.append(li); }); sec.append(ul); }
      rest.forEach(t => sec.append(el("p", "plain", t)));
    } }
  document.querySelectorAll("details").forEach(d => d.open = true);
  document.querySelectorAll("#final-body .edmark").forEach(m => { if (fam && lang !== "en") m.textContent = "Editado por el pastor"; });

  // The pastor copy adds the audit summary: what was approved or edited, and the sources the rights brief cites.
  if (!fam) {
    const a = el("section", "fp-sec audit long");
    a.append(el("h2", null, "Audit summary"));
    a.append(el("p", "meta", `Case ${((P.data.meta || {}).id) || ""}. Saved ${new Date(P.date).toLocaleString("en-US", { dateStyle: "long", timeStyle: "short" })}. Family language: ${lang === "es" ? "Spanish" : lang === "en" ? "English" : lang}.`));
    const tb = el("table"); const th = el("tr"); ["Stage", "Result"].forEach(h => th.append(el("th", null, h))); tb.append(th);
    auditSrc.forEach(x => { const r = el("tr"); r.append(el("td", null, x.title), el("td", null, x.status === "edited" ? "Edited by the pastor" : "Approved by the pastor")); tb.append(r); });
    a.append(tb);
    const rights = auditSrc.find(x => x.id === "rights" || x.id === "info");
    const cites = [...new Set(NuryFinal.parse.bullets(rights && rights.final).map(b => b.cite).filter(Boolean))];
    a.append(el("h3", null, "Sources cited in the rights brief"));
    a.querySelector("h3").style.cssText = "font-size:12pt;margin:12pt 0 4pt";
    if (cites.length) { const ul = el("ul"); cites.forEach(c => ul.append(el("li", null, c))); a.append(ul); }
    else a.append(el("p", "meta", "The rights brief lists its sources inside each point."));
    if (lang !== "en") a.append(el("p", "meta", "The stage texts in this copy are in the family's language, as the family received them."));
    document.getElementById("audit").append(a);
  }

  // Running header and footer: @page margin boxes (Chrome 131 or later). Strings are escaped for CSS.
  const cs = t => '"' + String(t).replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\n/g, " ") + '"';
  const dateTxt = new Date(P.date).toLocaleDateString(fam && lang === "es" ? "es-US" : "en-US", { year: "numeric", month: "long", day: "numeric" });
  const dis = (auditSrc.find(x => x.disclaimer) || {}).disclaimer || "Nury is an AI assistant. It is not a lawyer, pastor, counselor, or therapist. This is general information, not legal advice.";
  const pageWord = fam && lang === "es" ? "Página " : "Page ", ofWord = fam && lang === "es" ? " de " : " of ";
  const st = el("style");
  st.textContent = `@page{@top-left{content:${cs("Nury  ·  " + (s.playbook.title || P.title))};font:500 8.5pt Inter,sans-serif;color:#444;vertical-align:bottom;padding-bottom:6pt}` +
    `@top-right{content:${cs(dateTxt)};font:400 8.5pt Inter,sans-serif;color:#444;vertical-align:bottom;padding-bottom:6pt}` +
    `@bottom-left{content:${cs(dis)};font:400 7pt/1.3 Inter,sans-serif;color:#555;vertical-align:top;padding-top:6pt;width:80%}` +
    `@bottom-right{content:${cs(pageWord)} counter(page) ${cs(ofWord)} counter(pages);font:500 8.5pt Inter,sans-serif;color:#333;vertical-align:top;padding-top:6pt}}`;
  document.head.append(st);
  document.documentElement.lang = fam ? lang : "en";
  const note = document.getElementById("print-note");
  if (P.note) { note.textContent = P.note + "."; note.hidden = false; }
})();
