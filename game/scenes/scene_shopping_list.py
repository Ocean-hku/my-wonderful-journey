"""第二幕：超市门口 —— 购物清单单词学习（循环展示8件物品）"""
import pygame
from scenes.scene_base import SceneBase
from utils import asset_loader, audio_manager
from utils.asset_loader import get_font
from data.words_data import SHOPPING_ITEMS
from components.dialogue_box import DialogueBox

W, H = 960, 540


class SceneShoppingList(SceneBase):
    def on_enter(self, **kwargs):
        audio_manager.play_bgm("主场景BGM.mp3")
        self._font   = get_font(36, bold=True)
        self._small  = get_font(20)
        self._medium = get_font(26, bold=True)

        self._items = SHOPPING_ITEMS
        self._current = 0          # 当前展示物品下标
        self._phase = "intro"      # intro → learn → done
        self._dialogue = DialogueBox(None)

        # 导航按钮
        self.prev_btn  = pygame.Rect(30, H // 2 - 28, 56, 56)
        self.next_btn  = pygame.Rect(W - 86, H // 2 - 28, 56, 56)
        self.sound_btn = pygame.Rect(W // 2 - 50, H - 80, 100, 44)
        self.go_btn    = pygame.Rect(W // 2 - 100, H - 76, 200, 52)

        self._show_item(0)

    def _show_item(self, idx):
        self._current = idx
        item = self._items[idx]
        # 播放父母介绍语音（优先母，若无则父）
        intro = item["intro_audio"]
        if "mom" in intro:
            audio_manager.play_voice(intro["mom"])
        elif "dad" in intro:
            audio_manager.play_voice(intro["dad"])
        self._dialogue.show(
            f'This is a {item["word"].upper()}  ({item["zh"]})',
            speaker="Mom",
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            self._dialogue.handle_event(event)

            # 上一个
            if self.prev_btn.collidepoint(pos) and self._current > 0:
                self._show_item(self._current - 1)
                return

            # 下一个（未到末尾）
            if self.next_btn.collidepoint(pos) and self._current < len(self._items) - 1:
                self._show_item(self._current + 1)
                return

            # 单词发音
            if self.sound_btn.collidepoint(pos):
                item = self._items[self._current]
                audio_manager.play_voice(item["word_audio"])
                return

            # 去超市按钮（最后一个物品之后出现）
            if self._current == len(self._items) - 1:
                if self.go_btn.collidepoint(pos):
                    self.manager.switch("supermarket", fade=True)

    def update(self, dt):
        self._dialogue.update(dt)

    def draw(self, screen):
        self._dialogue.screen = screen
        bg = asset_loader.get_image("4购物清单.PNG", (W, H))
        screen.blit(bg, (0, 0))

        item = self._items[self._current]

        # 物品序号提示
        idx_txt = self._small.render(
            f"{self._current + 1} / {len(self._items)}", True, (255, 255, 255)
        )
        screen.blit(idx_txt, idx_txt.get_rect(center=(W // 2, 30)))

        # 单词大字
        word_surf = self._font.render(item["word"].upper(), True, (255, 255, 255))
        shadow = self._font.render(item["word"].upper(), True, (0, 0, 0))
        screen.blit(shadow, shadow.get_rect(center=(W // 2 + 2, 80 + 2)))
        screen.blit(word_surf, word_surf.get_rect(center=(W // 2, 80)))

        # 中文提示
        zh_surf = self._small.render(item["zh"], True, (255, 240, 180))
        screen.blit(zh_surf, zh_surf.get_rect(center=(W // 2, 114)))

        # 拼写预览图
        spell_img = asset_loader.get_image(item["image"], (320, 180))
        screen.blit(spell_img, spell_img.get_rect(center=(W // 2, 240)))

        # 左右翻页箭头
        if self._current > 0:
            self._draw_arrow_btn(screen, self.prev_btn, "◀")
        if self._current < len(self._items) - 1:
            self._draw_arrow_btn(screen, self.next_btn, "▶")

        # 发音按钮
        pygame.draw.rect(screen, (100, 180, 255), self.sound_btn, border_radius=22)
        pygame.draw.rect(screen, (40, 100, 200), self.sound_btn, 2, border_radius=22)
        st = self._small.render("🔊 Hear it", True, (20, 20, 80))
        screen.blit(st, st.get_rect(center=self.sound_btn.center))

        # 去超市按钮（最后一项）
        if self._current == len(self._items) - 1:
            pygame.draw.rect(screen, (80, 200, 100), self.go_btn, border_radius=26)
            pygame.draw.rect(screen, (30, 120, 50), self.go_btn, 3, border_radius=26)
            gt = self._medium.render("Go Shopping! →", True, (255, 255, 255))
            screen.blit(gt, gt.get_rect(center=self.go_btn.center))

        self._dialogue.draw(screen)

    def _draw_arrow_btn(self, screen, rect, label):
        mouse = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse)
        color = (200, 220, 255) if hover else (160, 180, 230)
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, (80, 100, 180), rect, 2, border_radius=10)
        font = get_font(28, bold=True)
        t = font.render(label, True, (40, 40, 120))
        screen.blit(t, t.get_rect(center=rect.center))
