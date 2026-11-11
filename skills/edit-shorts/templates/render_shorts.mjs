// Renders the Shorts graphics (hook titles, end card) for the 9:16 cuts as a transparent PNG sized in 4K canvas pixels.
// Run: node render.mjs   -> out/*.png + out/manifest.json
// C3 Research video: same dark glass cards as the Asgard edits, lime (#CCFF00, the C3 brand) in place of gold.
import { chromium } from "playwright";   // resolves via a node_modules link above this file (PC: junction to market-analyzer; pod: /opt/node)
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Fail loudly if a web font didn't load: Chromium silently swaps in a lookalike otherwise.
// For every element under #c that holds text in a WEB_FONTS family, each character needs a LOADED FontFace of that
// family covering the element's computed weight, style AND the character's unicode-range (Google splits a family
// into subset faces; a loaded Latin face does not cover a failed Greek one). Families outside WEB_FONTS are system
// fonts and are not checked. Keep WEB_FONTS in step with the @import line in CSS.
const WEB_FONTS = ["Space Grotesk", "Inter"];
async function assertFonts(page, label) {
  const bad = await page.evaluate((web) => {
    const ranges = (ur) => (ur || "U+0-10FFFF").split(",").map((r) => {
      const [a, b] = r.trim().replace(/^U\+/i, "").split("-");
      const lo = parseInt(a.replace(/\?/g, "0"), 16), hi = parseInt((b || a).replace(/\?/g, "F"), 16);
      return [lo, hi];
    });
    const faceFor = (f, wt, st) => {
      const [lo, hi = lo] = String(f.weight).trim().split(/\s+/).map(Number);   // "700" or a variable "100 900"
      const italic = f.style !== "normal";
      return wt >= lo && wt <= hi && (st === "normal" ? !italic : italic);
    };
    const out = new Set();
    for (const e of document.querySelectorAll("#c, #c *")) {
      const text = [...e.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join("").replace(/\s/g, "");
      if (!text) continue;
      const cs = getComputedStyle(e);
      const fam = cs.fontFamily.split(",")[0].replace(/["']/g, "").trim();
      if (!web.includes(fam)) continue;
      const wt = Number(cs.fontWeight), st = cs.fontStyle === "normal" ? "normal" : "italic";
      const faces = [...document.fonts].filter((f) => f.family.replace(/["']/g, "") === fam && faceFor(f, wt, st));
      if (!faces.some((f) => f.status === "loaded")) { out.add(`${fam} ${wt}${st === "italic" ? " italic" : ""}`); continue; }
      for (const ch of new Set(text)) {
        const cp = ch.codePointAt(0);
        const cover = faces.filter((f) => ranges(f.unicodeRange).some(([lo, hi]) => cp >= lo && cp <= hi));
        if (cover.length && !cover.some((f) => f.status === "loaded")) out.add(`${fam} ${wt} U+${cp.toString(16).toUpperCase()}`);
      }
    }
    return [...out];
  }, WEB_FONTS);
  if (bad.length) throw new Error(`${label}: web font face not loaded (would fall back): ${bad.join(", ")}`);
}

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, "out_shorts");
const LOGOS = join(HERE, "..", "logos");
mkdirSync(OUT, { recursive: true });

const svgPath = (name) => readFileSync(join(LOGOS, `${name}.svg`), "utf8").match(/<path d="([^"]+)"/)[1];
const icon = (name, color) => `<svg viewBox="0 0 24 24"><path fill="${color}" d="${svgPath(name)}"/></svg>`;
const dataUri = (p) => `data:image/png;base64,${readFileSync(p).toString("base64")}`;

const LIME = "#CCFF00";
const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@500;600;800&display=swap');
html,body{margin:0;background:transparent}
body{font-family:Inter,sans-serif;color:#fff;padding:60px;display:inline-block}
.glass{background:linear-gradient(135deg,rgba(20,20,14,.94),rgba(10,10,8,.94));border:3px solid rgba(255,255,255,.14);
  box-shadow:0 30px 80px rgba(0,0,0,.55),inset 0 2px 0 rgba(255,255,255,.08);border-radius:48px}
.logo{display:flex;align-items:center;gap:44px;padding:36px 64px 36px 36px}
.tile{width:200px;height:200px;border-radius:44px;display:grid;place-items:center;flex:none}
.tile svg{width:118px;height:118px}
.name{font-family:'Space Grotesk';font-weight:700;font-size:92px;letter-spacing:-2px;line-height:1}
.sub{font-size:44px;font-weight:600;color:#b4b6a0;margin-top:14px;letter-spacing:.5px}
.chip{display:flex;align-items:center;gap:40px;padding:34px 70px 34px 40px}
.bar{width:14px;height:120px;border-radius:8px;background:linear-gradient(${LIME},#8FD400)}
.idx{font-family:'Space Grotesk';font-weight:700;font-size:64px;color:${LIME}}
.ttl{font-family:'Space Grotesk';font-weight:700;font-size:100px;letter-spacing:4px}
.stat{padding:50px 90px;text-align:center}
.big{font-family:'Space Grotesk';font-weight:700;font-size:150px;letter-spacing:-3px;line-height:1.02}
.small{font-size:54px;font-weight:600;color:#b4b6a0;letter-spacing:6px;margin-top:22px;text-transform:uppercase}
.lime{color:${LIME}}.cyan{color:#5EE7FF}.red{color:#FF5A5F}
.tag{font-size:40px;font-weight:600;color:#d6d8c4;letter-spacing:3px;text-transform:uppercase}
.row{display:flex;gap:44px}
.sub-btn{display:flex;align-items:center;gap:36px;background:#FF0033;border-radius:30px;padding:40px 80px;
  font-family:'Space Grotesk';font-weight:700;font-size:96px;letter-spacing:3px;box-shadow:0 30px 80px rgba(0,0,0,.5)}
.sub-btn svg{width:96px;height:96px}
.steps{display:flex;gap:14px;padding:26px 30px}
.step{width:300px;padding:22px 20px;border-radius:26px;background:rgba(255,255,255,.04);border:3px solid rgba(255,255,255,.08);opacity:.45}
.step.done{opacity:.75}
.step.on{opacity:1;background:linear-gradient(135deg,rgba(204,255,0,.20),rgba(143,212,0,.10));border-color:${LIME};box-shadow:0 0 40px rgba(204,255,0,.35)}
.step .n{font-family:'Space Grotesk';font-weight:700;font-size:44px;color:${LIME}}
.step .t{font-size:40px;font-weight:800;line-height:1.08;margin-top:6px}
.step .w{font-size:30px;font-weight:600;color:#b4b6a0;margin-top:8px}
`;

const logoCard = (tileBg, iconHtml, name, sub) =>
  `<div id="c" class="glass logo"><div class="tile" style="background:${tileBg}">${iconHtml}</div>
   <div><div class="name">${name}</div><div class="sub">${sub}</div></div></div>`;
const imgCard = (src, tileBg, name, sub) =>
  `<div id="c" class="glass logo"><div class="tile" style="background:${tileBg};overflow:hidden"><img src="${src}" style="width:100%;height:100%;object-fit:contain"></div>
   <div><div class="name">${name}</div><div class="sub">${sub}</div></div></div>`;
const chip = (i, t) => `<div id="c" class="glass chip"><div class="bar"></div><div class="idx">${i}</div><div class="ttl">${t}</div></div>`;
const stat = (big, small, cls = "lime") =>
  `<div id="c" class="glass stat"><div class="big ${cls}">${big}</div><div class="small">${small}</div></div>`;
const PNG = (f) => dataUri(join(LOGOS, f));
const C3 = readFileSync(join(LOGOS, "mark.svg"), "utf8").replace(/<svg /, '<svg width="150" height="150" ');
const c3Card = (name, sub) => logoCard("#110E08;border:3px solid #2a2a14", C3, name, sub);

const chainTile = (bg, inner, name) =>
  `<div style="text-align:center"><div class="tile" style="background:${bg};margin:0 auto">${inner}</div><div class="tag" style="margin-top:16px">${name}</div></div>`;
const CHAINS = [
  ["#627EEA", icon("ethereum", "#fff"), "Ethereum"],
  // Base's official mark is "The Square" (base/brand-kit): white square on Base blue, like the other icon tiles
  ["#0000FF", readFileSync(join(LOGOS, "Base_square_white.svg"), "utf8").replace(/<\?xml[^>]*>/, "").replace(/<svg /, '<svg style="width:96px;height:96px" '), "Base"],
  ["#000;box-shadow:inset 0 0 0 3px #333", icon("solana", "#fff"), "Solana"],
  [LIME, icon("robinhood", "#000"), "Robinhood"],
];
const chainRow = `<div id="c" class="glass" style="padding:44px 60px"><div class="small" style="margin:0 0 30px;text-align:center">Chains supported</div>
  <div class="row">${CHAINS.map((c) => chainTile(...c)).join("")}</div></div>`;

const strip = (items, k) => `<div id="c" class="glass steps">${items.map(([t], i) =>
  `<div class="step ${i + 1 === k ? "on" : i + 1 < k ? "done" : ""}"><div class="n">0${i + 1}</div><div class="t" style="font-size:46px">${t}</div></div>`).join("")}</div>`;
const STEPS = [["Find a token", "DexScreener"], ["Copy the CA", "Contract address"], ["Paste + chain", "On C3 Research"], ["Pay", "SOL, USDT, USDC"], ["Agents research", "Report lands"]];
const STAGES = [["Contract", "Ownership, mint, fees"], ["Liquidity", "Pools, locks, holders"], ["The story", "Links, what people say"], ["Two audits", "Draft, then challenge"], ["Report ready", "Every finding checked"]];

const ff = `<div id="c" class="glass chip"><svg viewBox="0 0 24 24" style="width:110px;height:110px"><path fill="${LIME}" d="M3 5v14l9-7zm9 0v14l9-7z"/></svg>
  <div class="ttl">FAST FORWARD</div><div class="idx" style="font-size:90px">40x</div></div>`;
const bell = `<svg viewBox="0 0 24 24"><path fill="#fff" d="M12 22a2.5 2.5 0 0 0 2.45-2h-4.9A2.5 2.5 0 0 0 12 22Zm7-6V11a7 7 0 0 0-5.5-6.84V3.5a1.5 1.5 0 0 0-3 0v.66A7 7 0 0 0 5 11v5l-2 2v1h18v-1Z"/></svg>`;

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 3840, height: 2160 } });

  const hook = (a, b) => `<div id="c" class="glass" style="padding:56px 80px;text-align:center;max-width:1840px">
     <div class="big" style="font-size:150px;line-height:1.0">${a}</div>
     <div class="small" style="font-size:56px;margin-top:26px;color:${LIME}">${b}</div></div>`;
  // one current-step / current-stage label (Codex audit: one progress system, readable, top of frame)
  const label = (n, t) => `<div id="c" class="glass" style="display:flex;align-items:center;gap:34px;padding:30px 60px 30px 40px">
     <div class="idx" style="font-size:84px">${n}</div><div class="ttl" style="font-size:84px;letter-spacing:2px">${t}</div></div>`;
  const EX = (f) => dataUri(join(HERE, "excerpts", f));
  // a faithful excerpt of the real report, enlarged so it reads on a phone
  const excerpt = (f, tag, w = 1840) => `<div id="c" class="glass" style="padding:34px 40px 40px;width:${w}px">
     <div class="small" style="margin:0 0 22px 6px;font-size:46px;color:${LIME};text-align:left">${tag}</div>
     <img src="${EX(f)}" style="width:100%;border-radius:18px;display:block"></div>`;
  const quote = (q, by) => `<div id="c" class="glass" style="padding:50px 70px;max-width:1800px;text-align:center">
     <div style="font-family:'Space Grotesk';font-weight:700;font-size:92px;line-height:1.12">&ldquo;${q}&rdquo;</div>
     <div class="small" style="font-size:44px;margin-top:24px">${by}</div></div>`;
  // the closing line: the Short's own takeaway, then the site (payoff before CTA)
  const cta = (line) => `<div id="c" class="glass" style="padding:48px 80px;text-align:center;max-width:1840px">
     <div class="big" style="font-size:104px;line-height:1.05">${line}</div>
     <div style="display:flex;align-items:center;gap:26px;justify-content:center;margin-top:30px">${C3.replace('width="150" height="150"', 'width="96" height="96"')}<div class="name" style="font-size:84px">c3research.io</div></div></div>`;
  const assets = {
    "hook-s1": hook(`AI AGENTS <span class="lime">RUG-CHECK</span> YOUR TOKEN`, "Before you buy"),
    "hook-s2": hook(`HOW TO <span class="lime">AUDIT</span> A MEME COIN`, "Step by step, before you buy"),
    "hook-s3": hook(`13 MINUTES OF <span class="lime">AI RESEARCH</span>`, "Here's what came back"),
    "hook-s4": hook(`CHECK THIS <span class="lime">BEFORE</span> YOU AUDIT`, "For C3 Research requests"),
    "hook-s5": hook(`WHAT <span class="lime">"UNVERIFIED"</span> ACTUALLY MEANS`, "In an AI token report"),
    "hook-s6": hook(`WHY REPORTS <span class="lime">EXPIRE</span> IN 7 DAYS`, "Tokens change fast"),
    "step-1": label("1/5", "FIND THE TOKEN"), "step-2": label("2/5", "COPY THE ADDRESS"),
    "step-3": label("3/5", "PASTE IT ON C3"), "step-4": label("4/5", "PAY + CONNECT"), "step-5": label("5/5", "GET THE REPORT"),
    "stage-1": label("1/5", "READING THE CONTRACT"), "stage-2": label("2/5", "FOLLOWING THE LIQUIDITY"),
    "stage-3": label("3/5", "GATHERING THE STORY"), "stage-4": label("4/5", "TWO INDEPENDENT AUDITS"), "stage-5": label("5/5", "REPORT READY"),
    "compressed": `<div id="c" class="glass chip"><svg viewBox="0 0 24 24" style="width:90px;height:90px"><path fill="${LIME}" d="M3 5v14l9-7zm9 0v14l9-7z"/></svg><div class="ttl" style="font-size:80px">13 MIN, TIME COMPRESSED</div></div>`,
    "ex-verdict": excerpt("verdict.png", "FROM THE REPORT · VERDICT"),
    "ex-claim": excerpt("claim.png", "FROM THE REPORT · A CLAIM IT CHECKED"),
    "ex-unknowns": excerpt("unknowns.png", "FROM THE REPORT · WHAT STAYS UNKNOWN"),
    "quote-limits": quote("Limits on this review, not findings against the token.", "C3 Research report, on its unknowns"),
    "card-bonding": `<div id="c" class="glass stat" style="max-width:1840px"><div class="big cyan" style="font-size:130px">BONDING CURVE FIRST</div>
       <div class="small" style="font-size:50px;letter-spacing:3px">Not bonded yet? The audit fails. You get a retry credit.</div></div>`,
    "cta-s1": cta(`Unverified means <span class="lime">not enough evidence</span>`),
    "cta-s2": cta(`Paste a CA. <span class="lime">Get the report.</span>`),
    "cta-s3": cta(`Unverified means <span class="lime">not enough evidence</span>`),
    "cta-s4": cta(`Check the <span class="lime">bonding status</span> first`),
    "cta-s5": cta(`Read what was checked, <span class="lime">and what wasn't</span>`),
    "cta-s6": cta(`Check the <span class="lime">date</span> before you trust a report`),
  };

  const manifest = {};
  for (const [name, html] of Object.entries(assets)) {
    await page.setContent(`<style>${CSS}</style>${html}`, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    await assertFonts(page, name);
    const el = page.locator("#c");
    const file = join(OUT, `${name}.png`);
    // padding around the element keeps the drop shadow inside the PNG
    const box = await el.boundingBox();
    const pad = 60;
    await page.screenshot({ path: file, omitBackground: true,
      clip: { x: Math.max(0, box.x - pad), y: Math.max(0, box.y - pad), width: box.width + pad * 2, height: box.height + pad * 2 } });
    manifest[name] = { w: Math.round(box.width + pad * 2), h: Math.round(box.height + pad * 2) };
    console.log(name, manifest[name]);
  }
  writeFileSync(join(OUT, "manifest.json"), JSON.stringify(manifest, null, 2));
  await browser.close();
}
main().catch((e) => { console.error(e); process.exit(1); });
