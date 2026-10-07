/* Nury shared shell. One header, one tab bar, one theme toggle for every page.
   A page loads /shell.css and this file, sets <body data-nav="home|cases|network"> (or calls NuryShell.setActive), and adds a <main id="main">.
   Text on this page is fixed; nothing here comes from a server. */
(function () {
  const IC = (id, cls) => `<svg class="i${cls ? " " + cls : ""}" aria-hidden="true" focusable="false"><use href="/icons.svg#${id}"/></svg>`;
  const html = `
<a class="skip" href="#main">Skip to content</a>
<header class="top" data-shell="header"><div class="wrap">
  <a class="brand" href="/#/" aria-label="Nury, home">${IC("i-mark")}<b>Nury</b><small>An AI Crisis Response Agent</small></a>
  <nav class="tabs" aria-label="Main">
    <a href="/#/" data-nav="home">${IC("i-lantern")}<span>Home</span></a>
    <a href="/#/cases" data-nav="cases">${IC("i-cases")}<span>Cases</span></a>
    <a href="/network" data-nav="network">${IC("i-network")}<span>Our network</span></a>
  </nav>
  <div class="tools">
    <a class="iconbtn howlink" id="imp-link" href="/improvement" data-nav="improve" aria-label="Improvement">${IC("i-gate")}<span class="lbl">Improvement</span></a>
    <a class="iconbtn howlink" id="ops-link" href="/observability" data-nav="ops" aria-label="Observability">${IC("i-progress")}<span class="lbl">Observability</span></a>
    <a class="iconbtn howlink" id="how-link" href="/how-it-was-built" data-nav="how" aria-label="How this was built">${IC("i-build")}<span class="lbl">How this was built</span></a>
    <button class="iconbtn" id="theme" type="button" aria-pressed="false"></button>
  </div>
</div></header>`;
  document.body.insertAdjacentHTML("afterbegin", html);

  const root = document.documentElement, btn = document.getElementById("theme");
  function paint() {
    const light = root.dataset.theme === "light";
    btn.setAttribute("aria-pressed", String(light));
    btn.setAttribute("aria-label", light ? "Day mode. Switch to Night" : "Night mode. Switch to Day");
    btn.innerHTML = IC(light ? "i-sun" : "i-moon");
  }
  function setTheme(t) { root.dataset.theme = t === "light" ? "light" : "dark"; try { localStorage.setItem("nury-theme", root.dataset.theme); } catch (e) {} paint(); }
  btn.onclick = () => setTheme(root.dataset.theme === "light" ? "dark" : "light");
  paint();

  function setActive(name) {
    document.querySelectorAll("header [data-nav]").forEach(a => {
      if (a.dataset.nav === name) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
  }
  setActive(document.body.dataset.nav || "");
  // The consent note grows a fifth sentence only when feedback capture is on (it is then true). Same text on every page.
  fetch("/api/features").then(r => r.json()).then(f => {
    if (!f || !f.feedback || !f.consent_sentence) return;
    document.querySelectorAll("[data-consent]").forEach(n => { if (!n.dataset.fb) { n.dataset.fb = "1"; n.textContent = n.textContent.trim() + " " + f.consent_sentence; } });
  }).catch(() => {});
  window.NuryShell = { setActive, setTheme, paint };
})();
