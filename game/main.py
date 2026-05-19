"""
Forest Adventure - Main Game
All scenes implemented as a state machine in a single file.
"""
import pygame
import sys
import os
import random
import math

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR  = os.path.join(BASE_DIR, "..", "场景图")
AUDIO_DIR  = os.path.join(BASE_DIR, "..", "音频")

def img(name):
    """Load an image from 场景图/ (supports subfolders via name like '初级/背包')."""
    path = os.path.join(ASSET_DIR, name)
    # try extensions (jpg first for compressed assets, then PNG fallback)
    for ext in ["", ".jpg", ".PNG", ".png"]:
        p = path + ext if not os.path.splitext(path)[1] else path
        if os.path.exists(p):
            return pygame.image.load(p)
    # fallback: just load
    return pygame.image.load(path)

def aud(rel):
    """Return absolute path for an audio file relative to 音频/."""
    return os.path.join(AUDIO_DIR, rel)

# ── Window ───────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1280, 720
FPS = 60

# ── Colors ───────────────────────────────────────────────────────────────────
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
GRAY   = (180, 180, 180)
RED    = (220, 60, 60)
GREEN  = (60, 200, 60)
BLUE   = (60, 120, 220)
YELLOW = (255, 220, 50)
ORANGE = (255, 160, 40)
LIGHT_BLUE = (173, 216, 230)

# ── Audio helper ─────────────────────────────────────────────────────────────
class AudioManager:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(8)
        self.bgm_channel   = pygame.mixer.Channel(0)
        self.voice_channel = pygame.mixer.Channel(1)
        self.sfx_channel   = pygame.mixer.Channel(2)
        self._bgm_path = None

    def play_bgm(self, path, loops=-1):
        if path == self._bgm_path and self.bgm_channel.get_busy():
            return
        self._bgm_path = path
        if not os.path.exists(path):
            return
        snd = pygame.mixer.Sound(path)
        self.bgm_channel.play(snd, loops=loops)

    def stop_bgm(self):
        self.bgm_channel.stop()
        self._bgm_path = None

    def play_voice(self, path, on_done=None):
        """Play voice; on_done callback called once finished (polled each frame)."""
        if not os.path.exists(path):
            if on_done:
                on_done()
            return
        snd = pygame.mixer.Sound(path)
        self.voice_channel.play(snd)
        self._voice_done_cb = on_done
        self._voice_snd = snd

    def stop_voice(self):
        self.voice_channel.stop()
        self._voice_done_cb = None

    def voice_busy(self):
        return self.voice_channel.get_busy()

    def update(self):
        """Call each frame to fire on_done callbacks."""
        if hasattr(self, '_voice_done_cb') and self._voice_done_cb:
            if not self.voice_channel.get_busy():
                cb = self._voice_done_cb
                self._voice_done_cb = None
                cb()

audio = AudioManager()

# ── Image cache ──────────────────────────────────────────────────────────────
_img_cache = {}
def load_img(name):
    if name in _img_cache:
        return _img_cache[name]
    surface = img(name)
    surface = pygame.transform.scale(surface, (SCREEN_W, SCREEN_H))
    _img_cache[name] = surface
    return surface

def load_img_raw(name):
    """Load without scaling."""
    if ("raw_" + name) in _img_cache:
        return _img_cache["raw_" + name]
    surface = img(name)
    _img_cache["raw_" + name] = surface
    return surface

# ── Fade helper ───────────────────────────────────────────────────────────────
class Fader:
    def __init__(self):
        self.alpha   = 0
        self.active  = False
        self.dir     = 1   # 1=fade-out (→black), -1=fade-in (black→)
        self.speed   = 8   # alpha change per frame
        self.on_done = None

    def fade_out(self, on_done=None, speed=8):
        self.alpha   = 0
        self.dir     = 1
        self.speed   = speed
        self.active  = True
        self.on_done = on_done

    def fade_in(self, on_done=None, speed=8):
        self.alpha   = 255
        self.dir     = -1
        self.speed   = speed
        self.active  = True
        self.on_done = on_done

    def update(self):
        if not self.active:
            return
        self.alpha += self.dir * self.speed
        if self.dir == 1 and self.alpha >= 255:
            self.alpha  = 255
            self.active = False
            if self.on_done:
                self.on_done()
        elif self.dir == -1 and self.alpha <= 0:
            self.alpha  = 0
            self.active = False
            if self.on_done:
                self.on_done()

    def draw(self, screen):
        if self.alpha > 0:
            s = pygame.Surface((SCREEN_W, SCREEN_H))
            s.fill(BLACK)
            s.set_alpha(self.alpha)
            screen.blit(s, (0, 0))

fader = Fader()

# ── Spelling Widget ───────────────────────────────────────────────────────────
class SpellingWidget:
    """
    Reusable spelling widget drawn on top of the current background.
    word        : target word (e.g. 'backpack')
    bg_image    : full-screen background surface
    audio_path  : word pronunciation mp3
    hint_count  : number of pre-filled letters (for forest scenes, 0 for supermarket)
    on_success  : callback when word fully correct
    show_speaker: show speaker button
    """
    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    BTN_W, BTN_H = 42, 42
    SLOT_W, SLOT_H = 52, 58
    FONT_SIZE_LETTER = 28
    FONT_SIZE_SLOT   = 32

    def __init__(self, word, bg_image, audio_path, on_success,
                 hint_count=0, show_helper=True, overlay_img=None):
        self.word        = word.upper()
        self.bg_image    = bg_image          # full-screen surface to draw behind
        self.audio_path  = audio_path
        self.on_success  = on_success
        self.hint_count  = hint_count
        self.show_helper = show_helper
        self.overlay_img = overlay_img       # optional overlay (拼写界面图)

        self.font_letter = pygame.font.Font(None, self.FONT_SIZE_LETTER + 8)
        self.font_slot   = pygame.font.Font(None, self.FONT_SIZE_SLOT   + 8)
        self.font_btn    = pygame.font.Font(None, 28)

        # slots: list of char or None
        self.slots = [None] * len(self.word)
        # pre-fill hints (first N letters shown)
        for i in range(hint_count):
            self.slots[i] = self.word[i]

        self._build_layout()
        self.shake_slots  = {}   # slot_idx -> shake_frames
        self.helper_flash = 0

    # Per-word layout config:
    # speaker(l,r,t,b), slot_bottom, kb(l,r,t,b), confirm(l,r,t,b), helper(l,r,t,b)
    _LAYOUT = {
        # ── 超市物品 ──
        "bottle":   ((430,464,450,488), 485, (450,839,558,672), (497,637,685,719), (654,804,685,719)),
        "backpack": ((470,510,450,490), 485, (451,838,558,671), (497,637,685,719), (654,804,685,719)),
        "compass":  ((385,425,486,515), 485, (450,839,560,675), (497,637,685,719), (654,804,685,719)),
        "bandage":  ((427,453,487,520), 485, (450,839,558,672), (497,637,685,719), (654,804,685,719)),
        "umbrella": ((385,410,516,562), 485, (442,829,556,669), (497,637,685,719), (654,804,685,719)),
        "lollipop": ((560,735,434,480), 485, (442,829,556,669), (497,637,685,719), (654,804,685,719)),
        "cake":     ((560,735,481,520), 485, (442,829,556,669), (497,637,685,719), (654,804,685,719)),
        "apple":    ((565,663,524,565), 485, (447,833,556,668), (497,637,685,719), (654,804,685,719)),
        # ── 森林动物 ──
        "fox":      ((708,754,340,388), 528, (448,824,550,658), (494,627,669,710), (645,790,668,711)),
        "horse":    ((719,766,345,394), 536, (455,836,559,668), (502,636,679,719), (656,801,679,719)),
        "pig":      ((708,755,345,393), 536, (443,825,559,669), (490,625,680,719), (644,790,680,719)),
        "sheep":    ((693,740,344,393), 535, (428,810,559,670), (475,610,680,719), (629,775,680,719)),
        "elephant": ((753,799,345,393), 536, (466,847,559,668), (512,646,681,719), (666,812,681,719)),
        "tiger":    ((712,759,345,395), 540, (443,832,562,674), (491,628,685,719), (648,796,685,719)),
        "parrot":   ((710,758,346,395), 539, (444,829,562,672), (491,627,683,719), (647,794,683,719)),
        "giraffe":  ((725,769,299,343), 532, (461,803,562,663), (501,624,680,717), (639,774,680,717)),
        "monkey":   ((714,760,336,383), 534, (451,813,557,660), (494,624,679,716), (640,782,679,716)),
    }

    def _build_layout(self):
        n   = len(self.word)
        _w  = self.word.lower()
        cfg = self._LAYOUT.get(_w)

        if cfg:
            spk, slot_bot, kb, conf, hlp = cfg
            # slots: bottom edge at slot_bot, centered
            total_w = n * (self.SLOT_W + 6) - 6
            sx = (SCREEN_W - total_w) // 2
            sy = slot_bot - self.SLOT_H
            # speaker
            sl, sr, st, sb = spk
            self.speaker_rect = pygame.Rect(sl, st, sr - sl, sb - st)
            # confirm & helper
            cl, cr, ct, cb = conf
            self.confirm_rect = pygame.Rect(cl, ct, cr - cl, cb - ct)
            hl, hr, ht, hb = hlp
            self.helper_rect  = pygame.Rect(hl, ht, hr - hl, hb - ht)
            # keyboard
            KB_X1, KB_X2, KB_Y1, KB_Y2 = kb
        else:
            # fallback defaults
            sy = 485 - self.SLOT_H
            sx = (SCREEN_W - (n * (self.SLOT_W + 6) - 6)) // 2
            self.speaker_rect = pygame.Rect(737, 340, 50, 50)
            self.confirm_rect = pygame.Rect(497, 685, 140, 34)
            self.helper_rect  = pygame.Rect(654, 685, 150, 34)
            KB_X1, KB_X2, KB_Y1, KB_Y2 = 450, 839, 561, 675

        self.slot_rects = [
            pygame.Rect(sx + i * (self.SLOT_W + 6), sy, self.SLOT_W, self.SLOT_H)
            for i in range(n)
        ]

        # keyboard: 3 rows, invisible clickable areas
        rows   = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        KB_W   = KB_X2 - KB_X1
        KB_H   = KB_Y2 - KB_Y1
        CELL_W = 33
        CELL_H = (KB_H - 2 * 6) // 3
        GAP    = 6
        self.key_rects = {}
        for row_i, row in enumerate(rows):
            row_w = len(row) * CELL_W + (len(row) - 1) * GAP
            kx = KB_X1 + (KB_W - row_w) // 2
            ky = KB_Y1 + row_i * (CELL_H + GAP)
            for col_i, ch in enumerate(row):
                self.key_rects[ch] = pygame.Rect(
                    kx + col_i * (CELL_W + GAP), ky, CELL_W, CELL_H)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # speaker
            if self.speaker_rect.collidepoint(pos):
                audio.play_voice(self.audio_path)
                return
            # confirm
            if self.confirm_rect.collidepoint(pos):
                self._check()
                return
            # helper
            if self.show_helper and self.helper_rect.collidepoint(pos):
                self._give_hint()
                return
            # click on slot → remove letter
            for i, r in enumerate(self.slot_rects):
                if r.collidepoint(pos) and self.slots[i] and i >= self.hint_count:
                    self.slots[i] = None
                    return
            # keyboard
            for ch, r in self.key_rects.items():
                if r.collidepoint(pos):
                    self._type_letter(ch)
                    return

    def _first_empty(self):
        for i in range(len(self.slots)):
            if self.slots[i] is None:
                return i
        return None

    def _type_letter(self, ch):
        idx = self._first_empty()
        if idx is not None:
            self.slots[idx] = ch

    def _check(self):
        if None in self.slots:
            return  # not fully filled
        wrong = []
        for i, (s, w) in enumerate(zip(self.slots, self.word)):
            if s != w:
                wrong.append(i)
        if not wrong:
            self.on_success()
        else:
            # shake wrong, keep correct, play retry
            for i in wrong:
                self.shake_slots[i] = 20
                if i >= self.hint_count:
                    self.slots[i] = None
            retry_path = random.choice([
                aud("3超市/再试试 父.mp3"),
                aud("3超市/再试试 母.mp3"),
            ])
            audio.play_voice(retry_path)

    def _give_hint(self):
        """Fill one random empty slot with correct letter."""
        empty = [i for i in range(len(self.slots)) if self.slots[i] is None]
        if empty:
            i = random.choice(empty)
            self.slots[i] = self.word[i]
            self.helper_flash = 30

    def update(self):
        for k in list(self.shake_slots):
            self.shake_slots[k] -= 1
            if self.shake_slots[k] <= 0:
                del self.shake_slots[k]
        if self.helper_flash > 0:
            self.helper_flash -= 1

    def draw(self, screen):
        # background
        screen.blit(self.bg_image, (0, 0))
        # optional overlay (超市拼写界面图)
        if self.overlay_img:
            screen.blit(self.overlay_img, (0, 0))

        # slots (no Spell: prompt)
        for i, r in enumerate(self.slot_rects):
            ox = 0
            if i in self.shake_slots:
                ox = 5 * math.sin(self.shake_slots[i] * 1.2)
            shake_r = r.move(ox, 0)
            pygame.draw.rect(screen, WHITE, shake_r, border_radius=6)
            pygame.draw.rect(screen, BLUE, shake_r, 2, border_radius=6)
            if self.slots[i]:
                txt = self.font_slot.render(self.slots[i], True, BLACK)
                screen.blit(txt, (shake_r.x + shake_r.w // 2 - txt.get_width() // 2,
                                  shake_r.y + shake_r.h // 2 - txt.get_height() // 2))

        # keyboard: invisible clickable areas (no drawing)

        # speaker button: invisible clickable area (no drawing)
        pass

        # confirm button: invisible clickable area (no drawing)
        # helper button: invisible clickable area (no drawing)

# ── Test Spelling Widget (for 24-测试 quiz scenes) ────────────────────────────
class TestSpellingWidget:
    """
    Spelling widget used in test quiz scenes (24 测试).
    Coordinates match the original design (1280×720 screen, no scaling needed):
      - Speaker hot-zone : (588,681,257,349) → Rect(588,257,93,92)
      - Keyboard area    : left=289,right=991,top=395,bot=624, cell=66px
      - Confirm button   : green 66×66 after Z (9th cell of row 3)
      - Answer slots     : x∈[687,1028], top=257, bot=349
    """
    CELL = 66
    KB_LEFT  = 289
    KB_RIGHT = 992
    KB_TOP   = 395
    KB_BOT   = 624

    SPK_RECT  = pygame.Rect(588, 257, 93, 92)

    SLOT_LEFT  = 687
    SLOT_RIGHT = 1028
    SLOT_TOP   = 257
    SLOT_BOT   = 349

    def __init__(self, word, bg_image, audio_path, on_success, hint_count=0):
        self.word        = word.upper()
        self.bg_image    = bg_image
        self.audio_path  = audio_path
        self.on_success  = on_success
        self.hint_count  = hint_count

        self.slots       = [None] * len(self.word)
        for i in range(hint_count):
            self.slots[i] = self.word[i]

        self.shake_slots = {}
        self._build_layout()

    def _build_layout(self):
        n = len(self.word)

        # ── answer slots ──────────────────────────────────────────────────────
        slot_area_w = self.SLOT_RIGHT - self.SLOT_LEFT   # 341 px
        slot_area_h = self.SLOT_BOT   - self.SLOT_TOP    # 92 px
        max_sw = slot_area_w // n
        slot_h = min(max_sw, slot_area_h)
        slot_w = min(max_sw, slot_h)
        font_sz = max(20, int(slot_h * 0.6))
        self.font_slot = pygame.font.Font(None, font_sz + 8)
        gap = 4
        total_sw = n * slot_w + (n - 1) * gap
        sx = self.SLOT_LEFT + (slot_area_w - total_sw) // 2
        sy = self.SLOT_TOP  + (slot_area_h - slot_h)  // 2
        self.slot_rects = [
            pygame.Rect(sx + i * (slot_w + gap), sy, slot_w, slot_h)
            for i in range(n)
        ]

        # speaker rect
        self.spk_rect = self.SPK_RECT

        # ── keyboard ──────────────────────────────────────────────────────────
        rows = [
            list("ABCDEFGHI"),
            list("JKLMNOPQR"),
            list("STUVWXYZ"),
        ]
        C   = self.CELL
        GAP = 14
        kb_h = self.KB_BOT - self.KB_TOP
        row_gap = (kb_h - 3 * C) // 2
        kx_start = self.KB_LEFT
        self.key_rects = {}
        for row_i, row in enumerate(rows):
            ky = self.KB_TOP + row_i * (C + row_gap)
            for col_i, ch in enumerate(row):
                self.key_rects[ch] = pygame.Rect(
                    kx_start + col_i * (C + GAP), ky, C, C)

        ky3 = self.KB_TOP + 2 * (C + row_gap)
        self.confirm_rect = pygame.Rect(kx_start + 8 * (C + GAP), ky3, C, C)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.spk_rect.collidepoint(pos):
                audio.play_voice(self.audio_path)
                return
            if self.confirm_rect.collidepoint(pos):
                self._check()
                return
            for i, r in enumerate(self.slot_rects):
                if r.collidepoint(pos) and self.slots[i] and i >= self.hint_count:
                    self.slots[i] = None
                    return
            for ch, r in self.key_rects.items():
                if r.collidepoint(pos):
                    self._type_letter(ch)
                    return

    def _first_empty(self):
        for i in range(len(self.slots)):
            if self.slots[i] is None:
                return i
        return None

    def _type_letter(self, ch):
        idx = self._first_empty()
        if idx is not None:
            self.slots[idx] = ch

    def _check(self):
        if None in self.slots:
            return
        wrong = []
        for i, (s, w) in enumerate(zip(self.slots, self.word)):
            if s != w:
                wrong.append(i)
        if not wrong:
            self.on_success()
        else:
            for i in wrong:
                self.shake_slots[i] = 20
                if i >= self.hint_count:
                    self.slots[i] = None
            retry_path = random.choice([
                aud("3超市/再试试 父.mp3"),
                aud("3超市/再试试 母.mp3"),
            ])
            audio.play_voice(retry_path)

    def update(self):
        for k in list(self.shake_slots):
            self.shake_slots[k] -= 1
            if self.shake_slots[k] <= 0:
                del self.shake_slots[k]

    def draw(self, screen):
        screen.blit(self.bg_image, (0, 0))

        # answer slots
        for i, r in enumerate(self.slot_rects):
            ox = 0
            if i in self.shake_slots:
                ox = int(5 * math.sin(self.shake_slots[i] * 1.2))
            sr = r.move(ox, 0)
            pygame.draw.rect(screen, WHITE, sr, border_radius=6)
            pygame.draw.rect(screen, BLUE,  sr, 2, border_radius=6)
            if self.slots[i]:
                txt = self.font_slot.render(self.slots[i], True, BLACK)
                screen.blit(txt, (sr.x + sr.w // 2 - txt.get_width() // 2,
                                  sr.y + sr.h // 2 - txt.get_height() // 2))

        # keyboard: invisible hot-zones, no text/border drawn
        # confirm button: solid green square
        pygame.draw.rect(screen, GREEN, self.confirm_rect, border_radius=4)

        # speaker: invisible hot-zone (no drawing)


# ── Scene base ────────────────────────────────────────────────────────────────
class Scene:
    def on_enter(self): pass
    def handle_event(self, event): pass
    def update(self): pass
    def draw(self, screen): pass

# ── Scene manager ─────────────────────────────────────────────────────────────
class SceneManager:
    def __init__(self):
        self.scenes  = {}
        self.current = None

    def register(self, name, scene):
        self.scenes[name] = scene

    def switch(self, name):
        self.current = self.scenes[name]
        self.current.on_enter()
        fader.fade_in()   # always fade in after switching

sm = SceneManager()

# ── Global fonts (initialized after pygame.init() in main()) ──────────────────
FONT_SM   = None   # 20px
FONT_MD   = None   # 22px
FONT_LG   = None   # 26px
FONT_XL   = None   # 48px

def init_fonts():
    global FONT_SM, FONT_MD, FONT_LG, FONT_XL
    FONT_SM = pygame.font.Font(None, 24)
    FONT_MD = pygame.font.Font(None, 28)
    FONT_LG = pygame.font.Font(None, 34)
    FONT_XL = pygame.font.Font(None, 56)

# ── 0. Start Screen ───────────────────────────────────────────────────────────
class StartScene(Scene):
    # Click area for "进入" button (adjust after testing)
    BTN_RECT = pygame.Rect(520, 580, 240, 80)

    def on_enter(self):
        self.bg = load_img("1开始页.PNG")
        audio.stop_bgm()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.BTN_RECT.collidepoint(event.pos):
                fader.fade_out(on_done=lambda: sm.switch("living1"))

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

# ── 1. Living Room 1 ──────────────────────────────────────────────────────────
class LivingRoom1Scene(Scene):
    FOREST_CENTER = (640, 630)
    FOREST_RADIUS = 70

    def on_enter(self):
        self.bg = load_img("2.1客厅.png")
        audio.play_bgm(aud("主场景BGM.mp3"))
        audio.play_voice(aud("1开场/开场 去旅行 母.mp3"))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            cx, cy = self.FOREST_CENTER
            if (mx - cx) ** 2 + (my - cy) ** 2 <= self.FOREST_RADIUS ** 2:
                fader.fade_out(on_done=lambda: sm.switch("living2"))

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

# ── 2. Living Room 2 ──────────────────────────────────────────────────────────
class LivingRoom2Scene(Scene):
    def on_enter(self):
        self.bg     = load_img("2.2客厅.png")
        self.played = False
        audio.play_voice(aud("1开场/开场2 去超市 母.mp3"), on_done=self._go_next)

    def _go_next(self):
        fader.fade_out(on_done=lambda: sm.switch("transit_to_market"))

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

# ── 3. Transit home→market ───────────────────────────────────────────────────
class TransitScene(Scene):
    """Generic 3-second auto-advance scene."""
    def __init__(self, img_name, next_scene, bgm_path=None, bgm_loops=-1):
        self.img_name   = img_name
        self.next_scene = next_scene
        self.bgm_path   = bgm_path
        self.bgm_loops  = bgm_loops
        self.timer      = 0

    def on_enter(self):
        self.bg    = load_img(self.img_name)
        self.timer = FPS * 3  # 3 seconds
        if self.bgm_path:
            audio.play_bgm(self.bgm_path, loops=self.bgm_loops)

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.timer = 999999
            fader.fade_out(on_done=lambda: sm.switch(self.next_scene))

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

# ── 4. Shopping List ──────────────────────────────────────────────────────────
# Item map: img_index -> (audio_prefix, word, click_rect_on_image)
SHOPPING_ITEMS = [
    # (scene indices, audio_group_prefix, english_word, click_rect)
    # rect = pygame.Rect(x, y, w, h), centered on given point with side=80
    ([1, 2, 3],     "1",  "backpack",  pygame.Rect(410, 170, 80, 80)),   # center (450,210)
    ([4, 5],        "2",  "bottle",    pygame.Rect(410, 285, 80, 80)),   # center (450,325)
    ([6, 7, 8],     "3",  "compass",   pygame.Rect(410, 395, 80, 80)),   # center (450,435)
    ([9, 10, 11],   "4",  "apple",     pygame.Rect(410, 505, 80, 80)),   # center (450,545)
    ([12, 13, 14],  "5",  "bandage",   pygame.Rect(660, 170, 80, 80)),   # center (700,210)
    ([15, 16, 17],  "6",  "umbrella",  pygame.Rect(660, 285, 80, 80)),   # center (700,325)
    ([18, 19],      "7",  "cake",      pygame.Rect(660, 395, 80, 80)),   # center (700,435)
    ([20, 21, 22],  "8",  "lollipop",  pygame.Rect(660, 505, 80, 80)),   # center (700,545)
]

# Audio file names for父母介绍 (some have spaces, some don't)
def shopping_audio(group, sub):
    """Return path like '2.2 水壶' or '7.2蛋糕'."""
    name_map = {
        "1": "背包", "2": "水壶", "3": "指南针",
        "4": "苹果", "5": "创可贴", "6": "雨伞",
        "7": "蛋糕", "8": "棒棒糖",
    }
    label = name_map[group]
    # try with space then without
    for sep in [" ", ""]:
        p = aud(f"2采购清单/采购清单-父母介绍/{group}.{sub}{sep}{label}.mp3")
        if os.path.exists(p):
            return p
    return aud(f"2采购清单/采购清单-父母介绍/{group}.{sub} {label}.mp3")

def word_audio(word):
    return aud(f"2采购清单/采购清单-单词发音/{word}.mp3")

class ShoppingListScene(Scene):
    # All 8 item icon areas visible on every slide: (word, rect)
    ICON_RECTS = [
        ("backpack",  pygame.Rect(410, 170, 80, 80)),
        ("bandage",   pygame.Rect(660, 170, 80, 80)),
        ("bottle",    pygame.Rect(410, 285, 80, 80)),
        ("umbrella",  pygame.Rect(660, 285, 80, 80)),
        ("compass",   pygame.Rect(410, 395, 80, 80)),
        ("cake",      pygame.Rect(660, 395, 80, 80)),
        ("apple",     pygame.Rect(410, 505, 80, 80)),
        ("lollipop",  pygame.Rect(660, 505, 80, 80)),
    ]

    def __init__(self):
        # Flatten all slides: (img_name, group, sub)
        self.slides = []
        for item in SHOPPING_ITEMS:
            indices, group, word, _crect = item
            for j, idx in enumerate(indices):
                self.slides.append((f"4.{idx}.png", group, str(j + 1)))

        self.current = 0
        self.bg      = None

    def on_enter(self):
        self.current = 0
        self._load_slide()

    def _load_slide(self):
        img_name, group, sub = self.slides[self.current]
        self.bg = load_img(img_name)
        audio.play_voice(shopping_audio(group, sub))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # Check if any icon was clicked → play its pronunciation
            for word, rect in self.ICON_RECTS:
                if rect.collidepoint(pos):
                    audio.play_voice(word_audio(word))
                    return
            # Clicked outside all icons → advance to next slide
            self._advance()

    def _advance(self):
        if self.current < len(self.slides) - 1:
            self.current += 1
            self._load_slide()
        else:
            fader.fade_out(on_done=lambda: sm.switch("supermarket"))

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

# ── 5. Supermarket ────────────────────────────────────────────────────────────
ITEM_ENGLISH = {
    # (left, right, top, bottom) → Rect(left, top, right-left, bottom-top)
    "水壶":   ("bottle",   pygame.Rect(430, 450, 34,  38)),
    "背包":   ("backpack",  pygame.Rect(470, 450, 40,  40)),
    "指南针": ("compass",   pygame.Rect(385, 486, 40,  29)),
    "创可贴": ("bandage",   pygame.Rect(427, 487, 26,  33)),
    "雨伞":   ("umbrella",  pygame.Rect(385, 516, 25,  46)),
    "棒棒糖": ("lollipop",  pygame.Rect(560, 434, 175, 46)),
    "蛋糕":   ("cake",      pygame.Rect(560, 481, 175, 39)),
    "苹果":   ("apple",     pygame.Rect(565, 524, 98,  41)),
}
DISTRACT_RECTS = [
    pygame.Rect(383, 450, 42,  35),   # palette  画板
    pygame.Rect(455, 491, 40,  29),   # wallet   钱包
    pygame.Rect(420, 521, 95,  44),   # book     书
    pygame.Rect(560, 403, 175, 29),   # cookie   饼干
    pygame.Rect(668, 521, 67,  44),   # wine     酒
]
SPELL_IMAGES = {
    "backpack":  "6背包拼写.PNG",
    "bottle":    "6水壶拼写.PNG",
    "compass":   "6指南针拼写.PNG",
    "bandage":   "6创可贴拼写.PNG",
    "umbrella":  "6雨伞拼写.PNG",
    "lollipop":  "6棒棒糖拼写.PNG",
    "cake":      "6蛋糕拼写.PNG",
    "apple":     "6苹果拼写.PNG",
}

class SupermarketScene(Scene):
    def on_enter(self):
        self.bg            = load_img("5超市.PNG")
        self.hint_bg       = load_img("5.1.png")
        self.done_set      = set()
        self.spelling      = None
        self.miss_count    = 0       # misclicks not in any rect
        self.show_hint     = False   # 5.1 hint overlay
        self.hint_timer    = 0
        self.dwell_timer   = 0
        self.done_transit  = False

    def _open_spelling(self, name_cn, word):
        if word in self.done_set:
            return
        overlay = load_img(SPELL_IMAGES[word])
        self.spelling = SpellingWidget(
            word        = word,
            bg_image    = self.bg,
            audio_path  = word_audio(word),
            on_success  = lambda: self._on_spell_done(word),
            overlay_img = overlay,
        )
        self.show_hint = False

    def _on_spell_done(self, word):
        self.done_set.add(word)
        self.spelling = None
        # check completion
        if len(self.done_set) >= 8:
            self._end(full=True)
        elif len(self.done_set) >= 4:
            self.dwell_timer += 1   # tracked in update

    def _end(self, full):
        self.done_transit = True
        if full:
            p = aud("3超市/采购完成 母.mp3")
        else:
            p = aud("3超市/采购完成 父.mp3")
        audio.stop_bgm()
        audio.play_voice(p, on_done=lambda: fader.fade_out(on_done=lambda: sm.switch("transit_home")))

    def handle_event(self, event):
        if self.done_transit:
            return
        if self.spelling:
            self.spelling.handle_event(event)
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            self.show_hint = False
            hit = False
            # check target items
            for name_cn, (word, rect) in ITEM_ENGLISH.items():
                if rect.collidepoint(pos):
                    hit = True
                    if word not in self.done_set:
                        self._open_spelling(name_cn, word)
                    break
            if not hit:
                # check distractor
                for dr in DISTRACT_RECTS:
                    if dr.collidepoint(pos):
                        hit = True
                        p = random.choice([
                            aud("3超市/不需要 父.mp3"),
                            aud("3超市/不需要 母.mp3"),
                        ])
                        audio.play_voice(p)
                        break
            if not hit:
                self.miss_count += 1
                if self.miss_count >= 5:
                    self.miss_count = 0
                    self.show_hint  = True
                    self.hint_timer = FPS * 2

    def update(self):
        if self.spelling:
            self.spelling.update()
        if self.show_hint:
            self.hint_timer -= 1
            if self.hint_timer <= 0:
                self.show_hint = False
        if not self.done_transit and len(self.done_set) >= 4:
            self.dwell_timer += 1
            if self.dwell_timer > FPS * 120:   # 2 min dwell
                self._end(full=False)

    def draw(self, screen):
        if self.spelling:
            self.spelling.draw(screen)
        else:
            screen.blit(self.bg, (0, 0))
            if self.show_hint:
                screen.blit(self.hint_bg, (0, 0))
            # mark done items
            for name_cn, (word, rect) in ITEM_ENGLISH.items():
                if word in self.done_set:
                    s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                    s.fill((60, 200, 60, 100))
                    screen.blit(s, (rect.x, rect.y))
                    ok = FONT_SM.render("OK", True, GREEN)
                    screen.blit(ok, (rect.x + rect.w // 2 - ok.get_width() // 2,
                                     rect.y + rect.h // 2 - ok.get_height() // 2))

# ── 7. Transit back home ──────────────────────────────────────────────────────
class TransitHomeScene(Scene):
    def on_enter(self):
        self.bg    = load_img("7从超市回家.PNG")
        self.timer = FPS * 3
        audio.play_bgm(aud("主场景BGM.mp3"))

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.timer = 999999
            fader.fade_out(on_done=lambda: sm.switch("animal_book_1"))

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

# ── 8. Animal Handbook ────────────────────────────────────────────────────────
BOOK_DATA = [
    ("9动物手册.PNG",  [
        ("fox",      "fox.mp3",      "手册狐狸 母.mp3",   pygame.Rect(120, 200, 180, 180)),
        ("horse",    "horse.mp3",    "手册马 父.mp3",     pygame.Rect(540, 200, 180, 180)),
        ("pig",      "pig.mp3",      "手册小猪 母.mp3",   pygame.Rect(960, 200, 180, 180)),
    ], "animal_book_2"),
    ("10动物手册.PNG", [
        ("tiger",    "tiger.mp3",    "手册老虎 父.mp3",   pygame.Rect(120, 200, 180, 180)),
        ("sheep",    "sheep.mp3",    "手册小羊 母.mp3",   pygame.Rect(540, 200, 180, 180)),
        ("elephant", "elephant.mp3", "手册大象 父.mp3",   pygame.Rect(960, 200, 180, 180)),
    ], "animal_book_3"),
    ("11动物手册.PNG", [
        ("parrot",   "parrot.mp3",   "手册鹦鹉 母.mp3",   pygame.Rect(120, 200, 180, 180)),
        ("giraffe",  "giraffe.mp3",  "手册长颈鹿 母.mp3", pygame.Rect(540, 200, 180, 180)),
        ("monkey",   "monkey.mp3",   "手册猴子 母.mp3",   pygame.Rect(960, 200, 180, 180)),
    ], "depart"),
]

class AnimalBookScene(Scene):
    def __init__(self, book_idx):
        self.book_idx = book_idx

    def on_enter(self):
        img_name, animals, self.next_scene = BOOK_DATA[self.book_idx]
        self.bg      = load_img(img_name)
        self.animals = animals   # list of (name, word_mp3, intro_mp3, rect)
        # build audio sequence: word + intro for each animal
        self.seq     = []
        for name, word_mp3, intro_mp3, rect in animals:
            self.seq.append(aud(f"4森林动物手册/{word_mp3}"))
            self.seq.append(aud(f"4森林动物手册/{intro_mp3}"))
        self.seq_idx   = 0
        self.listening = True   # playing auto sequence
        self._play_next_seq()

    def _play_next_seq(self):
        if self.seq_idx < len(self.seq):
            path = self.seq[self.seq_idx]
            self.seq_idx += 1
            audio.play_voice(path, on_done=self._play_next_seq)
        else:
            self.listening = False  # sequence done, allow interaction

    def handle_event(self, event):
        if self.listening:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            clicked_animal = False
            for name, word_mp3, intro_mp3, rect in self.animals:
                if rect.collidepoint(pos):
                    audio.play_voice(aud(f"4森林动物手册/{word_mp3}"))
                    clicked_animal = True
                    break
            if not clicked_animal:
                fader.fade_out(on_done=lambda: sm.switch(self.next_scene))

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

# ── 9. Depart scene (7.2.png) ─────────────────────────────────────────────────
class DepartScene(Scene):
    def on_enter(self):
        self.bg = load_img("7.2.png")
        audio.stop_bgm()
        audio.play_voice(aud("4森林动物手册/出发 母.mp3"),
                          on_done=lambda: fader.fade_out(on_done=lambda: sm.switch("transit_to_forest")))

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

# ── 10. Transit home→forest ───────────────────────────────────────────────────
class TransitToForestScene(Scene):
    def on_enter(self):
        self.bg    = load_img("8从家去森林.PNG")
        self.timer = FPS * 3
        audio.play_bgm(aud("5森林动物交互/森林场景BGM.mp3"))

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.timer = 999999
            fader.fade_out(on_done=lambda: sm.switch("forest_fox"))

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

# ── 11. Forest Animal Scenes ──────────────────────────────────────────────────
FOREST_ANIMALS = [
    # (key, name_cn, prefix, word, frame_images, dialogue_audios)
    ("fox",      "狐狸",   "12",
     "fox",
     ["12狐狸1.PNG", "12狐狸2.PNG", "12狐狸3.PNG"],
     ["5森林动物交互/狐狸_我只是好奇里面有什么.mp3",
      "5森林动物交互/狐狸_这个包真酷还给你.mp3"]),

    ("horse",    "小马",   "13",
     "horse",
     ["13小马1.PNG", "13小马2.PNG", "13小马3.PNG"],
     ["5森林动物交互/小马_谢谢你的苹果.mp3",
      "5森林动物交互/小马_真甜啊.mp3"]),

    ("pig",      "小猪",   "14",
     "pig",
     ["14小猪1.PNG", "14小猪2.PNG", "14小猪3.PNG"],
     ["5森林动物交互/小猪_蛋糕.mp3",
      "5森林动物交互/小猪_从现在起.mp3"]),

    ("sheep",    "小羊",   "15",
     "sheep",
     ["15小羊1.PNG", "15小羊2.PNG", "15小羊3.PNG"],
     ["5森林动物交互/小羊_水真好喝.mp3",
      "5森林动物交互/小羊_你是我.mp3"]),

    ("elephant", "大象",   "16",
     "elephant",
     ["16大象1.PNG", "16大象2.PNG", "16大象3.PNG"],
     ["5森林动物交互/大象_对不起.mp3",
      "5森林动物交互/大象_幸好.mp3"]),

    ("tiger",    "老虎",   "17",
     "tiger",
     ["17老虎1.PNG", "17老虎2.PNG", "17老虎3.PNG"],
     ["5森林动物交互/老虎_谢谢.mp3",
      "5森林动物交互/老虎_有我在.mp3"]),

    ("parrot",   "鹦鹉",   "18",
     "parrot",
     ["18鹦鹉1.PNG", "18鹦鹉2.PNG", "18鹦鹉3.PNG"],
     ["5森林动物交互/鹦鹉_亮晶晶.mp3",
      "5森林动物交互/鹦鹉_好玩.mp3",
      "5森林动物交互/鹦鹉_还给你啦.mp3",
      "5森林动物交互/鹦鹉_哎呀.mp3"]),

    ("giraffe",  "长颈鹿", "19",
     "giraffe",
     ["19长颈鹿1.PNG", "19长颈鹿2.PNG", "19长颈鹿3.PNG"],
     ["5森林动物交互/长颈鹿_这点高度.mp3",
      "5森林动物交互/长颈鹿_别再.mp3"]),

    ("monkey",   "猴子",   "20",
     "monkey",
     ["20猴子1.PNG", "20猴子2.PNG", "20猴子3.PNG"],
     ["5森林动物交互/猴子_你真厉害.mp3",
      "5森林动物交互/猴子_欢迎来森林玩.mp3"]),
]

ANIMAL_ORDER = [a[0] for a in FOREST_ANIMALS]
ANIMAL_MAP   = {a[0]: a for a in FOREST_ANIMALS}

def next_animal_scene(key):
    idx = ANIMAL_ORDER.index(key)
    if idx + 1 < len(ANIMAL_ORDER):
        return "forest_" + ANIMAL_ORDER[idx + 1]
    return "group_photo"

class ForestAnimalScene(Scene):
    """
    Frame flow:
      frame1: play 交互XX 父/母 → auto-fade → frame2
      frame2: spelling widget (word pronunciation + 26-key) → correct → frame3
      frame3+: play dialogue audios in sequence → fade → next animal
    """
    def __init__(self, key):
        self.key  = key
        _, self.name_cn, _, self.word, self.frames, self.dialogues = ANIMAL_MAP[key]
        self.next = next_animal_scene(key)

    def on_enter(self):
        self.frame     = 0   # 0=frame1, 1=frame2, 2+=frame3+
        self.spelling  = None
        self.dial_idx  = 0
        self.locked    = False
        self._go_frame1()

    def _go_frame1(self):
        self.frame  = 0
        self.locked = True
        self.bg1    = load_img(self.frames[0])
        interact_p  = random.choice([
            aud(f"5森林动物交互/交互{self.name_cn} 父.mp3"),
            aud(f"5森林动物交互/交互{self.name_cn} 母.mp3"),
        ])
        audio.play_voice(interact_p,
                          on_done=lambda: fader.fade_out(on_done=self._go_frame2))

    def _go_frame2(self):
        self.frame  = 1
        self.locked = False
        bg2 = load_img(self.frames[1])
        word_p = aud(f"4森林动物手册/{self.word}.mp3")
        self.spelling = SpellingWidget(
            word        = self.word,
            bg_image    = bg2,
            audio_path  = word_p,
            on_success  = self._go_frame3,
            hint_count  = 1,   # first letter pre-filled
            show_helper = True,
        )
        fader.fade_in()

    def _go_frame3(self):
        self.spelling = None
        self.frame    = 2
        self.dial_idx = 0
        self._play_next_dialogue()

    def _play_next_dialogue(self):
        if self.dial_idx < len(self.dialogues):
            p = aud(self.dialogues[self.dial_idx])
            self.dial_idx += 1
            # show corresponding frame image
            frame_offset = min(2 + (self.dial_idx - 1), len(self.frames) - 1)
            self.current_bg = load_img(self.frames[frame_offset])
            audio.play_voice(p, on_done=self._play_next_dialogue)
        else:
            fader.fade_out(on_done=lambda: sm.switch(self.next))

    def handle_event(self, event):
        if self.spelling and not self.locked:
            self.spelling.handle_event(event)

    def update(self):
        if self.spelling:
            self.spelling.update()

    def draw(self, screen):
        if self.frame == 0:
            screen.blit(self.bg1, (0, 0))
        elif self.frame == 1 and self.spelling:
            self.spelling.draw(screen)
        else:
            if hasattr(self, 'current_bg'):
                screen.blit(self.current_bg, (0, 0))

# ── 12. Group Photo ───────────────────────────────────────────────────────────
class GroupPhotoScene(Scene):
    def on_enter(self):
        self.bg = load_img("21合影.PNG")
        audio.play_voice(aud("5森林动物交互/森林旅行结束 母.mp3"),
                          on_done=lambda: fader.fade_out(on_done=lambda: sm.switch("living_return")))

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

# ── 13. Return to Living Room ─────────────────────────────────────────────────
class LivingReturnScene(Scene):
    # word test button area (tune after testing)
    TEST_RECT = pygame.Rect(480, 520, 320, 100)

    def on_enter(self):
        self.bg = load_img("23 客厅.png")
        audio.play_bgm(aud("主场景BGM.mp3"))
        audio.play_voice(aud("单词测试.mp3"))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.TEST_RECT.collidepoint(event.pos):
                fader.fade_out(on_done=lambda: sm.switch("test_screen"))

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

# ── 14. Test Screen (difficulty selection) ───────────────────────────────────
class TestScreenScene(Scene):
    EASY_RECT   = pygame.Rect(225, 461, 199, 54)
    MED_RECT    = pygame.Rect(535, 461, 200, 54)
    HARD_RECT   = pygame.Rect(845, 461, 200, 54)

    def on_enter(self):
        self.bg = load_img("24 测试.png")

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.EASY_RECT.collidepoint(pos):
                fader.fade_out(on_done=lambda: sm.switch("test_easy"))
            elif self.MED_RECT.collidepoint(pos):
                fader.fade_out(on_done=lambda: sm.switch("test_medium"))
            elif self.HARD_RECT.collidepoint(pos):
                fader.fade_out(on_done=lambda: sm.switch("test_hard"))

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

# ── 15. Test Quiz ─────────────────────────────────────────────────────────────
# Animal words for test
ANIMAL_WORDS = {
    "狐狸":   "fox",
    "小马":   "horse",
    "小猪":   "pig",
    "小羊":   "sheep",
    "大象":   "elephant",
    "老虎":   "tiger",
    "鹦鹉":   "parrot",
    "长颈鹿": "giraffe",
    "猴子":   "monkey",
}
ITEM_WORDS = {
    "背包":   "backpack",
    "水壶":   "bottle",
    "指南针": "compass",
    "苹果":   "apple",
    "创可贴": "bandage",
    "雨伞":   "umbrella",
    "蛋糕":   "cake",
    "棒棒糖": "lollipop",
}
ALL_WORDS = {**ANIMAL_WORDS, **ITEM_WORDS}

DIFFICULTY = {
    "easy":   ("初级",  30),
    "medium": ("中级",  25),
    "hard":   ("高级",  20),
}

def quiz_audio(word):
    """Return pronunciation audio for quiz word."""
    # check forest animal audios first
    rev = {v: k for k, v in ANIMAL_WORDS.items()}
    if word in [v for v in ANIMAL_WORDS.values()]:
        return aud(f"4森林动物手册/{word}.mp3")
    return aud(f"2采购清单/采购清单-单词发音/{word}.mp3")

class TestQuizScene(Scene):
    def __init__(self, difficulty_key):
        self.diff_key = difficulty_key

    def on_enter(self):
        level_cn, countdown = DIFFICULTY[self.diff_key]
        self.level_cn      = level_cn
        self.countdown_max = countdown * FPS

        # pick 10 random words
        pool = list(ALL_WORDS.items())
        random.shuffle(pool)
        self.questions = pool[:10]   # list of (cn_name, word)
        self.q_idx     = 0
        self.score     = 0
        self.timer     = self.countdown_max
        self.spelling  = None
        self._load_question()

    def _img_name_for(self, name_cn):
        """Build image path based on difficulty.
        初级 & 中级 share the same folder '初级、中级' (files: 22XXX.PNG).
        高级 uses folder '高级' (files: 22XXX高级.PNG).
        """
        lvl = self.level_cn
        if lvl in ("初级", "中级"):
            folder = "初级、中级"
            for ext in [".PNG", ".png"]:
                p = os.path.join(ASSET_DIR, folder, "22" + name_cn + ext)
                if os.path.exists(p):
                    return p
        else:  # 高级
            for ext in [".PNG", ".png"]:
                p = os.path.join(ASSET_DIR, "高级", "22" + name_cn + "高级" + ext)
                if os.path.exists(p):
                    return p
        return None

    def _load_question(self):
        if self.q_idx >= 10:
            fader.fade_out(on_done=self._show_result)
            return
        name_cn, word = self.questions[self.q_idx]
        img_path = self._img_name_for(name_cn)
        if img_path and os.path.exists(img_path):
            raw = pygame.image.load(img_path)
        else:
            raw = pygame.Surface((SCREEN_W, SCREEN_H))
            raw.fill((30, 30, 30))
        bg = pygame.transform.scale(raw, (SCREEN_W, SCREEN_H))
        audio_p = quiz_audio(word)
        self.timer = self.countdown_max
        self.spelling = TestSpellingWidget(
            word        = word,
            bg_image    = bg,
            audio_path  = audio_p,
            on_success  = self._on_correct,
            hint_count  = 1,
        )

    def _on_correct(self):
        self.score += 1
        self.q_idx += 1
        self._load_question()

    def _show_result(self):
        sm.switch(f"result_{self.diff_key}")

    def handle_event(self, event):
        if self.spelling:
            self.spelling.handle_event(event)

    def update(self):
        if self.spelling:
            self.spelling.update()
        if self.timer > 0:
            self.timer -= 1
            if self.timer <= 0:
                # time up → next question
                self.q_idx += 1
                self._load_question()

    def draw(self, screen):
        if self.spelling:
            self.spelling.draw(screen)
            # draw countdown bar
            ratio = self.timer / self.countdown_max
            bar_w = int(SCREEN_W * ratio)
            pygame.draw.rect(screen, YELLOW, (0, 0, bar_w, 8))
            # progress text
            txt  = FONT_MD.render(f"Q {self.q_idx + 1}/10  Score: {self.score}", True, WHITE)
            screen.blit(txt, (10, 14))

# ── 16. Result Screen ─────────────────────────────────────────────────────────
class ResultScene(Scene):
    RETRY_CENTER = (560, 613)
    BACK_CENTER  = (720, 613)
    BTN_RADIUS   = 70

    def __init__(self, difficulty_key):
        self.diff_key = difficulty_key

    def on_enter(self):
        level_cn = DIFFICULTY[self.diff_key][0]
        quiz_scene = sm.scenes.get(f"test_{self.diff_key}")
        score = quiz_scene.score if quiz_scene else 0
        self.score = score

        if score < 5:
            star = "一星"
        elif score < 10:
            star = "两星"
        else:
            star = "三星"

        self.bg      = load_img(f"{level_cn}{star}.png")
        self.is_3star = (star == "三星")
        self.font_score = pygame.font.Font(None, 72)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            rx, ry = self.RETRY_CENTER
            bx, by = self.BACK_CENTER
            r2 = self.BTN_RADIUS ** 2
            if (mx - rx) ** 2 + (my - ry) ** 2 <= r2:
                fader.fade_out(on_done=lambda: sm.switch(f"test_{self.diff_key}"))
            elif (mx - bx) ** 2 + (my - by) ** 2 <= r2:
                fader.fade_out(on_done=lambda: sm.switch("living_return"))

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))
        # 一星/两星：在(605,400)只显示分数数字，黑色
        if not self.is_3star:
            txt = self.font_score.render(str(self.score), True, BLACK)
            screen.blit(txt, (605 - txt.get_width() // 2,
                               403 - txt.get_height() // 2))

# ── Register all scenes ───────────────────────────────────────────────────────
def register_scenes():
    sm.register("start",            StartScene())
    sm.register("living1",          LivingRoom1Scene())
    sm.register("living2",          LivingRoom2Scene())
    sm.register("transit_to_market",TransitScene("3从家去超市.PNG", "shopping_list"))
    sm.register("shopping_list",    ShoppingListScene())
    sm.register("supermarket",      SupermarketScene())
    sm.register("transit_home",     TransitHomeScene())
    sm.register("animal_book_1",    AnimalBookScene(0))
    sm.register("animal_book_2",    AnimalBookScene(1))
    sm.register("animal_book_3",    AnimalBookScene(2))
    sm.register("depart",           DepartScene())
    sm.register("transit_to_forest",TransitToForestScene())

    for key in ANIMAL_ORDER:
        sm.register(f"forest_{key}", ForestAnimalScene(key))

    sm.register("group_photo",      GroupPhotoScene())
    sm.register("living_return",    LivingReturnScene())
    sm.register("test_screen",      TestScreenScene())

    for dk in ["easy", "medium", "hard"]:
        sm.register(f"test_{dk}",    TestQuizScene(dk))
        sm.register(f"result_{dk}",  ResultScene(dk))

# ── Custom cursor ─────────────────────────────────────────────────────────────
class Cursor:
    def __init__(self):
        raw = img("鼠标.png")
        w, h = raw.get_size()
        scale = 40 / max(w, h)
        self.img = pygame.transform.scale(raw, (int(w * scale), int(h * scale)))
        raw_glow = img("发光鼠标.png")
        wg, hg = raw_glow.get_size()
        scale_g = 40 / max(wg, hg)
        self.img_glow = pygame.transform.scale(raw_glow, (int(wg * scale_g), int(hg * scale_g)))
        self.is_hover = False

    def draw(self, surface, ox, oy, scale):
        """Draw cursor at real mouse pos mapped to game surface coords."""
        mx, my = pygame.mouse.get_pos()
        # convert real screen pos → game surface pos
        gx = (mx - ox) / scale
        gy = (my - oy) / scale
        cur = self.img_glow if self.is_hover else self.img
        surface.blit(cur, (int(gx), int(gy)))

# ── Letterbox helper ──────────────────────────────────────────────────────────
def compute_letterbox(real_w, real_h, game_w=1280, game_h=720):
    """Return (scale, offset_x, offset_y) to fit game_w×game_h into real screen."""
    scale = min(real_w / game_w, real_h / game_h)
    ox = (real_w  - game_w * scale) / 2
    oy = (real_h  - game_h * scale) / 2
    return scale, ox, oy

def screen_to_game(pos, ox, oy, scale):
    """Convert real screen coordinates to game (1280×720) coordinates."""
    return ((pos[0] - ox) / scale, (pos[1] - oy) / scale)

# ── Main loop ─────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    init_fonts()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    real_w, real_h = screen.get_size()
    pygame.display.set_caption("Forest Adventure")
    clock = pygame.time.Clock()

    # Offscreen game surface at fixed 1280×720
    game_surf = pygame.Surface((SCREEN_W, SCREEN_H))

    # Compute letterbox parameters (constant, screen size won't change)
    lb_scale, lb_ox, lb_oy = compute_letterbox(real_w, real_h)
    # Pre-scaled display surface for fast blitting
    scaled_w = int(SCREEN_W * lb_scale)
    scaled_h = int(SCREEN_H * lb_scale)

    pygame.mouse.set_visible(False)

    register_scenes()
    sm.switch("start")

    cursor = Cursor()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F12:
                    _take_screenshot(screen)
            # Remap mouse position to game coordinates before passing to scenes
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                gx, gy = screen_to_game(event.pos, lb_ox, lb_oy, lb_scale)
                # Clamp to game surface bounds
                gx = max(0, min(SCREEN_W - 1, gx))
                gy = max(0, min(SCREEN_H - 1, gy))
                event = _remap_event(event, int(gx), int(gy))
            if not fader.active:
                sm.current.handle_event(event)

        if not fader.active:
            sm.current.update()
        fader.update()
        audio.update()

        # Update cursor hover state
        mx, my = pygame.mouse.get_pos()
        cgx = max(0, min(SCREEN_W - 1, (mx - lb_ox) / lb_scale))
        cgy = max(0, min(SCREEN_H - 1, (my - lb_oy) / lb_scale))
        cursor.is_hover = _is_over_hotspot(cgx, cgy, sm.current)

        # Draw everything to game surface
        game_surf.fill(BLACK)
        sm.current.draw(game_surf)
        fader.draw(game_surf)
        cursor.draw(game_surf, lb_ox, lb_oy, lb_scale)

        # Scale game surface to letterbox size and blit onto black screen
        scaled_surf = pygame.transform.scale(game_surf, (scaled_w, scaled_h))
        screen.fill(BLACK)
        screen.blit(scaled_surf, (int(lb_ox), int(lb_oy)))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

def _take_screenshot(surface):
    """Save current screen to a PNG file in the game directory."""
    import datetime
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(BASE_DIR, f"screenshot_{ts}.png")
    pygame.image.save(surface, path)

def _remap_event(event, gx, gy):
    """Return a new event with pos remapped to game coordinates."""
    if event.type == pygame.MOUSEBUTTONDOWN:
        return pygame.event.Event(pygame.MOUSEBUTTONDOWN,
            pos=(gx, gy), button=event.button)
    elif event.type == pygame.MOUSEBUTTONUP:
        return pygame.event.Event(pygame.MOUSEBUTTONUP,
            pos=(gx, gy), button=event.button)
    elif event.type == pygame.MOUSEMOTION:
        return pygame.event.Event(pygame.MOUSEMOTION,
            pos=(gx, gy), rel=event.rel, buttons=event.buttons)
    return event

def _is_over_hotspot(gx, gy, scene):
    """Return True if game-coords (gx, gy) is over any clickable hotspot in scene."""
    pos = (gx, gy)

    if isinstance(scene, StartScene):
        return scene.BTN_RECT.collidepoint(pos)

    if isinstance(scene, LivingRoom1Scene):
        cx, cy = scene.FOREST_CENTER
        return (gx - cx) ** 2 + (gy - cy) ** 2 <= scene.FOREST_RADIUS ** 2

    if isinstance(scene, ShoppingListScene):
        return any(rect.collidepoint(pos) for _, rect in scene.ICON_RECTS)

    if isinstance(scene, SupermarketScene):
        if scene.spelling:
            sp = scene.spelling
            return (sp.speaker_rect.collidepoint(pos) or
                    sp.confirm_rect.collidepoint(pos) or
                    (sp.show_helper and sp.helper_rect.collidepoint(pos)) or
                    any(r.collidepoint(pos) for r in sp.slot_rects) or
                    any(r.collidepoint(pos) for r in sp.key_rects.values()))
        return (any(rect.collidepoint(pos) for _, (_, rect) in ITEM_ENGLISH.items()) or
                any(r.collidepoint(pos) for r in DISTRACT_RECTS))

    if isinstance(scene, AnimalBookScene):
        if not scene.listening:
            return any(rect.collidepoint(pos) for _, _, _, rect in scene.animals)

    if isinstance(scene, LivingReturnScene):
        return scene.TEST_RECT.collidepoint(pos)

    if isinstance(scene, TestScreenScene):
        return (scene.EASY_RECT.collidepoint(pos) or
                scene.MED_RECT.collidepoint(pos) or
                scene.HARD_RECT.collidepoint(pos))

    if isinstance(scene, ResultScene):
        rx, ry = scene.RETRY_CENTER
        bx, by = scene.BACK_CENTER
        r2 = scene.BTN_RADIUS ** 2
        return ((gx - rx) ** 2 + (gy - ry) ** 2 <= r2 or
                (gx - bx) ** 2 + (gy - by) ** 2 <= r2)

    if isinstance(scene, ForestAnimalScene) and scene.spelling and not scene.locked:
        sp = scene.spelling
        return (sp.speaker_rect.collidepoint(pos) or
                sp.confirm_rect.collidepoint(pos) or
                (sp.show_helper and sp.helper_rect.collidepoint(pos)) or
                any(r.collidepoint(pos) for r in sp.slot_rects) or
                any(r.collidepoint(pos) for r in sp.key_rects.values()))

    if isinstance(scene, TestQuizScene) and hasattr(scene, 'spelling') and scene.spelling:
        sp = scene.spelling
        return (sp.spk_rect.collidepoint(pos) or
                sp.confirm_rect.collidepoint(pos) or
                any(r.collidepoint(pos) for r in sp.slot_rects) or
                any(r.collidepoint(pos) for r in sp.key_rects.values()))

    return False

if __name__ == "__main__":
    main()
