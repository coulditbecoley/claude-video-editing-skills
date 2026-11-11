// Renders v5 scenes (graphics/scenes/<id>.html, driven by lib/stage.js) to 60 fps frames.
//   node render_scene.mjs still <id> 0.5,2,4.5 [--full]   -> probe/<id>_<t>.jpg at 1920 (or 3840 with --full); also a tiled sheet
//   node render_scene.mjs video <id> [<id> ...] [--workers 6]
//        opaque scene  -> D:/edits/claude-edits-v5/gfx/<id>.mp4 (libx264 crf 10) + <id>/ folder kept empty for the EDL
//        alpha scene (body.alpha) -> D:/edits/claude-edits-v5/gfx/<id>/NNN.png
// Writes gfx/manifest.json {id: {frames, dur, alpha}}. Fails loudly on a missing font or image (stage.js ready()).
// the shared node_modules junction above the edits folder is dead (market-analyzer was removed): load a known install
const { chromium } = await import(process.env.PLAYWRIGHT_MJS || "file:///~/Code/C3Research/node_modules/playwright/index.mjs");
import { spawn, spawnSync } from "node:child_process";
import { mkdirSync, rmSync, existsSync, readFileSync, writeFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = process.env.GFX_OUT || "D:/edits/claude-edits-v5/gfx";
const PROBE = join(HERE, "..", "probe", "gfx");
const FPS = 60;
mkdirSync(OUT, { recursive: true }); mkdirSync(PROBE, { recursive: true });
const args = process.argv.slice(2), mode = args.shift();
const flag = (n, d) => { const i = args.indexOf(n); if (i < 0) return d; const v = args[i + 1]; args.splice(i, 2); return v; };
const has = (n) => { const i = args.indexOf(n); if (i < 0) return false; args.splice(i, 1); return true; };
// "launch@3" = scenes/launch.html?a=3, written out as launch_3 (one page, several variants)
const url = (id) => { const [f, a] = id.split("@"); return pathToFileURL(join(HERE, "scenes", f + ".html")).href + (a !== undefined ? "?a=" + encodeURIComponent(a) : ""); };
const name = (id) => id.replace("@", "_");

async function open(browser, id, scale) {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: scale });
  page.on("pageerror", (e) => { console.error(`[${id}] page error: ${e.message}`); process.exitCode = 1; });
  await page.goto(url(id));
  const info = await page.evaluate(() => window.Stage.ready());
  return { page, info };
}

if (mode === "still") {
  const full = has("--full"), id = args[0], times = (args[1] || "1").split(",").map(Number);
  const browser = await chromium.launch();
  const { page, info } = await open(browser, id, full ? 2 : 1);
  const files = [];
  for (const t of times) {
    await page.evaluate((x) => window.seek(x), t);
    const f = join(PROBE, `${name(id)}_${t.toFixed(2)}.jpg`);
    await page.screenshot({ path: f, type: "jpeg", quality: 88, omitBackground: info.alpha });
    files.push(f);
  }
  await browser.close();
  if (files.length > 1 && !full) {       // tile for one look
    const cols = files.length <= 4 ? 2 : 3, sheet = join(PROBE, `${name(id)}_sheet.jpg`);
    const inputs = files.flatMap((f) => ["-i", f]);
    const rows = Math.ceil(files.length / cols);
    spawnSync("ffmpeg", ["-v", "error", "-y", ...inputs, "-filter_complex",
      `${files.map((_, i) => `[${i}:v]scale=960:540[v${i}]`).join(";")};${files.map((_, i) => `[v${i}]`).join("")}xstack=inputs=${files.length}:layout=${files.map((_, i) => `${(i % cols) * 960}_${Math.floor(i / cols) * 540}`).join("|")}:fill=black[o]`,
      "-map", "[o]", "-q:v", "3", sheet], { stdio: "inherit" });
    console.log(`sheet ${sheet} (${cols}x${rows}, t=${times.join(", ")}) dur=${info.dur}`);
  } else console.log(files.join("\n"), `dur=${info.dur}`);
} else if (mode === "video") {
  const workers = parseInt(flag("--workers", "6")), has_force = has("--force");
  const alpha_or_mp4 = (id, m) => m.alpha ? join(OUT, id, "000.png") : join(OUT, id + ".mp4");
  const manPath = join(OUT, "manifest.json");
  const man = existsSync(manPath) ? JSON.parse(readFileSync(manPath, "utf8")) : {};
  // GPU rasterisation: 3x faster per 4K frame than software (bench 2026-11-09: 330 vs 780-1060 ms)
  // alpha overlays stay on the software path: transparent screenshots through the GPU ran at under 1 frame a second
  const GPU = ["--enable-gpu", "--ignore-gpu-blocklist", "--use-angle=d3d11", "--enable-gpu-rasterization"];
  const gpu = await chromium.launch({ args: GPU });
  const soft = await chromium.launch();
  let browser = soft;
  for (const sid of args) {
    const id = name(sid), t0 = Date.now();
    if (!has_force && man[id] && existsSync(alpha_or_mp4(id, man[id])) && statSync(join(HERE, "scenes", sid.split("@")[0] + ".html")).mtimeMs < statSync(alpha_or_mp4(id, man[id])).mtimeMs) {
      const pr = await open(soft, sid, 1); const same = Math.round(pr.info.dur * FPS) === man[id].frames; await pr.page.close();
      if (same) { console.log(`${id}: current, skipped`); continue; }
    }
    const probe = await open(soft, sid, 1); const { dur, alpha, hole, clip } = probe.info; await probe.page.close();
    browser = alpha ? soft : gpu;
    const n = Math.round(dur * FPS), dir = join(OUT, id);
    rmSync(dir, { recursive: true, force: true }); mkdirSync(dir, { recursive: true });
    rmSync(join(OUT, id + ".mp4"), { force: true });
    const w = Math.min(workers, Math.max(1, Math.ceil(n / 60)));
    await Promise.all([...Array(w)].map(async (_, k) => {
      // one browser PROCESS per worker: pages in one process queue their screenshots behind each other (3 fps total)
      const own = alpha || process.env.GFX_SOFT ? await chromium.launch() : await chromium.launch({ args: GPU });
      const { page } = await open(own, sid, 2);
      for (let f = k; f < n; f += w) {
        await page.evaluate((x) => window.seek(x), f / FPS);
        // opaque scenes: JPEG q96 (PNG encoding of a 4K frame was the bottleneck; they end up as yuv420 x264 anyway).
        // alpha overlays: PNG, clipped to the scene's data-clip box when it has one (chips only fill the lower third)
        if (alpha) await page.screenshot({ path: join(dir, String(f).padStart(3, "0") + ".png"), omitBackground: true, ...(clip ? { clip } : {}) });
        else await page.screenshot({ path: join(dir, String(f).padStart(3, "0") + ".jpg"), type: "jpeg", quality: 96 });
      }
      await own.close();
    }));
    if (readdirSync(dir).length !== n) throw new Error(`${id}: ${readdirSync(dir).length} of ${n} frames written`);
    if (!alpha) {
      // near-lossless, BT.709 limited, every 30th frame a keyframe (the renderer seeks into these)
      const r = spawnSync("ffmpeg", ["-v", "error", "-y", "-framerate", String(FPS), "-i", join(dir, "%03d.jpg"),
        "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "10", "-g", "30",
        "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", join(OUT, id + ".mp4")], { stdio: "inherit" });
      if (r.status !== 0) throw new Error(`${id}: ffmpeg failed`);
      for (const f of readdirSync(dir)) rmSync(join(dir, f));
    }
    man[id] = { frames: n, dur, alpha, hole, clip: clip ? { x: clip.x * 2, y: clip.y * 2, w: clip.width * 2, h: clip.height * 2 } : null };
    writeFileSync(manPath, JSON.stringify(man, null, 1));
    console.log(`${id}: ${n} frames (${dur}s${alpha ? ", alpha PNG" : ", mp4"}) in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  await gpu.close(); await soft.close();
} else {
  console.error("usage: node render_scene.mjs still <id> t1,t2,... [--full] | video <id>... [--workers N]"); process.exit(2);
}
