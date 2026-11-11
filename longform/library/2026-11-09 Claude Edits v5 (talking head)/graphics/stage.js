// v5 scene engine. A scene is one HTML page: <body data-dur="12.5" class="cyan?"> with content inside <div id="cam">.
// Everything is a pure function of time: window.seek(t) puts the page in its state at t seconds. No timers.
//
// Declarative attributes (times in seconds from scene start):
//   data-in="1.2"            entrance at 1.2 s (default fx "blur": blur + fade + slight rise, 0.5 s)
//   data-fx="blur|up|fade|scale|left|right|wipe|draw|mark|strike"
//   data-d="0.6"             entrance duration
//   data-out="6.0"           blur-fade out at 6.0 s (0.35 s)
//   data-words="0.07"        split text into words, stagger each by 0.07 s from data-in (headline reveal)
//   data-count="0,1093"      count up from..to over data-d (default 1.0 s) starting at data-in; data-fmt="int|1|pct|x"
//   data-type="18"           type the text in at N chars per second starting at data-in
//   data-on="3.0" data-off="6.0" data-cls="on"   add class between on and off (rows, tiles, icons lighting up)
// Custom: Stage.on(t => { ... }) runs on every seek (canvas, charts).
(() => {
  const E = { out: 'cubic-bezier(.16,1,.3,1)', io: 'cubic-bezier(.65,0,.35,1)' };
  const hooks = [], toggles = [], counters = [], typers = [];
  const num = (el, k, d) => (el.dataset[k] === undefined ? d : parseFloat(el.dataset[k]));
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const easeOut = (x) => 1 - Math.pow(1 - clamp(x), 3);
  const easeIO = (x) => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
  const FX = {
    blur: [{ opacity: 0, filter: 'blur(22px)', transform: 'translateY(26px) scale(.975)' }, { opacity: 1, filter: 'blur(0px)', transform: 'none' }],
    up: [{ opacity: 0, transform: 'translateY(46px)' }, { opacity: 1, transform: 'none' }],
    fade: [{ opacity: 0 }, { opacity: 1 }],
    scale: [{ opacity: 0, filter: 'blur(18px)', transform: 'scale(.86)' }, { opacity: 1, filter: 'blur(0px)', transform: 'none' }],
    left: [{ opacity: 0, filter: 'blur(16px)', transform: 'translateX(-90px)' }, { opacity: 1, filter: 'blur(0px)', transform: 'none' }],
    right: [{ opacity: 0, filter: 'blur(16px)', transform: 'translateX(90px)' }, { opacity: 1, filter: 'blur(0px)', transform: 'none' }],
    wipe: [{ clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0% 0 0)' }],
    draw: [{ strokeDashoffset: 1 }, { strokeDashoffset: 0 }],
    mark: [{ backgroundSize: '0% 100%' }, { backgroundSize: '100% 100%' }],
    strike: [{ '--k': 0 }, { '--k': 1 }],
  };
  try { CSS.registerProperty({ name: '--k', syntax: '<number>', inherits: true, initialValue: '0' }); } catch (e) {}

  function animate(el, fx, t0, d) {
    if (fx === 'draw') { el.setAttribute('pathLength', '1'); el.style.strokeDasharray = '1'; }
    const ease = fx === 'draw' || fx === 'mark' || fx === 'strike' || fx === 'wipe' ? E.io : E.out;
    el.animate(FX[fx] || FX.blur, { duration: d * 1000, delay: t0 * 1000, fill: 'both', easing: ease }).pause();
  }
  function build() {
    document.querySelectorAll('[data-words]').forEach((el) => {
      const step = parseFloat(el.dataset.words) || .07, t0 = num(el, 'in', 0), fx = el.dataset.fx || 'blur', d = num(el, 'd', .55);
      let i = 0;
      const walk = (node) => {
        [...node.childNodes].forEach((n) => {
          if (n.nodeType === 3) {
            const frag = document.createDocumentFragment();
            n.textContent.split(/(\s+)/).forEach((tok) => {
              if (!tok) return;
              if (/^\s+$/.test(tok)) { frag.appendChild(document.createTextNode(' ')); return; }
              const s = document.createElement('span'); s.className = 'w'; s.textContent = tok;
              // a gradient-clipped parent can't clip into inline-block children: carry the class down
              if (node.classList && node.classList.contains('grad')) s.classList.add('grad');
              frag.appendChild(s); animate(s, fx, t0 + i * step, d); i++;
            });
            n.replaceWith(frag);
          } else if (n.nodeType === 1 && n.tagName !== 'BR') walk(n);
        });
      };
      walk(el);
      el.dataset.wordsEnd = (t0 + i * step + d).toFixed(3);
      delete el.dataset.in;
    });
    document.querySelectorAll('[data-count]').forEach((el) => {
      const [a, b] = el.dataset.count.split(',').map(parseFloat);
      counters.push({ el, a, b, t0: num(el, 'in', 0), d: num(el, 'd', 1.0), fmt: el.dataset.fmt || 'int' });
    });
    document.querySelectorAll('[data-type]').forEach((el) => {
      typers.push({ el, text: el.textContent, t0: num(el, 'in', 0), cps: parseFloat(el.dataset.type) || 18 });
      el.textContent = '';
    });
    document.querySelectorAll('[data-in]').forEach((el) => {
      if (el.dataset.type !== undefined) return;
      animate(el, el.dataset.fx || 'blur', num(el, 'in', 0), num(el, 'd', el.dataset.fx === 'draw' ? 1.2 : .5));
    });
    document.querySelectorAll('[data-out]').forEach((el) => {
      el.animate([{ opacity: 1, filter: 'blur(0px)' }, { opacity: 0, filter: 'blur(18px)' }],
        { duration: 350, delay: num(el, 'out', 0) * 1000, fill: 'forwards', easing: E.io }).pause();
    });
    document.querySelectorAll('[data-on]').forEach((el) => toggles.push({ el, on: num(el, 'on', 0), off: num(el, 'off', 1e9), cls: el.dataset.cls || 'on' }));
  }
  const fmt = (v, f) => f === 'int' ? Math.round(v).toLocaleString('en-US') : f === 'pct' ? Math.round(v) + '%' : f === 'x' ? v.toFixed(1) + 'x'
    : f === 'ms' ? Math.round(v) + ' ms' : f === 'clock' ? Math.floor(v / 60) + ':' + String(Math.round(v) % 60).padStart(2, '0') : v.toFixed(parseInt(f) || 0);

  // dust: slow drifting particles, deterministic
  let dust = null, P = [];
  function rnd(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
  function initDust() {
    dust = document.getElementById('dust'); if (!dust) return;
    dust.width = 1920; dust.height = 1080;
    const r = rnd(parseInt(document.body.dataset.seed || '7')), n = 70;
    for (let i = 0; i < n; i++) P.push({ x: r() * 1920, y: r() * 1080, z: .3 + r() * .7, vx: (r() - .5) * 9, vy: -(3 + r() * 9), ph: r() * 6.28, sz: .8 + r() * 2.2 });
  }
  function drawDust(t) {
    if (!dust) return;
    const c = dust.getContext('2d'); c.clearRect(0, 0, 1920, 1080);
    const acc = getComputedStyle(document.body).getPropertyValue('--accrgb').trim() || '244,183,64';
    for (const p of P) {
      const x = ((p.x + p.vx * t * p.z) % 1920 + 1920) % 1920, y = ((p.y + p.vy * t * p.z) % 1080 + 1080) % 1080;
      const a = (.10 + .22 * (0.5 + 0.5 * Math.sin(p.ph + t * .9))) * p.z;
      c.beginPath(); c.fillStyle = `rgba(${acc},${a.toFixed(3)})`; c.arc(x, y, p.sz * p.z, 0, 6.2832); c.fill();
    }
  }

  const Stage = {
    dur: 0, t: 0, clamp, easeOut, easeIO,
    on(fn) { hooks.push(fn); },
    // progress 0..1 of a window starting at t0 lasting d
    p(t, t0, d) { return clamp((t - t0) / d); },
    seek(t) {
      Stage.t = t;
      for (const a of document.getAnimations()) a.currentTime = t * 1000;
      for (const g of toggles) g.el.classList.toggle(g.cls, t >= g.on && t < g.off);
      for (const c of counters) c.el.textContent = fmt(c.a + (c.b - c.a) * easeOut((t - c.t0) / c.d), c.fmt);
      for (const y of typers) { const n = Math.floor(clamp((t - y.t0) * y.cps, 0, y.text.length)); y.el.textContent = y.text.slice(0, n); }
      const cam = document.getElementById('cam');
      if (cam && !document.body.dataset.nopush) {           // slow 3.5 % push over the scene, like the reference
        const k = 1 + 0.035 * clamp(t / Math.max(Stage.dur, .001));
        cam.style.transform = `scale(${k.toFixed(5)})`;
      }
      drawDust(t);
      for (const h of hooks) h(t);
    },
    async ready() {
      // fonts load lazily: ask for each face, then prove it arrived (a fallback font must never render silently)
      const faces = ['800 40px Sora', '600 20px Inter', '400 20px "Instrument Serif"', 'italic 400 20px "Instrument Serif"', '600 20px "JetBrains Mono"'];
      await Promise.all(faces.map((f) => document.fonts.load(f)));
      await document.fonts.ready;
      for (const f of faces) if (!document.fonts.check(f)) throw new Error('font not loaded: ' + f);
      await Promise.all([...document.images].map((im) => im.decode().catch(() => { throw new Error('image failed: ' + im.src); })));
      Stage.dur = parseFloat(document.body.dataset.dur || '6');
      // alpha scenes: a .hole element punches a transparent rounded window through #bg and #dust (the talking head or
      // an insert shows through it). The hole must not move or scale: set data-nopush on the body.
      const hole = document.querySelector('.hole');
      if (hole && document.body.classList.contains('alpha')) {
        const r = hole.getBoundingClientRect(), rad = parseFloat(getComputedStyle(hole).borderRadius) || 0;
        const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='1920' height='1080'><rect x='${r.left}' y='${r.top}' width='${r.width}' height='${r.height}' rx='${rad}' fill='black'/></svg>`;
        const m = `linear-gradient(#000,#000), url("data:image/svg+xml;utf8,${encodeURIComponent(svg)}")`;
        for (const id of ['bg', 'dust', 'vig']) {
          const el = document.getElementById(id); if (!el) continue;
          el.style.webkitMaskImage = m; el.style.maskImage = m; el.style.webkitMaskComposite = 'xor'; el.style.maskComposite = 'exclude';
        }
        Stage.hole = { x: r.left * 2, y: r.top * 2, w: r.width * 2, h: r.height * 2 };   // canvas px, for the EDL's frame transform
      }
      initDust(); build(); Stage.seek(0);
      const c = (document.body.dataset.clip || '').split(',').map(Number);
      return { dur: Stage.dur, alpha: document.body.classList.contains('alpha'), hole: Stage.hole || null,
        clip: c.length === 4 ? { x: c[0], y: c[1], width: c[2], height: c[3] } : null };
    },
  };
  window.Stage = Stage; window.seek = Stage.seek;
  // open the file in a browser with ?t=3.2 to look at one moment, or ?play to watch it
  window.addEventListener('load', async () => {
    const q = new URLSearchParams(location.search);
    if (q.has('t') || q.has('play')) {
      await Stage.ready();
      if (q.has('play')) { const s = performance.now(); const tick = () => { Stage.seek(((performance.now() - s) / 1000) % (Stage.dur + .5)); requestAnimationFrame(tick); }; tick(); }
      else Stage.seek(parseFloat(q.get('t')));
    }
  });
})();
