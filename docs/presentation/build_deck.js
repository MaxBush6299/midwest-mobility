/* MMC Demo — Solution Overview deck. pptxgenjs 4.x */
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa6");

// ---------- palette (industrial Azure) ----------
const NAVY = "0B2942", AZURE = "1B6CA8", TEAL = "2A9D8F",
      AMBER = "E9A23B", LIGHT = "F4F7FB", CARD = "FFFFFF",
      INK = "16242F", MUTED = "5A6B7B", LINE = "DCE5EF", WHITE = "FFFFFF";
const HF = "Trebuchet MS", BF = "Calibri";

async function icon(IconComponent, color = "#FFFFFF", size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) }));
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}
const mkShadow = () => ({ type: "outer", color: "0B2942", blur: 9, offset: 3, angle: 90, opacity: 0.14 });

(async () => {
  const I = {
    brain: await icon(fa.FaBrain, "#FFFFFF"),
    robot: await icon(fa.FaRobot, "#FFFFFF"),
    db: await icon(fa.FaDatabase, "#FFFFFF"),
    users: await icon(fa.FaPeopleGroup, "#1B6CA8"),
    layers: await icon(fa.FaLayerGroup, "#2A9D8F"),
    table: await icon(fa.FaTableCells, "#E9A23B"),
    bolt: await icon(fa.FaBolt, "#E9A23B"),
    industry: await icon(fa.FaIndustry, "#FFFFFF"),
    book: await icon(fa.FaBookOpen, "#FFFFFF"),
    flow: await icon(fa.FaDiagramProject, "#FFFFFF"),
    check: await icon(fa.FaCircleCheck, "#2A9D8F"),
    plug: await icon(fa.FaPlug, "#1B6CA8"),
    eye: await icon(fa.FaEye, "#E9A23B"),
  };

  const p = new pptxgen();
  p.defineLayout({ name: "W", width: 13.333, height: 7.5 });
  p.layout = "W";
  p.author = "Microsoft · MMC demo";
  p.title = "MMC Multi-Agent Manufacturing Assistant";
  const W = 13.333, H = 7.5;

  // ---------- helpers ----------
  function kicker(s, txt, x, y, color = AMBER) {
    s.addShape(p.shapes.RECTANGLE, { x, y: y + 0.02, w: 0.22, h: 0.22, fill: { color } });
    s.addText(txt.toUpperCase(), { x: x + 0.32, y: y - 0.07, w: 9, h: 0.36, margin: 0,
      fontFace: HF, fontSize: 12, bold: true, color: color, charSpacing: 3, valign: "middle" });
  }
  function title(s, txt, x, y, w, color = INK, size = 30) {
    s.addText(txt, { x, y, w, h: 0.9, margin: 0, fontFace: HF, fontSize: size, bold: true,
      color, align: "left", valign: "top", lineSpacingMultiple: 0.98 });
  }
  function footer(s, n) {
    s.addText("Midwest Mobility Components  ·  Multi-Agent Manufacturing Demo", {
      x: 0.6, y: H - 0.42, w: 9, h: 0.3, margin: 0, fontFace: BF, fontSize: 9, color: MUTED });
    s.addText(String(n).padStart(2, "0"), { x: W - 1.1, y: H - 0.42, w: 0.5, h: 0.3, margin: 0,
      fontFace: HF, fontSize: 10, bold: true, color: AZURE, align: "right" });
  }
  function iconChip(s, data, x, y, d, fill, noShadow) {
    const opts = { x, y, w: d, h: d, fill: { color: fill } };
    if (!noShadow) opts.shadow = mkShadow();
    s.addShape(p.shapes.OVAL, opts);
    const pad = d * 0.26;
    s.addImage({ data, x: x + pad, y: y + pad, w: d - pad * 2, h: d - pad * 2 });
  }

  // ============ SLIDE 1 — TITLE ============
  let s = p.addSlide();
  s.background = { color: NAVY };
  // motif: amber tab + faint right band
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.14, fill: { color: AMBER } });
  s.addShape(p.shapes.RECTANGLE, { x: 9.7, y: 0.14, w: W - 9.7, h: H - 0.14, fill: { color: "0E3252" } });
  iconChip(s, I.industry, 10.95, 2.65, 1.5, AZURE);
  iconChip(s, I.robot, 10.05, 4.15, 1.1, TEAL);
  iconChip(s, I.flow, 11.7, 4.2, 1.0, AMBER);

  s.addText("AZURE AI FOUNDRY  ·  MULTI-AGENT REFERENCE SOLUTION", {
    x: 0.7, y: 1.5, w: 8.6, h: 0.4, margin: 0, fontFace: HF, fontSize: 13, bold: true,
    color: AMBER, charSpacing: 3 });
  s.addText("MMC Multi-Agent\nManufacturing Assistant", {
    x: 0.65, y: 2.05, w: 9, h: 2.1, margin: 0, fontFace: HF, fontSize: 46, bold: true,
    color: WHITE, lineSpacingMultiple: 1.0 });
  s.addText([
    { text: "A Magentic manager turns one plant-floor question into a plan — then dispatches a network of ", options: {} },
    { text: "10 portal-managed Foundry prompt agents", options: { bold: true, color: "CADCFC" } },
    { text: " grounded in policy docs and ", options: {} },
    { text: "live Azure SQL rows.", options: { bold: true, color: "CADCFC" } },
  ], { x: 0.7, y: 4.35, w: 8.6, h: 1.1, margin: 0, fontFace: BF, fontSize: 16, color: "Afo".replace("Afo","C8D6E5"), lineSpacingMultiple: 1.12 });
  s.addText("Solution Overview  ·  v1.0  ·  June 2026", {
    x: 0.7, y: 6.6, w: 8, h: 0.4, margin: 0, fontFace: BF, fontSize: 12, color: "8FA6BC" });

  // ============ SLIDE 2 — WHAT IT IS ============
  s = p.addSlide();
  s.background = { color: LIGHT };
  kicker(s, "What it is", 0.6, 0.6);
  title(s, "One question in. A cited, ledger-grounded answer out.", 0.6, 1.0, 8.3, INK, 27);
  s.addText([
    { text: "A user asks a real manufacturing question", options: { bold: true } },
    { text: " — e.g. \u201Can open PO for a brake-caliper part is flagged At Risk; which Plant 7 Line 1 PM tasks use it, and is there a backup supplier?\u201D", options: {} },
  ], { x: 0.6, y: 2.0, w: 7.4, h: 1.0, margin: 0, fontFace: BF, fontSize: 14.5, color: INK, lineSpacingMultiple: 1.12 });
  s.addText([
    { text: "A Magentic manager decomposes it into a plan, picks the right specialists from a pool of 10 agents, dispatches them in sequence or parallel, watches every output, replans when a path dead-ends, and synthesizes a final answer ", options: {} },
    { text: "with citations down to the individual SQL row.", options: { bold: true, color: AZURE } },
  ], { x: 0.6, y: 3.05, w: 7.4, h: 1.6, margin: 0, fontFace: BF, fontSize: 14.5, color: MUTED, lineSpacingMultiple: 1.18 });
  s.addText("Every plan, hop, and replan streams live to a FastAPI + SSE trace UI — the orchestration is watchable in real time.", {
    x: 0.6, y: 4.75, w: 7.4, h: 0.9, margin: 0, fontFace: BF, italic: true, fontSize: 13, color: TEAL, lineSpacingMultiple: 1.1 });

  // stat rail (right)
  const stats = [
    { n: "10", l: "portal-managed\nFoundry prompt agents", c: AZURE, ic: I.users },
    { n: "2", l: "Azure AI Foundry\nprojects (plant + ent.)", c: TEAL, ic: I.layers },
    { n: "283", l: "live SQL rows across\n5 change-tracked tables", c: AMBER, ic: I.table },
  ];
  let sy = 1.05;
  stats.forEach(st => {
    s.addShape(p.shapes.RECTANGLE, { x: 8.5, y: sy, w: 4.2, h: 1.7, fill: { color: CARD }, line: { color: LINE, width: 1 }, shadow: mkShadow() });
    s.addShape(p.shapes.RECTANGLE, { x: 8.5, y: sy, w: 0.12, h: 1.7, fill: { color: st.c } });
    s.addImage({ data: st.ic, x: 11.7, y: sy + 0.3, w: 0.72, h: 0.72 });
    s.addText(st.n, { x: 8.8, y: sy + 0.18, w: 2.8, h: 0.95, margin: 0, fontFace: HF, fontSize: 44, bold: true, color: st.c, valign: "middle" });
    s.addText(st.l, { x: 8.82, y: sy + 1.02, w: 3.6, h: 0.6, margin: 0, fontFace: BF, fontSize: 11.5, color: MUTED, lineSpacingMultiple: 0.98 });
    sy += 1.92;
  });
  footer(s, 2);

  // ============ SLIDE 3 — THREE TIERS ============
  s = p.addSlide();
  s.background = { color: LIGHT };
  kicker(s, "How it works", 0.6, 0.6);
  title(s, "Three tiers, one source of truth", 0.6, 1.0, 11, INK, 28);
  s.addText("Everything below derives from a single profile.yaml — agents, knowledge sources, and tools all live in one place.", {
    x: 0.6, y: 1.62, w: 12, h: 0.4, margin: 0, fontFace: BF, fontSize: 13, color: MUTED });

  const tiers = [
    { ic: I.brain, c: AZURE, t: "Orchestrator", st: "Magentic manager",
      b: ["Decomposes the question into a plan", "Dispatches agents, watches the ledger, replans", "Manager (gpt-5.4) + workers (gpt-5.4-mini) on separate deployments"] },
    { ic: I.robot, c: TEAL, t: "Agents", st: "10 Foundry prompt agents",
      b: ["Portal-managed PromptAgentDefinitions — visible & editable in Foundry", "5 plant + 5 enterprise specialists", "Foundry IQ knowledge baked in as an MCP tool"] },
    { ic: I.db, c: AMBER, t: "Knowledge", st: "Foundry IQ + Azure SQL",
      b: ["Policy docs (SOPs, OEM manuals) via doc index", "Live operational rows via IndexedSqlKnowledgeSource", "Managed-identity auth + SQL change tracking"] },
  ];
  let tx = 0.6;
  const tw = 3.92, gap = 0.28;
  tiers.forEach((ti, i) => {
    const y0 = 2.25, hh = 4.35;
    s.addShape(p.shapes.RECTANGLE, { x: tx, y: y0, w: tw, h: hh, fill: { color: CARD }, line: { color: LINE, width: 1 }, shadow: mkShadow() });
    s.addShape(p.shapes.RECTANGLE, { x: tx, y: y0, w: tw, h: 0.1, fill: { color: ti.c } });
    iconChip(s, ti.ic, tx + 0.32, y0 + 0.4, 1.0, ti.c);
    s.addText(`TIER ${i + 1}`, { x: tx + 1.5, y: y0 + 0.45, w: tw - 1.6, h: 0.3, margin: 0, fontFace: HF, fontSize: 11, bold: true, color: ti.c, charSpacing: 2 });
    s.addText(ti.t, { x: tx + 1.5, y: y0 + 0.72, w: tw - 1.6, h: 0.5, margin: 0, fontFace: HF, fontSize: 22, bold: true, color: INK });
    s.addText(ti.st, { x: tx + 0.34, y: y0 + 1.6, w: tw - 0.6, h: 0.35, margin: 0, fontFace: BF, italic: true, fontSize: 12.5, color: ti.c });
    s.addText(ti.b.map(t => ({ text: t, options: { bullet: { code: "2022", indent: 14 }, breakLine: true, paraSpaceAfter: 9 } })),
      { x: tx + 0.34, y: y0 + 2.05, w: tw - 0.62, h: 2.1, margin: 0, fontFace: BF, fontSize: 12.5, color: MUTED, lineSpacingMultiple: 1.0 });
    tx += tw + gap;
  });
  footer(s, 3);

  // ============ SLIDE 4 — ARCHITECTURE ============
  s = p.addSlide();
  s.background = { color: WHITE };
  kicker(s, "Architecture", 0.6, 0.5);
  title(s, "Solution architecture — Container view (C4 L2)", 0.6, 0.9, 12, INK, 24);
  // diagram (1895 x 1190 -> aspect 1.5924)
  const aw = 11.7, ah = aw / (1895 / 1190);
  s.addImage({ path: "mmc-arch.png", x: (W - aw) / 2, y: 1.62, w: aw, h: ah });
  s.addShape(p.shapes.RECTANGLE, { x: (W - aw) / 2, y: 1.62, w: aw, h: ah, fill: { type: "none" }, line: { color: LINE, width: 1 } });
  footer(s, 4);

  // ============ SLIDE 5 — AGENT NETWORK ============
  s = p.addSlide();
  s.background = { color: LIGHT };
  kicker(s, "The agent network", 0.6, 0.6);
  title(s, "Ten specialists across two Foundry projects", 0.6, 1.0, 12, INK, 27);

  const cols = [
    { head: "mmc-plant", sub: "Plant 7 floor operations", c: AZURE, ic: I.industry,
      rows: [["plant7-ehs", "EHS · machine guarding · incidents"], ["plant7-maintenance", "PM schedules · work orders"], ["plant7-quality", "NCR/CAPA · QA specs"], ["plant7-shiftops", "changeover · shift handover"], ["plant7-training", "LOTO certs · competency"]] },
    { head: "mmc-enterprise", sub: "Cross-plant enterprise functions", c: TEAL, ic: I.flow,
      rows: [["ent-supply-chain", "suppliers · logistics · BOM"], ["ent-procurement", "POs · contracts · should-cost"], ["ent-engineering-plm", "ECOs · part numbering"], ["ent-quality", "warranty · recall thresholds"], ["ent-demand-program", "OEM programs · allocation"]] },
  ];
  let cx = 0.6;
  cols.forEach(col => {
    const cw = 6.0, y0 = 1.95;
    s.addShape(p.shapes.RECTANGLE, { x: cx, y: y0, w: cw, h: 4.7, fill: { color: CARD }, line: { color: LINE, width: 1 }, shadow: mkShadow() });
    s.addShape(p.shapes.RECTANGLE, { x: cx, y: y0, w: cw, h: 0.92, fill: { color: col.c } });
    s.addImage({ data: col.ic, x: cx + 0.32, y: y0 + 0.26, w: 0.42, h: 0.42 });
    s.addText(col.head, { x: cx + 0.92, y: y0 + 0.14, w: cw - 1, h: 0.4, margin: 0, fontFace: HF, fontSize: 19, bold: true, color: WHITE });
    s.addText(col.sub, { x: cx + 0.92, y: y0 + 0.53, w: cw - 1, h: 0.3, margin: 0, fontFace: BF, fontSize: 11.5, color: "E8F1F8" });
    let ry = y0 + 1.12;
    col.rows.forEach((r, i) => {
      if (i % 2 === 1) s.addShape(p.shapes.RECTANGLE, { x: cx + 0.18, y: ry - 0.04, w: cw - 0.36, h: 0.68, fill: { color: LIGHT } });
      s.addText(r[0], { x: cx + 0.34, y: ry, w: 2.5, h: 0.6, margin: 0, fontFace: "Consolas", fontSize: 12.5, bold: true, color: col.c, valign: "middle" });
      s.addText(r[1], { x: cx + 2.7, y: ry, w: cw - 2.9, h: 0.6, margin: 0, fontFace: BF, fontSize: 11.5, color: MUTED, valign: "middle" });
      ry += 0.7;
    });
    cx += cw + 0.7;
  });
  s.addText("The orchestrator merges both pools into one participant set of up to 10 — each scenario whitelists only the agents it needs.", {
    x: 0.6, y: 6.78, w: 12.1, h: 0.35, margin: 0, fontFace: BF, italic: true, fontSize: 12, color: MUTED });
  footer(s, 5);

  // ============ SLIDE 6 — GROUNDING ============
  s = p.addSlide();
  s.background = { color: LIGHT };
  kicker(s, "Grounded in truth", 0.6, 0.6);
  title(s, "Two kinds of knowledge, deliberately split", 0.6, 1.0, 12, INK, 27);

  const kcards = [
    { c: AZURE, ic: I.book, t: "Policy documents", st: "searchIndex · doc indexer",
      b: ["SOPs, OEM manuals, regulatory & quality docs", "Markdown / PDF pushed to Azure AI Search", "Answers the \u201Chow / why / per-procedure\u201D questions"] },
    { c: AMBER, ic: I.table, t: "Operational rows", st: "IndexedSqlKnowledgeSource",
      b: ["Training, PM, incidents, suppliers, POs", "Indexed live from Azure SQL, PK as document key", "Returns discrete, cited rows — listed verbatim"] },
  ];
  let kx = 0.6;
  kcards.forEach(k => {
    const kw = 6.0, y0 = 1.95, kh = 3.1;
    s.addShape(p.shapes.RECTANGLE, { x: kx, y: y0, w: kw, h: kh, fill: { color: CARD }, line: { color: LINE, width: 1 }, shadow: mkShadow() });
    s.addShape(p.shapes.RECTANGLE, { x: kx, y: y0, w: 0.12, h: kh, fill: { color: k.c } });
    iconChip(s, k.ic, kx + 0.35, y0 + 0.34, 0.95, k.c);
    s.addText(k.t, { x: kx + 1.5, y: y0 + 0.36, w: kw - 1.6, h: 0.45, margin: 0, fontFace: HF, fontSize: 20, bold: true, color: INK });
    s.addText(k.st, { x: kx + 1.5, y: y0 + 0.82, w: kw - 1.6, h: 0.32, margin: 0, fontFace: "Consolas", fontSize: 12, color: k.c });
    s.addText(k.b.map(t => ({ text: t, options: { bullet: { code: "2022", indent: 14 }, breakLine: true, paraSpaceAfter: 8 } })),
      { x: kx + 0.4, y: y0 + 1.5, w: kw - 0.7, h: 1.45, margin: 0, fontFace: BF, fontSize: 12.5, color: MUTED, lineSpacingMultiple: 1.0 });
    kx += kw + 0.7;
  });
  // insight callout
  s.addShape(p.shapes.RECTANGLE, { x: 0.6, y: 5.35, w: 12.1, h: 1.45, fill: { color: NAVY }, shadow: mkShadow() });
  s.addShape(p.shapes.RECTANGLE, { x: 0.6, y: 5.35, w: 0.14, h: 1.45, fill: { color: AMBER } });
  s.addImage({ data: I.eye, x: 0.95, y: 5.72, w: 0.7, h: 0.7 });
  s.addText("Why split docs from rows?", { x: 1.85, y: 5.55, w: 10.6, h: 0.4, margin: 0, fontFace: HF, fontSize: 15, bold: true, color: AMBER });
  s.addText("When the same data lived in both, the agent paraphrased a doc chunk instead of citing the row — and replanned to max_rounds. Splitting row data into a SQL knowledge source made retrieval return exact, cited rows. That one change made the demo trustworthy.", {
    x: 1.85, y: 5.92, w: 10.6, h: 0.8, margin: 0, fontFace: BF, fontSize: 12.5, color: "D5E2F0", lineSpacingMultiple: 1.05 });
  footer(s, 6);

  // ============ SLIDE 7 — SCENARIOS ============
  s = p.addSlide();
  s.background = { color: LIGHT };
  kicker(s, "Demo scenarios", 0.6, 0.6);
  title(s, "From a one-agent spot-check to a ten-agent fan-out", 0.6, 1.0, 12.2, INK, 26);

  const head = ["Scenario", "What it shows", "Agents", "Scale"];
  const data = [
    ["training_gap", "LOTO certs expiring — cites Training_Log rows", "1", "~1 hop"],
    ["po_status", "Open POs flagged At Risk — cites po_spend rows", "1", "~1 hop"],
    ["pm_check", "Line 1 PMs with follow-up work orders this quarter", "1", "~1 hop"],
    ["supplier_risk_pm", "At-risk PO \u2192 dependent PMs \u2192 backup supplier (cross-KB)", "3", "6\u201310 hops"],
    ["loto_cluster", "Cluster L1 Press near-misses \u2192 escalate to ent. quality", "5\u20136", "~15 hops"],
    ["brake_caliper", "Full fan-out: delay impact, mitigation, cost + replan", "10", "~30 hops"],
  ];
  const rowsTbl = [head.map((h, i) => ({ text: h, options: {
    fill: { color: NAVY }, color: WHITE, bold: true, fontFace: HF, fontSize: 13,
    align: i >= 2 ? "center" : "left", valign: "middle", margin: [4, 6, 4, 6] } }))];
  data.forEach((r, ri) => {
    const hl = ri === 3 || ri === 5;
    rowsTbl.push(r.map((c, ci) => ({ text: c, options: {
      fill: { color: hl ? "EAF2F9" : (ri % 2 ? "FFFFFF" : "F7FAFD") },
      color: ci === 0 ? AZURE : INK,
      bold: ci === 0 || (ci >= 2 && hl),
      fontFace: ci === 0 ? "Consolas" : BF,
      fontSize: 12.5, align: ci >= 2 ? "center" : "left", valign: "middle",
      margin: [4, 6, 4, 6] } })));
  });
  s.addTable(rowsTbl, { x: 0.6, y: 1.95, w: 12.13, colW: [2.5, 6.43, 1.4, 1.8],
    rowH: [0.5, 0.62, 0.62, 0.62, 0.62, 0.62, 0.62], border: { type: "solid", pt: 0.5, color: LINE } });
  s.addText([
    { text: "Same code, same agents, same data. ", options: { bold: true, color: INK } },
    { text: "Only the participant whitelist and max_rounds change — the network scales from a trivial lookup to a full multi-agent investigation.", options: {} },
  ], { x: 0.6, y: 6.55, w: 12.1, h: 0.5, margin: 0, fontFace: BF, italic: true, fontSize: 12.5, color: MUTED });
  footer(s, 7);

  // ============ SLIDE 8 — WHY IT MATTERS ============
  s = p.addSlide();
  s.background = { color: NAVY };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.14, fill: { color: AMBER } });
  kicker(s, "Why it matters", 0.7, 0.85, AMBER);
  s.addText("A blueprint for trustworthy, watchable agent networks", {
    x: 0.7, y: 1.25, w: 11.8, h: 1.0, margin: 0, fontFace: HF, fontSize: 30, bold: true, color: WHITE, lineSpacingMultiple: 1.0 });

  const takeaways = [
    { ic: I.check, t: "Cited, not paraphrased", d: "Row-level SQL grounding means every claim traces to a specific record — recall thresholds and at-risk POs you can trust." },
    { ic: I.plug, t: "Portal-managed & composable", d: "Agents are Foundry PromptAgentDefinitions, visible and editable in the portal. Add an agent in profile.yaml and re-seed." },
    { ic: I.eye, t: "Watchable orchestration", d: "Plan, every hop, and every replan stream live to the trace UI — the manager's reasoning is observable, not a black box." },
    { ic: I.layers, t: "Scales by configuration", d: "One engine spans a 1-hop spot-check to a 10-agent fan-out. Whitelists and caps keep narrow scenarios narrow." },
  ];
  let bx = 0.7, by = 2.55;
  takeaways.forEach((tk, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x0 = 0.7 + col * 6.15, y0 = 2.55 + row * 1.95;
    s.addShape(p.shapes.RECTANGLE, { x: x0, y: y0, w: 5.9, h: 1.72, fill: { color: "0E3252" }, line: { color: "1C4A72", width: 1 } });
    iconChip(s, tk.ic, x0 + 0.28, y0 + 0.32, 0.92, "13314F", true);
    s.addText(tk.t, { x: x0 + 1.4, y: y0 + 0.28, w: 4.3, h: 0.4, margin: 0, fontFace: HF, fontSize: 16, bold: true, color: WHITE });
    s.addText(tk.d, { x: x0 + 1.4, y: y0 + 0.72, w: 4.35, h: 0.9, margin: 0, fontFace: BF, fontSize: 11.5, color: "B9CCDE", lineSpacingMultiple: 1.04 });
  });
  s.addText("Built on Microsoft Agent Framework · Azure AI Foundry (Agents Service + Foundry IQ) · Azure SQL", {
    x: 0.7, y: 6.75, w: 12, h: 0.4, margin: 0, fontFace: BF, fontSize: 11.5, italic: true, color: "8FA6BC" });

  await p.writeFile({ fileName: "MMC_Demo_Overview.pptx" });
  console.log("WROTE MMC_Demo_Overview.pptx");
})();
