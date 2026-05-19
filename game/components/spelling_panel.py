"""
拼写面板组件（复用于第三幕/第五幕/挑战模式）

用法：
    panel = SpellingPanel(screen, word, bg_image_name, on_correct, on_wrong)
    每帧调用 panel.handle_event / panel.update / panel.draw
    答对时回调 on_correct()；错误时回调 on_wrong()
"""
import pygame
import math
import random
from utils import asset_loader
from utils import audio_manager
from utils.asset_loader import get_font

W, H = 960, 540

# ── 配色 ─────────────────────────────────────────────────────────
COLORS = {
    "slot_bg":     (255, 255, 255),
    "slot_border": (80,  120, 200),
    "slot_filled": (200, 230, 255),
    "slot_correct":(120, 220, 120),
    "slot_wrong":  (255, 160, 130),
    "btn_bg":      (240, 240, 255),
    "btn_hover":   (200, 215, 255),
    "btn_border":  (100, 130, 210),
    "btn_text":    (30,  30,  80),
    "hint_btn":    (255, 220, 100),
    "confirm_btn": (100, 200, 120),
    "confirm_dis": (180, 180, 180),
    "panel_bg":    (0,   0,   0,  160),
    "overlay_bg":  (30,  30,  60,  200),
}

ALPHABET = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
SLOT_H = 56
SLOT_W = 54
BTN_SIZE = 44
BTN_COLS = 13


class SpellingPanel:
    def __init__(self, screen: pygame.Surface, word: str, bg_image: str,
                 on_correct=None, on_wrong=None, colorblind_mode="normal",
                 challenge_mode=False):
        self.screen = screen
        self.word = word.upper()
        self.bg_image = bg_image          # 拼写背景图文件名（场景图/）
        self.on_correct = on_correct or (lambda: None)
        self.on_wrong   = on_wrong   or (lambda: None)
        self.colorblind_mode = colorblind_mode
        self.challenge_mode = challenge_mode

        # 字母槽：每格存 None 或 字母字符
        self.slots: list[str | None] = [None] * len(self.word)
        # 已点击的字母按钮下标集合（避免重复）
        self.used_btn_indices: set[int] = set()

        # 随机打乱字母表（含正确字母保证出现）
        self._letters = self._make_letter_pool()

        self.hint_count = 3          # 剩余求助次数
        self.shake_timer = 0.0       # 错误抖动计时
        self.shake_slot = -1         # 抖动的槽下标
        self.result = None           # None / 'correct' / 'wrong'
        self.result_timer = 0.0

        # 选中的槽（下一个填入位置）
        self._next_slot = 0

        self._font_letter = get_font(28, bold=True)
        self._font_small  = get_font(18)
        self._font_hint   = get_font(16)

        self._layout()
        self._done = False

    # ── 布局计算 ────────────────────────────────────────────────
    def _layout(self):
        n = len(self.word)
        total_w = n * SLOT_W + (n - 1) * 8
        start_x = (W - total_w) // 2
        slot_y = H - 180

        self.slot_rects = []
        for i in range(n):
            x = start_x + i * (SLOT_W + 8)
            self.slot_rects.append(pygame.Rect(x, slot_y, SLOT_W, SLOT_H))

        # 字母按钮（26个，2行）
        total_btns = len(self._letters)
        btn_y_start = slot_y + SLOT_H + 20
        self.btn_rects = []
        for i, ch in enumerate(self._letters):
            col = i % BTN_COLS
            row = i // BTN_COLS
            x = (W - BTN_COLS * (BTN_SIZE + 6)) // 2 + col * (BTN_SIZE + 6)
            y = btn_y_start + row * (BTN_SIZE + 6)
            self.btn_rects.append(pygame.Rect(x, y, BTN_SIZE, BTN_SIZE))

        # 求助按钮
        self.hint_rect = pygame.Rect(W - 160, slot_y - 50, 130, 40)
        # 确认按钮
        self.confirm_rect = pygame.Rect(W // 2 - 65, slot_y + SLOT_H + 10 + 2 * (BTN_SIZE + 6) + 10, 130, 44)

    def _make_letter_pool(self):
        """生成26个字母（含单词所有字母，随机排列）"""
        pool = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        random.shuffle(pool)
        return pool

    # ── 公开接口 ────────────────────────────────────────────────
    @property
    def done(self):
        return self._done

    def handle_event(self, event: pygame.event.Event):
        if self._done:
            return
        if self.result is not None:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            # 求助
            if self.hint_rect.collidepoint(pos) and self.hint_count > 0:
                self._use_hint()
                return
            # 字母按钮
            for i, rect in enumerate(self.btn_rects):
                if rect.collidepoint(pos) and i not in self.used_btn_indices:
                    self._input_letter(i)
                    return
            # 槽：点击取消
            for i, rect in enumerate(self.slot_rects):
                if rect.collidepoint(pos) and self.slots[i] is not None:
                    self._remove_slot(i)
                    return
            # 确认按钮
            if self.confirm_rect.collidepoint(pos):
                self._confirm()

    def update(self, dt: float):
        if self.shake_timer > 0:
            self.shake_timer = max(0, self.shake_timer - dt)
        if self.result_timer > 0:
            self.result_timer -= dt
            if self.result_timer <= 0:
                self._done = True

    def draw(self, surface: pygame.Surface):
        # 背景图（场景图中的拼写背景）
        bg = asset_loader.get_image(self.bg_image, (W, H))
        surface.blit(bg, (0, 0))

        # 半透明遮罩
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        surface.blit(overlay, (0, 0))

        self._draw_slots(surface)
        self._draw_buttons(surface)
        self._draw_hint_btn(surface)
        self._draw_confirm_btn(surface)

        if self.result == "correct":
            self._draw_result_overlay(surface, True)
        elif self.result == "wrong":
            self._draw_result_overlay(surface, False)

    # ── 内部逻辑 ────────────────────────────────────────────────
    def _input_letter(self, btn_idx: int):
        if self._next_slot >= len(self.slots):
            return
        ch = self._letters[btn_idx]
        self.slots[self._next_slot] = ch
        self.used_btn_indices.add(btn_idx)
        self._next_slot += 1

    def _remove_slot(self, slot_idx: int):
        ch = self.slots[slot_idx]
        # 找回对应按钮下标
        for i in self.used_btn_indices:
            if self._letters[i] == ch:
                self.used_btn_indices.discard(i)
                break
        self.slots[slot_idx] = None
        # 重排 _next_slot（找最左空格）
        for i, s in enumerate(self.slots):
            if s is None:
                self._next_slot = i
                return
        self._next_slot = len(self.slots)

    def _use_hint(self):
        if self.hint_count <= 0:
            return
        # 找第一个还是空的且填错的槽
        for i, s in enumerate(self.slots):
            if s is None:
                correct_ch = self.word[i]
                # 找该字母的按钮
                for bi, ch in enumerate(self._letters):
                    if ch == correct_ch and bi not in self.used_btn_indices:
                        self._input_letter_direct(i, bi)
                        self.hint_count -= 1
                        return
                # 若被用掉（同字母另一个位置填了），找另一个
                break

    def _input_letter_direct(self, slot_idx: int, btn_idx: int):
        self.slots[slot_idx] = self._letters[btn_idx]
        self.used_btn_indices.add(btn_idx)
        # 更新 _next_slot
        for i, s in enumerate(self.slots):
            if s is None:
                self._next_slot = i
                return
        self._next_slot = len(self.slots)

    def _confirm(self):
        if None in self.slots:
            return
        answer = "".join(self.slots)
        if answer == self.word:
            self.result = "correct"
            self.result_timer = 1.2
            audio_manager.play_sfx("sfx/correct.mp3")
            self.on_correct()
        else:
            self.result = "wrong"
            self.result_timer = 1.0
            audio_manager.play_sfx("sfx/wrong.mp3")
            self.shake_timer = 0.4
            self.on_wrong()
            # 清空错误的槽
            for i in range(len(self.slots)):
                if self.slots[i] != self.word[i]:
                    self.slots[i] = None
            self.used_btn_indices.clear()
            # 重建：保留正确槽的按钮占用
            for i, s in enumerate(self.slots):
                if s is not None:
                    for bi, ch in enumerate(self._letters):
                        if ch == s and bi not in self.used_btn_indices:
                            self.used_btn_indices.add(bi)
                            break
            for i, s in enumerate(self.slots):
                if s is None:
                    self._next_slot = i
                    return
            self._next_slot = len(self.slots)
            self.result = None   # 立即允许重新输入

    # ── 绘制子函数 ───────────────────────────────────────────────
    def _draw_slots(self, surface):
        for i, rect in enumerate(self.slot_rects):
            r = rect.copy()
            # 抖动
            if self.shake_timer > 0 and self.result == "wrong":
                r.x += int(math.sin(self.shake_timer * 50) * 4)

            ch = self.slots[i]
            color = COLORS["slot_filled"] if ch else COLORS["slot_bg"]
            pygame.draw.rect(surface, color, r, border_radius=8)
            pygame.draw.rect(surface, COLORS["slot_border"], r, 2, border_radius=8)

            if ch:
                txt = self._font_letter.render(ch, True, COLORS["btn_text"])
                surface.blit(txt, txt.get_rect(center=r.center))

    def _draw_buttons(self, surface):
        mouse = pygame.mouse.get_pos()
        for i, (rect, ch) in enumerate(zip(self.btn_rects, self._letters)):
            used = i in self.used_btn_indices
            if used:
                color = (200, 200, 200)
                border = (160, 160, 160)
                txt_color = (150, 150, 150)
            elif rect.collidepoint(mouse):
                color = COLORS["btn_hover"]
                border = COLORS["slot_border"]
                txt_color = COLORS["btn_text"]
            else:
                color = COLORS["btn_bg"]
                border = COLORS["btn_border"]
                txt_color = COLORS["btn_text"]
            pygame.draw.rect(surface, color, rect, border_radius=6)
            pygame.draw.rect(surface, border, rect, 2, border_radius=6)
            txt = self._font_letter.render(ch, True, txt_color)
            surface.blit(txt, txt.get_rect(center=rect.center))

    def _draw_hint_btn(self, surface):
        rect = self.hint_rect
        color = COLORS["hint_btn"] if self.hint_count > 0 else (200, 200, 200)
        pygame.draw.rect(surface, color, rect, border_radius=8)
        pygame.draw.rect(surface, (180, 140, 0), rect, 2, border_radius=8)
        label = f"Hint ({self.hint_count})"
        txt = self._font_small.render(label, True, (60, 40, 0))
        surface.blit(txt, txt.get_rect(center=rect.center))

    def _draw_confirm_btn(self, surface):
        rect = self.confirm_rect
        ready = None not in self.slots
        color = COLORS["confirm_btn"] if ready else COLORS["confirm_dis"]
        pygame.draw.rect(surface, color, rect, border_radius=10)
        pygame.draw.rect(surface, (0, 100, 0) if ready else (130, 130, 130), rect, 2, border_radius=10)
        txt = self._font_small.render("Confirm", True, (255, 255, 255) if ready else (180, 180, 180))
        surface.blit(txt, txt.get_rect(center=rect.center))

    def _draw_result_overlay(self, surface, correct: bool):
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        alpha = 120
        if correct:
            overlay.fill((100, 220, 100, alpha))
        else:
            overlay.fill((220, 100, 100, alpha))
        surface.blit(overlay, (0, 0))
        msg = "Correct!" if correct else "Try again!"
        font = get_font(48, bold=True)
        txt = font.render(msg, True, (255, 255, 255))
        # 描边
        shadow = font.render(msg, True, (0, 0, 0))
        cx, cy = W // 2, H // 2
        surface.blit(shadow, shadow.get_rect(center=(cx + 2, cy + 2)))
        surface.blit(txt,    txt.get_rect(center=(cx, cy)))
