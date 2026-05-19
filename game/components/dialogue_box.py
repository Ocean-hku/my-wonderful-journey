"""
对话框组件：底部横条 + 人物头像位置
支持逐字显示效果，点击跳过/翻页
"""
import pygame
from utils.asset_loader import get_font

W, H = 960, 540
BOX_H = 120
BOX_Y = H - BOX_H - 10
PAD = 18
CHAR_SPEED = 40   # 每秒字符数


class DialogueBox:
    def __init__(self, screen: pygame.Surface, font_size=22):
        self.screen = screen
        self._font = get_font(font_size)
        self._name_font = get_font(18, bold=True)

        self.lines: list[dict] = []   # [{text, speaker, on_done}, ...]
        self._current = 0
        self._char_pos = 0.0
        self._timer = 0.0
        self._visible = False
        self._done_cb = None

    def show(self, text: str, speaker: str = "", on_done=None):
        """显示单条对话"""
        self.lines = [{"text": text, "speaker": speaker}]
        self._done_cb = on_done
        self._current = 0
        self._char_pos = 0.0
        self._timer = 0.0
        self._visible = True

    def show_sequence(self, sequence: list, on_done=None):
        """sequence: [{"text":"...", "speaker":"..."}, ...]"""
        self.lines = sequence
        self._done_cb = on_done
        self._current = 0
        self._char_pos = 0.0
        self._timer = 0.0
        self._visible = True

    def hide(self):
        self._visible = False

    @property
    def visible(self):
        return self._visible

    @property
    def finished(self):
        """当前序列是否全部结束"""
        return not self._visible

    def handle_event(self, event: pygame.event.Event):
        if not self._visible:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 点击屏幕任意位置均可推进对话
            line = self.lines[self._current]
            full_len = len(line["text"])
            if self._char_pos < full_len:
                # 跳到结尾
                self._char_pos = float(full_len)
            else:
                self._advance()

    def _advance(self):
        self._current += 1
        if self._current >= len(self.lines):
            self._visible = False
            if self._done_cb:
                self._done_cb()
        else:
            self._char_pos = 0.0
            self._timer = 0.0

    def update(self, dt: float):
        if not self._visible:
            return
        line = self.lines[self._current]
        full_len = len(line["text"])
        if self._char_pos < full_len:
            self._char_pos = min(float(full_len), self._char_pos + CHAR_SPEED * dt)

    def draw(self, surface: pygame.Surface):
        if not self._visible:
            return
        box_rect = pygame.Rect(20, BOX_Y, W - 40, BOX_H)

        # 背景
        bg = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        bg.fill((20, 20, 50, 210))
        surface.blit(bg, box_rect.topleft)
        pygame.draw.rect(surface, (100, 140, 220), box_rect, 2, border_radius=12)

        line = self.lines[self._current]
        text = line["text"]
        speaker = line.get("speaker", "")
        display_text = text[:int(self._char_pos)]

        # 说话者名字
        if speaker:
            name_surf = self._name_font.render(speaker, True, (255, 220, 100))
            surface.blit(name_surf, (box_rect.x + PAD, box_rect.y + 8))
            text_y = box_rect.y + 34
        else:
            text_y = box_rect.y + PAD

        # 自动换行文字
        self._draw_wrapped(surface, display_text, box_rect.x + PAD,
                           text_y, box_rect.width - PAD * 2)

        # 继续箭头（文字全显示后）
        if self._char_pos >= len(text):
            arrow = self._font.render("▶", True, (200, 200, 255))
            surface.blit(arrow, (box_rect.right - 30, box_rect.bottom - 28))

    def _draw_wrapped(self, surface, text, x, y, max_w):
        words = text.split(" ")
        line_surf = []
        current_line = ""
        for word in words:
            test = current_line + (" " if current_line else "") + word
            if self._font.size(test)[0] <= max_w:
                current_line = test
            else:
                if current_line:
                    line_surf.append(current_line)
                current_line = word
        if current_line:
            line_surf.append(current_line)
        for i, ln in enumerate(line_surf[:3]):
            txt = self._font.render(ln, True, (240, 240, 240))
            surface.blit(txt, (x, y + i * 28))
