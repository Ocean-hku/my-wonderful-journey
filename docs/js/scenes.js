'use strict';

/* ==========================================================================
   场景层 —— 对应 Python 版 main.py 的全部 22 个场景
   所有热区坐标、常量、流程均从 main.py 逐字搬运，未做任何换算或重新标定
   ========================================================================== */

const FPS = 60;

/* ============================ 词表 / 工具 ============================ */

function shuffle(a) {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    const t = a[i]; a[i] = a[j]; a[j] = t;
  }
  return a;
}

function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

function wordAudio(w) { return '2采购清单/采购清单-单词发音/' + w + '.mp3'; }

const SHOPPING_CN = { '1': '背包', '2': '水壶', '3': '指南针', '4': '苹果', '5': '创可贴', '6': '雨伞', '7': '蛋糕', '8': '棒棒糖' };

function shoppingAudio(group, sub) {
  const label = SHOPPING_CN[group];
  for (const sep of [' ', '']) {
    const p = `2采购清单/采购清单-父母介绍/${group}.${sub}${sep}${label}.mp3`;
    if (aud(p)) return p;
  }
  return `2采购清单/采购清单-父母介绍/${group}.${sub} ${label}.mp3`;
}

/* ============================ 常量（照搬 main.py） ============================ */

/* main.py:652-663 */
const SHOPPING_ITEMS = [
  { idx: [1, 2, 3], group: '1', word: 'backpack', rect: { x: 410, y: 170, w: 80, h: 80 } },
  { idx: [4, 5], group: '2', word: 'bottle', rect: { x: 410, y: 285, w: 80, h: 80 } },
  { idx: [6, 7, 8], group: '3', word: 'compass', rect: { x: 410, y: 395, w: 80, h: 80 } },
  { idx: [9, 10, 11], group: '4', word: 'apple', rect: { x: 410, y: 505, w: 80, h: 80 } },
  { idx: [12, 13, 14], group: '5', word: 'bandage', rect: { x: 660, y: 170, w: 80, h: 80 } },
  { idx: [15, 16, 17], group: '6', word: 'umbrella', rect: { x: 660, y: 285, w: 80, h: 80 } },
  { idx: [18, 19], group: '7', word: 'cake', rect: { x: 660, y: 395, w: 80, h: 80 } },
  { idx: [20, 21, 22], group: '8', word: 'lollipop', rect: { x: 660, y: 505, w: 80, h: 80 } },
];

/* main.py:686-695 */
const ICON_RECTS = [
  ['backpack', { x: 410, y: 170, w: 80, h: 80 }],
  ['bandage', { x: 660, y: 170, w: 80, h: 80 }],
  ['bottle', { x: 410, y: 285, w: 80, h: 80 }],
  ['umbrella', { x: 660, y: 285, w: 80, h: 80 }],
  ['compass', { x: 410, y: 395, w: 80, h: 80 }],
  ['cake', { x: 660, y: 395, w: 80, h: 80 }],
  ['apple', { x: 410, y: 505, w: 80, h: 80 }],
  ['lollipop', { x: 660, y: 505, w: 80, h: 80 }],
];

/* main.py:739-766 */
const ITEM_ENGLISH = [
  { cn: '水壶', word: 'bottle', rect: { x: 430, y: 450, w: 34, h: 38 } },
  { cn: '背包', word: 'backpack', rect: { x: 470, y: 450, w: 40, h: 40 } },
  { cn: '指南针', word: 'compass', rect: { x: 385, y: 486, w: 40, h: 29 } },
  { cn: '创可贴', word: 'bandage', rect: { x: 427, y: 487, w: 26, h: 33 } },
  { cn: '雨伞', word: 'umbrella', rect: { x: 385, y: 516, w: 25, h: 46 } },
  { cn: '棒棒糖', word: 'lollipop', rect: { x: 560, y: 434, w: 175, h: 46 } },
  { cn: '蛋糕', word: 'cake', rect: { x: 560, y: 481, w: 175, h: 39 } },
  { cn: '苹果', word: 'apple', rect: { x: 565, y: 524, w: 98, h: 41 } },
];

const DISTRACT_RECTS = [
  { x: 383, y: 450, w: 42, h: 35 },
  { x: 455, y: 491, w: 40, h: 29 },
  { x: 420, y: 521, w: 95, h: 44 },
  { x: 560, y: 403, w: 175, h: 29 },
  { x: 668, y: 521, w: 67, h: 44 },
];

const SPELL_IMAGES = {
  backpack: '6背包拼写.PNG',
  bottle: '6水壶拼写.PNG',
  compass: '6指南针拼写.PNG',
  bandage: '6创可贴拼写.PNG',
  umbrella: '6雨伞拼写.PNG',
  lollipop: '6棒棒糖拼写.PNG',
  cake: '6蛋糕拼写.PNG',
  apple: '6苹果拼写.PNG',
};

/* main.py:892-908 */
const BOOK_DATA = [
  {
    img: '9动物手册.PNG', next: 'animal_book_2',
    animals: [
      ['fox', 'fox.mp3', '手册狐狸 母.mp3', { x: 330, y: 200, w: 180, h: 140 }],
      ['horse', 'horse.mp3', '手册马 父.mp3', { x: 330, y: 360, w: 180, h: 155 }],
      ['pig', 'pig.mp3', '手册小猪 母.mp3', { x: 332, y: 528, w: 175, h: 138 }],
    ],
  },
  {
    img: '10动物手册.PNG', next: 'animal_book_3',
    animals: [
      ['tiger', 'tiger.mp3', '手册老虎 父.mp3', { x: 330, y: 200, w: 180, h: 140 }],
      ['sheep', 'sheep.mp3', '手册小羊 母.mp3', { x: 330, y: 360, w: 180, h: 155 }],
      ['elephant', 'elephant.mp3', '手册大象 父.mp3', { x: 332, y: 528, w: 175, h: 138 }],
    ],
  },
  {
    img: '11动物手册.PNG', next: 'depart',
    animals: [
      ['parrot', 'parrot.mp3', '手册鹦鹉 母.mp3', { x: 330, y: 200, w: 180, h: 140 }],
      ['giraffe', 'giraffe.mp3', '手册长颈鹿 母.mp3', { x: 330, y: 360, w: 180, h: 155 }],
      ['monkey', 'monkey.mp3', '手册猴子 母.mp3', { x: 332, y: 528, w: 175, h: 138 }],
    ],
  },
];

/* main.py:980-1037 */
const FOREST_ANIMALS = [
  { key: 'fox', cn: '狐狸', word: 'fox', frames: ['12狐狸1.PNG', '12狐狸2.PNG', '12狐狸3.PNG'],
    dialogues: ['5森林动物交互/狐狸_我只是好奇里面有什么.mp3', '5森林动物交互/狐狸_这个包真酷还给你.mp3'] },
  { key: 'horse', cn: '小马', word: 'horse', frames: ['13小马1.PNG', '13小马2.PNG', '13小马3.PNG'],
    dialogues: ['5森林动物交互/小马_谢谢你的苹果.mp3', '5森林动物交互/小马_真甜啊.mp3'] },
  { key: 'pig', cn: '小猪', word: 'pig', frames: ['14小猪1.PNG', '14小猪2.PNG', '14小猪3.PNG'],
    dialogues: ['5森林动物交互/小猪_蛋糕.mp3', '5森林动物交互/小猪_从现在起.mp3'] },
  { key: 'sheep', cn: '小羊', word: 'sheep', frames: ['15小羊1.PNG', '15小羊2.PNG', '15小羊3.PNG'],
    dialogues: ['5森林动物交互/小羊_水真好喝.mp3', '5森林动物交互/小羊_你是我.mp3'] },
  { key: 'elephant', cn: '大象', word: 'elephant', frames: ['16大象1.PNG', '16大象2.PNG', '16大象3.PNG'],
    dialogues: ['5森林动物交互/大象_对不起.mp3', '5森林动物交互/大象_幸好.mp3'] },
  { key: 'tiger', cn: '老虎', word: 'tiger', frames: ['17老虎1.PNG', '17老虎2.PNG', '17老虎3.PNG'],
    dialogues: ['5森林动物交互/老虎_谢谢.mp3', '5森林动物交互/老虎_有我在.mp3'] },
  { key: 'parrot', cn: '鹦鹉', word: 'parrot', frames: ['18鹦鹉1.PNG', '18鹦鹉2.PNG', '18鹦鹉3.PNG'],
    dialogues: ['5森林动物交互/鹦鹉_亮晶晶.mp3', '5森林动物交互/鹦鹉_好玩.mp3',
                '5森林动物交互/鹦鹉_还给你啦.mp3', '5森林动物交互/鹦鹉_哎呀.mp3'] },
  { key: 'giraffe', cn: '长颈鹿', word: 'giraffe', frames: ['19长颈鹿1.PNG', '19长颈鹿2.PNG', '19长颈鹿3.PNG'],
    dialogues: ['5森林动物交互/长颈鹿_这点高度.mp3', '5森林动物交互/长颈鹿_别再.mp3'] },
  { key: 'monkey', cn: '猴子', word: 'monkey', frames: ['20猴子1.PNG', '20猴子2.PNG', '20猴子3.PNG'],
    dialogues: ['5森林动物交互/猴子_你真厉害.mp3', '5森林动物交互/猴子_欢迎来森林玩.mp3'] },
];

const ANIMAL_ORDER = FOREST_ANIMALS.map(a => a.key);
const ANIMAL_MAP = {};
FOREST_ANIMALS.forEach(a => { ANIMAL_MAP[a.key] = a; });

function nextAnimalScene(key) {
  const i = ANIMAL_ORDER.indexOf(key);
  return (i + 1 < ANIMAL_ORDER.length) ? 'forest_' + ANIMAL_ORDER[i + 1] : 'group_photo';
}

/* main.py:1179-1206 */
const ANIMAL_WORDS = {
  '狐狸': 'fox', '小马': 'horse', '小猪': 'pig', '小羊': 'sheep', '大象': 'elephant',
  '老虎': 'tiger', '鹦鹉': 'parrot', '长颈鹿': 'giraffe', '猴子': 'monkey',
};
const ITEM_WORDS = {
  '背包': 'backpack', '水壶': 'bottle', '指南针': 'compass', '苹果': 'apple',
  '创可贴': 'bandage', '雨伞': 'umbrella', '蛋糕': 'cake', '棒棒糖': 'lollipop',
};
const ALL_WORDS = Object.assign({}, ANIMAL_WORDS, ITEM_WORDS);

const DIFFICULTY = {
  easy: ['初级', 30],
  medium: ['中级', 25],
  hard: ['高级', 20],
};

function quizAudio(word) {
  if (Object.values(ANIMAL_WORDS).indexOf(word) >= 0) return '4森林动物手册/' + word + '.mp3';
  return '2采购清单/采购清单-单词发音/' + word + '.mp3';
}

/* main.py:1235-1252 */
function quizImage(levelCn, nameCn) {
  if (levelCn === '初级' || levelCn === '中级') return '初级、中级/22' + nameCn + '.PNG';
  return '高级/22' + nameCn + '高级.PNG';
}

/* ==========================================================================
   拼写面板（超市 / 森林）—— 对应 main.py:163-378
   _LAYOUT 逐字搬运：speaker(l,r,t,b), slot_bottom, kb(l,r,t,b), confirm(l,r,t,b), helper(l,r,t,b)
   ========================================================================== */

const SPELL_LAYOUT = {
  // 超市 8 项：拼写图是同一套模板，喇叭图标固定在同一位置 → spk 统一
  // 注意：原 Python 版此处的 spk 误填成了货架商品的点击热区（见 ITEM_ENGLISH），已修正
  // 实测喇叭图标 bbox ≈ (735,339)-(787,396)，统一放宽到 56×60 确保完全覆盖
  bottle:   { spk: [734, 790, 337, 397], slotBot: 485, kb: [450, 839, 558, 672], conf: [497, 637, 685, 719], hlp: [654, 804, 685, 719] },
  backpack: { spk: [734, 790, 337, 397], slotBot: 485, kb: [451, 838, 558, 671], conf: [497, 637, 685, 719], hlp: [654, 804, 685, 719] },
  compass:  { spk: [734, 790, 337, 397], slotBot: 485, kb: [450, 839, 560, 675], conf: [497, 637, 685, 719], hlp: [654, 804, 685, 719] },
  bandage:  { spk: [734, 790, 337, 397], slotBot: 485, kb: [450, 839, 558, 672], conf: [497, 637, 685, 719], hlp: [654, 804, 685, 719] },
  umbrella: { spk: [734, 790, 337, 397], slotBot: 485, kb: [442, 829, 556, 669], conf: [497, 637, 685, 719], hlp: [654, 804, 685, 719] },
  lollipop: { spk: [734, 790, 337, 397], slotBot: 485, kb: [442, 829, 556, 669], conf: [497, 637, 685, 719], hlp: [654, 804, 685, 719] },
  cake:     { spk: [734, 790, 337, 397], slotBot: 485, kb: [442, 829, 556, 669], conf: [497, 637, 685, 719], hlp: [654, 804, 685, 719] },
  apple:    { spk: [734, 790, 337, 397], slotBot: 485, kb: [447, 833, 556, 668], conf: [497, 637, 685, 719], hlp: [654, 804, 685, 719] },
  fox:      { spk: [708, 754, 340, 388], slotBot: 528, kb: [448, 824, 550, 658], conf: [494, 627, 669, 710], hlp: [645, 790, 668, 711] },
  horse:    { spk: [719, 766, 345, 394], slotBot: 536, kb: [455, 836, 559, 668], conf: [502, 636, 679, 719], hlp: [656, 801, 679, 719] },
  pig:      { spk: [708, 755, 345, 393], slotBot: 536, kb: [443, 825, 559, 669], conf: [490, 625, 680, 719], hlp: [644, 790, 680, 719] },
  sheep:    { spk: [693, 740, 344, 393], slotBot: 535, kb: [428, 810, 559, 670], conf: [475, 610, 680, 719], hlp: [629, 775, 680, 719] },
  elephant: { spk: [753, 799, 345, 393], slotBot: 536, kb: [466, 847, 559, 668], conf: [512, 646, 681, 719], hlp: [666, 812, 681, 719] },
  tiger:    { spk: [712, 759, 345, 395], slotBot: 540, kb: [443, 832, 562, 674], conf: [491, 628, 685, 719], hlp: [648, 796, 685, 719] },
  parrot:   { spk: [710, 758, 346, 395], slotBot: 539, kb: [444, 829, 562, 672], conf: [491, 627, 683, 719], hlp: [647, 794, 683, 719] },
  giraffe:  { spk: [725, 769, 299, 343], slotBot: 532, kb: [461, 803, 562, 663], conf: [501, 624, 680, 717], hlp: [639, 774, 680, 717] },
  monkey:   { spk: [714, 760, 336, 383], slotBot: 534, kb: [451, 813, 557, 660], conf: [494, 624, 679, 716], hlp: [640, 782, 679, 716] },
};

const SLOT_W = 52;
const SLOT_H = 58;

class SpellingWidget {
  constructor(word, bgName, audioKey, onSuccess, hintCount = 0, showHelper = true, overlayName = null) {
    this.word = word.toUpperCase();
    this.bgName = bgName;
    this.audioKey = audioKey;
    this.onSuccess = onSuccess;
    this.hintCount = hintCount;
    this.showHelper = showHelper;
    this.overlayName = overlayName;

    this.slots = new Array(this.word.length).fill(null);
    for (let i = 0; i < hintCount && i < this.slots.length; i++) this.slots[i] = this.word[i];

    this.shake = {};
    this.helperFlash = 0;
    this._buildLayout();
  }

  _buildLayout() {
    const n = this.word.length;
    const cfg = SPELL_LAYOUT[this.word.toLowerCase()];

    let slotBot, kbBox;
    if (cfg) {
      slotBot = cfg.slotBot;
      this.speakerRect = rectFrom(cfg.spk);
      this.confirmRect = rectFrom(cfg.conf);
      this.helperRect = rectFrom(cfg.hlp);
      kbBox = cfg.kb;
    } else {
      slotBot = 485;
      this.speakerRect = { x: 737, y: 340, w: 50, h: 50 };
      this.confirmRect = { x: 497, y: 685, w: 140, h: 34 };
      this.helperRect = { x: 654, y: 685, w: 150, h: 34 };
      kbBox = [450, 839, 561, 675];
    }

    const totalW = n * (SLOT_W + 6) - 6;
    const sx = Math.floor((GW - totalW) / 2);
    const sy = slotBot - SLOT_H;
    this.slotRects = [];
    for (let i = 0; i < n; i++) this.slotRects.push({ x: sx + i * (SLOT_W + 6), y: sy, w: SLOT_W, h: SLOT_H });

    const rows = ['QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM'];
    const X1 = kbBox[0], X2 = kbBox[1], Y1 = kbBox[2], Y2 = kbBox[3];
    const KB_W = X2 - X1, KB_H = Y2 - Y1;
    const CELL_W = 33;
    const CELL_H = Math.floor((KB_H - 2 * 6) / 3);
    const GAP = 6;

    this.keyRects = {};
    rows.forEach((row, ri) => {
      const rowW = row.length * CELL_W + (row.length - 1) * GAP;
      const kx = X1 + Math.floor((KB_W - rowW) / 2);
      const ky = Y1 + ri * (CELL_H + GAP);
      row.split('').forEach((ch, ci) => {
        this.keyRects[ch] = { x: kx + ci * (CELL_W + GAP), y: ky, w: CELL_W, h: CELL_H };
      });
    });
  }

  handleEvent(e) {
    const p = e.pos;
    if (inRect(p, this.speakerRect)) { audio.playVoice(this.audioKey); return; }
    if (inRect(p, this.confirmRect)) { this._check(); return; }
    if (this.showHelper && inRect(p, this.helperRect)) { this._hint(); return; }

    for (let i = 0; i < this.slotRects.length; i++) {
      if (inRect(p, this.slotRects[i]) && this.slots[i] && i >= this.hintCount) {
        this.slots[i] = null;
        return;
      }
    }
    for (const ch in this.keyRects) {
      if (inRect(p, this.keyRects[ch])) { this._type(ch); return; }
    }
  }

  _firstEmpty() { return this.slots.indexOf(null); }

  _type(ch) {
    const i = this._firstEmpty();
    if (i >= 0) this.slots[i] = ch;
  }

  _check() {
    if (this.slots.indexOf(null) >= 0) return;
    const wrong = [];
    for (let i = 0; i < this.slots.length; i++) {
      if (this.slots[i] !== this.word[i]) wrong.push(i);
    }
    if (wrong.length === 0) { this.onSuccess(); return; }
    for (const i of wrong) {
      this.shake[i] = 20;
      if (i >= this.hintCount) this.slots[i] = null;
    }
    audio.playVoice(pick(['3超市/再试试 父.mp3', '3超市/再试试 母.mp3']));
  }

  _hint() {
    const empty = [];
    for (let i = 0; i < this.slots.length; i++) if (this.slots[i] === null) empty.push(i);
    if (!empty.length) return;
    const i = pick(empty);
    this.slots[i] = this.word[i];
    this.helperFlash = 30;
  }

  update() {
    for (const k in this.shake) {
      this.shake[k] -= 1;
      if (this.shake[k] <= 0) delete this.shake[k];
    }
    if (this.helperFlash > 0) this.helperFlash -= 1;
  }

  draw(c) {
    blitFull(c, img(this.bgName));
    if (this.overlayName) blitFull(c, img(this.overlayName));

    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.font = '500 34px system-ui, -apple-system, "Segoe UI", sans-serif';

    this.slotRects.forEach((r, i) => {
      const ox = this.shake[i] ? Math.sin(this.shake[i] * 1.2) * 5 : 0;
      roundRect(c, r.x + ox, r.y, r.w, r.h, 6);
      c.fillStyle = '#ffffff';
      c.fill();
      c.lineWidth = 2;
      c.strokeStyle = '#3c78dc';
      c.stroke();
      if (this.slots[i]) {
        c.fillStyle = '#000000';
        c.fillText(this.slots[i], r.x + ox + r.w / 2, r.y + r.h / 2 + 1);
      }
    });

    if (this.helperFlash > 0) {
      c.save();
      c.globalAlpha = (this.helperFlash / 30) * 0.5;
      c.lineWidth = 3;
      c.strokeStyle = '#ffd24a';
      roundRect(c, this.helperRect.x, this.helperRect.y, this.helperRect.w, this.helperRect.h, 6);
      c.stroke();
      c.restore();
    }
  }

  hotspots() {
    return [this.speakerRect, this.confirmRect, this.helperRect]
      .concat(this.slotRects)
      .concat(Object.keys(this.keyRects).map(k => this.keyRects[k]));
  }
}

/* ==========================================================================
   测试用拼写面板 —— 对应 main.py:381-536（ABC 三行键盘，格 66px）
   ========================================================================== */

const T_KB_LEFT = 289, T_KB_TOP = 395, T_KB_BOT = 624;
const T_SLOT_LEFT = 687, T_SLOT_RIGHT = 1028, T_SLOT_TOP = 257, T_SLOT_BOT = 349;
const T_CELL = 66;

class TestSpellingWidget {
  constructor(word, bgName, audioKey, onSuccess, hintCount = 0, drawSpeaker = false) {
    this.word = word.toUpperCase();
    this.bgName = bgName;
    this.audioKey = audioKey;
    this.onSuccess = onSuccess;
    this.hintCount = hintCount;
    // 高级难度的背景图（22XX高级.jpg）上没有喇叭图标，需要代码补画，否则看不出可点
    this.drawSpeaker = drawSpeaker;

    this.slots = new Array(this.word.length).fill(null);
    for (let i = 0; i < hintCount && i < this.slots.length; i++) this.slots[i] = this.word[i];

    this.shake = {};
    this._buildLayout();
  }

  _buildLayout() {
    const n = this.word.length;
    const areaW = T_SLOT_RIGHT - T_SLOT_LEFT;
    const areaH = T_SLOT_BOT - T_SLOT_TOP;
    const maxSw = Math.floor(areaW / n);
    const slotH = Math.min(maxSw, areaH);
    const slotW = Math.min(maxSw, slotH);
    this.fontSlot = Math.max(20, Math.floor(slotH * 0.6));

    const gap = 4;
    const totalW = n * slotW + (n - 1) * gap;
    const sx = T_SLOT_LEFT + Math.floor((areaW - totalW) / 2);
    const sy = T_SLOT_TOP + Math.floor((areaH - slotH) / 2);

    this.slotRects = [];
    for (let i = 0; i < n; i++) this.slotRects.push({ x: sx + i * (slotW + gap), y: sy, w: slotW, h: slotH });

    this.spkRect = { x: 588, y: 257, w: 93, h: 92 };

    const rows = ['ABCDEFGHI', 'JKLMNOPQR', 'STUVWXYZ'];
    const C = T_CELL, GAP = 14;
    const kbH = T_KB_BOT - T_KB_TOP;
    const rowGap = Math.floor((kbH - 3 * C) / 2);

    this.keyRects = {};
    rows.forEach((row, ri) => {
      const ky = T_KB_TOP + ri * (C + rowGap);
      row.split('').forEach((ch, ci) => {
        this.keyRects[ch] = { x: T_KB_LEFT + ci * (C + GAP), y: ky, w: C, h: C };
      });
    });

    const ky3 = T_KB_TOP + 2 * (C + rowGap);
    this.confirmRect = { x: T_KB_LEFT + 8 * (C + GAP), y: ky3, w: C, h: C };
  }

  handleEvent(e) {
    const p = e.pos;
    if (inRect(p, this.spkRect)) { audio.playVoice(this.audioKey); return; }
    if (inRect(p, this.confirmRect)) { this._check(); return; }

    for (let i = 0; i < this.slotRects.length; i++) {
      if (inRect(p, this.slotRects[i]) && this.slots[i] && i >= this.hintCount) {
        this.slots[i] = null;
        return;
      }
    }
    for (const ch in this.keyRects) {
      if (inRect(p, this.keyRects[ch])) { this._type(ch); return; }
    }
  }

  _type(ch) {
    const i = this.slots.indexOf(null);
    if (i >= 0) this.slots[i] = ch;
  }

  _check() {
    if (this.slots.indexOf(null) >= 0) return;
    const wrong = [];
    for (let i = 0; i < this.slots.length; i++) {
      if (this.slots[i] !== this.word[i]) wrong.push(i);
    }
    if (wrong.length === 0) { this.onSuccess(); return; }
    for (const i of wrong) {
      this.shake[i] = 20;
      if (i >= this.hintCount) this.slots[i] = null;
    }
    audio.playVoice(pick(['3超市/再试试 父.mp3', '3超市/再试试 母.mp3']));
  }

  update() {
    for (const k in this.shake) {
      this.shake[k] -= 1;
      if (this.shake[k] <= 0) delete this.shake[k];
    }
  }

  draw(c) {
    blitFull(c, img(this.bgName));

    // 高级难度补画喇叭按钮（背景图上没有）
    if (this.drawSpeaker) {
      const r = this.spkRect;
      roundRect(c, r.x, r.y, r.w, r.h, 10);
      c.fillStyle = '#f5a623';
      c.fill();
      c.lineWidth = 3;
      c.strokeStyle = '#c47d0a';
      c.stroke();

      const cx = r.x + r.w / 2;
      const cy = r.y + r.h / 2;
      c.fillStyle = '#ffffff';
      c.beginPath();
      c.moveTo(cx - 20, cy - 9);
      c.lineTo(cx - 6, cy - 9);
      c.lineTo(cx + 9, cy - 24);
      c.lineTo(cx + 9, cy + 24);
      c.lineTo(cx - 6, cy + 9);
      c.lineTo(cx - 20, cy + 9);
      c.closePath();
      c.fill();

      c.strokeStyle = '#ffffff';
      c.lineWidth = 4;
      c.lineCap = 'round';
      c.beginPath(); c.arc(cx + 12, cy, 13, -0.75, 0.75); c.stroke();
      c.beginPath(); c.arc(cx + 12, cy, 22, -0.75, 0.75); c.stroke();
      c.lineCap = 'butt';
    }

    c.textAlign = 'center';
    c.textBaseline = 'middle';
    this.slotRects.forEach((r, i) => {
      const ox = this.shake[i] ? Math.sin(this.shake[i] * 1.2) * 5 : 0;
      roundRect(c, r.x + ox, r.y, r.w, r.h, 6);
      c.fillStyle = '#ffffff';
      c.fill();
      c.lineWidth = 2;
      c.strokeStyle = '#3c78dc';
      c.stroke();
      if (this.slots[i]) {
        c.fillStyle = '#000000';
        c.font = '500 ' + this.fontSlot + 'px system-ui, -apple-system, sans-serif';
        c.fillText(this.slots[i], r.x + ox + r.w / 2, r.y + r.h / 2 + 1);
      }
    });

    roundRect(c, this.confirmRect.x, this.confirmRect.y, this.confirmRect.w, this.confirmRect.h, 4);
    c.fillStyle = '#3cc83c';
    c.fill();
  }

  hotspots() {
    return [this.spkRect, this.confirmRect]
      .concat(this.slotRects)
      .concat(Object.keys(this.keyRects).map(k => this.keyRects[k]));
  }
}

/* ==========================================================================
   0. 开始页（main.py:576-590）
   ========================================================================== */

const StartScene = {
  BTN: { x: 520, y: 580, w: 240, h: 80 },
  onEnter() { audio.stopBgm(); },
  handleEvent(e) {
    if (e.type === 'down' && inRect(e.pos, this.BTN)) fader.fadeOut(() => sm.switch('living1'));
  },
  draw(c) { blitFull(c, img('1开始页.PNG')); },
  isHot(p) { return inRect(p, this.BTN); },
  hotspots() { return [this.BTN]; },
};

/* ==========================================================================
   1. 客厅 1（main.py:593-610）
   ========================================================================== */

const LivingRoom1Scene = {
  FOREST_CENTER: [640, 630],
  FOREST_RADIUS: 70,
  onEnter() {
    audio.playBgm('主场景BGM.mp3');
    audio.playVoice('1开场/开场 去旅行 母.mp3');
  },
  handleEvent(e) {
    if (e.type === 'down' && inCircle(e.pos, this.FOREST_CENTER[0], this.FOREST_CENTER[1], this.FOREST_RADIUS)) {
      fader.fadeOut(() => sm.switch('living2'));
    }
  },
  draw(c) { blitFull(c, img('2.1客厅.png')); },
  isHot(p) { return inCircle(p, this.FOREST_CENTER[0], this.FOREST_CENTER[1], this.FOREST_RADIUS); },
  hotspots() {
    const r = this.FOREST_RADIUS;
    return [{ x: this.FOREST_CENTER[0] - r, y: this.FOREST_CENTER[1] - r, w: 2 * r, h: 2 * r }];
  },
};

/* ==========================================================================
   2. 客厅 2（main.py:613-623）
   ========================================================================== */

const LivingRoom2Scene = {
  onEnter() {
    audio.playVoice('1开场/开场2 去超市 母.mp3', () => fader.fadeOut(() => sm.switch('transit_to_market')));
  },
  draw(c) { blitFull(c, img('2.2客厅.png')); },
};

/* ==========================================================================
   3. 通用过场（main.py:626-648）—— 3 秒后自动跳转
   ========================================================================== */

function makeTransitScene(imgName, nextScene, bgmKey) {
  return {
    timer: 0,
    onEnter() {
      this.timer = 3.0;
      if (bgmKey) audio.playBgm(bgmKey);
    },
    update(dt) {
      this.timer -= dt;
      if (this.timer <= 0) {
        this.timer = 1e9;
        fader.fadeOut(() => sm.switch(nextScene));
      }
    },
    draw(c) { blitFull(c, img(imgName)); },
  };
}

/* ==========================================================================
   4. 采购清单（main.py:684-736）
   ========================================================================== */

const ShoppingListScene = {
  slides: [],
  current: 0,

  onEnter() {
    this.current = 0;
    this._loadSlide();
  },
  _loadSlide() {
    const s = this.slides[this.current];
    audio.playVoice(shoppingAudio(s[1], s[2]));
  },
  handleEvent(e) {
    if (e.type !== 'down') return;
    for (const [word, rect] of ICON_RECTS) {
      if (inRect(e.pos, rect)) { audio.playVoice(wordAudio(word)); return; }
    }
    this._advance();
  },
  _advance() {
    if (this.current < this.slides.length - 1) {
      this.current++;
      this._loadSlide();
    } else {
      fader.fadeOut(() => sm.switch('supermarket'));
    }
  },
  draw(c) { blitFull(c, img(this.slides[this.current][0])); },
  isHot(p) { return ICON_RECTS.some(([, r]) => inRect(p, r)); },
  hotspots() { return ICON_RECTS.map(([, r]) => r); },
};

SHOPPING_ITEMS.forEach(it => {
  it.idx.forEach((idx, j) => {
    ShoppingListScene.slides.push(['4.' + idx + '.png', it.group, String(j + 1)]);
  });
});

/* ==========================================================================
   5. 超市（main.py:768-873）
   ========================================================================== */

const SupermarketScene = {
  onEnter() {
    this.done = new Set();
    this.spelling = null;
    this.miss = 0;
    this.showHint = false;
    this.hintTimer = 0;
    this.dwellTimer = 0;
    this.doneTransit = false;
    audio.playBgm('主场景BGM.mp3');
  },

  openSpelling(word) {
    if (this.done.has(word)) return;
    this.spelling = new SpellingWidget(
      word, '5超市.PNG', wordAudio(word),
      () => this.onSpellDone(word), 0, true, SPELL_IMAGES[word],
    );
    this.showHint = false;
  },

  onSpellDone(word) {
    this.done.add(word);
    this.spelling = null;
    if (this.done.size >= 8) this._end(true);
  },

  /* main.py:802-809 —— 播完「采购完成」后淡出并进入回程过场 */
  _end(full) {
    if (this.doneTransit) return;
    this.doneTransit = true;
    audio.stopBgm();
    audio.playVoice(
      full ? '3超市/采购完成 母.mp3' : '3超市/采购完成 父.mp3',
      () => fader.fadeOut(() => sm.switch('transit_home')),
    );
  },

  handleEvent(e) {
    if (this.doneTransit) return;
    if (this.spelling) { this.spelling.handleEvent(e); return; }
    if (e.type !== 'down') return;

    const p = e.pos;
    this.showHint = false;
    let hit = false;

    for (const it of ITEM_ENGLISH) {
      if (inRect(p, it.rect)) {
        hit = true;
        if (!this.done.has(it.word)) this.openSpelling(it.word);
        break;
      }
    }
    if (!hit) {
      for (const r of DISTRACT_RECTS) {
        if (inRect(p, r)) {
          hit = true;
          audio.playVoice(pick(['3超市/不需要 父.mp3', '3超市/不需要 母.mp3']));
          break;
        }
      }
    }
    if (!hit) {
      this.miss += 1;
      if (this.miss >= 5) { this.miss = 0; this.showHint = true; this.hintTimer = 2.0; }
    }
  },

  update(dt) {
    if (this.spelling) this.spelling.update();
    if (this.showHint) {
      this.hintTimer -= dt;
      if (this.hintTimer <= 0) this.showHint = false;
    }
    // main.py:853-856 —— 收满 4 件后若停留超过 2 分钟，按未完成收尾
    if (!this.doneTransit && this.done.size >= 4) {
      this.dwellTimer += dt;
      if (this.dwellTimer > 120) this._end(false);
    }
  },

  draw(c) {
    if (this.spelling) { this.spelling.draw(c); return; }

    blitFull(c, img('5超市.PNG'));
    if (this.showHint) blitFull(c, img('5.1.png'));

    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.font = '500 22px system-ui, -apple-system, sans-serif';

    for (const it of ITEM_ENGLISH) {
      if (!this.done.has(it.word)) continue;
      const r = it.rect;
      c.save();
      c.globalAlpha = 0.39;
      c.fillStyle = '#3cc83c';
      c.fillRect(r.x, r.y, r.w, r.h);
      c.restore();
      c.fillStyle = '#3cc83c';
      c.fillText('OK', r.x + r.w / 2, r.y + r.h / 2);
    }
  },

  isHot(p) {
    if (this.spelling) return this.spelling.hotspots().some(r => inRect(p, r));
    return ITEM_ENGLISH.some(it => inRect(p, it.rect)) || DISTRACT_RECTS.some(r => inRect(p, r));
  },

  hotspots() {
    if (this.spelling) return this.spelling.hotspots();
    return ITEM_ENGLISH.map(it => it.rect).concat(DISTRACT_RECTS);
  },
};

/* ==========================================================================
   8. 动物手册（main.py:910-950）
   ========================================================================== */

function makeAnimalBookScene(bookIdx) {
  return {
    onEnter() {
      const book = BOOK_DATA[bookIdx];
      this.next = book.next;
      this.seq = [];
      for (const a of book.animals) {
        this.seq.push('4森林动物手册/' + a[1]);
        this.seq.push('4森林动物手册/' + a[2]);
      }
      this.seqIdx = 0;
      this.listening = true;
      this._playNext();
    },
    _playNext() {
      if (this.seqIdx < this.seq.length) {
        const p = this.seq[this.seqIdx];
        this.seqIdx += 1;
        audio.playVoice(p, () => this._playNext());
      } else {
        this.listening = false;
      }
    },
    handleEvent(e) {
      if (this.listening || e.type !== 'down') return;
      for (const a of BOOK_DATA[bookIdx].animals) {
        if (inRect(e.pos, a[3])) { audio.playVoice('4森林动物手册/' + a[1]); return; }
      }
      fader.fadeOut(() => sm.switch(this.next));
    },
    draw(c) { blitFull(c, img(BOOK_DATA[bookIdx].img)); },
    isHot(p) { return !this.listening && BOOK_DATA[bookIdx].animals.some(a => inRect(p, a[3])); },
    hotspots() { return this.listening ? [] : BOOK_DATA[bookIdx].animals.map(a => a[3]); },
  };
}

/* ==========================================================================
   9. 出发（main.py:953-961）
   ========================================================================== */

const DepartScene = {
  onEnter() {
    audio.stopBgm();
    audio.playVoice('4森林动物手册/出发 母.mp3',
      () => fader.fadeOut(() => sm.switch('transit_to_forest')));
  },
  draw(c) { blitFull(c, img('7.2.png')); },
};

/* ==========================================================================
   11. 森林动物（main.py:1048-1125）
   ========================================================================== */

function makeForestAnimalScene(key) {
  const A = ANIMAL_MAP[key];
  const next = nextAnimalScene(key);

  return {
    onEnter() {
      this.frame = 0;
      this.spelling = null;
      this.dialIdx = 0;
      this.locked = false;
      this.currentBg = null;
      this._goFrame1();
    },

    _goFrame1() {
      this.frame = 0;
      this.locked = true;
      this.currentBg = img(A.frames[0]);
      const p = pick([
        '5森林动物交互/交互' + A.cn + ' 父.mp3',
        '5森林动物交互/交互' + A.cn + ' 母.mp3',
      ]);
      audio.playVoice(p, () => fader.fadeOut(() => this._goFrame2()));
    },

    _goFrame2() {
      this.frame = 1;
      this.locked = false;
      this.spelling = new SpellingWidget(
        A.word, A.frames[1], '4森林动物手册/' + A.word + '.mp3',
        () => this._goFrame3(), 1, true,
      );
      fader.fadeIn();
    },

    _goFrame3() {
      this.spelling = null;
      this.frame = 2;
      this.dialIdx = 0;
      this._playNextDialogue();
    },

    _playNextDialogue() {
      if (this.dialIdx < A.dialogues.length) {
        const p = A.dialogues[this.dialIdx];
        this.dialIdx += 1;
        const off = Math.min(2 + (this.dialIdx - 1), A.frames.length - 1);
        this.currentBg = img(A.frames[off]);
        audio.playVoice(p, () => this._playNextDialogue());
      } else {
        fader.fadeOut(() => sm.switch(next));
      }
    },

    handleEvent(e) {
      if (this.spelling && !this.locked) this.spelling.handleEvent(e);
    },
    update() {
      if (this.spelling) this.spelling.update();
    },
    draw(c) {
      if (this.frame === 0) blitFull(c, img(A.frames[0]));
      else if (this.frame === 1 && this.spelling) this.spelling.draw(c);
      else if (this.currentBg) blitFull(c, this.currentBg);
    },
    isHot(p) {
      return !!(this.spelling && !this.locked && this.spelling.hotspots().some(r => inRect(p, r)));
    },
    hotspots() {
      return (this.spelling && !this.locked) ? this.spelling.hotspots() : [];
    },
  };
}

/* ==========================================================================
   12. 合影（main.py:1128-1135）
   ========================================================================== */

const GroupPhotoScene = {
  onEnter() {
    audio.playVoice('5森林动物交互/森林旅行结束 母.mp3',
      () => fader.fadeOut(() => sm.switch('living_return')));
  },
  draw(c) { blitFull(c, img('21合影.PNG')); },
};

/* ==========================================================================
   13. 回到客厅（main.py:1138-1153）
   ========================================================================== */

const LivingReturnScene = {
  // 实测「单词测试」圆形按钮：外框 x[742..885] y[565..710]，圆心约 (813,637)
  TEST_RECT: { x: 738, y: 562, w: 150, h: 150 },
  onEnter() {
    audio.playBgm('主场景BGM.mp3');
    audio.playVoice('单词测试.mp3');
  },
  handleEvent(e) {
    if (e.type === 'down' && inRect(e.pos, this.TEST_RECT)) fader.fadeOut(() => sm.switch('test_screen'));
  },
  draw(c) { blitFull(c, img('23 客厅.png')); },
  isHot(p) { return inRect(p, this.TEST_RECT); },
  hotspots() { return [this.TEST_RECT]; },
};

/* ==========================================================================
   14. 难度选择（main.py:1156-1175）
   ========================================================================== */

const TestScreenScene = {
  EASY_RECT: { x: 225, y: 461, w: 199, h: 54 },
  MED_RECT: { x: 535, y: 461, w: 200, h: 54 },
  HARD_RECT: { x: 845, y: 461, w: 200, h: 54 },
  onEnter() { audio.stopBgm(); },
  handleEvent(e) {
    if (e.type !== 'down') return;
    if (inRect(e.pos, this.EASY_RECT)) fader.fadeOut(() => sm.switch('test_easy'));
    else if (inRect(e.pos, this.MED_RECT)) fader.fadeOut(() => sm.switch('test_medium'));
    else if (inRect(e.pos, this.HARD_RECT)) fader.fadeOut(() => sm.switch('test_hard'));
  },
  draw(c) { blitFull(c, img('24 测试.png')); },
  isHot(p) {
    return inRect(p, this.EASY_RECT) || inRect(p, this.MED_RECT) || inRect(p, this.HARD_RECT);
  },
  hotspots() { return [this.EASY_RECT, this.MED_RECT, this.HARD_RECT]; },
};

/* ==========================================================================
   15. 单词挑战（main.py:1216-1307）
   ========================================================================== */

function makeQuizScene(dk) {
  return {
    onEnter() {
      const info = DIFFICULTY[dk];
      this.levelCn = info[0];
      this.countdownMax = info[1];
      this.questions = shuffle(Object.keys(ALL_WORDS).map(cn => [cn, ALL_WORDS[cn]])).slice(0, 10);
      this.qIdx = 0;
      state.score = 0;
      state.diffKey = dk;
      this.timer = this.countdownMax;
      this.spelling = null;
      this._loadQuestion();
    },

    _loadQuestion() {
      if (this.qIdx >= 10) { fader.fadeOut(() => sm.switch('result_' + dk)); return; }
      const q = this.questions[this.qIdx];
      this.timer = this.countdownMax;
      this.spelling = new TestSpellingWidget(
        q[1], quizImage(this.levelCn, q[0]), quizAudio(q[1]),
        () => this._onCorrect(), 1, this.levelCn === '高级',
      );
    },

    _onCorrect() {
      state.score += 1;
      this.qIdx += 1;
      this._loadQuestion();
    },

    handleEvent(e) { if (this.spelling) this.spelling.handleEvent(e); },

    update() {
      if (this.spelling) this.spelling.update();
      if (this.timer > 0) {
        this.timer -= 1 / FPS;
        if (this.timer <= 0) { this.qIdx += 1; this._loadQuestion(); }
      }
    },

    draw(c) {
      if (!this.spelling) return;
      this.spelling.draw(c);

      const ratio = Math.max(0, this.timer / this.countdownMax);
      c.fillStyle = '#ffdc32';
      c.fillRect(0, 0, GW * ratio, 8);

      c.fillStyle = '#ffffff';
      c.textAlign = 'left';
      c.textBaseline = 'top';
      c.font = '500 26px system-ui, -apple-system, sans-serif';
      c.fillText('Q ' + (this.qIdx + 1) + '/10  Score: ' + state.score, 10, 14);
    },

    hotspots() { return this.spelling ? this.spelling.hotspots() : []; },
    isHot(p) { return !!(this.spelling && this.spelling.hotspots().some(r => inRect(p, r))); },
  };
}

/* ==========================================================================
   16. 结算（main.py:1310-1352）
   ========================================================================== */

function makeResultScene(dk) {
  return {
    onEnter() {
      const levelCn = DIFFICULTY[dk][0];
      const score = (state.diffKey === dk) ? state.score : 0;
      this.score = score;
      const star = score < 5 ? '一星' : (score < 10 ? '两星' : '三星');
      this.bgName = levelCn + star + '.png';
      this.is3star = (star === '三星');
    },
    handleEvent(e) {
      if (e.type !== 'down') return;
      if (inCircle(e.pos, 560, 613, 70)) fader.fadeOut(() => sm.switch('test_' + dk));
      else if (inCircle(e.pos, 720, 613, 70)) fader.fadeOut(() => sm.switch('living_return'));
    },
    draw(c) {
      blitFull(c, img(this.bgName));
      if (!this.is3star) {
        c.fillStyle = '#000000';
        c.textAlign = 'center';
        c.textBaseline = 'middle';
        c.font = '500 72px system-ui, -apple-system, sans-serif';
        c.fillText(String(this.score), 605, 403);
      }
    },
    isHot(p) { return inCircle(p, 560, 613, 70) || inCircle(p, 720, 613, 70); },
    hotspots() {
      const r = 70;
      return [{ x: 560 - r, y: 613 - r, w: 2 * r, h: 2 * r }, { x: 720 - r, y: 613 - r, w: 2 * r, h: 2 * r }];
    },
  };
}

/* ==========================================================================
   开发者菜单：场景分组清单（供左上角跳转用）
   ========================================================================== */

const SCENE_MENU = [
  { group: '序幕', items: [
    ['start', '开始页'],
    ['living1', '客厅 · 去旅行'],
    ['living2', '客厅 · 去超市'],
  ]},
  { group: '超市', items: [
    ['transit_to_market', '过场 · 去超市'],
    ['shopping_list', '采购清单'],
    ['supermarket', '超市采购'],
    ['transit_home', '过场 · 回家'],
  ]},
  { group: '森林', items: [
    ['animal_book_1', '动物手册 1'],
    ['animal_book_2', '动物手册 2'],
    ['animal_book_3', '动物手册 3'],
    ['depart', '出发'],
    ['transit_to_forest', '过场 · 去森林'],
    ['forest_fox', '森林 · 狐狸'],
    ['forest_horse', '森林 · 小马'],
    ['forest_pig', '森林 · 小猪'],
    ['forest_sheep', '森林 · 小羊'],
    ['forest_elephant', '森林 · 大象'],
    ['forest_tiger', '森林 · 老虎'],
    ['forest_parrot', '森林 · 鹦鹉'],
    ['forest_giraffe', '森林 · 长颈鹿'],
    ['forest_monkey', '森林 · 猴子'],
    ['group_photo', '合影'],
  ]},
  { group: '单词挑战', items: [
    ['living_return', '回到客厅'],
    ['test_screen', '难度选择'],
    ['test_easy', '挑战 · 初级'],
    ['test_medium', '挑战 · 中级'],
    ['test_hard', '挑战 · 高级'],
    ['result_easy', '结算 · 初级'],
    ['result_medium', '结算 · 中级'],
    ['result_hard', '结算 · 高级'],
  ]},
];

/* ==========================================================================
   注册全部场景 —— 对应 main.py:1355-1378
   ========================================================================== */

function registerAllScenes() {
  sm.register('start', StartScene);
  sm.register('living1', LivingRoom1Scene);
  sm.register('living2', LivingRoom2Scene);
  sm.register('transit_to_market', makeTransitScene('3从家去超市.PNG', 'shopping_list'));
  sm.register('shopping_list', ShoppingListScene);
  sm.register('supermarket', SupermarketScene);
  sm.register('transit_home', makeTransitScene('7从超市回家.PNG', 'animal_book_1', '主场景BGM.mp3'));
  sm.register('animal_book_1', makeAnimalBookScene(0));
  sm.register('animal_book_2', makeAnimalBookScene(1));
  sm.register('animal_book_3', makeAnimalBookScene(2));
  sm.register('depart', DepartScene);
  sm.register('transit_to_forest', makeTransitScene('8从家去森林.PNG', 'forest_fox', '5森林动物交互/森林场景BGM.mp3'));

  ANIMAL_ORDER.forEach(key => sm.register('forest_' + key, makeForestAnimalScene(key)));

  sm.register('group_photo', GroupPhotoScene);
  sm.register('living_return', LivingReturnScene);
  sm.register('test_screen', TestScreenScene);

  ['easy', 'medium', 'hard'].forEach(dk => {
    sm.register('test_' + dk, makeQuizScene(dk));
    sm.register('result_' + dk, makeResultScene(dk));
  });
}
