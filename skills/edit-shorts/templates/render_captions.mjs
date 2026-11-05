// Shorts captions: one transparent PNG per unique chunk (shorts/caps/caps.json -> capNNN.png + manifest.json).
// Style: heavy uppercase, white with ONE key word in C3 lime, on a dark pill so it reads over the screen/facecam seam.
import { chromium } from "file:///~/Code/market-analyzer/node_modules/playwright/index.mjs";
import { readFileSync, writeFileSync } from "node:fs";
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
