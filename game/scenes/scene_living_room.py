"""第一幕：客厅 —— 选择目的地，色盲模式切换，查看奖章"""
import pygame
from scenes.scene_base import SceneBase
from utils import asset_loader, audio_manager
from utils.asset_loader import get_font
from game_state import state
from components.dialogue_box import DialogueBox

W, H = 960, 540

# 色盲模式标签与色调
CB_MODES = ["normal", "deuteranopia", "protanopia", "tritanopia"]
CB_LABELS = ["Normal", "Deuteranopia", "Protanopia", "Tritanopia"]


class SceneLivingRoom(SceneBase):
    def on_enter(self, **kwargs):
        audio_manager.play_bgm("主场景BGM.mp3")
        self._font = get_font(22, bold=True)
        self._small = get_font(17)
        self._title_font = get_font(26, bold=True)

        self._dialogue = DialogueBox(None)  # 用主screen绘制
        self._dialogue.screen = None  # 由draw传入

        # 按钮
        self.forest_btn  = pygame.Rect(W // 2 - 130, 360, 260, 56)
        self.challenge_btn = pygame.Rect(W // 2 - 130, 430, 260, 46)
        self.cb_btn = pygame.Rect(W - 220, 20, 200, 36)

        self._hover_forest = False
        self._hover_challenge = False
        self._hover_cb = False

        self._intro_played = False
        self._cb_menu_open = False
        self._cb_btn_rects = []

        # 开场对话
        self._dialogue.show_sequence([
            {"text": "Let's go on a trip! Where shall we go?", "speaker": "Mom"},
        ], on_done=self._on_intro_done)

    def _on_intro_done(self):
        self._intro_played = True
        audio_manager.play_voice("1开场/开场 去旅行 母.mp3")

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # 先处理对话框点击
            if self._dialogue.visible:
                self._dialogue.handle_event(event)
                return

            # 色盲菜单
            if self._cb_menu_open:
                for i, r in enumerate(self._cb_btn_rects):
                    if r.collidepoint(pos):
                        state.colorblind_mode = CB_MODES[i]
                        self._cb_menu_open = False
                        return
                self._cb_menu_open = False
                return

            if self.cb_btn.collidepoint(pos):
                self._cb_menu_open = not self._cb_menu_open
                self._build_cb_menu()
                return

            if self.forest_btn.collidepoint(pos):
                audio_manager.play_voice("1开场/开场2 去超市 母.mp3")
                self.manager.switch("transit", fade=True,
                                    image="3从家去超市.PNG",
                                    next_scene="shopping_list")
                return

            if self.challenge_btn.collidepoint(pos):
                self.manager.switch("challenge", fade=True)
                return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self._dialogue.handle_event(event)

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            self._hover_forest    = self.forest_btn.collidepoint(pos)
            self._hover_challenge = self.challenge_btn.collidepoint(pos)
            self._hover_cb        = self.cb_btn.collidepoint(pos)

    def _build_cb_menu(self):
        self._cb_btn_rects = []
        for i in range(len(CB_MODES)):
            r = pygame.Rect(self.cb_btn.x, self.cb_btn.bottom + i * 38, self.cb_btn.width, 34)
            self._cb_btn_rects.append(r)

    def update(self, dt):
        self._dialogue.update(dt)

    def draw(self, screen):
        self._dialogue.screen = screen
        bg = asset_loader.get_image("2客厅.PNG", (W, H))
        screen.blit(bg, (0, 0))

        # 奖章展示（右下角）
        self._draw_medals(screen)

        # 森林出发按钮
        c1 = (120, 200, 120) if self._hover_forest else (90, 170, 90)
        pygame.draw.rect(screen, c1, self.forest_btn, border_radius=28)
        pygame.draw.rect(screen, (40, 100, 40), self.forest_btn, 3, border_radius=28)
        t = self._font.render("Go to the Forest!", True, (255, 255, 255))
        screen.blit(t, t.get_rect(center=self.forest_btn.center))

        # 挑战模式按钮
        c2 = (220, 180, 80) if self._hover_challenge else (200, 160, 60)
        pygame.draw.rect(screen, c2, self.challenge_btn, border_radius=22)
        pygame.draw.rect(screen, (140, 100, 20), self.challenge_btn, 2, border_radius=22)
        t2 = self._small.render("Challenge Mode", True, (60, 30, 0))
        screen.blit(t2, t2.get_rect(center=self.challenge_btn.center))

        # 色盲切换按钮
        cb_color = (180, 220, 255) if self._hover_cb else (150, 190, 230)
        pygame.draw.rect(screen, cb_color, self.cb_btn, border_radius=8)
        pygame.draw.rect(screen, (80, 120, 180), self.cb_btn, 2, border_radius=8)
        label = f"Mode: {CB_LABELS[CB_MODES.index(state.colorblind_mode)]}"
        t3 = self._small.render(label, True, (20, 40, 100))
        screen.blit(t3, t3.get_rect(center=self.cb_btn.center))

        # 色盲下拉菜单
        if self._cb_menu_open:
            for i, r in enumerate(self._cb_btn_rects):
                bg_c = (200, 230, 255) if CB_MODES[i] == state.colorblind_mode else (230, 245, 255)
                pygame.draw.rect(screen, bg_c, r, border_radius=6)
                pygame.draw.rect(screen, (80, 120, 180), r, 1, border_radius=6)
                lt = self._small.render(CB_LABELS[i], True, (20, 40, 100))
                screen.blit(lt, lt.get_rect(center=r.center))

        self._dialogue.draw(screen)

    def _draw_medals(self, screen):
        """在右下角显示已获得的奖章数量"""
        gold   = sum(1 for v in state.medals.values() if v == "gold")
        silver = sum(1 for v in state.medals.values() if v == "silver")
        bronze = sum(1 for v in state.medals.values() if v == "bronze")
        if gold + silver + bronze == 0:
            return
        font = get_font(16)
        x, y = W - 160, H - 50
        for emoji, count, color in [
            ("★", gold,   (255, 210, 0)),
            ("☆", silver, (180, 180, 200)),
            ("◆", bronze, (180, 100, 40)),
        ]:
            if count:
                t = font.render(f"{emoji}×{count}", True, color)
                screen.blit(t, (x, y))
                x += 50
