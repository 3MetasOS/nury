(() => {
  const w = document.getElementById("f").contentWindow;
  return w.eval(`(() => {
    const S = vis(), r = [];
    for (let k = 0; k < S.length; k++) {
      go(k);
      const d = document.documentElement, f = document.querySelector(".foot");
      const fx = getComputedStyle(f).position === "fixed";
      if (d.scrollWidth > innerWidth + 2) r.push((k + 1) + "H");
      if (fx && d.scrollHeight > innerHeight + 2) r.push((k + 1) + "V:" + (d.scrollHeight - innerHeight));
    }
    return innerWidth + "x" + innerHeight + " " + S.length + " slides, problems: " + (r.join(" ") || "none");
  })()`);
})()
