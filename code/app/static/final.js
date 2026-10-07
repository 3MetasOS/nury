/* The final package page: one clear page the pastor can hand to the family. Built from the approved stage texts only.
   Nothing here invents content: every sentence on the page is a stage text, a fixed heading, or the pastor's own name.
   Server text goes in with textContent. */
(function () {
  const $ = id => document.getElementById(id);
  const el = (t, c, x) => { const e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; };
  // Fixed headings (interface words, not content). The family copy uses the family's language when we have it.
  const H = {
    en: { happening: "What is happening", next: "What to do next", spirit: "Spiritual support", resources: "Resources", tonight: "Tonight", donot: "Do not", docs: "Gather these documents", full: "Read the full brief", more: n => `Show ${n} more`, generic: "Information for the family", prepared: "Prepared by", date: "Date", case: "Case", lang: "Family language", call: "Call", church: "Your church's own list", official: "Official list", national: "National directory", notend: "Listed does not mean recommended.", foot: p => `This was prepared by ${p || "the pastor"} with Nury. It is information, not legal advice.`, footgen: p => `This was prepared by ${p || "the pastor"} with Nury. It is information, not advice.` },
    es: { happening: "Lo que está pasando", next: "Qué hacer ahora", spirit: "Apoyo espiritual", resources: "Recursos", tonight: "Esta noche", donot: "No haga esto", docs: "Reúna estos documentos", full: "Leer el resumen completo", more: n => `Ver ${n} más`, generic: "Información para la familia", prepared: "Preparado por", date: "Fecha", case: "Caso", lang: "Idioma de la familia", call: "Llamar", church: "Lista de su iglesia", official: "Lista oficial", national: "Directorio nacional", notend: "Estar en la lista no significa que se recomiende.", foot: p => `Esto fue preparado por ${p || "el pastor"} con Nury. Es información, no consejo legal.`, footgen: p => `Esto fue preparado por ${p || "el pastor"} con Nury. Es información, no consejo.` },
  };
  const tr = lang => H[lang] || H.en;
  const stage = (s, id) => (s.stages || []).find(x => x.id === id);
  const stageBy = (s, ids) => ids.map(i => stage(s, i)).find(Boolean);

  function bullets(text) {
    return (text || "").split("\n").filter(l => /^\s*-\s+/.test(l)).map(l => {
      let t = l.replace(/^\s*-\s+/, "").trim(), cite = "";
      const m = t.match(/\s*\(([^()]{3,80})\)\s*$/);
      if (m) { cite = m[1]; t = t.slice(0, m.index).trim(); }
      return { text: t, cite };
    });
  }
  function checklist(text) {
    const out = { tonight: [], donot: [], docs: [], titles: {} };
    let cur = null, group = null;
    for (const raw of (text || "").split("\n")) {
      const line = raw.trim(); let m;
      if ((m = line.match(/^(DO TONIGHT|DO NOT DO|GATHER THESE DOCUMENTS)\b\s*(?:\/\s*(.+))?$/i))) {
        const k = /TONIGHT/i.test(m[1]) ? "tonight" : /NOT/i.test(m[1]) ? "donot" : "docs";
        cur = k; group = null; out.titles[k] = { en: m[1], fam: (m[2] || "").trim() }; continue;
      }
      if (line === "---") { cur = null; continue; }
      if (!cur || !line) continue;
      if (cur === "docs") {
        if (/^church contacts/i.test(line)) { group = "skip"; continue; }
        if (/:$/.test(line)) { group = line.replace(/:$/, ""); continue; }
        if (/^-\s+/.test(line) && group !== "skip") out.docs.push({ group, text: line.replace(/^-\s+/, "") });
      } else if ((m = line.match(/^\d+\.\s+(.*)$/))) out[cur].push(m[1]);
    }
    return out;
  }
  function phoneFmt(p) {
    const d = p.replace(/\D/g, "");
    if (d.length === 11 && d[0] === "1") return { show: `1-${d.slice(1, 4)}-${d.slice(4, 7)}-${d.slice(7)}`, tel: "+" + d };
    if (d.length === 10) return { show: `${d.slice(0, 3)}-${d.slice(3, 6)}-${d.slice(6)}`, tel: "+1" + d };
    return { show: p.trim(), tel: d ? "+" + d : "" };
  }
  function contacts(text) {
    const groups = []; let g = null, c = null;
    const PH = /\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}/g, URL = /https?:\/\/[^\s)|]+/g, MAIL = /[\w.+-]+@[\w-]+\.[\w.-]+/g;
    const flush = () => { if (c && g) { g.items.push(c); } c = null; };
    for (const raw of (text || "").split("\n")) {
      const line = raw.replace(/\s+$/, "");
      let m;
      if (/^\*\*[^*]+\*\*$/.test(line.trim()) && !/^\s*-/.test(line)) { flush(); g = { title: line.trim().slice(2, -2), note: "", items: [] }; if (!/before you call/i.test(g.title)) groups.push(g); else g = null; continue; }
      if (!g) continue;
      if ((m = line.trim().match(/^\*([^*].*)\*$/))) { g.note = m[1]; continue; }
      if (line.trim() && !/^-\s/.test(line.trim()) && !c && !g.items.length && !g.note) { g.note = line.trim(); continue; }
      if (/^\s*---\s*$/.test(line)) { flush(); continue; }
      if ((m = line.match(/^-\s+\*\*([^*]+)\*\*(.*)$/))) {
        flush(); c = { name: m[1].replace(/:$/, "").trim(), rest: m[2], phones: [], urls: [], mails: [] }; c.rest += " "; 
      } else if (c && line.trim() && !/^-\s/.test(line.trim())) c.rest += " " + line.trim();
      else if (!line.trim()) flush();
      if (c) { /* collected at flush time */ }
    }
    flush();
    groups.forEach(gr => gr.items.forEach(it => {
      const r = it.rest;
      it.phones = (r.match(PH) || []).map(p => p.trim()); it.urls = (r.match(URL) || []); it.mails = (r.match(MAIL) || []);
      let d = r.replace(PH, " ").replace(URL, " ").replace(MAIL, " ").replace(/\|/g, " ").replace(/\*/g, "").replace(/\s[\/\u2014\u2013-]\s/g, " ").replace(/^\s*:\s*/, "").replace(/\s+/g, " ").trim();
      d = d.replace(/^\(([^)]*)\)\s*:?\s*$/, "$1").replace(/[:\u2014\u2013-]+\s*$/, "").replace(/^\(([^)]*)\)$/, "$1").trim();
      it.desc = d; delete it.rest;
    }));
    return groups.filter(x => x.items.length);
  }
  function pastoral(text) {
    const lines = (text || "").split("\n"); const msg = [], why = []; let verse = null, i = 0;
    for (; i < lines.length; i++) {
      if (/^«.+»\s*$/.test(lines[i].trim())) { verse = { text: lines[i].trim(), ref: "" }; if (/^[—–-]\s?.+/.test((lines[i + 1] || "").trim())) { verse.ref = lines[i + 1].trim(); i++; } i++; break; }
      msg.push(lines[i]);
    }
    for (; i < lines.length; i++) why.push(lines[i]);
    const j = a => a.join("\n").trim();
    return { message: j(msg), verse, why: j(why) };
  }
  const para = (t, c) => { const d = el("div", c); (t || "").split(/\n{2,}/).forEach(p => { if (p.trim()) d.append(el("p", null, p.trim())); }); return d; };
  const h2 = (en, fam, famOn) => { const h = el("h2"); h.append(el("span", "h-en", en)); if (fam && fam !== en) { h.append(el("span", "h-fam", fam)); } return h; };

  function key() { try { return localStorage.getItem("nury-pastor") || ""; } catch (e) { return ""; } }

  // Plain text of the whole package, for Copy all and Download. Every stage as approved, with its disclaimer.
  function text(s) {
    return (s.stages || []).map(x => x.title + "\n\n" + x.final + "\n\n" + x.disclaimer).join("\n\n----------\n\n");
  }

  function render(s) {
    const root = $("final-body"), headRoot = $("final-head"); root.replaceChildren(); headRoot.replaceChildren();
    const lang = s.language || "en", T = tr(lang), E = H.en, fam = lang !== "en";
    const tri = stage(s, "triage"), rights = stageBy(s, ["rights", "info"]), res = stageBy(s, ["attorney", "resources"]), chk = stage(s, "checklist"), pas = stage(s, "pastoral");
    const edited = id => { const x = stage(s, id); return x && x.status === "edited"; };
    const mark = (id) => edited(id) ? el("span", "edmark", "Edited by the pastor") : null;
    const pre = $("kf-prefill");  // not used
    // ---- 0 headline and key facts
    const head = el("header", "fp-head");
    { const w0 = el("div", "fp-lock"); w0.innerHTML = (window.NuryShell && NuryShell.lockup) ? NuryShell.lockup() : ""; head.append(w0); }
    const sit = ((tri && tri.final || "").match(/SITUATION:\s*(.+)/i) || [])[1] || "";
    const first = sit.split(/(?<=[.!?])\s/)[0].trim();
    const h1 = el("h1", "fp-h1"); h1.id = "fp-h1"; h1.tabIndex = -1;
    h1.dataset.print = fam ? T.generic : "";
    const short = first.length > 72 ? first.slice(0, first.lastIndexOf(" ", 70)).replace(/[,;:]$/, "") + "\u2026" : first;   // the headline stays short; the full sentence is in the case summary
    h1.textContent = short ? `${short} Here is what the family can do tonight.` : "Here is what the family can do tonight.";
    head.append(h1);
    const kf = el("dl", "keyfacts");
    const bil = (en, fm) => { const f = document.createDocumentFragment(); f.append(el("span", "g-en", en)); if (fm) f.append(el("span", "g-fam", fm)); return f; };
    const row = (k, v, kf2) => { const d = el("div"); const dt = el("dt", "mono"); dt.append(bil(k, kf2)); d.append(dt); const dd = el("dd"); if (typeof v === "string") dd.textContent = v; else dd.append(v); d.append(dd); kf.append(d); };
    row(E.case, s.playbook ? s.playbook.title : "", fam ? T.case : "");
    row(E.date, (s.date ? new Date(s.date) : new Date()).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" }), fam ? T.date : "");
    const inp = el("input"); inp.id = "kf-pastor"; inp.type = "text"; inp.placeholder = "Your name"; inp.autocomplete = "off"; inp.setAttribute("aria-label", "Pastor's name, printed on the family copy"); inp.value = key();
    const pn = el("span", "pn-print"); pn.id = "kf-pastor-print";
    inp.oninput = () => { try { localStorage.setItem("nury-pastor", inp.value); } catch (e) {} pn.textContent = inp.value; foot.textContent = T.foot(inp.value.trim()); };
    pn.textContent = inp.value;
    const w = el("span", "pn-wrap"); w.append(inp, pn);
    row(E.prepared, w, fam ? T.prepared : "");
    if (s.replay) row("Mode", "Recorded run", fam ? "Modo" : "");
    row(E.lang, fam ? ({ es: "Spanish", pt: "Portuguese", fr: "French" }[lang] || lang) : "English", fam ? T.lang : "");
    head.append(kf); headRoot.append(head);
    // ---- 1 what is happening
    const b = bullets(rights && rights.final);
    const s1 = el("section", "fp-sec"); s1.id = "fp-1"; s1.setAttribute("aria-labelledby", "fp-1h");
    const t1 = h2(E.happening, fam ? T.happening : ""); t1.id = "fp-1h"; s1.append(t1);
    t1.dataset.note = "read this before you call"; t1.dataset.arrow = "up"; t1.dataset.rot = "-1.5";
    if (rights && edited(rights.id)) s1.append(mark(rights.id));
    const ul = el("ul", "lines"); b.slice(0, 4).forEach(x => { const li = el("li"); li.append(el("span", "ltxt", x.text)); if (x.cite) li.append(el("span", "cite mono", x.cite)); ul.append(li); });
    if (b.length) s1.append(ul);
    const full = el("details", "full"); full.append(el("summary", null, fam ? T.full : E.full));
    full.append(b.length > 4 || !b.length ? para(rights && rights.final, "fullbody") : (() => { const u = el("ul", "lines"); b.slice(4).forEach(x => { const li = el("li"); li.append(el("span", "ltxt", x.text)); if (x.cite) li.append(el("span", "cite mono", x.cite)); u.append(li); }); return u; })());
    if (b.length > 4 || !b.length) { full.querySelector(".fullbody") && null; }
    s1.append(full); root.append(s1);
    // ---- 2 what to do next
    const c = checklist(chk && chk.final);
    const s2 = el("section", "fp-sec"); s2.id = "fp-2"; s2.setAttribute("aria-labelledby", "fp-2h");
    const t2 = h2(E.next, fam ? T.next : ""); t2.id = "fp-2h"; s2.append(t2);
    if (chk && edited("checklist")) s2.append(mark("checklist"));
    if (c.tonight.length) {
      const g = el("div", "tgroup"); { const p = el("p", "mono grp"); p.append(bil(E.tonight, fam ? T.tonight : "")); g.append(p); }
      const ol = el("ol", "todo"); c.tonight.forEach(t => { const li = el("li"); const m = t.match(/^([A-ZÁÉÍÓÚÑ][^\s.,:;]*)(\s.*)$/); if (m) { const v = el("strong", null, m[1]); li.append(v, document.createTextNode(m[2])); } else li.textContent = t; ol.append(li); });
      g.append(ol); s2.append(g);
    }
    if (c.donot.length) {
      const box = el("div", "donot"); { const p = el("p", "mono grp"); p.append(bil(E.donot, fam ? T.donot : "")); box.append(p); }
      const ul2 = el("ul"); c.donot.forEach(t => ul2.append(el("li", null, t))); box.append(ul2); s2.append(box);
    }
    if (c.docs.length) {
      const d = el("div", "docs"); { const p = el("p", "mono grp"); p.append(bil(E.docs, fam ? T.docs : "")); d.append(p); }
      let lastG = null, ulx = null;
      c.docs.forEach((x, i) => { if (x.group !== lastG || !ulx) { if (x.group) d.append(el("p", "dg", x.group)); ulx = el("ul", "ck"); d.append(ulx); lastG = x.group; }
        const li = el("li"); const id = "ck" + i; const cb = el("input"); cb.type = "checkbox"; cb.id = id; const lb = el("label", null, x.text); lb.htmlFor = id; li.append(cb, lb); ulx.append(li); });
      s2.append(d);
    }
    if (!c.tonight.length && !c.donot.length && !c.docs.length && chk) s2.append(para(chk.final, "plain"));
    root.append(s2);
    // ---- 3 spiritual support
    const p = pastoral(pas && pas.final);
    const s3 = el("section", "fp-sec spirit"); s3.id = "fp-3"; s3.setAttribute("aria-labelledby", "fp-3h");
    const lant = document.createElementNS("http://www.w3.org/2000/svg", "svg"); lant.setAttribute("class", "i lant"); lant.setAttribute("aria-hidden", "true"); lant.innerHTML = '<use href="/icons.svg#i-mark"/>';
    const t3 = h2(E.spirit, fam ? T.spirit : ""); t3.id = "fp-3h"; t3.prepend(lant); s3.append(t3);
    t3.dataset.note = "this part is for them, from you"; t3.dataset.arrow = "up"; t3.dataset.rot = "-1.5";
    if (pas && edited("pastoral")) s3.append(mark("pastoral"));
    if (p.message) s3.append(para(p.message, "pmsg"));
    if (p.verse) {
      const v = el("blockquote", "verse"); v.append(el("p", "vt", p.verse.text)); if (p.verse.ref) v.append(el("p", "vr mono", p.verse.ref)); s3.append(v);
      const prov = ((s.log || []).filter(e => e.kind === "scripture").pop() || {}).provider;
      const srcTxt = prov === "youversion" ? "YouVersion" : "the church's verified verse bank";
      const vs = el("p", "vsrc"); vs.append(el("span", "g-en", `The system chose this verse from ${srcTxt} and checked it matches the source word for word. The pastor approved it.`));
      if (fam && lang === "es") vs.append(el("span", "g-fam", `El sistema eligió este versículo ${prov === "youversion" ? "de YouVersion" : "del banco de versículos verificado de la iglesia"} y comprobó que coincide palabra por palabra con la fuente. El pastor lo aprobó.`));
      s3.append(vs);
    }
    if (p.why) s3.append(para(p.why, "pwhy"));
    root.append(s3);
    // ---- 4 resources
    const gs = contacts(res && res.final);
    const s4 = el("section", "fp-sec"); s4.id = "fp-4"; s4.setAttribute("aria-labelledby", "fp-4h");
    const t4 = h2(E.resources, fam ? T.resources : ""); t4.id = "fp-4h"; s4.append(t4);
    if (res && edited(res.id)) s4.append(mark(res.id));
    const label = g => /iglesia|church/i.test(g.title) ? T.church : /departamento|justice|doj|oficial/i.test(g.title) ? T.official : T.national;
    const cards = []; gs.forEach(g => g.items.forEach(it => cards.push({ g, it })));
    const list = el("ul", "cards");
    const card = ({ g, it }) => {
      const li = el("li", "rc"); li.append(el("span", "rtag mono", label(g)));
      li.append(el("h3", "rn", it.name)); if (it.desc) li.append(el("p", "rd", it.desc));
      const act = el("div", "ract");
      it.phones.slice(0, 1).forEach(ph => { const f = phoneFmt(ph); const a = el("a", "call", `${T.call} ${f.show}`); a.href = "tel:" + f.tel; a.dataset.phone = f.show; act.append(a); });
      if (!it.phones.length && it.mails[0]) { const a = el("a", "call alt", it.mails[0]); a.href = "mailto:" + it.mails[0]; act.append(a); }
      if (act.children.length) li.append(act);
      const small = el("p", "rsmall");
      it.phones.slice(1).forEach(ph => { const f = phoneFmt(ph); const a = el("a", null, f.show); a.href = "tel:" + f.tel; small.append(a, document.createTextNode(" ")); });
      it.urls.slice(0, 1).forEach(u => { const a = el("a", null, u.replace(/^https?:\/\//, "").replace(/\/$/, "")); a.href = u; a.rel = "noopener"; a.target = "_blank"; small.append(a); });
      if (it.phones.length && it.mails[0]) { const a = el("a", null, it.mails[0]); a.href = "mailto:" + it.mails[0]; small.append(document.createTextNode(" "), a); }
      if (small.childNodes.length) li.append(small);
      return li;
    };
    cards.slice(0, 5).forEach(x => list.append(card(x)));
    s4.append(list);
    if (cards.length > 5) {
      const more = el("details", "more"); more.append(el("summary", null, T.more(cards.length - 5)));
      const l2 = el("ul", "cards"); cards.slice(5).forEach(x => l2.append(card(x))); more.append(l2); s4.append(more);
    }
    [...new Set(gs.map(g => g.note).filter(Boolean))].forEach(n => s4.append(el("p", "rnote", n)));
    if (!cards.length && res) s4.append(para(res.final, "plain"));
    root.append(s4);
    // ---- foot
    const foot = el("footer", "fp-foot"); foot.id = "fp-foot";
    foot.textContent = (c.tonight.length || b.length) ? T.foot(inp.value.trim()) : T.footgen(inp.value.trim());
    root.append(foot);
    if (s.replay) { const rc = el("p", "fp-rec"); rc.append(el("span", "g-en", "Recorded run. The words were written by the model earlier; the checks ran live.")); if (fam && lang === "es") rc.append(el("span", "g-fam", "Ejecución grabada. El modelo escribió las palabras antes; las comprobaciones se hicieron en vivo.")); root.append(rc); }
    const dis = (rights && rights.disclaimer) || (tri && tri.disclaimer) || "";
    if (dis) root.append(el("p", "fp-disc", dis));
    if (window.NuryShell && NuryShell.notes) { NuryShell.notes(root); }
    return { sections: ["fp-1", "fp-2", "fp-3", "fp-4"], contacts: cards.length };
  }

  function download(name, textBody) {
    // a BOM so Windows Notepad reads the Spanish accents as UTF-8; attached to the page and revoked later so the browser finishes the save
    const blob = new Blob(["﻿" + textBody], { type: "text/plain;charset=utf-8" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = name; a.style.display = "none";
    document.body.append(a); a.click(); setTimeout(() => { a.remove(); URL.revokeObjectURL(a.href); }, 4000);
  }
  window.NuryFinal = { render, text, download, parse: { bullets, checklist, contacts, pastoral, phoneFmt } };
})();
