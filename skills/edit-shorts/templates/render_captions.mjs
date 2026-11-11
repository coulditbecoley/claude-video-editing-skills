// Shorts captions: one transparent PNG per unique chunk (shorts/caps/caps.json -> capNNN.png + manifest.json).
// Style: heavy uppercase, white with ONE key word in C3 lime, on a dark pill so it reads over the screen/facecam seam.
import { chromium } from "playwright";   // resolves via a node_modules link above this file (PC: junction to market-analyzer; pod: /opt/node)
import { readFileSync, writeFileSync } from "node:fs";
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
const CAPS = join(HERE, "..", "shorts", "caps");
const list = JSON.parse(readFileSync(join(CAPS, "caps.json"), "utf8"));
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&display=swap');
html,body{margin:0;background:transparent}
body{padding:50px;display:inline-block;font-family:'Space Grotesk',sans-serif}
#c{background:rgba(10,10,8,.82);border:3px solid rgba(255,255,255,.10);border-radius:40px;padding:22px 52px 26px;
  box-shadow:0 20px 60px rgba(0,0,0,.55);font-weight:700;font-size:132px;letter-spacing:1px;line-height:1.05;color:#fff;
  text-align:center;max-width:1900px}
.k{color:#CCFF00}
`;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 2400, height: 1200 } });
const manifest = {};
for (const c of list) {
  const html = c.words.map((w, i) => (i === c.hi ? `<span class="k">${esc(w)}</span>` : esc(w))).join(" ");
  await page.setContent(`<style>${CSS}</style><div id="c">${html}</div>`, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await assertFonts(page, c.file);
  const box = await page.locator("#c").boundingBox();
  const pad = 40;
  await page.screenshot({ path: join(CAPS, c.file), omitBackground: true,
    clip: { x: box.x - pad, y: box.y - pad, width: box.width + pad * 2, height: box.height + pad * 2 } });
  manifest[c.file] = { w: Math.round(box.width + pad * 2), h: Math.round(box.height + pad * 2) };
}
writeFileSync(join(CAPS, "manifest.json"), JSON.stringify(manifest, null, 1));
await browser.close();
console.log(Object.keys(manifest).length, "captions");
