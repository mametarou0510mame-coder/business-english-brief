// Scene components (theme A: light, editorial). Each returns { update(ts, ctx) }.
// ctx: dur, cues (beat start times in the scene), bi (current beat), bt (time in beat).
const C = { ink: "#1C1C1E", sub: "#606068", muted: "#8E8E96", red: "#DE4A28", navy: "#1A365D", amber: "#FFAA3C",
            line: "#DCD8D0", top: "#D6DAE2", left: "#96A0B2", right: "#BAC2D0", off: "#7C8496", paper: "#F7F5F0", green: "#2E9E6B" };

const iso = (x, y, z, ox, oy, s = 1) => [ox + (x - y) * 0.866 * s, oy + (x + y) * 0.5 * s - z * s];
const P = pts => pts.map(p => p.join(",")).join(" ");
const hash = n => { const x = Math.sin(n * 127.1) * 43758.5453; return x - Math.floor(x); };

// ---------------------------------------------------------------- shared: isometric data center
function dataCenter(svg, ox, oy, s = 1) {
  const g = E.el("g", {}, svg);
  E.el("polygon", { points: P([iso(-40, -40, 0, ox, oy, s), iso(560, -40, 0, ox, oy, s), iso(560, 360, 0, ox, oy, s), iso(-40, 360, 0, ox, oy, s)]),
    fill: "#000", opacity: .07, filter: "url(#soft)", transform: "translate(14,20)" }, g);
  const blocks = [];
  for (let k = 0; k < 3; k++) {
    const bg = E.el("g", {}, g), x0 = k * 175, w = 150, l = 320, h = 120;
    const top = E.el("polygon", { fill: C.top }, bg), lf = E.el("polygon", { fill: C.left }, bg), rt = E.el("polygon", { fill: C.right }, bg);
    const wins = [];
    for (let i = 0; i < 8; i++) for (let j = 0; j < 3; j++) wins.push({ n: E.el("polygon", { fill: C.off }, bg), i, j });
    const fans = [0, 1, 2].map(i => E.el("ellipse", { fill: C.left, stroke: C.right, "stroke-width": 2 }, bg));
    blocks.push({ x0, w, l, h, top, lf, rt, wins, fans });
  }
  return {
    g,
    update(rise, power) {          // rise 0..1 per block (array), power 0..1 = how many windows lit
      blocks.forEach((b, k) => {
        const hh = b.h * E.back(rise[k]);
        const Q = (x, y, z) => iso(x, y, z, ox, oy, s);
        b.top.setAttribute("points", P([Q(b.x0, 0, hh), Q(b.x0 + b.w, 0, hh), Q(b.x0 + b.w, b.l, hh), Q(b.x0, b.l, hh)]));
        b.lf.setAttribute("points", P([Q(b.x0, b.l, 0), Q(b.x0 + b.w, b.l, 0), Q(b.x0 + b.w, b.l, hh), Q(b.x0, b.l, hh)]));
        b.rt.setAttribute("points", P([Q(b.x0 + b.w, 0, 0), Q(b.x0 + b.w, b.l, 0), Q(b.x0 + b.w, b.l, hh), Q(b.x0 + b.w, 0, hh)]));
        b.wins.forEach(({ n, i, j }) => {
          const yy = 20 + i * 37, zz = (22 + j * 32) * hh / b.h, zh = 18 * hh / b.h;
          n.setAttribute("points", P([Q(b.x0 + b.w, yy, zz), Q(b.x0 + b.w, yy + 26, zz), Q(b.x0 + b.w, yy + 26, zz + zh), Q(b.x0 + b.w, yy, zz + zh)]));
          const on = hash(k * 31 + i * 7 + j) < power;
          n.setAttribute("fill", on ? C.amber : C.off);
        });
        b.fans.forEach((f, i) => { const [cx, cy] = Q(b.x0 + 75, 50 + i * 100, hh); f.setAttribute("cx", cx); f.setAttribute("cy", cy);
          f.setAttribute("rx", 26 * s); f.setAttribute("ry", 14 * s); f.setAttribute("opacity", rise[k] > .6 ? 1 : 0); });
      });
    },
  };
}

function pylon(svg, x, y, h) {
  const g = E.el("g", { stroke: "#8A8A94", "stroke-width": 5, "stroke-linecap": "round" }, svg);
  E.el("line", { x1: x - 30, y1: y, x2: x, y2: y - h }, g);
  E.el("line", { x1: x + 30, y1: y, x2: x, y2: y - h }, g);
  for (let k = 1; k < 4; k++) { const yy = y - h * k / 4, ww = 30 * (1 - k / 4) + 6;
    E.el("line", { x1: x - ww - 22, y1: yy, x2: x + ww + 22, y2: yy, "stroke-width": 4 }, g); }
  return [[x - 40, y - h * .75], [x + 40, y - h * .75]];
}

function defs(svg) {
  const d = E.el("defs", {}, svg);
  const f = E.el("filter", { id: "soft", x: "-20%", y: "-20%", width: "140%", height: "140%" }, d);
  E.el("feGaussianBlur", { stdDeviation: 18 }, f);
  const g2 = E.el("filter", { id: "glow", x: "-50%", y: "-50%", width: "200%", height: "200%" }, d);
  E.el("feGaussianBlur", { stdDeviation: 6 }, g2);
}

function stageSvg(root) {
  const svg = E.el("svg", { width: 1920, height: 1080, viewBox: "0 0 1920 1080", style: "position:absolute;inset:0" }, root);
  defs(svg);
  return svg;
}

function div(root, css, html, cls) { const n = E.el("div", cls ? { class: cls } : {}, root, html); n.style.cssText = "position:absolute;" + css; return n; }

// ---------------------------------------------------------------- 1. hook
SCENES.hook = (root, v) => {
  const svg = stageSvg(root);
  const dc = dataCenter(svg, 1180, 330, 1);
  const a1 = pylon(svg, 230, 760, 260), a2 = pylon(svg, 640, 720, 220);
  const wires = [0, 18, 36].map(dy => {
    const pts = [[a1[1][0], a1[1][1] + dy], [a2[0][0], a2[0][1] + dy], [a2[1][0], a2[1][1] + dy], [1180, 520 + dy]];
    const path = E.el("polyline", { points: P(pts), fill: "none", stroke: C.red, "stroke-width": 3, opacity: .55 }, svg);
    const dots = [0, 1, 2, 3, 4].map(() => E.el("circle", { r: 7, fill: C.red }, svg));
    return { path, dots, len: 0 };
  });
  // chat bubble above the building
  const bub = div(root, "left:1250px;top:120px;background:#fff;border:2px solid #DCD8D0;border-radius:24px;padding:16px 26px;font:600 30px Inter;box-shadow:0 8px 24px rgba(0,0,0,.08);transform-origin:20% 100%",
    'Ask AI: <span style="color:#606068">"Summarize this report"</span><span id="hkdots"></span>');
  const num = div(root, "left:190px;top:180px", "", "num");
  const tag = div(root, "left:330px;top:352px;transform-origin:50% 50%", "+17% in one year", "tag");
  const src = div(root, "left:330px;top:440px", "Data centers' electricity use, 2025 (IEA)", "src");
  const chip = div(root, "left:1320px;top:770px;background:#DE4A28;color:#fff;font:800 34px Inter;border-radius:14px;padding:8px 22px;transform-origin:50% 50%", "power-hungry");
  return {
    update(ts, { cues }) {
      const c = i => cues[Math.min(i, cues.length - 1)];
      dc.update([0, 1, 2].map(k => (ts - 0.2 - k * 0.25) / 0.7), E.clamp((ts - 1.2) / 2.5) * 0.85 + 0.1);
      wires.forEach((w, k) => {
        if (!w.len) w.len = w.path.getTotalLength();
        const on = E.clamp((ts - 1.0) / 0.6);
        w.dots.forEach((d, i) => { const p = w.path.getPointAtLength(((ts * 0.33 + i / 5 + k * 0.07) % 1) * w.len);
          d.setAttribute("cx", p.x); d.setAttribute("cy", p.y); d.setAttribute("opacity", on); });
      });
      const pb = E.ease((ts - 0.6) / 0.4) * (1 - E.clamp((ts - c(1) + 0.3) / 0.4));
      bub.style.opacity = pb; bub.style.transform = `scale(${0.8 + 0.2 * E.back((ts - 0.6) / 0.4)})`;
      const dots = root.querySelector("#hkdots"); if (dots) dots.textContent = ".".repeat(1 + Math.floor(ts * 3) % 3);
      const pn = E.easeIO((ts - c(1)) / 1.4);
      num.textContent = ts < c(1) ? "" : `${Math.round(485 * pn)} TWh`;
      num.style.opacity = ts < c(1) ? 0 : 1;
      const pt = (ts - c(2)) / 0.45;
      tag.style.opacity = pt > 0 ? 1 : 0; tag.style.transform = `scale(${0.6 + 0.4 * E.back(pt)})`;
      src.style.opacity = E.ease((ts - c(1) - 0.6) / 0.5);
      const pc = (ts - c(3) - 0.8) / 0.4;
      chip.style.opacity = pc > 0 ? 1 : 0; chip.style.transform = `scale(${0.6 + 0.4 * E.back(pc)}) rotate(-3deg)`;
    },
  };
};

// ---------------------------------------------------------------- 2. one rack = 65 homes, then x11 density
SCENES.rack = (root, v) => {
  const svg = stageSvg(root);
  const rx = 300, ry = 170, rw = 230, rh = 600;
  E.el("rect", { x: rx + 10, y: ry + 16, width: rw, height: rh, rx: 16, fill: "#000", opacity: .08, filter: "url(#soft)" }, svg);
  E.el("rect", { x: rx, y: ry, width: rw, height: rh, rx: 16, fill: "#2A2F3A", stroke: "#1C1C1E", "stroke-width": 4 }, svg);
  const leds = [];
  for (let i = 0; i < 14; i++) {
    const y = ry + 24 + i * 40;
    E.el("rect", { x: rx + 18, y, width: rw - 36, height: 30, rx: 6, fill: "#3A4150" }, svg);
    for (let k = 0; k < 5; k++) leds.push(E.el("circle", { cx: rx + 34 + k * 16, cy: y + 15, r: 4.5, fill: "#5A6070" }, svg));
    E.el("rect", { x: rx + 130, y: y + 12, width: rw - 160, height: 6, rx: 3, fill: "#555C6C" }, svg);
  }
  const label = div(root, "left:300px;top:800px;width:230px;text-align:center;font:600 28px Inter;color:#1C1C1E", "1 AI server rack<br><span style='font:500 22px Inter;color:#8E8E96'>(2027, peak)</span>");
  const eq = div(root, "left:610px;top:395px;font:900 120px Inter;color:#DE4A28", "=");
  const houses = [], hx0 = 790, hy0 = 190;
  const hg = E.el("g", {}, svg);
  for (let i = 0; i < 65; i++) {
    const r = Math.floor(i / 11), c = i % 11, x = hx0 + c * 82, y = hy0 + r * 96;
    const g = E.el("g", { transform: `translate(${x},${y})` }, hg);
    const roof = E.el("polygon", { points: "-26,0 0,-22 26,0", fill: "#C8CCD4" }, g);
    const body = E.el("rect", { x: -20, y: 0, width: 40, height: 30, fill: "#DADDE3" }, g);
    const win = E.el("rect", { x: -9, y: 8, width: 18, height: 12, fill: "#B0B6C0" }, g);
    houses.push({ g, roof, body, win });
  }
  const count = div(root, "left:1080px;top:770px;font:900 84px Inter;color:#DE4A28", "");
  // x11 overlay
  const ov = div(root, "left:760px;top:200px;width:960px;height:560px;background:#fff;border:2px solid #DCD8D0;border-radius:28px;box-shadow:0 14px 40px rgba(0,0,0,.08)", "");
  const ovT = div(ov, "left:0;right:0;top:34px;text-align:center;font:700 38px Inter", "Power packed into one AI server rack");
  const ovJ = div(ov, "left:0;right:0;top:88px;text-align:center", "AIサーバー1台あたりの電力密度", "jpS");
  const b20 = div(ov, "left:200px;bottom:110px;width:160px;background:#96A0B2;border-radius:12px 12px 0 0", "");
  const b25 = div(ov, "left:560px;bottom:110px;width:160px;background:#DE4A28;border-radius:12px 12px 0 0", "");
  div(ov, "left:200px;bottom:60px;width:160px;text-align:center;font:700 30px Inter", "2020");
  div(ov, "left:560px;bottom:60px;width:160px;text-align:center;font:700 30px Inter", "2025");
  const x11 = div(ov, "left:740px;top:170px;font:900 110px Inter;color:#DE4A28", "×11");
  return {
    update(ts, { cues, bi }) {
      const c = i => cues[Math.min(i, cues.length - 1)];
      leds.forEach((l, i) => l.setAttribute("fill", hash(i + Math.floor(ts * 6) * 0.37) > 0.45 ? (i % 3 ? "#5AC8FF" : "#3CCB8F") : "#5A6070"));
      const ph = ts - c(1);
      eq.style.opacity = E.ease(ph / 0.4);
      const lit = E.clamp((ph - 0.3) / 2.2) * 65;
      houses.forEach((h, i) => {
        const appear = E.ease((ph - i * 0.012) / 0.3);
        h.g.setAttribute("opacity", appear);
        const on = i < lit;
        h.roof.setAttribute("fill", on ? "#E88A3C" : "#C8CCD4");
        h.body.setAttribute("fill", on ? "#FFD27A" : "#DADDE3");
        h.win.setAttribute("fill", on ? "#FFF3C4" : "#B0B6C0");
      });
      count.textContent = ph > 0 ? `${Math.round(lit)} homes` : "";
      count.style.opacity = 1 - E.ease((ts - c(2)) / 0.4);
      const po = E.ease((ts - c(2)) / 0.5);
      ov.style.opacity = ts > c(2) ? po : 0;
      ov.style.transform = `translateY(${(1 - po) * 30}px)`;
      const g = E.easeIO((ts - c(2) - 0.5) / 1.2);
      b20.style.height = (30 * g) + "px"; b25.style.height = (330 * g) + "px";
      x11.style.opacity = E.ease((ts - c(2) - 1.6) / 0.4);
    },
  };
};

// ---------------------------------------------------------------- 3. big tech investment
SCENES.capex = (root, v) => {
  const svg = stageSvg(root);
  const title = div(root, "left:0;right:0;top:130px;text-align:center", "Capital spending by five big tech companies", "h2");
  div(root, "left:0;right:0;top:186px;text-align:center", "大手IT企業5社の設備投資", "jpS");
  const base = 800;
  const bars = [
    { x: 620, lab: "2025", val: 400, col: C.navy, txt: "$400B+" },
    { x: 1080, lab: "2026", val: 700, col: C.red, txt: "+75%" },
  ].map(b => {
    const r = E.el("rect", { x: b.x, width: 220, rx: 14, fill: b.col }, svg);
    E.el("text", { x: b.x + 110, y: base + 48, "text-anchor": "middle", "font-size": 32, "font-weight": 700, fill: C.ink }, svg).textContent = b.lab;
    const t = div(root, `left:${b.x - 60}px;width:340px;text-align:center;font:900 64px Inter;color:${b.col}`, "");
    return { ...b, r, t };
  });
  E.el("line", { x1: 520, x2: 1400, y1: base, y2: base, stroke: C.line, "stroke-width": 3 }, svg);
  const note = div(root, "left:1080px;width:220px;text-align:center", "expected (IEA)", "src");
  return {
    update(ts, { cues }) {
      const c = i => cues[Math.min(i, cues.length - 1)];
      title.style.opacity = E.ease(ts / 0.4);
      bars.forEach((b, i) => {
        const p = E.easeIO((ts - (i === 0 ? c(1) : c(2)) - 0.1) / 1.0);
        const h = b.val * 0.62 * p;
        b.r.setAttribute("y", base - h); b.r.setAttribute("height", Math.max(0, h));
        b.t.style.top = (base - h - 84) + "px"; b.t.style.opacity = p > 0.05 ? 1 : 0;
        b.t.textContent = i === 0 ? `$${Math.round(400 * p)}B+` : `+${Math.round(75 * p)}%`;
      });
      note.style.opacity = E.ease((ts - c(2) - 1.0) / 0.4);
      note.style.top = (base - 700 * 0.62 - 120) + "px";
    },
  };
};
