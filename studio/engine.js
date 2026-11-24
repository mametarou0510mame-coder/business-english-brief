// BEB studio engine: a deterministic timeline. Python sets the timeline, then calls seek(t) for every frame.
const E = {
  clamp: (x, a = 0, b = 1) => Math.max(a, Math.min(b, x)),
  ease: p => { p = E.clamp(p); return 1 - Math.pow(1 - p, 3); },
  easeIO: p => { p = E.clamp(p); return p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2; },
  back: p => { p = E.clamp(p); const c = 1.7; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); },
  lerp: (a, b, p) => a + (b - a) * p,
  ns: "http://www.w3.org/2000/svg",
  el(tag, attrs = {}, parent, html) {
    const svgTags = ["svg", "g", "path", "polygon", "line", "circle", "rect", "text", "ellipse", "defs", "linearGradient", "stop", "filter", "feGaussianBlur", "polyline"];
    const n = svgTags.includes(tag) ? document.createElementNS(E.ns, tag) : document.createElement(tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (html !== undefined) n.innerHTML = html;
    if (parent) parent.appendChild(n);
    return n;
  },
  fmt: (v, d = 0) => v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d }),
};

const SCENES = {};       // type -> (root, props) => ({ update(ts, ctx) })
let TL = null, INST = [];

function esc(s) { return s.replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c])); }
function markup(s, hl) {
  let h = esc(s || "");
  for (const k of (hl || [])) if (k) h = h.replace(esc(k), `<span class="hl">${esc(k)}</span>`);
  return h;
}

window.loadTimeline = function (tl) {
  TL = tl;
  const world = document.getElementById("world");
  world.innerHTML = "";
  INST = tl.scenes.map(sc => {
    const root = E.el("div", { class: "layer" }, world);
    root.style.opacity = 0;
    const make = SCENES[sc.vis.type];
    if (!make) throw new Error("unknown scene " + sc.vis.type);
    return { sc, root, comp: make(root, sc.vis) };
  });
  return tl.total;
};

window.seek = function (t) {
  const subsEn = document.getElementById("en"), subsJp = document.getElementById("jp");
  let shown = null;
  for (const it of INST) {
    const { sc, root, comp } = it;
    const active = t >= sc.start - 0.0001 && t < sc.end;
    if (!active) { root.style.opacity = 0; root.style.visibility = "hidden"; continue; }
    root.style.visibility = "visible";
    const ts = t - sc.start, dur = sc.end - sc.start;
    const cues = sc.beats.map(b => b.start - sc.start);
    let bi = 0;
    for (let i = 0; i < cues.length; i++) if (ts >= cues[i]) bi = i;
    comp.update(ts, { dur, cues, bi, bt: ts - cues[bi], beat: sc.beats[bi], beats: sc.beats });
    // enter: slide + fade, exit: fade; slow camera push over the scene
    const pin = E.ease(ts / 0.55), pout = E.clamp((sc.end - t) / 0.35);
    const cam = 1 + 0.03 * E.easeIO(ts / Math.max(dur, 4));
    root.style.opacity = Math.min(pin, pout);
    root.style.transform = `translateX(${(1 - pin) * 90}px) scale(${cam})`;
    root.style.transformOrigin = "50% 42%";
    shown = { sc, b: sc.beats[bi], bt: ts - cues[bi] };
  }
  const chap = document.getElementById("chapter");
  if (shown) {
    const b = shown.b;
    const on = t < b.end + 0.15;
    subsEn.innerHTML = on ? markup(b.en, [b.hl && b.hl[0]]) : "";
    subsJp.innerHTML = on ? markup(b.jp, [b.hl && b.hl[1]]) : "";
    const fit = el => { el.style.transform = ""; const w = el.scrollWidth; const max = 1340; el.style.transform = w > max ? `scale(${max / w})` : ""; };
    fit(subsEn); fit(subsJp);
    document.getElementById("subs").style.opacity = on ? 1 : 0;
    chap.textContent = shown.sc.chapter || "";
    chap.style.display = shown.sc.chapter ? "block" : "none";
  }
  document.getElementById("progress").style.width = (1920 * t / TL.total) + "px";
};
