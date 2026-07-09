const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const FA = require("react-icons/fa");

// ---------- palette ----------
const BG_DARK = "12141C", BG_DARK2 = "1B1E2A", BG_LIGHT = "F4F5F8";
const CARD = "FFFFFF", INK = "1A1C24", MUTED = "6B7280", MUTED_LT = "9AA0AD";
const LIGHTTX = "E9EBF2", ACCENT = "FF5A3C", GREEN = "1FA971", SLATE = "334155";

const W = 13.33, H = 7.5;
const makeShadow = () => ({ type: "outer", color: "000000", blur: 9, offset: 3, angle: 90, opacity: 0.16 });

// ---------- icons ----------
async function icon(IconComponent, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(IconComponent, { color, size: String(size) }));
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}
let IC = {};
async function loadIcons() {
  const spec = {
    bolt: [FA.FaBolt, "#FFFFFF"], route: [FA.FaRoute, "#FFFFFF"], cut: [FA.FaCut, "#FFFFFF"],
    layers: [FA.FaLayerGroup, "#FFFFFF"], check: [FA.FaCheckCircle, "#FFFFFF"], cube: [FA.FaCube, "#FFFFFF"],
    code: [FA.FaCode, "#FFFFFF"], trophy: [FA.FaTrophy, "#FFFFFF"], flask: [FA.FaFlask, "#FFFFFF"],
    chip: [FA.FaMicrochip, "#FFFFFF"], gauge: [FA.FaTachometerAlt, "#FFFFFF"], shield: [FA.FaShieldAlt, "#FFFFFF"],
    times: [FA.FaTimesCircle, "#FF7A62"], tasks: [FA.FaTasks, "#FFFFFF"], robot: [FA.FaRobot, "#FFFFFF"],
    scale: [FA.FaBalanceScale, "#FFFFFF"],
  };
  for (const k in spec) IC[k] = await icon(spec[k][0], spec[k][1]);
}

// ---------- helpers ----------
function dots(slide, ox, oy) {
  // token-dot motif: scattered small circles, a few accent-coloured
  const pts = [[0,0,GREEN,60],[0.55,0.18,ACCENT,0],[1.05,-0.05,"3A3F52",0],[0.35,0.62,"3A3F52",0],
    [0.95,0.55,GREEN,55],[1.5,0.35,ACCENT,35],[1.35,0.9,"2A2E3D",0],[0.05,1.05,ACCENT,70]];
  pts.forEach(([dx,dy,c,tr]) => slide.addShape("ellipse",
    { x: ox+dx, y: oy+dy, w: 0.18, h: 0.18, fill: { color: c, transparency: tr }, line: { type: "none" } }));
}
function eyebrow(slide, txt, x, y, color = ACCENT) {
  slide.addText(txt, { x, y, w: 9, h: 0.3, margin: 0, fontFace: "Arial", fontSize: 12.5, bold: true, color, charSpacing: 3 });
}
function iconCircle(slide, x, y, d, circleColor, iconKey) {
  slide.addShape("ellipse", { x, y, w: d, h: d, fill: { color: circleColor }, line: { type: "none" }, shadow: makeShadow() });
  const p = d * 0.42;
  slide.addImage({ data: IC[iconKey], x: x + (d - p) / 2, y: y + (d - p) / 2, w: p, h: p });
}
function card(slide, x, y, w, h, fill = CARD) {
  slide.addShape("roundRect", { x, y, w, h, rectRadius: 0.09, fill: { color: fill }, line: { type: "none" }, shadow: makeShadow() });
}

async function build() {
  await loadIcons();
  const pres = new pptxgen();
  pres.defineLayout({ name: "W", width: W, height: H });
  pres.layout = "W";
  pres.author = "Team ZaynDev";
  pres.title = "Token-Efficient General-Purpose AI Agent";

  // ===== Slide 1 — Title (dark) =====
  let s = pres.addSlide(); s.background = { color: BG_DARK };
  dots(s, 11.15, 0.7);
  eyebrow(s, "AMD DEVELOPER HACKATHON: ACT II   ·   TRACK 1", 0.85, 1.5);
  s.addText([
    { text: "Token-Efficient", options: { breakLine: true, color: LIGHTTX } },
    { text: "General-Purpose ", options: { color: LIGHTTX } },
    { text: "AI Agent", options: { color: ACCENT } },
  ], { x: 0.8, y: 2.05, w: 11.7, h: 2.1, fontFace: "Calibri", fontSize: 54, bold: true, lineSpacingMultiple: 0.98, margin: 0 });
  s.addText("One agent. Eight task categories. The fewest tokens on the leaderboard.",
    { x: 0.85, y: 4.35, w: 11, h: 0.5, fontFace: "Calibri", fontSize: 19, color: MUTED_LT, margin: 0 });
  s.addText([
    { text: "Team ZaynDev", options: { color: LIGHTTX, bold: true } },
    { text: "   ·   Nairobi, Kenya   ·   github.com/paulandrew12/zayndev-amd-act2-agent", options: { color: MUTED_LT } },
  ], { x: 0.85, y: 6.5, w: 12, h: 0.4, fontFace: "Calibri", fontSize: 13, margin: 0 });

  // ===== Slide 2 — The Challenge (light) =====
  s = pres.addSlide(); s.background = { color: BG_LIGHT };
  eyebrow(s, "THE CHALLENGE", 0.85, 0.7);
  s.addText("One agent, eight jobs, judged on tokens", { x: 0.8, y: 1.05, w: 8.4, h: 1.4, fontFace: "Calibri", fontSize: 33, bold: true, color: INK, margin: 0, valign: "top" });
  s.addText([
    { text: "Track 1 asks for a single agent that handles ", options: {} },
    { text: "eight capability categories", options: { bold: true, color: INK } },
    { text: " — factual Q&A, math, sentiment, summarisation, NER, code debugging, logic, and code generation — using Fireworks-hosted models, shipped as a Docker container.", options: {} },
  ], { x: 0.85, y: 2.5, w: 6.05, h: 2.4, fontFace: "Calibri", fontSize: 16.5, color: SLATE, lineSpacingMultiple: 1.15, margin: 0, valign: "top" });
  // two rule cards on the right
  const rx = 7.35, rw = 5.25;
  card(s, rx, 1.5, rw, 2.35);
  iconCircle(s, rx + 0.35, 1.85, 0.9, INK, "check");
  s.addText("1 · Accuracy gate", { x: rx + 1.45, y: 1.95, w: rw - 1.7, h: 0.4, fontFace: "Calibri", fontSize: 18, bold: true, color: INK, margin: 0 });
  s.addText("An LLM-judge scores every answer. Miss the threshold and you're off the leaderboard entirely.", { x: rx + 1.45, y: 2.4, w: rw - 1.7, h: 1.2, fontFace: "Calibri", fontSize: 14, color: MUTED, lineSpacingMultiple: 1.1, margin: 0, valign: "top" });
  card(s, rx, 4.15, rw, 2.35);
  iconCircle(s, rx + 0.35, 4.5, 0.9, ACCENT, "gauge");
  s.addText("2 · Fewest tokens win", { x: rx + 1.45, y: 4.6, w: rw - 1.7, h: 0.4, fontFace: "Calibri", fontSize: 18, bold: true, color: INK, margin: 0 });
  s.addText("Everyone who clears the gate is then ranked by total tokens. Lowest count takes the prize.", { x: rx + 1.45, y: 5.05, w: rw - 1.7, h: 1.2, fontFace: "Calibri", fontSize: 14, color: MUTED, lineSpacingMultiple: 1.1, margin: 0, valign: "top" });
  s.addText("Pass a binary gate, then win a token race — an objective, leaderboard-scored race.",
    { x: 0.85, y: 5.55, w: 6.05, h: 1.2, fontFace: "Calibri", fontSize: 15, italic: true, color: ACCENT, margin: 0, valign: "top" });

  // ===== Slide 3 — The Insight (dark) =====
  s = pres.addSlide(); s.background = { color: BG_DARK };
  dots(s, 11.2, 0.6);
  eyebrow(s, "THE INSIGHT", 0.85, 0.75);
  s.addText([
    { text: "Token count is dominated by ", options: { color: LIGHTTX } },
    { text: "output verbosity", options: { color: ACCENT } },
    { text: " —\nnot by which model you pick.", options: { color: LIGHTTX } },
  ], { x: 0.8, y: 1.2, w: 11.8, h: 1.7, fontFace: "Calibri", fontSize: 34, bold: true, lineSpacingMultiple: 1.0, margin: 0, valign: "top" });
  s.addText("Left alone, these models “think out loud” before answering. That preamble does two kinds of damage:",
    { x: 0.85, y: 3.15, w: 11.4, h: 0.5, fontFace: "Calibri", fontSize: 16.5, color: MUTED_LT, margin: 0 });
  // two damage cards + a truncated-answer example
  card(s, 0.85, 3.95, 3.55, 2.7, BG_DARK2);
  iconCircle(s, 1.15, 4.28, 0.8, ACCENT, "cut");
  s.addText("Wastes tokens", { x: 1.1, y: 5.2, w: 3.05, h: 0.4, fontFace: "Calibri", fontSize: 17, bold: true, color: LIGHTTX, margin: 0 });
  s.addText("Hundreds of tokens of reasoning you're billed for on every single task.", { x: 1.1, y: 5.65, w: 3.05, h: 1, fontFace: "Calibri", fontSize: 13.5, color: MUTED_LT, lineSpacingMultiple: 1.1, margin: 0 });
  card(s, 4.6, 3.95, 3.55, 2.7, BG_DARK2);
  iconCircle(s, 4.9, 4.28, 0.8, "B4442E", "times");
  s.addText("Fails the gate", { x: 4.85, y: 5.2, w: 3.05, h: 0.4, fontFace: "Calibri", fontSize: 17, bold: true, color: LIGHTTX, margin: 0 });
  s.addText("The token cap truncates the reply before the actual answer arrives — an automatic miss.", { x: 4.85, y: 5.65, w: 3.05, h: 1, fontFace: "Calibri", fontSize: 13.5, color: MUTED_LT, lineSpacingMultiple: 1.1, margin: 0 });
  card(s, 8.35, 3.95, 4.1, 2.7, "0E1017");
  s.addText("classify sentiment →", { x: 8.6, y: 4.2, w: 3.6, h: 0.35, fontFace: "Courier New", fontSize: 11.5, color: MUTED_LT, margin: 0 });
  s.addText("“The user wants me to classify the\nsentiment. Let me analyze each\nclause for emotional valence…”", { x: 8.6, y: 4.6, w: 3.65, h: 1.2, fontFace: "Courier New", fontSize: 12.5, color: "C7CBD6", lineSpacingMultiple: 1.15, margin: 0, valign: "top" });
  s.addText([{ text: "✗ truncated — no label — ", options: { color: "FF7A62" } }, { text: "FAIL", options: { color: "FF7A62", bold: true } }],
    { x: 8.6, y: 6.02, w: 3.65, h: 0.4, fontFace: "Courier New", fontSize: 12.5, margin: 0 });

  // ===== Slide 4 — Architecture (light) =====
  s = pres.addSlide(); s.background = { color: BG_LIGHT };
  eyebrow(s, "ARCHITECTURE", 0.85, 0.7);
  s.addText("A three-stage pipeline", { x: 0.8, y: 1.05, w: 10, h: 0.9, fontFace: "Calibri", fontSize: 33, bold: true, color: INK, margin: 0 });
  const stages = [
    ["route", GREEN, "Zero-token router", "Pure-regex classifier sorts each task into one of 8 categories. No LLM call — costs 0 tokens.", "0 tokens"],
    ["layers", INK, "Model per category", "Reads ALLOWED_MODELS at runtime and picks the strongest allowed model for that category.", "best fit"],
    ["bolt", ACCENT, "Answer-only prompt", "A terse, category-specific prompt forbids preamble; a tight cap backstops truncation.", "fewest tokens"],
  ];
  const cw = 3.75, gap = 0.42; let cx = 0.85;
  stages.forEach((st, i) => {
    card(s, cx, 2.15, cw, 3.35);
    iconCircle(s, cx + 0.35, 2.5, 0.85, st[1], st[0]);
    s.addText(`0${i + 1}`, { x: cx + cw - 1.05, y: 2.5, w: 0.8, h: 0.6, fontFace: "Calibri", fontSize: 30, bold: true, color: "E4E6EC", align: "right", margin: 0 });
    s.addText(st[2], { x: cx + 0.35, y: 3.55, w: cw - 0.7, h: 0.5, fontFace: "Calibri", fontSize: 18.5, bold: true, color: INK, margin: 0 });
    s.addText(st[3], { x: cx + 0.35, y: 4.1, w: cw - 0.7, h: 1.1, fontFace: "Calibri", fontSize: 14, color: MUTED, lineSpacingMultiple: 1.12, margin: 0, valign: "top" });
    s.addText(st[4], { x: cx + 0.35, y: 5.0, w: cw - 0.7, h: 0.35, fontFace: "Calibri", fontSize: 13, bold: true, color: st[1] === INK ? SLATE : st[1], margin: 0 });
    if (i < 2) s.addText("→", { x: cx + cw - 0.02, y: 3.35, w: gap, h: 0.9, fontFace: "Calibri", fontSize: 26, bold: true, color: MUTED_LT, align: "center", margin: 0 });
    cx += cw + gap;
  });
  s.addText([
    { text: "Container contract:  ", options: { bold: true, color: INK } },
    { text: "reads /input/tasks.json  →  writes /output/results.json  ·  runs tasks concurrently within the 10-minute budget", options: { color: MUTED } },
  ], { x: 0.85, y: 5.95, w: 11.7, h: 0.5, fontFace: "Calibri", fontSize: 14, margin: 0 });

  // ===== Slide 5 — Three levers (light) =====
  s = pres.addSlide(); s.background = { color: BG_LIGHT };
  eyebrow(s, "WHY IT'S EFFICIENT", 0.85, 0.7);
  s.addText("Three levers, one goal: fewer tokens", { x: 0.8, y: 1.05, w: 11, h: 0.9, fontFace: "Calibri", fontSize: 33, bold: true, color: INK, margin: 0 });
  const levers = [
    ["route", GREEN, "Zero-token routing", "Classification is pure regex. Competitors who route with an LLM call pay for it twice — the routing call plus the answer."],
    ["cut", ACCENT, "Preamble suppression", "Answer-only prompts cut the chain-of-thought that inflates every response — the single biggest lever on the score."],
    ["scale", INK, "Strongest model, per task", "Accuracy headroom is free under the gate. We spend tokens on the answer, never on a model hedging or second-guessing."],
  ];
  let ly = 2.15;
  levers.forEach((lv) => {
    card(s, 0.85, ly, 11.65, 1.42);
    iconCircle(s, 1.2, ly + 0.31, 0.8, lv[1], lv[0]);
    s.addText(lv[2], { x: 2.35, y: ly + 0.24, w: 3.5, h: 0.9, fontFace: "Calibri", fontSize: 18.5, bold: true, color: INK, margin: 0, valign: "middle" });
    s.addText(lv[3], { x: 6.0, y: ly + 0.2, w: 6.25, h: 1.05, fontFace: "Calibri", fontSize: 13.8, color: MUTED, lineSpacingMultiple: 1.1, margin: 0, valign: "middle" });
    ly += 1.62;
  });

  // ===== Slide 6 — Results (dark, stats) =====
  s = pres.addSlide(); s.background = { color: BG_DARK };
  eyebrow(s, "VALIDATED END-TO-END, LIVE", 0.85, 0.7);
  s.addText("The pipeline runs — and we can measure it", { x: 0.8, y: 1.05, w: 11.5, h: 0.9, fontFace: "Calibri", fontSize: 32, bold: true, color: LIGHTTX, margin: 0 });
  const stats = [
    ["98%", "router accuracy\n(0 tokens spent)", GREEN],
    ["95%", "task accuracy, live\non public models", LIGHTTX],
    ["0", "tokens spent\nrouting each task", ACCENT],
    ["48MB", "image  ·  <60s start\n(limit 10GB)", LIGHTTX],
  ];
  let sx = 0.7; const sw = 2.72, sgap = 0.35;
  stats.forEach((stt) => {
    card(s, sx, 2.35, sw, 2.9, BG_DARK2);
    s.addText(stt[0], { x: sx + 0.15, y: 2.7, w: sw - 0.3, h: 1.2, fontFace: "Calibri", fontSize: 50, bold: true, color: stt[2], align: "center", margin: 0, valign: "middle" });
    s.addText(stt[1], { x: sx + 0.15, y: 4.05, w: sw - 0.3, h: 1.0, fontFace: "Calibri", fontSize: 13.5, color: MUTED_LT, align: "center", lineSpacingMultiple: 1.12, margin: 0, valign: "top" });
    sx += sw + sgap;
  });
  s.addText([
    { text: "Full 40-task eval, real Fireworks API, real token counts. ", options: { color: MUTED_LT } },
    { text: "Final leaderboard tokens are tuned on the hackathon's own models.", options: { color: LIGHTTX, italic: true } },
  ], { x: 0.85, y: 5.65, w: 11.7, h: 0.6, fontFace: "Calibri", fontSize: 14.5, margin: 0 });

  // ===== Slide 7 — The edge (light, comparison) =====
  s = pres.addSlide(); s.background = { color: BG_LIGHT };
  eyebrow(s, "THE EDGE", 0.85, 0.7);
  s.addText("Most entries optimise the wrong thing", { x: 0.8, y: 1.05, w: 11.5, h: 0.9, fontFace: "Calibri", fontSize: 33, bold: true, color: INK, margin: 0 });
  // common approach
  card(s, 0.85, 2.15, 5.7, 4.05);
  s.addText("The common approach", { x: 1.15, y: 2.45, w: 5.1, h: 0.4, fontFace: "Calibri", fontSize: 17, bold: true, color: MUTED, margin: 0 });
  s.addText([
    { text: "Fine-tune a router to pick a cheap vs. expensive model", options: { bullet: true, breakLine: true } },
    { text: "Send the raw task prompt straight to the model", options: { bullet: true, breakLine: true } },
    { text: "Let the model answer however verbosely it likes", options: { bullet: true, breakLine: true } },
    { text: "Result: output length quietly dominates the token bill", options: { bullet: true } },
  ], { x: 1.15, y: 3.05, w: 5.1, h: 2.9, fontFace: "Calibri", fontSize: 15, color: SLATE, lineSpacingMultiple: 1.15, paraSpaceAfter: 10, margin: 0, valign: "top" });
  // ours
  card(s, 6.9, 2.15, 5.6, 4.05);
  s.addText("Ours", { x: 7.2, y: 2.45, w: 5, h: 0.4, fontFace: "Calibri", fontSize: 17, bold: true, color: ACCENT, margin: 0 });
  s.addText([
    { text: "Route for free — regex, zero tokens, no second call", options: { bullet: true, breakLine: true } },
    { text: "Per-category answer-only prompts kill the preamble", options: { bullet: true, breakLine: true } },
    { text: "Attack the real cost: how long the answer is", options: { bullet: true, breakLine: true } },
    { text: "Strongest allowed model — accuracy headroom is free", options: { bullet: true } },
  ], { x: 7.2, y: 3.05, w: 5.0, h: 2.9, fontFace: "Calibri", fontSize: 15, color: INK, lineSpacingMultiple: 1.15, paraSpaceAfter: 10, margin: 0, valign: "top" });
  s.addText("A fancy router can tie “always use the cheap model.” The untapped lever is verbosity.",
    { x: 0.85, y: 6.45, w: 11.7, h: 0.5, fontFace: "Calibri", fontSize: 14.5, italic: true, color: MUTED, margin: 0, align: "center" });

  // ===== Slide 8 — Engineering (light, grid) =====
  s = pres.addSlide(); s.background = { color: BG_LIGHT };
  eyebrow(s, "ENGINEERING", 0.85, 0.7);
  s.addText("Built to the spec, built not to break", { x: 0.8, y: 1.05, w: 11.5, h: 0.9, fontFace: "Calibri", fontSize: 33, bold: true, color: INK, margin: 0 });
  const specs = [
    ["chip", "linux/amd64 manifest", "Cross-built for the judging VM — the silent-failure requirement, handled."],
    ["cube", "48MB, <60s cold start", "Tiny image, well under the 10GB cap; ready long before the 60-second limit."],
    ["check", "Contract-perfect I/O", "Always writes valid /output/results.json — malformed output scores zero."],
    ["shield", "Fails gracefully", "Per-task isolation + retries: one bad task can never sink the whole run."],
    ["gauge", "Async concurrency", "Tasks run in parallel, comfortably inside the 10-minute runtime budget."],
    ["code", "MIT & reproducible", "Public repo, clean modules, one-command local test harness."],
  ];
  const gw = 3.75, gh = 1.72, ggx = 0.42, ggy = 0.35; let gx = 0.85, gy = 2.15;
  specs.forEach((sp, i) => {
    card(s, gx, gy, gw, gh);
    iconCircle(s, gx + 0.3, gy + 0.32, 0.72, i % 2 ? ACCENT : INK, sp[0]);
    s.addText(sp[1], { x: gx + 1.2, y: gy + 0.22, w: gw - 1.4, h: 0.55, fontFace: "Calibri", fontSize: 15.5, bold: true, color: INK, margin: 0, valign: "middle" });
    s.addText(sp[2], { x: gx + 0.3, y: gy + 0.92, w: gw - 0.55, h: 0.7, fontFace: "Calibri", fontSize: 12.8, color: MUTED, lineSpacingMultiple: 1.08, margin: 0, valign: "top" });
    gx += gw + ggx;
    if (i % 3 === 2) { gx = 0.85; gy += gh + ggy; }
  });

  // ===== Slide 9 — Eval harness (light) =====
  s = pres.addSlide(); s.background = { color: BG_LIGHT };
  eyebrow(s, "DISCIPLINE", 0.85, 0.7);
  s.addText("We measure before we spend a submission", { x: 0.8, y: 1.05, w: 11.5, h: 0.9, fontFace: "Calibri", fontSize: 32, bold: true, color: INK, margin: 0 });
  card(s, 0.85, 2.2, 7.1, 4.0);
  iconCircle(s, 1.2, 2.55, 0.85, GREEN, "flask");
  s.addText("A scoring harness that mirrors the judge", { x: 2.35, y: 2.62, w: 5.4, h: 0.7, fontFace: "Calibri", fontSize: 18, bold: true, color: INK, margin: 0, valign: "middle" });
  s.addText([
    { text: "40 labelled tasks spanning all 8 categories", options: { bullet: true, breakLine: true } },
    { text: "Checkers mirror the accuracy gate — including sandboxed execution of generated code", options: { bullet: true, breakLine: true } },
    { text: "Offline mode (routing + token estimate) and live mode (real accuracy + real tokens)", options: { bullet: true, breakLine: true } },
    { text: "Per-category accuracy and token report on every run", options: { bullet: true } },
  ], { x: 1.2, y: 3.65, w: 6.5, h: 2.4, fontFace: "Calibri", fontSize: 14.5, color: SLATE, lineSpacingMultiple: 1.12, paraSpaceAfter: 9, margin: 0, valign: "top" });
  card(s, 8.25, 2.2, 4.25, 4.0, BG_DARK);
  s.addText("10", { x: 8.5, y: 2.9, w: 3.75, h: 1.1, fontFace: "Calibri", fontSize: 60, bold: true, color: ACCENT, align: "center", margin: 0 });
  s.addText("submissions per hour", { x: 8.5, y: 4.05, w: 3.75, h: 0.4, fontFace: "Calibri", fontSize: 15, bold: true, color: LIGHTTX, align: "center", margin: 0 });
  s.addText("So we don't waste them guessing. Every submission is a measured step, not a shot in the dark.", { x: 8.55, y: 4.6, w: 3.65, h: 1.3, fontFace: "Calibri", fontSize: 13.5, color: MUTED_LT, align: "center", lineSpacingMultiple: 1.15, margin: 0, valign: "top" });

  // ===== Slide 10 — Closing (dark) =====
  s = pres.addSlide(); s.background = { color: BG_DARK };
  dots(s, 0.85, 0.75);
  dots(s, 11.15, 5.9);
  s.addText([
    { text: "Pass the gate.\n", options: { color: LIGHTTX } },
    { text: "Spend the fewest tokens.", options: { color: ACCENT } },
  ], { x: 0.8, y: 2.35, w: 11.7, h: 2.0, fontFace: "Calibri", fontSize: 46, bold: true, align: "center", lineSpacingMultiple: 1.05, margin: 0 });
  s.addText("A general-purpose agent engineered for one number: total tokens.",
    { x: 0.8, y: 4.45, w: 11.7, h: 0.5, fontFace: "Calibri", fontSize: 18, color: MUTED_LT, align: "center", margin: 0 });
  s.addText([
    { text: "Team ZaynDev", options: { color: LIGHTTX, bold: true } },
    { text: "   ·   Track 1   ·   github.com/paulandrew12/zayndev-amd-act2-agent", options: { color: MUTED_LT } },
  ], { x: 0.8, y: 6.4, w: 11.7, h: 0.4, fontFace: "Calibri", fontSize: 13.5, align: "center", margin: 0 });

  await pres.writeFile({ fileName: "/Users/Zayn/projects/amd-hackathon/deck/ZaynDev-Track1.pptx" });
  console.log("deck written");
}
build().catch(e => { console.error(e); process.exit(1); });
