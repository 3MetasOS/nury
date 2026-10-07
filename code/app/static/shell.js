/* Nury shared shell. ONE header, ONE footer, one theme switch and the hand-written notes for every page.
   A page loads /shell.css and this file, sets <body data-nav="home|cases|network|how|ops|improve"> (or calls NuryShell.setActive) and adds <main id="main">.
   Text here is fixed; nothing in the header or footer comes from a server. */
(function () {
  const IC = (id, cls) => `<svg class="i${cls ? " " + cls : ""}" aria-hidden="true" focusable="false"><use href="/icons.svg#${id}"/></svg>`;
  const root = document.documentElement;

  const header = `
<a class="skip" href="#main">Skip to content</a>
<header class="top" data-shell="header"><div class="wrap">
  <a class="brand" href="/#/" aria-label="Nury, An AI Crisis Response Agent, home"><span class="lk">${IC("i-mark")}<b>Nury</b></span><span class="tg">An AI Crisis Response Agent</span></a>
  <nav class="tabs" aria-label="Main">
    <a href="/#/" data-nav="home">${IC("i-lantern")}<span>Home</span></a>
    <a href="/#/cases" data-nav="cases">${IC("i-cases")}<span>Cases</span></a>
    <a href="/network" data-nav="network">${IC("i-network")}<span>Network</span></a>
  </nav>
  <div class="tools"><button class="iconbtn" id="theme" type="button" aria-pressed="false"></button></div>
</div></header>`;
  document.body.insertAdjacentHTML("afterbegin", header);

  // The footer is the same component on every page. The three pages for judges and reviewers live here, not in the header.
  const footer = `
<footer class="sitefoot" data-shell="footer"><div class="wrap">
  <div class="lockup" data-lockup><span class="lk">${IC("i-mark")}<b>Nury</b></span><span class="tg">An AI Crisis Response Agent</span></div>
  <div class="fj">
    <div class="flrow"><p class="fl mono">For judges and reviewers</p></div>
    <nav class="fnav" aria-label="For judges and reviewers">
      <a href="/how-it-was-built" data-nav="how">How this was built</a>
      <a href="/observability" data-nav="ops">Observability</a>
      <a href="/self-improvement" data-nav="improve">Self-improvement</a>
      <a href="/what-did-not-work" data-nav="wdnw">What did not work</a>
      <a href="/economics" data-nav="economics">Economics</a>
      <a href="/pattern" data-nav="pattern">The pattern</a>
      <a href="/standards" data-nav="standards">Standards we use</a>
    </nav>
  </div>
  <div class="fm">
    <p class="fl mono ft">How it was made</p>
    <div class="fb"><p class="fl mono">Writer</p><p>Claude Sonnet 4.6, through Gloo AI Studio's guarded endpoint, with Gloo's guardrails.</p></div>
    <div class="fb"><p class="fl mono">Checks</p><p><span id="fm-checks"></span>named rules and a safety floor on every draft, plus a second check by Jev, from TypeSafe. <a href="/how-it-was-built#honest-limits-in-one-place">See the limits</a></p></div>
    <div class="fb"><p class="fl mono">Outside review</p><p>Before release, AI models from other makers read sample drafts and flagged problems. Their notes are advice to us. They are not part of the app. <a href="/how-it-was-built#who-does-what">Details</a></p></div>
    <div class="fb" id="fm-build" hidden><p class="fl mono">Build</p><p><span></span></p></div>
  </div>
  <p class="prov">Built in Boulder, Colorado, during the Gloo AI Hackathon, October 6 to 8, 2026. <a href="/build-log">See the build log</a></p>
  <p class="fine">Nury is an AI assistant. It is not a lawyer, doctor, pastor, counselor or therapist. Nury never sends anything. You do.</p>
</div></footer>`;

  const btn = document.getElementById("theme");
  function paint() {
    const light = root.dataset.theme === "light";
    btn.setAttribute("aria-pressed", String(light));
    btn.setAttribute("aria-label", light ? "Day mode. Switch to Night" : "Night mode. Switch to Day");
    btn.innerHTML = IC(light ? "i-sun" : "i-moon");
  }
  function setTheme(t) { root.dataset.theme = t === "light" ? "light" : "dark"; try { localStorage.setItem("nury-theme", root.dataset.theme); } catch (e) {} paint(); }
  btn.onclick = () => setTheme(root.dataset.theme === "light" ? "dark" : "light");
  paint();

  // ---- hand-written notes: decoration only. aria-hidden; the real label always carries the same information. ----
  const ARROWS = {
    up: '<path d="M6 27 C10 17 14 11 22 4 M22 4 L14 6 M22 4 L22 12"/>',
    down: '<path d="M6 3 C10 13 14 19 22 26 M22 26 L14 24 M22 26 L22 18"/>',
    left: '<path d="M30 15 C22 7 12 8 4 15 M4 15 L12 9 M4 15 L13 18"/>',
    right: '<path d="M4 15 C12 7 22 8 30 15 M30 15 L22 9 M30 15 L21 18"/>',
  };
  function noteEl(text, dir, rot) {
    const n = document.createElement("span");
    n.className = "hnote"; n.setAttribute("aria-hidden", "true"); n.style.setProperty("--rot", rot + "deg");
    n.innerHTML = `<svg class="hn-a" viewBox="0 0 34 30" focusable="false">${ARROWS[dir] || ARROWS.up}</svg><span class="hn-t"></span>`;
    n.querySelector(".hn-t").textContent = "(" + text + ")";
    return n;
  }
  // Any element with data-note="text" gets one note after it (data-note-at="before" puts it before, "in" puts it inside).
  // data-arrow = up | down | left | right (where the arrow points), data-rot = degrees. One note, one text, at every width.
  function notes(scope) {
    (scope || document).querySelectorAll("[data-note]").forEach(el => {
      if (el.dataset.noted) return;
      el.dataset.noted = "1";
      const n = noteEl(el.dataset.note, el.dataset.arrow || "up", el.dataset.rot || "-1.5");
      if (el.dataset.noteAt === "in") el.appendChild(n);
      else if (el.dataset.noteAt === "before") el.parentNode.insertBefore(n, el); else el.parentNode.insertBefore(n, el.nextSibling);
    });
  }
  function setActive(name) {
    document.querySelectorAll("[data-shell] [data-nav]").forEach(a => {
      if (a.dataset.nav === name) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
  }
  setActive(document.body.dataset.nav || "");

  // The footer rises in once, when it first comes into view. JS applies the hidden state, so a page without JS shows the footer as it is.
  function revealFooter() {
    const f = document.querySelector(".sitefoot");
    if (!f || !("IntersectionObserver" in window) || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const parts = [...f.querySelectorAll(".lockup, .fj, .fm, .prov, .fine")];
    parts.forEach((p, i) => p.style.setProperty("--fd", (i < 3 ? i * 80 : 240 + (i - 2) * 80) + "ms"));
    f.classList.add("rv");
    let done = false;
    const show = () => { if (done) return; done = true; f.classList.add("rv-in"); io.disconnect(); setTimeout(() => f.classList.remove("rv"), 1200); };
    const io = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) show(); }, { threshold: 0.15 });
    io.observe(f);
    setTimeout(show, 4000);   // a page that never scrolls the footer in still shows it
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.body.insertAdjacentHTML("beforeend", footer);
    const fn = document.querySelector(".sitefoot .fl");
    fn.dataset.note = "psst, for judges"; fn.dataset.arrow = "down"; fn.dataset.rot = "-2";
    notes(); setActive(document.body.dataset.nav || (window.__navNow || ""));
    revealFooter();
    // The build line and the test counts come from the server (read once at its start). A line with no data stays hidden.
    fetch("/api/build").then(r => r.json()).then(b => {
      const parts = [];
      if (b && b.commit) parts.push(b.commit);
      if (b && b.date) parts.push(b.date);
      if (b && b.tests) parts.push(b.tests.product + " product tests, " + b.tests.evaluation + " evaluation tests.");
      if (parts.length) { const li = document.getElementById("fm-build"); li.querySelector("span").textContent = parts.join(" \u00b7 "); li.hidden = false; }
    }).catch(() => {});
  });

  // The consent note grows a fifth sentence only when feedback capture is on (it is then true). Same text on every page.
  fetch("/api/features").then(r => r.json()).then(f => {
    { const c = document.getElementById("fm-checks"); if (c && f && f.named_checks) c.textContent = f.named_checks + " "; }
    if (!f || !f.feedback || !f.consent_sentence) return;
    document.querySelectorAll("[data-consent]").forEach(n => { if (!n.dataset.fb) { n.dataset.fb = "1"; n.textContent = n.textContent.trim() + " " + f.consent_sentence; } });
  }).catch(() => {});
  window.NuryShell = { setActive, setTheme, paint, notes, lockup: () => `<div class="lockup" data-lockup><span class="lk">${IC("i-mark")}<b>Nury</b></span><span class="tg">An AI Crisis Response Agent</span></div>` };
})();
