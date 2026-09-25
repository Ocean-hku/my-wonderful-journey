'use strict';

/* ==========================================================================
   引擎层 —— 虚拟画布 1280×720 + letterbox 自适应
   与 Python 版 game/main.py 的 compute_letterbox() / screen_to_game() 一一对应
   ========================================================================== */

const GW = 1280;
const GH = 720;

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d', { alpha: false });

let viewScale = 1, viewOX = 0, viewOY = 0, dpr = 1;

/* ---------- letterbox：与 Python compute_letterbox() 完全一致 ---------- */
function computeLetterbox(realW, realH, gameW = GW, gameH = GH) {
  const scale = Math.min(realW / gameW, realH / gameH);
  const ox = (realW - gameW * scale) / 2;
  const oy = (realH - gameH * scale) / 2;
  return { scale, ox, oy };
}

/* ---------- 屏幕坐标 → 游戏坐标：等价于 Python screen_to_game() ---------- */
function screenToGame(clientX, clientY) {
  const r = canvas.getBoundingClientRect();
  return {
    x: (clientX - r.left) / r.width * GW,
    y: (clientY - r.top) / r.height * GH,
  };
}

function resize() {
  dpr = Math.min(window.devicePixelRatio || 1, 2);
  const w = window.innerWidth;
  const h = window.innerHeight;
  const lb = computeLetterbox(w, h);
  viewScale = lb.scale;
  viewOX = lb.ox;
  viewOY = lb.oy;

  canvas.width = Math.round(GW * dpr);
  canvas.height = Math.round(GH * dpr);

  const fit = computeLetterbox(w, h);
  canvas.style.width = Math.round(GW * fit.scale) + 'px';
  canvas.style.height = Math.round(GH * fit.scale) + 'px';

  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = 'high';
}

window.addEventListener('resize', resize);
window.addEventListener('orientationchange', () => setTimeout(resize, 120));

/* ============================== 资源 ============================== */

const Res = { img: {}, aud: {} };

async function loadManifest(manifest) {
  const images = manifest.images || {};
  const audios = manifest.audio || {};

  const imgPaths = Array.from(new Set(Object.values(images)));
  const total = imgPaths.length;
  let done = 0;
  const tick = () => { done++; setStat('加载资源 ' + done + '/' + total); };

  const imgMap = {};
  await Promise.all(imgPaths.map(p => new Promise(res => {
    const im = new Image();
    im.onload = () => { imgMap[p] = im; tick(); res(); };
    im.onerror = () => { console.warn('[缺失图片]', p); tick(); res(); };
    im.src = p;
  })));

  for (const k in images) Res.img[k] = imgMap[images[k]] || null;
  for (const k in audios) Res.aud[k] = audios[k];   // 音频只登记 URL，播放时按需创建
}

/* 与 Python 版 img() / aud() 对应的名字解析 */
function img(name) { return Res.img[name] || null; }
function aud(name) { return Res.aud[name] || null; }

/* ==================== 音频：替代 pygame.mixer ==================== */

const audio = {
  _bgm: null, _bgmKey: null,
  _voice: null, _voiceGuard: null,
  _unlocked: false,

  unlock() {
    if (this._unlocked) return;
    this._unlocked = true;
    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (AC) { const ac = new AC(); if (ac.state === 'suspended') ac.resume(); }
    } catch (e) { /* ignore */ }
  },

  playBgm(key, loop = true) {
    const src = aud(key);
    if (!src) return;                                   // 与 Python 一致：文件缺失则静默
    if (this._bgmKey === key && this._bgm && !this._bgm.paused) return;
    this.stopBgm();
    const a = new Audio(src);
    a.loop = loop;
    a.volume = 0.45;
    a.play().catch(() => {});
    this._bgm = a;
    this._bgmKey = key;
  },

  stopBgm() {
    if (this._bgm) { this._bgm.pause(); this._bgm.currentTime = 0; }
    this._bgm = null;
    this._bgmKey = null;
  },

  playVoice(key, onDone) {
    const src = aud(key);
    if (!src) { if (onDone) onDone(); return; }         // 与 Python 一致：文件缺失则立即回调
    this.stopVoice();
    const a = new Audio(src);
    let fired = false;
    const fire = () => {
      if (fired) return;
      fired = true;
      if (this._voiceGuard) { clearTimeout(this._voiceGuard); this._voiceGuard = null; }
      if (onDone) onDone();
    };
    a.addEventListener('ended', fire, { once: true });
    a.addEventListener('error', fire, { once: true });
    // 兜底：环境无法正常播完（静音、自动播放受限、无头浏览器）时也要放行，避免流程卡死
    this._voiceGuard = setTimeout(fire, 8000);
    a.play().catch(fire);
    this._voice = a;
  },

  stopVoice() {
    if (this._voiceGuard) { clearTimeout(this._voiceGuard); this._voiceGuard = null; }
    if (this._voice) {
      const v = this._voice;
      this._voice = null;
      try { v.pause(); v.currentTime = 0; } catch (e) { /* ignore */ }
    }
  },
};

/* ====================== 淡入淡出：对应 Fader ====================== */

const fader = {
  alpha: 0, active: false, dir: 1, speed: 8, onDone: null,

  fadeOut(cb, speed = 8) { this.alpha = 0; this.dir = 1; this.speed = speed; this.active = true; this.onDone = cb || null; },
  fadeIn(cb, speed = 8) { this.alpha = 255; this.dir = -1; this.speed = speed; this.active = true; this.onDone = cb || null; },

  update(dt) {
    if (!this.active) return;
    this.alpha += this.dir * this.speed * (dt * 60);
    if (this.dir === 1 && this.alpha >= 255) {
      this.alpha = 255; this.active = false;
      const cb = this.onDone; this.onDone = null; if (cb) cb();
    } else if (this.dir === -1 && this.alpha <= 0) {
      this.alpha = 0; this.active = false;
      const cb = this.onDone; this.onDone = null; if (cb) cb();
    }
  },

  draw(c) {
    if (this.alpha <= 0) return;
    c.save();
    c.globalAlpha = Math.min(1, this.alpha / 255);
    c.fillStyle = '#000';
    c.fillRect(0, 0, GW, GH);
    c.restore();
  },
};

/* ====================== 全局状态 ====================== */

const state = {
  diffKey: '',
  score: 0,
};

/* ====================== 场景管理 ====================== */

const sm = {
  scenes: {}, current: null, currentName: '',

  register(name, scene) { this.scenes[name] = scene; },

  switch(name) {
    if (!this.scenes[name]) {
      console.warn('[未知场景]', name);
      return;
    }
    this.currentName = name;
    this.current = this.scenes[name];
    if (this.current.onEnter) this.current.onEnter();
    fader.fadeIn();
    syncDevMenu();
  },
};

/* ============================== 工具 ============================== */

function inRect(p, r) {
  return r && p.x >= r.x && p.x <= r.x + r.w && p.y >= r.y && p.y <= r.y + r.h;
}

function inCircle(p, cx, cy, radius) {
  const dx = p.x - cx, dy = p.y - cy;
  return dx * dx + dy * dy <= radius * radius;
}

/* [left, right, top, bottom] → {x,y,w,h}，对应 pygame.Rect(l, t, r-l, b-t) */
function rectFrom(a) {
  return { x: a[0], y: a[2], w: a[1] - a[0], h: a[3] - a[2] };
}

function blitFull(c, im) {
  if (im) c.drawImage(im, 0, 0, GW, GH);
}

function roundRect(c, x, y, w, h, r) {
  c.beginPath();
  if (c.roundRect) { c.roundRect(x, y, w, h, r); return; }
  c.moveTo(x + r, y);
  c.arcTo(x + w, y, x + w, y + h, r);
  c.arcTo(x + w, y + h, x, y + h, r);
  c.arcTo(x, y + h, x, y, r);
  c.arcTo(x, y, x + w, y, r);
  c.closePath();
}

function setStat(txt) {
  const el = document.getElementById('stat');
  if (el) el.textContent = txt;
}

/* ============================== 光标 ============================== */

const isTouch = window.matchMedia('(pointer: coarse)').matches;

const cursor = {
  x: GW / 2, y: GH / 2, hover: false,
  draw(c) {
    if (isTouch) return;
    const im = this.hover ? img('发光鼠标.png') : img('鼠标.png');
    if (!im) return;
    c.drawImage(im, this.x - 20, this.y - 20, 40, 40);
  },
};

const DEBUG = { hotspots: false };

function drawHotspots(c) {
  if (!DEBUG.hotspots || !sm.current || !sm.current.hotspots) return;
  c.save();
  c.lineWidth = 3;
  c.strokeStyle = '#ff00ff';              // 品红：在蓝/绿/暖色背景上都醒目
  c.fillStyle = 'rgba(255,0,255,.16)';
  for (const r of sm.current.hotspots()) {
    if (!r) continue;
    c.fillRect(r.x, r.y, r.w, r.h);
    c.strokeRect(r.x + 0.5, r.y + 0.5, r.w, r.h);
  }
  c.restore();
}

/* ============================== 主循环 ============================== */

let lastT = 0;

function loop(t) {
  const dt = Math.min((t - lastT) / 1000 || 0, 0.05);
  lastT = t;

  if (!fader.active && sm.current && sm.current.update) sm.current.update(dt);
  fader.update(dt);

  ctx.fillStyle = '#000';
  ctx.fillRect(0, 0, GW, GH);

  if (sm.current && sm.current.draw) sm.current.draw(ctx);
  drawHotspots(ctx);
  fader.draw(ctx);
  cursor.draw(ctx);

  requestAnimationFrame(loop);
}

/* ============================== 事件 ============================== */

function bindEvents() {
  canvas.addEventListener('pointerdown', e => {
    e.preventDefault();
    audio.unlock();
    const p = screenToGame(e.clientX, e.clientY);
    cursor.x = p.x; cursor.y = p.y;
    if (!fader.active && sm.current && sm.current.handleEvent) {
      sm.current.handleEvent({ type: 'down', pos: p, x: p.x, y: p.y });
    }
  }, { passive: false });

  canvas.addEventListener('pointermove', e => {
    const p = screenToGame(e.clientX, e.clientY);
    cursor.x = p.x; cursor.y = p.y;
    if (sm.current && sm.current.isHot && !isTouch) cursor.hover = sm.current.isHot(p);
  });

  canvas.addEventListener('contextmenu', e => e.preventDefault());

  window.addEventListener('keydown', e => {
    if (e.key === 'd' || e.key === 'D') toggleDebug();
  });

  const btn = document.getElementById('btn-debug');
  if (btn) btn.addEventListener('click', toggleDebug);
}

function toggleDebug() {
  DEBUG.hotspots = !DEBUG.hotspots;
  const btn = document.getElementById('btn-debug');
  if (btn) btn.classList.toggle('on', DEBUG.hotspots);
  updateStat();
}

/* ============================== 开发者菜单 ============================== */

function sceneLabel(name) {
  const groups = (typeof SCENE_MENU !== 'undefined') ? SCENE_MENU : [];
  for (const g of groups) {
    for (const it of g.items) {
      if (it[0] === name) return it[1];
    }
  }
  return name;
}

function updateStat() {
  const el = document.getElementById('stat');
  if (!el) return;
  const n = (sm.current && sm.current.hotspots) ? sm.current.hotspots().length : 0;
  el.textContent = sceneLabel(sm.currentName) + (DEBUG.hotspots ? ' · 热区 ' + n : '');
}

/* 场景切换后同步下拉框与状态文本 */
function syncDevMenu() {
  const sel = document.getElementById('scene-select');
  if (sel && sel.value !== sm.currentName) sel.value = sm.currentName;
  updateStat();
}

function initDevMenu() {
  const sel = document.getElementById('scene-select');
  if (!sel) return;

  const groups = (typeof SCENE_MENU !== 'undefined') ? SCENE_MENU : [];
  for (const g of groups) {
    const og = document.createElement('optgroup');
    og.label = g.group;
    for (const it of g.items) {
      const op = document.createElement('option');
      op.value = it[0];
      op.textContent = it[1];
      og.appendChild(op);
    }
    sel.appendChild(og);
  }

  sel.addEventListener('change', () => {
    const name = sel.value;
    if (!name) return;
    audio.unlock();
    sm.switch(name);
    if (DEBUG.hotspots) { fader.alpha = 0; fader.active = false; }   // 调试模式下立即呈现，不等淡入

    // 同步到 hash（保留 debug / spell=xx 等非场景段），刷新后仍停在当前场景
    try {
      const parts = (location.hash || '').replace('#', '').split(/[,&]/).filter(Boolean);
      const keep = parts.filter(p => !sm.scenes[p]);
      location.hash = [name].concat(keep).join(',');
    } catch (e) { /* ignore */ }
  });
}

/* ============================== 启动 ============================== */

async function boot() {
  resize();
  bindEvents();

  await loadManifest(window.ASSET_MANIFEST || { images: {}, audio: {} });

  registerAllScenes();
  initDevMenu();

  const bootEl = document.getElementById('boot');
  if (bootEl) {
    bootEl.classList.add('hide');
    setTimeout(() => { if (bootEl.parentNode) bootEl.parentNode.removeChild(bootEl); }, 350);
  }

  // 调试入口： #场景名[,debug][,spell=word]
  const parts = (location.hash || '').replace('#', '').split(/[,&]/).filter(Boolean);
  const isDebug = parts.indexOf('debug') >= 0;
  if (isDebug) {
    DEBUG.hotspots = true;
    const b = document.getElementById('btn-debug');
    if (b) b.classList.add('on');
  }

  const target = parts.filter(p => sm.scenes[p])[0];
  sm.switch(target || 'start');

  const spellArg = parts.filter(p => p.indexOf('spell=') === 0)[0];
  if (spellArg && sm.current.openSpelling) sm.current.openSpelling(spellArg.split('=')[1]);

  // 调试入口： autodone 直接把超市场景标记为全部收齐，用于验证后续跳转链路
  if (parts.indexOf('autodone') >= 0 && sm.current && sm.current._end && sm.current.done) {
    ITEM_ENGLISH.forEach(it => sm.current.done.add(it.word));
    sm.current.doneTransit = false;
    sm.current._end(true);
  }

  if (isDebug) {
    fader.speed = 255;   // 调试：淡入淡出 1 帧完成，便于立即观察与自动化验证
    fader.alpha = 0;
    fader.active = false;
  }
  updateStat();

  requestAnimationFrame(t => { lastT = t; loop(t); });
}
