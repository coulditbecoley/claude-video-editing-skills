// Caption PNGs for the Shorts: 1-4 UPPERCASE words on a dark pill, one accent word in gold, sized for a 1080 px canvas.
import { chromium } from "file:///~/Code/market-analyzer/node_modules/playwright/index.mjs";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const HERE = dirname(fileURLToPath(import.meta.url));
const DIR = join(HERE, "captions");
const jobs = JSON.parse(readFileSync(join(DIR, "jobs.json"), "utf8"));
const CSS = `@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@800&display=swap');
html,body{margin:0;background:transparent}body{padding:30px;display:inline-block}
#c{max-width:960px;display:inline-flex;flex-wrap:wrap;justify-content:center;gap:0 22px;padding:14px 34px 18px;border-radius:30px;
background:rgba(10,10,14,.78);box-shadow:0 14px 40px rgba(0,0,0,.45);font-family:'Barlow Condensed';font-weight:800;font-size:96px;
line-height:1.02;letter-spacing:.01em;color:#fff;text-shadow:0 4px 0 rgba(0,0,0,.55)}
span{display:inline-block;transform-origin:50% 60%}
.a{color:#F5C451;transform:scale(1.07);text-shadow:0 4px 0 rgba(0,0,0,.55),0 0 26px rgba(245,196,81,.45)}`;
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 600 } });
await page.setContent(`<style>${CSS}</style><div id="c">X</div>`, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
for (const j of jobs) {
  // round 2: one PNG per spoken word, that word lit (same pill size in every state)
  for (let a = 0; a < j.words.length; a++) {
    await page.evaluate(([w, a]) => { document.getElementById("c").innerHTML = w.map((x, i) => `<span class="${i === a ? "a" : ""}">${x}</span>`).join(""); },
      [j.words.map(esc), a]);
    await page.locator("#c").screenshot({ path: join(DIR, `${j.name}_${a}.png`), omitBackground: true });
  }
}
await browser.close();
console.log(jobs.length, "captions");
