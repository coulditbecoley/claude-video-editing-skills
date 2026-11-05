// Renders every on-screen graphic for the edit as a transparent PNG sized in 4K canvas pixels.
// Run: NODE_PATH=<dir with playwright> node render.mjs   -> out/*.png + out/manifest.json
import { chromium } from "file:///~/Code/market-analyzer/node_modules/playwright/index.mjs";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Fail loudly if a web font didn't load: Chromium silently swaps in a lookalike otherwise.
// Checks the first family of every element under #c that holds text.
async function assertFonts(page, label) {
  const bad = await page.evaluate(() => {
    const used = new Set([...document.querySelectorAll("#c, #c *")]
      .filter((e) => [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()))
      .map((e) => getComputedStyle(e).fontFamily.split(",")[0].replace(/["']/g, "").trim()));
    return [...used].filter((n) => ![...document.fonts].some((f) => f.family.replace(/["']/g, "") === n && f.status === "loaded"));
  });
  if (bad.length) throw new Error(`${label}: font fell back, not loaded: ${bad.join(", ")}`);
}

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, "out");
const LOGOS = join(HERE, "..", "logos");
const PORTRAITS = "~/FenrirVault/Projects/Asgard Agents/Canvas Images";
mkdirSync(OUT, { recursive: true });

const svgPath = (name) => readFileSync(join(LOGOS, `${name}.svg`), "utf8").match(/<path d="([^"]+)"/)[1];
const icon = (name, color) => `<svg viewBox="0 0 24 24"><path fill="${color}" d="${svgPath(name)}"/></svg>`;
const dataUri = (p) => `data:image/png;base64,${readFileSync(p).toString("base64")}`;

const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@500;600;800&display=swap');
html,body{margin:0;background:transparent}
body{font-family:Inter,sans-serif;color:#fff;padding:60px;display:inline-block}
.glass{background:linear-gradient(135deg,rgba(18,20,34,.94),rgba(10,11,20,.94));border:3px solid rgba(255,255,255,.14);
  box-shadow:0 30px 80px rgba(0,0,0,.55),inset 0 2px 0 rgba(255,255,255,.08);border-radius:48px}
.logo{display:flex;align-items:center;gap:44px;padding:36px 64px 36px 36px}
.tile{width:200px;height:200px;border-radius:44px;display:grid;place-items:center;flex:none}
.tile svg{width:118px;height:118px}
.name{font-family:'Space Grotesk';font-weight:700;font-size:92px;letter-spacing:-2px;line-height:1}
.sub{font-size:44px;font-weight:600;color:#9aa3c7;margin-top:14px;letter-spacing:.5px}
.chip{display:flex;align-items:center;gap:40px;padding:34px 70px 34px 40px}
.bar{width:14px;height:120px;border-radius:8px;background:linear-gradient(#F5C451,#E58A2B)}
.idx{font-family:'Space Grotesk';font-weight:700;font-size:64px;color:#F5C451}
.ttl{font-family:'Space Grotesk';font-weight:700;font-size:100px;letter-spacing:4px}
.stat{padding:50px 90px;text-align:center}
.big{font-family:'Space Grotesk';font-weight:700;font-size:150px;letter-spacing:-3px;line-height:1.02}
.small{font-size:54px;font-weight:600;color:#9aa3c7;letter-spacing:6px;margin-top:22px;text-transform:uppercase}
.gold{color:#F5C451}.cyan{color:#5EE7FF}.red{color:#FF5A5F}
.agent{text-align:center;width:360px}
.agent img{width:330px;height:330px;filter:drop-shadow(0 20px 40px rgba(0,0,0,.6))}
.agent .an{font-family:'Space Grotesk';font-weight:700;font-size:64px;margin-top:6px;text-shadow:0 6px 24px rgba(0,0,0,.9)}
.agent .ar{font-size:38px;font-weight:600;color:#cfd5f2;letter-spacing:3px;text-transform:uppercase;text-shadow:0 4px 16px rgba(0,0,0,.9)}
.sub-btn{display:flex;align-items:center;gap:36px;background:#FF0033;border-radius:30px;padding:40px 80px;
  font-family:'Space Grotesk';font-weight:700;font-size:96px;letter-spacing:3px;box-shadow:0 30px 80px rgba(0,0,0,.5)}
.sub-btn svg{width:96px;height:96px}

.coin{display:flex;align-items:center;gap:44px;padding:30px 70px 30px 30px}
.coin img{width:230px;height:230px;border-radius:40px;flex:none}
.vs{display:flex;align-items:stretch;padding:0;overflow:hidden}
.vs .side{padding:44px 64px;display:flex;flex-direction:column;align-items:center;gap:18px;min-width:760px}
.vs .side svg{width:120px;height:120px}
.vs .tag{font-size:40px;font-weight:600;color:#cfd5f2;letter-spacing:3px;text-transform:uppercase}
.vs .faces{display:flex;gap:14px}.vs .faces img{width:130px;height:130px}
.vs .mid{display:grid;place-items:center;padding:0 36px;font-family:'Space Grotesk';font-weight:700;font-size:90px;color:#F5C451;background:rgba(255,255,255,.04)}
.foot{font-size:44px;font-weight:600;color:#9aa3c7;text-align:center;padding:22px 0 30px}
.steps{display:flex;gap:14px;padding:26px 30px}
.step{width:300px;padding:22px 20px;border-radius:26px;background:rgba(255,255,255,.04);border:3px solid rgba(255,255,255,.08);opacity:.45}
.step.done{opacity:.75}
.step.on{opacity:1;background:linear-gradient(135deg,rgba(245,196,81,.22),rgba(229,138,43,.12));border-color:#F5C451;box-shadow:0 0 40px rgba(245,196,81,.35)}
.step .n{font-family:'Space Grotesk';font-weight:700;font-size:44px;color:#F5C451}
.step .t{font-size:40px;font-weight:800;line-height:1.08;margin-top:6px}
.step .w{font-size:30px;font-weight:600;color:#9aa3c7;margin-top:8px}
`;

const logoCard = (tileBg, iconHtml, name, sub) =>
  `<div id="c" class="glass logo"><div class="tile" style="background:${tileBg}">${iconHtml}</div>
   <div><div class="name">${name}</div><div class="sub">${sub}</div></div></div>`;
const chip = (i, t) => `<div id="c" class="glass chip"><div class="bar"></div><div class="idx">${i}</div><div class="ttl">${t}</div></div>`;
const stat = (big, small, cls = "gold") =>
  `<div id="c" class="glass stat"><div class="big ${cls}">${big}</div><div class="small">${small}</div></div>`;
const agent = (n, role) =>
  `<div id="c" class="agent"><img src="${dataUri(`${PORTRAITS}/${n} Round.png`)}"><div class="an">${n}</div><div class="ar">${role}</div></div>`;

const COINS = "~/Projects/CryptoFlow/coins";
const coin = (dir, name, sub) =>
  `<div id="c" class="glass coin"><img src="${dataUri(`${COINS}/${dir}/logo.png`)}"><div><div class="name">${name}</div><div class="sub">${sub}</div></div></div>`;
const face = (n) => `<img src="${dataUri(`${PORTRAITS}/${n} Round.png`)}">`;
const STEPS = [["Spot a story", "Loki"], ["Turn it into a coin", "Loki"], ["Safety check", "Heimdall"], ["Launch at 8 PM ET", "Thor"],
  ["Tell the world", "Loki"], ["Earn fees", "Mimir"], ["Count every cent", "Mimir"], ["Plan tomorrow", "Odin"]];
const steps = (k) => `<div id="c" class="glass steps">${STEPS.map(([t, w], i) =>
  `<div class="step ${i + 1 === k ? "on" : i + 1 < k ? "done" : ""}"><div class="n">0${i + 1}</div><div class="t">${t}</div><div class="w">${w}</div></div>`).join("")}</div>`;

const paperclipEmblem = readFileSync(join(LOGOS, "paperclip-emblem.svg"), "utf8")
  .replace(/<rect[^>]*\/>/, "").replace(/width="32" height="32"/, "");
const bell = `<svg viewBox="0 0 24 24"><path fill="#fff" d="M12 22a2.5 2.5 0 0 0 2.45-2h-4.9A2.5 2.5 0 0 0 12 22Zm7-6V11a7 7 0 0 0-5.5-6.84V3.5a1.5 1.5 0 0 0-3 0v.66A7 7 0 0 0 5 11v5l-2 2v1h18v-1Z"/></svg>`;

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 3840, height: 2160 } });

  // Paperclip's own wordmark, straight from their site.
  await page.goto("https://paperclip.ing", { waitUntil: "domcontentloaded" });
  const wordmark = (await page.locator(".sn-logo").first().innerHTML())
    .replace(/width="\d+" height="\d+"/, 'height="84"').replace(/currentColor/g, "#fff");

  const assets = {
    "logo-paperclip": logoCard("#0A0A0A;border:3px solid #333", paperclipEmblem, "Paperclip", "AI agent workforce"),
    "logo-obsidian": logoCard("#7C3AED", icon("obsidian", "#fff"), "Obsidian", "Notes &amp; canvas"),
    "logo-x": logoCard("#000", icon("x", "#fff"), "X", "Where the agents post"),
    "logo-ethereum": logoCard("#627EEA", icon("ethereum", "#fff"), "Ethereum", "The company wallet"),
    "logo-claude": logoCard("#D97757", icon("claude", "#fff"), "Claude Code", "by Anthropic"),
    "logo-codex": logoCard("#fff", icon("openai", "#000"), "Codex", "by OpenAI"),
    "handle-asgard": `<div id="c" class="glass logo"><div class="tile" style="background:#000">${icon("x", "#fff")}</div>
       <div><div class="name">@AsgardAgentsLab</div><div class="sub">Follow the experiment</div></div></div>`,
    "hook-title": stat(`5 AI AGENTS <span style="color:#fff">·</span> $50 <span style="color:#fff">·</span> 1 JOB`, "Day 1 of the experiment"),
    "chip-council": chip("01", "THE COUNCIL"),
    "chip-loop": chip("02", "THE DAILY LOOP"),
    "chip-rules": chip("03", "THE RULES"),
    "chip-paperclip": chip("04", "INSIDE PAPERCLIP"),
    "chip-x": chip("05", "THE X ACCOUNT"),
    "stat-daily": stat("1 TOKEN / DAY", "Launch at 8 PM ET"),
    "stat-broke": stat("OUT OF FUNDS = GAME OVER", "No second wallet", "red"),
    "stat-bank": stat("$50 IN ETH", "The entire starting bank"),
    "stat-max": stat("MAX 10%", "Of the wallet per launch", "cyan"),
    "stat-fees": stat("FEES ONLY", "No hype. No shilling."),
    "stat-day1": stat("DAY 1", "Just over 12 hours in", "cyan"),
    "agent-odin": agent("Odin", "Orchestrator"),
    "agent-thor": agent("Thor", "Builder"),
    "agent-loki": agent("Loki", "Creative"),
    "agent-mimir": agent("Mimir", "Numbers"),
    "agent-heimdall": agent("Heimdall", "Security"),

    "coin-emu": coin("not-an-ostrich", "Not An Ostrich", "$EMU · their first launch"),
    "coin-bulk": coin("hibernation-bulk", "Hibernation Bulk", "$BULK · live and being promoted"),
    "vs-providers": `<div id="c" class="glass" style="border-radius:48px;overflow:hidden"><div class="vs">
       <div class="side"><div style="width:170px;height:170px;border-radius:40px;background:#D97757;display:grid;place-items:center">${icon("claude", "#fff")}</div>
         <div class="name">Claude Code</div><div class="faces">${face("Odin")}${face("Thor")}${face("Loki")}</div><div class="tag">Odin · Thor · Loki</div></div>
       <div class="mid">VS</div>
       <div class="side"><div style="width:170px;height:170px;border-radius:40px;background:#fff;display:grid;place-items:center">${icon("openai", "#000")}</div>
         <div class="name">Codex</div><div class="faces">${face("Mimir")}${face("Heimdall")}</div><div class="tag">Mimir · Heimdall</div></div></div>
       <div class="foot">Two providers, so they challenge each other</div></div>`,
    "steps-1": steps(1),
    "steps-2": steps(2),
    "steps-3": steps(3),
    "steps-4": steps(4),
    "steps-5": steps(5),
    "steps-6": steps(6),
    "steps-7": steps(7),
    "steps-8": steps(8),
    "cta-subscribe": `<div id="c" class="sub-btn">${bell}SUBSCRIBE</div>`,
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
