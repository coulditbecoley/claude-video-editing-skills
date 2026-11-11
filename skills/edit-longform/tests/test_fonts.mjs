// Font-guard regression: extracts WEB_FONTS + assertFonts from each renderer template and runs 6 browser cases.
//   node test_fonts.mjs        (needs network for Google Fonts; uses local Arial for the subset case)
import { chromium } from "playwright";   // resolves via a node_modules link above this file (PC: junction to market-analyzer; pod: /opt/node)
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
const SKILLS = fileURLToPath(new URL("../../", import.meta.url));   // .../skills/
const files = [
  join(SKILLS, "edit-longform/templates/render.mjs"),
  join(SKILLS, "edit-shorts/templates/render_shorts.mjs"),
  join(SKILLS, "edit-shorts/templates/render_captions.mjs"),
];
const cases = [
  ["loaded 700, text 700", true, `@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&display=swap');#c{font-family:'Space Grotesk';font-weight:700}`, "HELLO"],
  ["only 400 loaded, text 700", false, `@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400&display=swap');#c{font-family:'Space Grotesk';font-weight:700}`, "HELLO"],
  ["import failed entirely", false, `@import url('https://fonts.googleapis.invalid/css2?family=Space+Grotesk:wght@700');#c{font-family:'Space Grotesk';font-weight:700}`, "HELLO"],
  ["variable face 100-900", true, `@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');#c{font-family:Inter;font-weight:800}`, "HELLO"],
  ["system Arial", true, `#c{font-family:Arial;font-weight:700}`, "HELLO"],
  ["Latin subset loaded, needed Greek subset failed", false,
   `@font-face{font-family:'Space Grotesk';src:local('Arial');font-weight:400;unicode-range:U+0041-005A}
    @font-face{font-family:'Space Grotesk';src:url('http://127.0.0.1:9/none.woff2');font-weight:400;unicode-range:U+0370-03FF}
    #c{font-family:'Space Grotesk';font-weight:400}`, "AB\u03A9"],
];
const b = await chromium.launch();
let failures = 0;
try {
  for (const f of files) {
    const src = readFileSync(f, "utf8");
    const start = src.indexOf("const WEB_FONTS"), fn = src.indexOf("async function assertFonts");
    const end = fn + src.slice(fn).search(/\r?\n}\r?\n/) + 3;    // templates mix CRLF and LF
    const block = src.slice(start, end);
    const assertFonts = new Function(`${block}; return assertFonts;`)();
    for (const [name, shouldPass, css, text] of cases) {
      const page = await b.newPage();
      await page.setContent(`<style>${css}</style><div id="c">${text}</div>`, { waitUntil: "networkidle" });
      await page.evaluate(() => document.fonts.ready);
      let passed = true;
      try { await assertFonts(page, "t"); } catch { passed = false; }
      if (passed !== shouldPass) { failures++; console.log("WRONG", f.split("/").pop(), name, "passed=", passed); }
      await page.close();
    }
  }
} finally { await b.close(); }
console.log(failures ? `FONT TEST FAILED (${failures})` : `font guard OK: ${files.length} templates x ${cases.length} cases`);
process.exit(failures ? 1 : 0);
