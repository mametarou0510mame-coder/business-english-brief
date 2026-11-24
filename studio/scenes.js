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
      hg.setAttribute("opacity", 1 - E.ease((ts - c(2)) / 0.4));
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

// ---------------------------------------------------------------- helpers for the full episode
function pop(el, p, rot = 0) { el.style.opacity = p > 0 ? E.clamp(p * 3) : 0; el.style.transform = `scale(${0.7 + 0.3 * E.back(p)}) rotate(${rot}deg)`; }
function card(root, css, title, jp, col) {
  return div(root, `${css};background:#fff;border:2px solid ${col || "#DCD8D0"};border-radius:22px;padding:22px 30px;box-shadow:0 10px 28px rgba(0,0,0,.06);transform-origin:50% 50%`,
    `<div style="font:800 36px Inter;color:${col || C.ink}">${title}</div><div class="jpS" style="margin-top:6px">${jp}</div>`);
}

// ---------------------------------------------------------------- 2. growth: 485 -> 950 TWh, AI-focused, 3% of world
SCENES.growth = (root, v) => {
  const svg = stageSvg(root);
  const iea = div(root, "left:240px;top:150px;display:flex;align-items:center;gap:16px",
    `<span style="background:${C.navy};color:#fff;font:900 34px Inter;border-radius:10px;padding:6px 16px">IEA</span><span class="h2" style="font-size:34px">Data center electricity use</span>`);
  const base = 790, bx = [330, 640];
  E.el("line", { x1: 250, x2: 900, y1: base, y2: base, stroke: C.line, "stroke-width": 3 }, svg);
  const bars = [[485, "2025", C.navy], [950, "2030", C.red]].map(([v, lab, col], i) => {
    const r = E.el("rect", { x: bx[i], width: 200, rx: 14, fill: col }, svg);
    E.el("text", { x: bx[i] + 100, y: base + 46, "text-anchor": "middle", "font-size": 32, "font-weight": 700, fill: C.ink }, svg).textContent = lab + (i ? " (est.)" : "");
    const t = div(root, `left:${bx[i] - 70}px;width:340px;text-align:center;font:900 54px Inter;color:${col}`, "");
    return { v, r, t };
  });
  const x2 = div(root, "left:548px;top:520px;font:900 50px Inter;color:#fff;background:#DE4A28;border-radius:40px;padding:4px 18px;transform-origin:50% 50%", "×2");
  // right panel
  const pAI = card(root, "left:1080px;top:230px;width:560px", "AI-focused data centers", "AI向けのデータセンター", C.ink);
  const b1 = div(root, "left:1080px;top:420px;width:270px;text-align:center;background:#FDECE7;border-radius:20px;padding:20px 0;transform-origin:50% 50%",
    `<div style="font:900 64px Inter;color:${C.red}">+50%</div><div class="src">in 2025</div>`);
  const b2 = div(root, "left:1390px;top:420px;width:270px;text-align:center;background:#FDECE7;border-radius:20px;padding:20px 0;transform-origin:50% 50%",
    `<div style="font:900 64px Inter;color:${C.red}">×3</div><div class="src">by 2030 (est.)</div>`);
  // donut 3%
  const dg = E.el("g", { transform: "translate(1370,470)" }, svg);
  E.el("circle", { r: 170, fill: "none", stroke: "#E4E0D8", "stroke-width": 60 }, dg);
  const arc = E.el("circle", { r: 170, fill: "none", stroke: C.red, "stroke-width": 60, transform: "rotate(-90)", "stroke-dasharray": `0 ${2 * Math.PI * 170}` }, dg);
  const dl = div(root, "left:1220px;top:410px;width:300px;text-align:center", `<div style="font:900 80px Inter;color:${C.red}">3%</div><div class="src">of world electricity, 2030</div>`);
  const fast = div(root, "left:1080px;top:330px;width:600px;text-align:center", `<div style="display:flex;gap:30px;justify-content:center">
    <span style="background:${C.red};color:#fff;font:900 48px Inter;border-radius:18px;padding:18px 34px">how fast</span>
    <span style="background:${C.navy};color:#fff;font:900 48px Inter;border-radius:18px;padding:18px 34px">where</span></div>
    <div class="jpS" style="margin-top:20px;font-size:30px">増える速さと、場所</div>`);
  return {
    update(ts, { cues, bi }) {
      const c = i => cues[Math.min(i, cues.length - 1)];
      iea.style.opacity = E.ease(ts / 0.5);
      bars.forEach((b, i) => {
        const p = E.easeIO((ts - (i ? c(1) + 0.3 : 0.4)) / 1.1);
        const h = b.v * 0.5 * p;
        b.r.setAttribute("y", base - h); b.r.setAttribute("height", Math.max(0, h));
        b.t.style.top = (base - h - 72) + "px"; b.t.style.opacity = p > .03 ? 1 : 0;
        b.t.textContent = `${Math.round(b.v * p)} TWh`;
      });
      pop(x2, (ts - c(1) - 1.4) / 0.4, -6);
      const on = (a, b) => ts >= c(a) && (b === undefined || ts < c(b));
      pAI.style.opacity = on(2, 4) ? E.ease((ts - c(2)) / 0.4) : 0;
      pop(b1, on(2, 4) ? (ts - c(3) + 0.2) / 0.4 : -1);
      pop(b2, on(2, 4) ? (ts - c(3) - 1.6) / 0.4 : -1);
      const pd = on(4, 5) ? E.easeIO((ts - c(4) - 0.2) / 1.2) : 0;
      dg.setAttribute("opacity", on(4, 5) ? 1 : 0);
      arc.setAttribute("stroke-dasharray", `${2 * Math.PI * 170 * 0.03 * pd} ${2 * Math.PI * 170}`);
      dl.style.opacity = on(4, 5) ? E.ease((ts - c(4) - 0.6) / 0.4) : 0;
      pop(fast, on(5) ? (ts - c(5)) / 0.45 : -1);
    },
  };
};

// ---------------------------------------------------------------- 4. bottleneck pipe
SCENES.bottleneck = (root, v) => {
  const svg = stageSvg(root);
  const T = [[150, 330], [800, 330], [980, 450], [1260, 450]], B = [[150, 720], [800, 720], [980, 600], [1260, 600]];
  const pipe = E.el("polygon", { points: P([...T, ...B.slice().reverse()]), fill: "#EFEBE3", stroke: "#B9B3A8", "stroke-width": 4 }, svg);
  const parts = [];
  for (let i = 0; i < 140; i++) parts.push({ n: E.el("circle", { r: 7, fill: C.amber }, svg), x: hash(i) , y: hash(i + 99) });
  const neck = E.el("circle", { cx: 980, cy: 525, r: 120, fill: C.red, opacity: 0, filter: "url(#soft)" }, svg);
  const lab1 = div(root, "left:330px;top:745px;font:800 32px Inter;color:#C9781A", "AI demand <span class='jpS'>AIの需要</span>");
  const lab2 = div(root, "left:980px;top:625px;font:600 26px Inter;color:#8E8E96", "what supply can deliver");
  const head = div(root, "left:0;right:0;top:140px;text-align:center", "You can't build power as fast as software", "h2");
  const items = [["Grid connections", "送電網への接続", "getting slower"], ["Gas turbines", "発電タービン", "orders +70% (2025)"],
                 ["Transformers", "変圧器", "in short supply"], ["Memory chips", "メモリー半導体", "short to end-2027"]].map(([a, j, n], i) =>
    div(root, `left:1330px;top:${300 + i * 108}px;width:440px;background:#fff;border:2px solid ${C.red};border-radius:18px;padding:12px 22px;transform-origin:0 50%`,
      `<div style="display:flex;justify-content:space-between;align-items:baseline"><span style="font:800 30px Inter">${a}</span><span style="font:700 22px Inter;color:${C.red}">${n}</span></div><div class="jpS">${j}</div>`));
  const stamp = div(root, "left:640px;top:200px;font:900 84px Inter;color:#DE4A28;border:8px solid #DE4A28;border-radius:16px;padding:0 24px;transform-origin:50% 50%;background:rgba(247,245,240,.9)", "BOTTLENECK");
  return {
    update(ts, { cues }) {
      const c = i => cues[Math.min(i, cues.length - 1)];
      head.style.opacity = E.ease(ts / 0.4) * (1 - E.ease((ts - c(5)) / 0.3));
      parts.forEach((p, i) => {
        const sp = 70 + p.y * 40;
        let x = 170 + ((p.x * 1100 + ts * sp) % 1080);
        let half = x < 800 ? 175 : x < 980 ? 175 - (x - 800) / 180 * 60 : 60;
        // crowding: only every 6th particle passes the neck
        if (x > 900 && i % 6) x = 900 - (i % 5) * 18 - hash(i + 7) * 40, half = 140;
        const y = 525 + (p.y - 0.5) * 2 * (half - 14);
        p.n.setAttribute("cx", x); p.n.setAttribute("cy", y);
      });
      neck.setAttribute("opacity", 0.35 * E.ease((ts - c(1)) / 0.6));
      items.forEach((it, i) => pop(it, (ts - c(i + 1)) / 0.4));
      pop(stamp, (ts - c(5) - 0.2) / 0.4, -4);
    },
  };
};

// ---------------------------------------------------------------- 5. scramble for power: hub and spokes
SCENES.scramble = (root, v) => {
  const svg = stageSvg(root);
  const cx = 960, cy = 500;
  const head = div(root, "left:0;right:0;top:120px;text-align:center", `A <span class="hl">scramble for</span> power`, "h2");
  const nodes = [
    { x: 470, y: 330, t: "Renewable power deals", j: "再エネ購入契約", n: "~40% signed by tech (2025)", col: C.green },
    { x: 1450, y: 330, t: "Small nuclear reactors", j: "小型原子炉", n: "deals 25 → 45 GW", col: C.navy },
    { x: 470, y: 690, t: "On-site gas plants", j: "自前のガス発電", n: "15–27 GW by 2030 · mostly US", col: C.red },
    { x: 1450, y: 690, t: "Big batteries", j: "大型蓄電池", n: "20–25 GW by 2030", col: "#C9781A" },
  ];
  nodes.forEach(nd => {
    nd.line = E.el("line", { x1: cx, y1: cy, x2: cx, y2: cy, stroke: nd.col, "stroke-width": 4, opacity: .5 }, svg);
    nd.dots = [0, 1, 2].map(() => E.el("circle", { r: 8, fill: nd.col }, svg));
    nd.el = div(root, `left:${nd.x - 220}px;top:${nd.y - 70}px;width:440px;text-align:center;background:#fff;border:3px solid ${nd.col};border-radius:22px;padding:14px 10px;transform-origin:50% 50%`,
      `<div style="font:800 32px Inter">${nd.t}</div><div class="jpS">${nd.j}</div><div style="font:800 26px Inter;color:${nd.col};margin-top:4px">${nd.n}</div>`);
  });
  const dcSvg = E.el("g", {}, svg);
  const dc = dataCenter(dcSvg, cx - 60, cy - 150, 0.45);
  const lab = div(root, `left:${cx - 120}px;top:${cy + 95}px;width:240px;text-align:center;font:800 26px Inter`, "Data center");
  return {
    update(ts, { cues }) {
      const c = i => cues[Math.min(i, cues.length - 1)];
      head.style.opacity = E.ease(ts / 0.4);
      dc.update([1, 1, 1], 0.6 + 0.3 * Math.sin(ts * 2) * 0.5);
      nodes.forEach((nd, i) => {
        const p = E.ease((ts - c(i + 1)) / 0.5);
        nd.line.setAttribute("x2", E.lerp(cx, nd.x, p)); nd.line.setAttribute("y2", E.lerp(cy, nd.y, p));
        pop(nd.el, (ts - c(i + 1) - 0.25) / 0.4);
        nd.dots.forEach((d, k) => { const q = 1 - ((ts * 0.5 + k / 3) % 1);
          d.setAttribute("cx", E.lerp(cx, nd.x, q * p)); d.setAttribute("cy", E.lerp(cy, nd.y, q * p)); d.setAttribute("opacity", p > .9 ? 1 : 0); });
      });
    },
  };
};

// ---------------------------------------------------------------- 6. Japan
SCENES.japan = (root, v) => {
  const svg = stageSvg(root);
  const head = div(root, "left:240px;top:140px;display:flex;align-items:center;gap:18px",
    `<svg width="72" height="48"><rect width="72" height="48" rx="6" fill="#fff" stroke="#DCD8D0" stroke-width="2"/><circle cx="36" cy="24" r="14" fill="#BC002D"/></svg>
     <span class="h2">Japan: peak power demand forecast</span>`);
  const src = div(root, "left:330px;top:205px", "OCCTO (Organization for Cross-regional Coordination of Transmission Operators), Jan 2025", "src");
  const base = 800, bx = [380, 700];
  E.el("line", { x1: 300, x2: 1000, y1: base, y2: base, stroke: C.line, "stroke-width": 3 }, svg);
  const bars = [[157.7, "FY2024", "#96A0B2"], [164.6, "FY2034", C.red]].map(([v, lab, col], i) => {
    const r = E.el("rect", { x: bx[i], width: 200, rx: 12, fill: col }, svg);
    E.el("text", { x: bx[i] + 100, y: base + 46, "text-anchor": "middle", "font-size": 32, "font-weight": 700, fill: C.ink }, svg).textContent = lab;
    const t = E.el("text", { x: bx[i] + 100, "text-anchor": "middle", "font-size": 36, "font-weight": 900, fill: "#fff" }, svg);
    return { v, r, t };
  });
  const plus = div(root, "left:920px;top:250px;font:900 80px Inter;color:#DE4A28;transform-origin:50% 50%", "+4.4%");
  const drv = div(root, "left:1240px;top:380px;width:500px;background:#fff;border:2px solid #DCD8D0;border-radius:24px;padding:26px 34px;box-shadow:0 10px 28px rgba(0,0,0,.06)", "");
  const rows = [["#2E9EDB", "New data centers", "データセンター"], ["#FFAA3C", "Chip factories", "半導体工場"], ["#8E8E96", "Households: use falls (−5.4%)", "家庭の使用量は減少"]].map(([col, a, j], i) =>
    div(drv, `position:relative;display:flex;gap:18px;align-items:center;margin:${i ? 22 : 0}px 0 0`,
      `<span style="width:30px;height:30px;border-radius:50%;background:${col};flex:none"></span><span><div style="font:800 32px Inter">${a}</div><div class="jpS">${j}</div></span>`));
  return {
    update(ts, { cues }) {
      const c = i => cues[Math.min(i, cues.length - 1)];
      head.style.opacity = E.ease(ts / 0.4); src.style.opacity = E.ease((ts - c(1)) / 0.4);
      bars.forEach((b, i) => {
        const p = E.easeIO((ts - c(1) - i * 0.5) / 1.0);
        const h = b.v * 3.4 * p;
        b.r.setAttribute("y", base - h); b.r.setAttribute("height", Math.max(0, h));
        b.t.setAttribute("y", base - h + 50); b.t.textContent = p > .2 ? `${Math.round(b.v)} GW` : "";
      });
      pop(plus, (ts - c(1) - 1.6) / 0.4, -4);
      drv.style.opacity = E.ease((ts - c(2)) / 0.4);
      rows.forEach((r, i) => r.style.opacity = E.ease((ts - (i < 2 ? c(2) + i * 0.6 : c(3))) / 0.4));
    },
  };
};

// ---------------------------------------------------------------- 6b. efficiency counterpoint
SCENES.efficiency = (root, v) => {
  const svg = stageSvg(root);
  const head = div(root, "left:0;right:0;top:130px;text-align:center", `Good news: <span class="hl">energy per AI task</span> keeps falling`, "h2");
  div(root, "left:0;right:0;top:186px;text-align:center", "AIの1回の処理に使う電力(ここ数年、毎年10分の1以下に)", "jpS");
  const base = 760;
  const bars = [1, 0.1, 0.01].map((v, i) => {
    const x = 330 + i * 230;
    const r = E.el("rect", { x, width: 150, rx: 10, fill: i ? C.green : "#96A0B2" }, svg);
    E.el("text", { x: x + 75, y: base + 44, "text-anchor": "middle", "font-size": 28, "font-weight": 700, fill: C.ink }, svg).textContent = ["Year 1", "Year 2", "Year 3"][i];
    const t = div(root, `left:${x - 40}px;width:230px;text-align:center;font:900 40px Inter;color:${i ? C.green : C.sub}`, ["1", "1/10", "1/100"][i]);
    return { v, r, t };
  });
  div(root, "left:330px;top:860px", "illustration: at least 1/10 each year (IEA)", "src").style.top = "820px";
  // tug of war: demand vs efficiency
  const tug = div(root, "left:1060px;top:300px;width:640px;height:420px", `
    <div style="position:absolute;left:0;top:30px;width:640px;text-align:center;font:800 34px Inter">Can efficiency keep up?</div>
    <div class="jpS" style="position:absolute;left:0;top:84px;width:640px;text-align:center">効率化は、需要の伸びに追いつけるか</div>
    <div id="dm" style="position:absolute;left:60px;top:170px;font:900 44px Inter;color:#DE4A28">Demand ▲</div>
    <div id="ef" style="position:absolute;left:340px;top:170px;font:900 44px Inter;color:#2E9E6B">Efficiency ▼</div>
    <div style="position:absolute;left:250px;top:260px;font:900 120px Inter;color:#1A365D">?</div>`);
  return {
    update(ts, { cues }) {
      const c = i => cues[Math.min(i, cues.length - 1)];
      head.style.opacity = E.ease(ts / 0.4);
      bars.forEach((b, i) => {
        const p = E.ease((ts - 0.5 - i * 0.7) / 0.6);
        const h = Math.max(4, 420 * b.v) * p;
        b.r.setAttribute("y", base - h); b.r.setAttribute("height", h);
        b.t.style.top = (base - h - 58) + "px"; b.t.style.opacity = p;
      });
      tug.style.opacity = E.ease((ts - c(1)) / 0.4);
      const dm = tug.querySelector("#dm"), ef = tug.querySelector("#ef");
      if (dm) dm.style.transform = `translateY(${Math.sin(ts * 3) * 6}px)`;
      if (ef) ef.style.transform = `translateY(${-Math.sin(ts * 3) * 6}px)`;
    },
  };
};

// ---------------------------------------------------------------- 7. phrases review: say -> think -> meaning + example
SCENES.phrases = (root, v) => {
  const P_ = v.items;
  const intro = div(root, "left:0;right:0;top:360px;text-align:center", `<div style="font:900 96px Inter;color:${C.red}">3 phrases</div><div class="h2" style="margin-top:10px">for your next meeting</div><div class="jpS" style="font-size:30px;margin-top:8px">次の会議で使える英語</div>`);
  const dots = div(root, "left:0;right:0;top:150px;text-align:center;font:800 26px Inter;color:#8E8E96", "");
  const cardEl = div(root, "left:360px;top:220px;width:1200px;height:560px;background:#fff;border:2px solid #DCD8D0;border-radius:30px;box-shadow:0 14px 40px rgba(0,0,0,.07)", "");
  const ph = div(cardEl, "left:0;right:0;top:70px;text-align:center;font:900 96px Inter;color:#1C1C1E", "");
  const ring = div(cardEl, "left:540px;top:230px;width:120px;height:120px;border-radius:50%;border:10px solid #EEE;display:grid;place-items:center;font:900 54px Inter;color:#DE4A28", "");
  const mean = div(cardEl, "left:0;right:0;top:220px;text-align:center;font:800 56px 'Noto Sans CJK JP';color:#DE4A28", "");
  const ex = div(cardEl, "left:80px;right:80px;top:360px;text-align:center;background:#F7F5F0;border-radius:18px;padding:22px 20px", "");
  return {
    update(ts, { beat, beats, bi, bt }) {
      const isIntro = beat.step === "intro";
      intro.style.opacity = isIntro ? E.ease(ts / 0.4) : 0;
      cardEl.style.opacity = isIntro ? 0 : 1;
      if (isIntro) { dots.textContent = ""; return; }
      const k = beat.ph, it = P_[k];
      dots.textContent = `PHRASE ${k + 1} / ${P_.length}`;
      ph.textContent = it.en;
      const firstOfPh = beats.findIndex(b => b.ph === k);
      const tIn = ts - (beats[firstOfPh].start - beats[0].start + 0) ;
      cardEl.style.transform = `translateY(${(1 - E.ease((bi === firstOfPh ? bt : 9) / 0.4)) * 30}px)`;
      const thinking = beat.step === "think";
      ring.style.opacity = thinking ? 1 : 0;
      if (thinking) ring.textContent = String(Math.max(1, Math.ceil(beat.end - beat.start - bt)));
      const revealed = beat.step === "ex";
      mean.style.opacity = revealed ? E.ease(bt / 0.4) : 0;
      mean.textContent = it.jp;
      ex.style.opacity = revealed ? E.ease((bt - 0.3) / 0.4) : 0;
      ex.innerHTML = `<div style="font:700 40px Inter">${it.ex.replace(it.key || it.en, `<span class="hl">${it.key || it.en}</span>`)}</div><div class="jpS" style="font-size:28px;margin-top:8px">${it.ex_jp}</div>`;
    },
  };
};

// ---------------------------------------------------------------- outro
SCENES.outro = (root, v) => {
  const q = div(root, "left:0;right:0;top:300px;text-align:center", `<div style="font:900 72px Inter">Which one will you use this week?</div>
    <div class="jpS" style="font-size:34px;margin-top:14px">今週使うのはどれ? コメントで教えてください</div>
    <div style="display:flex;gap:24px;justify-content:center;margin-top:50px">${v.items.map(p => `<span style="background:#fff;border:3px solid ${C.red};border-radius:16px;padding:12px 26px;font:800 36px Inter">${p}</span>`).join("")}</div>`);
  const sub = div(root, "left:0;right:0;top:720px;text-align:center;font:700 30px Inter;color:#606068", "Subscribe for world business news in simple English");
  return { update(ts) { q.style.opacity = E.ease(ts / 0.5); sub.style.opacity = E.ease((ts - 1) / 0.5); } };
};

// ---------------------------------------------------------------- CTA (end of a short)
SCENES.cta = (root, v) => {
  const q = div(root, "left:0;right:0;top:300px;text-align:center", `<div style="font:900 84px Inter">${v.en || ""}</div>
    <div class="jpS" style="font-size:44px;margin-top:18px">${v.jp || ""}</div>
    <div style="margin-top:50px;display:inline-block;background:#DE4A28;color:#fff;font:900 52px 'Noto Sans CJK JP';border-radius:20px;padding:18px 44px">${v.btn || ""}</div>`);
  return { update(ts) { q.style.opacity = E.ease(ts / 0.4); q.style.transform = `scale(${0.9 + 0.1 * E.back(ts / 0.5)})`; } };
};
