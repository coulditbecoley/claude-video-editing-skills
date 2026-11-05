// Animated graphics for "3 AI Setups Challenge, Video 1": every asset is HTML + CSS animations, captured frame by frame
// at 60 fps (all animations paused and stepped through currentTime) into out/<name>/NNN.png, plus out/<name>.png (the
// last frame) and out/manifest.json {w, h, frames, hit}. render_mp4.py plays the sequence, then holds the last frame,
// then runs a 0.3 s exit. "hit" = when the main element lands, so its SFX peak sits on that frame.
// Look: the series banner (dark glass, cream type, team colours: Paperclip red, Hermes blue, Grok green, gold accents).
// No em dashes in any copy. Run: node render_anim.mjs [name ...]
import { chromium } from "file:///~/Code/market-analyzer/node_modules/playwright/index.mjs";
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, "out");
const LOGOS = join(HERE, "..", "logos");
mkdirSync(OUT, { recursive: true });
const uri = (f) => `data:image/png;base64,${readFileSync(join(LOGOS, f)).toString("base64")}`;
const svg = (f) => readFileSync(join(LOGOS, f), "utf8");
const svgUri = (f) => `data:image/svg+xml;base64,${Buffer.from(svg(f)).toString("base64")}`;

const C = { red: "#EF655C", blue: "#4FC3FF", green: "#54D59B", gold: "#E7BD66", purple: "#AC80F5", cream: "#F3EADB", amber: "#F2A93B" };
const TEAM = {
  paperclip: { logo: uri("Paperclip Round.png"), col: C.red, name: "PAPERCLIP", run: "Claude Code &middot; Opus 5.5" },
  hermes: { logo: uri("Hermes Round.png"), col: C.blue, name: "HERMES AGENT", run: "Codex &middot; GPT-6 Astra" },
  grok: { logo: uri("Grok Round.png"), col: C.green, name: "GROK BOT", run: "Grok" },
};
const AG = ["Odin", "Thor", "Loki", "Mimir", "Heimdall"];

const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=Barlow:wght@500;600;700&family=JetBrains+Mono:wght@600&display=swap');
html,body{margin:0;background:transparent}
body{font-family:Barlow,sans-serif;color:${C.cream};padding:120px;display:inline-block}
.glass{position:relative;background:linear-gradient(140deg,rgba(26,27,32,.95),rgba(12,13,16,.95));border:3px solid rgba(255,255,255,.13);
  border-radius:44px;box-shadow:0 40px 90px rgba(0,0,0,.6),inset 0 2px 0 rgba(255,255,255,.07);overflow:hidden}
.glass::after{content:"";position:absolute;inset:0;background:linear-gradient(105deg,transparent 30%,rgba(255,255,255,.16) 48%,transparent 62%);
  transform:translateX(-120%);animation:sheen .55s cubic-bezier(.4,0,.2,1) .1s both}
@keyframes sheen{to{transform:translateX(120%)}}
.cond{font-family:'Barlow Condensed';font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.k{font-family:'Barlow Condensed';font-weight:600;letter-spacing:.22em;text-transform:uppercase;font-size:44px;color:#a9a39a}
@keyframes popIn{0%{transform:scale(.4);opacity:0}60%{transform:scale(1.08);opacity:1}80%{transform:scale(.97)}100%{transform:scale(1)}}
@keyframes rise{0%{transform:translateY(110%)}100%{transform:translateY(0)}}
@keyframes fadeUp{0%{transform:translateY(30px);opacity:0}100%{transform:translateY(0);opacity:1}}
@keyframes slideL{0%{transform:translateX(-140px);opacity:0;filter:blur(14px)}70%{transform:translateX(10px);opacity:1;filter:blur(0)}100%{transform:translateX(0)}}
@keyframes slideR{0%{transform:translateX(140px);opacity:0;filter:blur(14px)}70%{transform:translateX(-10px);opacity:1;filter:blur(0)}100%{transform:translateX(0)}}
@keyframes grow{0%{transform:scaleX(0)}100%{transform:scaleX(1)}}
@keyframes growY{0%{transform:scaleY(0)}100%{transform:scaleY(1)}}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes glowp{0%{box-shadow:0 0 0 rgba(231,189,102,0)}50%{box-shadow:0 0 70px rgba(231,189,102,.55)}100%{box-shadow:0 0 30px rgba(231,189,102,.25)}}
@keyframes type{from{width:0}}
@keyframes blink{50%{opacity:0}}
@keyframes cardIn{0%{transform:translateY(60px) scale(.94);opacity:0;filter:blur(10px)}65%{transform:translateY(-6px) scale(1.01);opacity:1;filter:blur(0)}100%{transform:none}}
.mask{display:inline-block;overflow:hidden;vertical-align:bottom;padding:0 .02em}
.mask>span{display:inline-block;animation:rise .55s cubic-bezier(.2,.85,.25,1) both}
.ring{border-radius:50%;box-shadow:0 26px 60px rgba(0,0,0,.6)}
`;
const E = "cubic-bezier(.2,.85,.25,1)";
const words = (txt, d0, step, cls = "") => txt.split(" ").map((w, i) =>
  `<span class="mask"><span class="${cls}" style="animation-delay:${(d0 + i * step).toFixed(3)}s">${w}</span></span>`).join(" ");
const bars = (d0) => `<div style="display:flex;gap:14px;margin-top:34px">${[C.red, C.blue, C.green, C.gold, C.purple].map((c, i) =>
  `<div style="width:96px;height:12px;border-radius:6px;background:${c};transform-origin:left;animation:grow .4s ${E} ${(d0 + i * .06).toFixed(2)}s both"></div>`).join("")}</div>`;

// ---- components --------------------------------------------------------------------------------------------------
const title = (kicker, big, sub) => ({ hit: 0.3, dur: 1.4, html: `<div id="c" style="text-align:center;padding:20px 40px">
  <div class="k" style="animation:fadeUp .5s ${E} 0s both">${kicker}</div>
  <div class="cond" style="font-size:190px;line-height:1;margin-top:18px;text-shadow:0 10px 50px rgba(0,0,0,.85)">${words(big, .05, .09)}</div>
  <div style="display:flex;justify-content:center">${bars(.45)}</div>
  ${sub ? `<div style="font-size:58px;font-weight:600;margin-top:30px;color:#d9d1c4;text-shadow:0 6px 30px rgba(0,0,0,.9);animation:fadeUp .5s ${E} .6s both">${sub}</div>` : ""}</div>` });

const teamRow = (n, label) => ({ hit: 0.14, dur: 0.9, html: `<div id="c" style="display:flex;align-items:center;gap:40px;padding:10px">
  ${["grok", "hermes", "paperclip"].map((k, i) => {
    const t = TEAM[k], on = i < n, anim = i === n - 1;
    const vs = i ? `<div class="cond" style="font-size:90px;color:${C.gold};opacity:${on ? 1 : 0};${anim ? `animation:popIn .45s ${E} .05s both` : ""}">VS</div>` : "";
    return `${vs}<div style="text-align:center;opacity:${on ? 1 : 0};${anim ? `animation:popIn .55s ${E} 0s both` : ""}">
      <img class="ring" src="${t.logo}" style="width:330px;height:330px">
      <div class="cond" style="font-size:62px;margin-top:14px;text-shadow:0 6px 24px rgba(0,0,0,.9)">${t.name}</div></div>`;
  }).join("")}</div>${label ? `<div class="k" style="text-align:center;margin-top:10px">${label}</div>` : ""}` });

const agents = (head) => ({ hit: 0.2, dur: 1.3, html: `<div id="c" class="glass" style="padding:44px 60px 40px">
  <div class="k" style="animation:fadeUp .4s ${E} 0s both">${head}</div>
  <div style="display:flex;gap:30px;margin-top:26px">${AG.map((a, i) => `<div style="text-align:center;animation:popIn .5s ${E} ${(.08 + i * .1).toFixed(2)}s both">
    <img src="${uri(`${a} Round.png`)}" style="width:210px;height:210px;filter:drop-shadow(0 16px 30px rgba(0,0,0,.6))">
    <div class="cond" style="font-size:58px;margin-top:6px">${a}</div></div>`).join("")}</div></div>` });

const chip = (i, t, col = C.gold) => ({ hit: 0.12, dur: 0.9, html: `<div id="c" class="glass" style="display:flex;align-items:center;gap:34px;padding:30px 66px 30px 36px;animation:slideL .5s ${E} both">
  <div style="width:14px;height:110px;border-radius:7px;background:linear-gradient(${col},#8f753f);transform-origin:top;animation:growY .35s ${E} .1s both"></div>
  <div class="cond" style="font-size:72px;color:${col}">${i}</div>
  <div class="cond" style="font-size:88px;letter-spacing:.08em">${words(t, .15, .06)}</div></div>` });

const stat = (big, small, col = C.gold, w) => ({ hit: 0.16, dur: 1.0, html: `<div id="c" class="glass" style="padding:46px 80px;text-align:center;${w ? `width:${w}px;` : ""}animation:cardIn .6s ${E} both">
  <div class="cond" style="font-size:150px;line-height:1;color:${col}">${words(big, .06, .07)}</div>
  ${small ? `<div class="k" style="margin-top:22px;font-size:48px;color:#cfc7ba;animation:fadeUp .45s ${E} .35s both">${small}</div>` : ""}</div>` });

const rules = (items, on, head = "THE RULES") => ({ hit: 0.12, dur: 0.8, html: `<div id="c" class="glass" style="width:760px;padding:40px 40px 30px">
  <div class="k" style="color:${C.gold}">${head}</div>
  <div style="display:flex;flex-direction:column;gap:16px;margin-top:22px">${items.map(([ic, t, s], i) => {
    const st = i + 1 === on ? `background:linear-gradient(135deg,rgba(231,189,102,.2),rgba(231,189,102,.05));border-color:${C.gold};animation:glowp .8s ease-out both,cardIn .5s ${E} both`
      : i + 1 < on ? "opacity:.65" : "opacity:.35";
    return `<div style="display:flex;align-items:center;gap:26px;padding:20px 24px;border-radius:26px;border:3px solid rgba(255,255,255,.08);background:rgba(255,255,255,.03);${st}">
      <img src="${svgUri(ic)}" style="width:96px;height:96px;flex:none">
      <div><div class="cond" style="font-size:58px;line-height:1">${t}</div><div style="font-size:48px;font-weight:600;color:#b9b2a6;margin-top:6px">${s}</div></div></div>`;
  }).join("")}</div></div>` });

const lower = (k) => {
  const t = TEAM[k];
  return { hit: 0.12, dur: 1.0, html: `<div id="c" class="glass" style="display:flex;align-items:center;gap:36px;padding:26px 64px 26px 26px;border-color:${t.col}66;animation:slideL .55s ${E} both">
  <img class="ring" src="${t.logo}" style="width:180px;height:180px;animation:popIn .5s ${E} .05s both">
  <div><div class="cond" style="font-size:84px;line-height:1">${words(t.name, .12, .06)}</div>
  <div style="font-size:46px;font-weight:600;color:${t.col};margin-top:10px;animation:fadeUp .4s ${E} .3s both">runs on ${t.run}</div></div></div>` };
};

const url = (u, k, sub) => {
  const t = TEAM[k];
  return { hit: 0.1, dur: 1.2, html: `<div id="c" class="glass" style="display:flex;align-items:center;gap:30px;padding:26px 56px 26px 26px;border-color:${t.col}77;animation:slideL .5s ${E} both">
  <img class="ring" src="${t.logo}" style="width:130px;height:130px">
  <div><div style="font-family:'JetBrains Mono';font-size:62px;white-space:nowrap;overflow:hidden;display:inline-block;vertical-align:bottom;animation:type .7s steps(${u.length}) .2s both;width:${u.length * 0.6 + 0.2}em">${u}</div><span style="font-family:'JetBrains Mono';font-size:62px;color:${t.col};animation:blink .5s steps(1) .2s 4 both">|</span>
  <div class="k" style="font-size:38px;margin-top:6px;animation:fadeUp .4s ${E} .5s both">${sub}</div></div></div>` };
};

const product = (k, name, line, price) => {
  const t = TEAM[k];
  return { hit: 0.14, dur: 1.2, html: `<div id="c" class="glass" style="width:1040px;padding:40px 50px;border-color:${t.col}88;animation:cardIn .6s ${E} both">
  <div style="display:flex;align-items:center;gap:22px"><img class="ring" src="${t.logo}" style="width:90px;height:90px"><div class="k" style="color:${t.col}">${t.name} BUILT</div></div>
  <div class="cond" style="font-size:118px;line-height:1;margin-top:22px">${words(name, .12, .07)}</div>
  <div style="font-size:44px;font-weight:600;color:#d3cbbe;margin-top:16px;animation:fadeUp .45s ${E} .35s both">${line}</div>
  <div style="display:flex;align-items:baseline;gap:18px;margin-top:26px;animation:popIn .5s ${E} .55s both"><div class="cond" style="font-size:110px;color:${C.gold}">${price}</div><div class="k" style="font-size:38px">one time &middot; digital download</div></div></div>` };
};

const productCold = (k, name, price) => {
  const t = TEAM[k];
  return { hit: 0.12, dur: 0.7, html: `<div id="c" class="glass" style="padding:30px 44px;border-color:${t.col}88;animation:cardIn .45s ${E} both">
  <div style="display:flex;align-items:center;gap:18px"><img class="ring" src="${t.logo}" style="width:80px;height:80px"><div class="k" style="font-size:36px;color:${t.col}">${t.name} &middot; POST-DEADLINE PREVIEW</div></div>
  <div style="display:flex;align-items:baseline;gap:30px;margin-top:14px"><div class="cond" style="font-size:96px;line-height:1">${name}</div><div class="cond" style="font-size:96px;color:${C.gold}">${price}</div></div></div>` };
};
const summary = (k, name, price, lines) => {
  const t = TEAM[k];
  return { hit: 0.12, dur: 1.0, html: `<div id="c" class="glass" style="width:900px;padding:36px 46px;border-color:${t.col}88;animation:cardIn .55s ${E} both">
  <div style="display:flex;align-items:center;gap:18px"><img class="ring" src="${t.logo}" style="width:80px;height:80px"><div class="k" style="font-size:36px;color:${t.col}">${t.name} &middot; IN SHORT</div></div>
  <div style="display:flex;align-items:baseline;gap:26px;margin-top:14px"><div class="cond" style="font-size:84px;line-height:1">${name}</div><div class="cond" style="font-size:84px;color:${C.gold}">${price}</div></div>
  ${lines.map((l, i) => `<div style="font-size:42px;font-weight:600;line-height:1.25;margin-top:12px;color:#e3dbcd;animation:fadeUp .4s ${E} ${(.2 + i * .1).toFixed(2)}s both">${l}</div>`).join("")}</div>` };
};
const hookCard = (l1, l2, col = C.gold, kicker = "THE AUTOMATED BUSINESS CHALLENGE") => ({ hit: 0.18, dur: 1.0, html: `<div id="c" style="text-align:center;width:1900px;padding:30px 20px">
  <div class="k" style="font-size:54px;color:#e9e1d3;text-shadow:0 4px 18px rgba(0,0,0,.9);animation:fadeUp .4s ${E} 0s both">${kicker}</div>
  <div class="cond" style="font-size:210px;line-height:.98;margin-top:14px;color:#fff;text-shadow:0 10px 0 rgba(0,0,0,.35),0 14px 50px rgba(0,0,0,.9)">${words(l1, .04, .07)}</div>
  <div class="cond" style="font-size:230px;line-height:.98;color:${col};text-shadow:0 10px 0 rgba(0,0,0,.35),0 14px 50px rgba(0,0,0,.9)">${words(l2, .2, .08)}</div>
  <div style="display:flex;justify-content:center">${bars(.45)}</div></div>` });
const endCard = (l1, l2) => ({ hit: 0.15, dur: 1.0, html: `<div id="c" class="glass" style="width:1700px;padding:56px 70px;text-align:center;border-color:${C.gold}aa;animation:cardIn .55s ${E} both">
  <div style="display:flex;justify-content:center;gap:30px;animation:fadeUp .4s ${E} .1s both">${["paperclip", "hermes", "grok"].map((k) => `<img class="ring" src="${TEAM[k].logo}" style="width:170px;height:170px">`).join("")}</div>
  <div class="cond" style="font-size:120px;line-height:1;margin-top:30px">${words(l1, .15, .06)}</div>
  <div class="cond" style="font-size:96px;line-height:1;color:${C.gold};margin-top:10px">${words(l2, .3, .06)}</div></div>` });
const shHook = (l1, l2, col = C.gold, kicker = "THE AUTOMATED BUSINESS CHALLENGE") => ({ hit: 0.16, dur: 0.9, html: `<div id="c" style="text-align:center;width:1000px;padding:10px 0">
  <div class="k" style="font-size:40px;letter-spacing:.16em;color:#efe7d8;text-shadow:0 3px 14px rgba(0,0,0,.9);animation:fadeUp .35s ${E} 0s both">${kicker}</div>
  <div class="cond" style="font-size:118px;line-height:.98;margin-top:8px;color:#fff;text-shadow:0 6px 0 rgba(0,0,0,.4),0 10px 34px rgba(0,0,0,.9)">${words(l1, .03, .06)}</div>
  <div class="cond" style="font-size:130px;line-height:.98;color:${col};text-shadow:0 6px 0 rgba(0,0,0,.4),0 10px 34px rgba(0,0,0,.9)">${words(l2, .16, .07)}</div></div>` });
const shRule = (ic, t, sub) => ({ hit: 0.12, dur: 0.6, html: `<div id="c" class="glass" style="width:900px;display:flex;align-items:center;gap:34px;padding:34px 40px;border-color:${C.gold}aa;animation:cardIn .45s ${E} both">
  <img src="${svgUri(ic)}" style="width:150px;height:150px;flex:none;animation:popIn .45s ${E} .05s both">
  <div><div class="cond" style="font-size:88px;line-height:1">${words(t, .08, .06)}</div><div style="font-size:46px;font-weight:600;color:#d6cebf;margin-top:10px;text-wrap:balance;animation:fadeUp .35s ${E} .22s both">${sub}</div></div></div>` });
const shBadge = (l1, l2, col = C.amber) => ({ hit: 0.1, dur: 0.5, html: `<div id="c" class="glass" style="display:flex;align-items:center;gap:22px;padding:18px 34px;border-color:${col}cc;animation:fadeUp .35s ${E} both">
  <div style="width:26px;height:26px;border-radius:50%;background:${col};box-shadow:0 0 20px ${col};flex:none"></div>
  <div><div class="cond" style="font-size:50px;line-height:1;color:${col}">${l1}</div><div style="font-size:40px;font-weight:600;color:#ece4d6;margin-top:4px">${l2}</div></div></div>` });
const shPrices = (on) => ({ hit: 0.12, dur: 0.6, html: `<div id="c" class="glass" style="width:960px;padding:26px 20px 30px">
  <div class="k" style="font-size:40px;color:${C.gold};text-align:center">ASKING PRICES &middot; SAME RULES</div>
  <div style="display:flex;margin-top:16px">${["paperclip", "hermes", "grok"].map((k, i) => {
    const t = TEAM[k], lit = i < on, now = i === on - 1;
    return `<div style="flex:1;text-align:center;opacity:${lit ? 1 : .3};${now ? `animation:popIn .45s ${E} both` : ""}">
      <img class="ring" src="${t.logo}" style="width:150px;height:150px">
      <div class="cond" style="font-size:44px;margin-top:8px">${t.name}</div>
      <div class="cond" style="font-size:120px;line-height:1;color:${lit ? t.col : "#777"}">${lit ? ["$12", "$9", "$9"][i] : "?"}</div></div>`;
  }).join("")}</div></div>` });
const shHelp = (k, t, sub) => ({ hit: 0.12, dur: 0.6, html: `<div id="c" class="glass" style="width:880px;padding:30px 40px;border-color:${C.amber}aa;animation:cardIn .45s ${E} both">
  <div class="k" style="font-size:36px;color:${C.amber}">LOGGED HUMAN HELP &middot; ${k} OF 3</div>
  <div class="cond" style="font-size:90px;line-height:1;margin-top:10px">${words(t, .08, .06)}</div>
  <div style="font-size:44px;font-weight:600;color:#ece4d6;margin-top:10px;text-wrap:balance;animation:fadeUp .35s ${E} .22s both">${sub}</div></div>` });
const shTeam = (k) => ({ hit: 0.1, dur: 0.4, html: `<div id="c" class="glass" style="display:flex;align-items:center;gap:16px;padding:12px 26px 12px 14px;border-color:${TEAM[k].col}cc;animation:fadeUp .3s ${E} both">
  <img class="ring" src="${TEAM[k].logo}" style="width:64px;height:64px"><div class="cond" style="font-size:48px;line-height:1;color:#fff">${TEAM[k].name}</div></div>` });
const shEnd = (l1, l2) => ({ hit: 0.12, dur: 0.7, html: `<div id="c" class="glass" style="width:960px;padding:34px 40px;text-align:center;border-color:${C.gold}aa;animation:cardIn .45s ${E} both">
  <div class="cond" style="font-size:104px;line-height:1">${words(l1, .06, .06)}</div>
  ${l2 ? `<div class="cond" style="font-size:64px;line-height:1;color:${C.gold};margin-top:10px">${words(l2, .2, .05)}</div>` : ""}</div>` });
const disclose = (head, lines, w = 1180) => ({ hit: 0.12, dur: 1.0, html: `<div id="c" class="glass" style="width:${w}px;padding:38px 50px;border-color:${C.amber}aa;animation:cardIn .55s ${E} both">
  <div style="display:flex;align-items:center;gap:20px"><div style="width:22px;height:22px;border-radius:50%;background:${C.amber};box-shadow:0 0 22px ${C.amber}"></div><div class="k" style="color:${C.amber}">${head}</div></div>
  ${lines.map((l, i) => `<div style="font-size:44px;font-weight:600;line-height:1.25;margin-top:16px;color:#e8e0d2;animation:fadeUp .4s ${E} ${(.2 + i * .12).toFixed(2)}s both">${l}</div>`).join("")}</div>` });

const prices = (on) => ({ hit: 0.12, dur: 0.8, html: `<div id="c" class="glass" style="padding:0"><div class="k" style="color:${C.gold};padding:30px 40px 0">10 &middot; THE VERDICT &middot; PRICES</div><div style="display:flex">${["paperclip", "hermes", "grok"].map((k, i) => {
    const t = TEAM[k], p = ["$12", "$9", "$9"][i], prod = ["Home Year", "First Market Loadout", "Midnight Workshop"][i];
    const vis = i < on, anim = i === on - 1;
    return `<div style="width:560px;padding:44px 30px;text-align:center;border-left:${i ? "3px solid rgba(255,255,255,.08)" : "0"};opacity:${vis ? 1 : .12};${anim ? `animation:fadeUp .45s ${E} both` : ""}">
      <img class="ring" src="${t.logo}" style="width:150px;height:150px;${anim ? `animation:popIn .5s ${E} both` : ""}">
      <div class="cond" style="font-size:50px;margin-top:14px">${t.name}</div>
      <div class="cond" style="font-size:150px;line-height:1.05;color:${t.col};${anim ? `animation:popIn .5s ${E} .1s both` : ""}">${p}</div>
      <div style="font-size:40px;font-weight:600;color:#b9b2a6">${prod}</div></div>`;
  }).join("")}</div></div>` });

const scoreboard = (on) => ({ hit: 0.12, dur: 0.8, html: `<div id="c" class="glass" style="padding:40px 50px">
  <div class="k" style="color:${C.gold}">THE SCOREBOARD &middot; DAY 30</div>
  <div style="display:flex;gap:26px;margin-top:24px">${[["trophy-e7bd66.svg", "SALES"], ["piggy-bank-e7bd66.svg", "PROFIT"], ["hand-helping-e7bd66.svg", "HUMAN HELP"]].map(([ic, l], i) =>
    `<div style="width:360px;padding:30px 20px;border-radius:28px;text-align:center;border:3px solid ${i + 1 === on ? C.gold : "rgba(255,255,255,.08)"};background:rgba(255,255,255,.03);opacity:${i < on ? 1 : .15};${i + 1 === on ? `animation:popIn .5s ${E} both` : ""}">
      <img src="${svgUri(ic)}" style="width:120px;height:120px"><div class="cond" style="font-size:66px;margin-top:12px">${l}</div></div>`).join("")}</div>
  <div style="font-size:54px;font-weight:600;color:#b9b2a6;margin-top:20px">Counted business costs reduce profit. AI usage excluded.</div></div>` });

const clock = (secs) => {     // the build time-lapse: a ring filling and a 0:00 -> 6:00 counter, for the whole stretch
  const n = Math.round((secs + 0.7) * 60);   // reaches 6:00 at secs, then holds
  return { hit: 0.1, dur: secs, frames: n, counter: true, html: `<div id="c" class="glass" style="display:flex;align-items:center;gap:44px;padding:36px 70px 36px 40px;animation:slideL .5s ${E} both">
  <svg width="230" height="230" viewBox="0 0 100 100" style="transform:rotate(-90deg)"><circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,.1)" stroke-width="9"/>
  <circle cx="50" cy="50" r="42" fill="none" stroke="${C.gold}" stroke-width="9" stroke-linecap="round" stroke-dasharray="264" stroke-dashoffset="264" style="animation:draw ${secs}s linear both"/></svg>
  <div><div class="k">05 &middot; THE BUILD &middot; TIME-LAPSE</div><div id="ct" class="cond" style="font-size:170px;line-height:1;font-variant-numeric:tabular-nums">0:00</div>
  <div style="font-size:40px;font-weight:600;color:#b9b2a6">hours : minutes &middot; three teams working</div></div></div>` };
};

const subscribe = () => ({ hit: 0.15, dur: 1.4, html: `<div id="c" style="display:flex;align-items:center;gap:30px;padding:10px">
  <div style="display:flex;align-items:center;gap:30px;background:#E62117;border-radius:30px;padding:36px 74px;box-shadow:0 30px 80px rgba(0,0,0,.55);animation:popIn .55s ${E} both">
  <svg viewBox="0 0 24 24" width="92" height="92" style="transform-origin:50% 10%;animation:ring 1s ease-in-out .5s both"><path fill="#fff" d="M12 22a2.5 2.5 0 0 0 2.45-2h-4.9A2.5 2.5 0 0 0 12 22Zm7-6V11a7 7 0 0 0-5.5-6.84V3.5a1.5 1.5 0 0 0-3 0v.66A7 7 0 0 0 5 11v5l-2 2v1h18v-1Z"/></svg>
  <div class="cond" style="font-size:96px;color:#fff">SUBSCRIBE</div></div>
  <div class="glass" style="padding:28px 44px;animation:slideR .5s ${E} .3s both"><div class="k" style="color:${C.gold}">NEXT</div><div class="cond" style="font-size:64px">THE DAY 30 RESULTS</div></div></div>
  <style>@keyframes ring{0%,100%{transform:rotate(0)}15%{transform:rotate(16deg)}30%{transform:rotate(-14deg)}45%{transform:rotate(10deg)}60%{transform:rotate(-6deg)}}</style>` });

const recap = (items) => ({ hit: 0.12, dur: 1.2, html: `<div id="c" class="glass" style="padding:40px 64px;text-align:center;animation:cardIn .55s ${E} both">
  <div class="k" style="color:${C.gold}">THE THREE PRODUCTS</div>
  <div style="display:flex;gap:34px;margin-top:24px">${items.map(([k, n, p], i) => `<div style="display:flex;align-items:center;gap:18px;animation:fadeUp .45s ${E} ${(.15 + i * .12).toFixed(2)}s both">
    <img class="ring" src="${TEAM[k].logo}" style="width:96px;height:96px"><div style="text-align:left"><div class="cond" style="font-size:58px;line-height:1">${n}</div><div class="cond" style="font-size:44px;color:${TEAM[k].col}">${p}</div></div></div>`).join("")}</div></div>` });

// ---- the assets ---------------------------------------------------------------------------------------------------
const RULES = [["timer-e7bd66.svg", "6 hours", "Build a business, end to end"], ["download-54d59b.svg", "Digital download", "Nothing physical to ship"],
  ["piggy-bank-e7bd66.svg", "$100 budget", "Per team. AI usage excluded"], ["badge-dollar-sign-54d59b.svg", "$20 max", "One-time purchase, no subscriptions"],
  ["ban-ef655c.svg", "No top-ups", "No borrowing from me or other agents"], ["megaphone-ef655c.svg", "Honest marketing", "No spam, fake reviews or cold emails"]];
const BUILD = [["globe-4fc3ff.svg", "Live website", "Anyone can visit it"], ["credit-card-4fc3ff.svg", "Checkout", "Built by them, connected by me"],
  ["download-54d59b.svg", "Auto delivery", "The download emails itself"], ["bot-ac80f5.svg", "Autopilot", "Support and upkeep, 30 days"]];
const A = {
  "cold-title": title("THE BUSINESS CHALLENGE", "3 AI teams &middot; 6 hours &middot; $100", "Six hours later: post-deadline previews of what they made"),
  "team-1": teamRow(1), "team-2": teamRow(2), "team-3": teamRow(3, "THE SAME FIVE ASGARD AGENTS ON EACH TEAM"),
  "agents-5": agents("THE ASGARD AGENT COMPANY KIT &middot; FIVE AGENTS PER TEAM"),
  "stat-human": stat("Very little human help", "Top up usage &middot; unstick them &middot; keep the PC on", C.gold),
  "chip-01": chip("01", "The kit"), "chip-02": chip("02", "Paperclip setup"), "chip-03": chip("03", "The rules"),
  "chip-04": chip("04", "Three teams"), "chip-05": chip("05", "The build"), "chip-06": chip("06", "Six hours later"),
  "chip-07": chip("07", "Home Year", C.red), "chip-08": chip("08", "First Market Loadout", C.blue), "chip-09": chip("09", "Midnight Workshop", C.green),
  "chip-10": chip("10", "The verdict"),
  "url-asgard": { ...url("asgardagents.com", "paperclip", "watch the agents live, 24/7"), html: url("asgardagents.com", "paperclip", "watch the agents live, 24/7").html.replace(TEAM.paperclip.logo, uri("Odin Round.png")).replace(`${C.red}77`, `${C.gold}77`) },
  "stat-kit": stat("Five business-savvy agents", "Business creation &middot; apps &middot; payments", C.gold),
  "lower-paperclip": lower("paperclip"), "lower-hermes": lower("hermes"), "lower-grok": lower("grok"),
  "stat-odin": stat("Odin leads", "The orchestrator on every team", C.gold),
  ...Object.fromEntries(RULES.map((_, i) => [`rule-${i + 1}`, rules(RULES, i + 1)])),
  ...Object.fromEntries(BUILD.map((_, i) => [`build-${i + 1}`, rules(BUILD, i + 1, "IN SIX HOURS, THEY MUST SHIP")])),
  "score-1": scoreboard(1), "score-2": scoreboard(2), "score-3": scoreboard(3),
  "stat-30": stat("30 days on autopilot", "Then the results video", C.gold),
  "stat-deadline": stat("Six hours. No extensions.", "Unfinished means out of the race", C.red),
  "stat-go": stat("Same prompt. Same start.", "Paperclip &middot; Hermes &middot; Grok Bot", C.gold),
  "clock": clock(8.8),
  "disclose-touch": disclose("LOGGED HUMAN TOUCHES &middot; ALL THREE TEAMS", ["Setup by Coley: accounts, keys, storage, support email",
    "Stripe test webhooks made at each team's request", "Approvals, restarts, requeues and keep-working prompts", "Grok Bot hit its weekly usage limit before the deadline"]),
  "qual-goal": disclose("THE GOAL, NOT A GUARANTEE", ["Agent-run businesses. Every human touch is logged"], 980),
  "qual-human": disclose("ALSO NEEDED", ["Human setup and recovery during the build"], 900),
  "qual-test": disclose("AT RECORDING", ["Test mode. Live checkout is not shown in this video"], 980),
  "disclose-polish": disclose("DISCLOSED &middot; POST-DEADLINE VERSIONS", ["The six-hour builds were frozen and tagged",
    "These tours show later versions, revised by Claude and Codex", "Post-deadline work included design and functionality fixes"]),
  "url-paperclip": url("homeyearplanner.com", "paperclip", "Paperclip &middot; post-deadline version"),
  "url-hermes": url("firstmarketloadout.com", "hermes", "Hermes &middot; post-deadline version"),
  "url-grok": url("midnightworkshopgames.com", "grok", "Grok Bot &middot; post-deadline version"),
  "prod-paperclip": product("paperclip", "Home Year", "A 12-month home maintenance planner", "$12"),
  "prod-hermes": product("hermes", "First Market Loadout", "A packing kit for your first craft fair", "$9"),
  "prod-grok": product("grok", "Midnight Workshop", "A printable holiday escape room", "$9"),
  "cold-paperclip": productCold("paperclip", "Home Year", "$12"), "cold-hermes": productCold("hermes", "First Market Loadout", "$9"),
  "cold-grok": productCold("grok", "Midnight Workshop", "$9"),
  "sum-paperclip": summary("paperclip", "Home Year", "$12", ["A 12-month home upkeep planner", "PDF + XLSX + CSV in one zip", "Delivery after Stripe checkout (described)"]),
  "sum-hermes": summary("hermes", "First Market Loadout", "$9", ["A craft-fair packing and load tracker", "Downloadable files in a zip", "Sales disabled at recording"]),
  "sum-grok": summary("grok", "Midnight Workshop", "$9", ["A printable holiday escape room", "6 puzzles, 12 hints, host guide", "Delivery after Stripe checkout (described)"]),
  "pill-post": { hit: 0.1, dur: 0.6, html: `<div id="c" class="glass" style="display:flex;align-items:center;gap:20px;padding:24px 44px;border-color:${C.amber}aa;animation:slideR .45s ${E} both">
    <div style="width:22px;height:22px;border-radius:50%;background:${C.amber};box-shadow:0 0 22px ${C.amber}"></div><div class="k" style="font-size:46px;color:${C.amber}">POST-DEADLINE VERSION</div></div>` },
  "sh-hook-1": hookCard("3 AI TEAMS", "6 HOURS &middot; $100"),
  "sh-hook-2": hookCard("CLAUDE'S TEAM", "MADE THIS", C.red),
  "sh-hook-3": hookCard("THE AI MADE", "A PACKING LIST?!", C.blue),
  "sh-hook-4": hookCard("GROK BUILT AN", "ESCAPE ROOM", C.green),
  "sh-hook-5": hookCard("WHICH AI", "CHARGED MORE?"),
  "sh-hook-6": hookCard("THE RULES", "6 HOURS &middot; $100"),
  "sh-hook-7": hookCard("3 AI TEAMS", "READY. SET. GO."),
  "sh-hook-8": hookCard("DID THE AI", "NEED HELP?"),
  "sh-end-full": endCard("WHO WINS IN 30 DAYS?", "FULL CHALLENGE ON THE CHANNEL"),
  "sh-clock": clock(5.2),
  "sh2-hook-1": shHook("3 AI TEAMS", "6 HOURS &middot; $100", C.gold, "$100 PER TEAM &middot; AI USAGE EXCLUDED"),
  "sh2-hook-2": shHook("A $12 HOME", "PLANNER?", C.red),
  "sh2-hook-3": shHook("WHAT AM I", "LOOKING AT?!", C.blue),
  "sh2-hook-4": shHook("GROK BUILT AN", "ESCAPE ROOM", C.green),
  "sh2-hook-5": shHook("WHICH AI", "PRICED HIGHER?"),
  "sh2-hook-6": shHook("6 HOURS.", "NO SECOND CHANCE.", C.red),
  "sh2-hook-7": shHook("AUTOMATED, BUT", "IT ASKS PERMISSION", C.blue),
  "sh2-hook-8": shHook("HOW MUCH HELP", "DID THE AI NEED?", C.amber),
  "sh2-r1": shRule("timer-e7bd66.svg", "6 HOURS", "Build a business, end to end"),
  "sh2-r2": shRule("download-54d59b.svg", "DIGITAL DOWNLOAD", "Nothing physical to ship"),
  "sh2-r3": shRule("piggy-bank-e7bd66.svg", "$100 PER TEAM", "AI usage excluded"),
  "sh2-r4": shRule("badge-dollar-sign-54d59b.svg", "$20 MAX, ONE-TIME", "No subscriptions"),
  "sh2-r5": shRule("ban-ef655c.svg", "NO TOP-UPS", "No borrowing from me or other agents"),
  "sh2-r6": shRule("megaphone-ef655c.svg", "HONEST MARKETING", "No spam, fake reviews or cold emails"),
  "sh2-post": shBadge("POST-DEADLINE TOUR", "Extra Claude + Codex polish"),
  "sh2-test": shBadge("TEST MODE AT RECORDING", "Live checkout not shown"),
  "sh2-mont": shBadge("BUILD EXCERPTS", "Time compressed", C.gold),
  "sh2-p0": shPrices(0), "sh2-p1": shPrices(1), "sh2-p2": shPrices(2), "sh2-p3": shPrices(3),
  "sh2-h1": shHelp(1, "SETUP + ACCOUNTS", "Keys, storage, the support email"),
  "sh2-h2": shHelp(2, "APPROVALS + RECOVERY", "Restarts, requeues, keep-working nudges"),
  "sh2-h3": shHelp(3, "POST-DEADLINE POLISH", "Claude + Codex revised the sites"),
  "sh2-end-1": shEnd("WHAT DID", "THEY BUILD?"), "sh2-end-2": shEnd("WOULD YOU", "PAY $12?"),
  "sh2-end-3": shEnd("WOULD YOU", "BUY THIS?"), "sh2-end-4": shEnd("SIX PUZZLES.", "NINE DOLLARS."),
  "sh2-end-5": shEnd("SAME RULES.", "DIFFERENT PRICES."), "sh2-end-6": shEnd("RESULTS", "IN 30 DAYS"),
  "sh2-end-7": shEnd("AUTOMATED", "NOT UNATTENDED"), "sh2-end-8": shEnd("HUMAN HELP", "WAS LOGGED"),
  "sh2-hook-8b": shHook("HOW MUCH HELP", "DID THE AI NEED?", C.amber, "BEFORE THE BUILD &middot; THE RULES"),
  "sh2-after": shBadge("AFTER THE BUILD", "The six hours are up", C.gold),
  "sh2-t-paperclip": shTeam("paperclip"), "sh2-t-hermes": shTeam("hermes"), "sh2-t-grok": shTeam("grok"),
  "stat-zip": stat("PDF + XLSX + CSV", "One zip, instant download", C.red),
  "stat-168": stat("168 hours", "How long the download link works (7 days)", C.red),
  "stat-puzzles": stat("6 puzzles &middot; 12 hints", "Ages 8+ &middot; 2 to 6 players &middot; 60 min", C.green),
  "stat-test": stat("Preview at recording", "Live checkout not demonstrated here", C.amber),
  "price-1": prices(1), "price-2": prices(2), "price-3": prices(3),
  "recap": recap([["paperclip", "Home Year", "$12"], ["hermes", "First Market Loadout", "$9"], ["grok", "Midnight Workshop", "$9"]]),
  "stat-domains": stat("$12.08 each", "Domain cost only. AI usage excluded from the $100", C.gold),
  "subscribe": subscribe(),
};

async function main() {
  const only = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 3840, height: 2160 } });
  const manPath = join(OUT, "manifest.json");
  const manifest = existsSync(manPath) ? JSON.parse(readFileSync(manPath, "utf8")) : {};
  for (const [name, a] of Object.entries(A)) {
    if (only.length && !only.includes(name)) continue;
    await page.setContent(`<style>${CSS}</style>${a.html}`, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    const frames = a.frames || Math.round(a.dur * 60) + 1;
    // the box at the final state, padded for overshoot and shadows
    await page.evaluate((ms) => document.getAnimations().forEach((x) => { x.pause(); x.currentTime = ms; }), a.dur * 1000);
    const b = await page.locator("#c").boundingBox();
    const pad = 110;
    const clip = { x: Math.max(0, b.x - pad), y: Math.max(0, b.y - pad), width: b.width + 2 * pad, height: b.height + 2 * pad };
    const dir = join(OUT, name);
    rmSync(dir, { recursive: true, force: true }); mkdirSync(dir, { recursive: true });
    for (let f = 0; f < frames; f++) {
      const ms = f * 1000 / 60;
      await page.evaluate(([ms, secs, counter]) => {
        document.getAnimations().forEach((x) => { x.pause(); x.currentTime = ms; });
        if (counter) {
          const m = Math.min(360, Math.round(360 * Math.min(1, ms / (secs * 1000))));
          document.getElementById("ct").textContent = `${Math.floor(m / 60)}:${String(m % 60).padStart(2, "0")}`;
        }
      }, [ms, a.dur, !!a.counter]);
      await page.screenshot({ path: join(dir, `${String(f).padStart(3, "0")}.png`), omitBackground: true, clip });
    }
    await page.screenshot({ path: join(OUT, `${name}.png`), omitBackground: true, clip });
    manifest[name] = { w: Math.round(clip.width), h: Math.round(clip.height), frames, hit: a.hit };
    console.log(name, frames, Math.round(clip.width), Math.round(clip.height));
  }
  writeFileSync(manPath, JSON.stringify(manifest, null, 1));
  await browser.close();
}
main().catch((e) => { console.error(e); process.exit(1); });
