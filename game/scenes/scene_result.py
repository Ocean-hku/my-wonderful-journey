"""结算画面：全家合影 + 统计 + 返回主菜单"""
import pygame
from scenes.scene_base import SceneBase
from utils import asset_loader, audio_manager
from utils.asset_loader import get_font
from game_state import state

W, H = 960, 540


class SceneResult(SceneBase):
    def on_enter(self, **kwargs):
        audio_manager.play_bgm("主场景BGM.mp3")
        self._font  = get_font(32, bold=True)
        self._small = get_font(20)
        self._alpha = 0

        self.back_btn = pygame.Rect(W // 2 - 120, H - 90, 240, 56)
        self._hover = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_btn.collidepoint(event.pos):
                state.reset()
                self.manager.switch("title", fade=True)
        if event.type == pygame.MOUSEMOTION:
            self._hover = self.back_btn.collidepoint(event.pos)

    def update(self, dt):
        if self._alpha < 255:
            self._alpha = min(255, self._alpha + 200 * dt)

    def draw(self, screen):
        bg = asset_loader.get_image("21合影.PNG", (W, H))
        screen.blit(bg, (0, 0))

        # 渐变遮罩
        overlay = pygame.Surface((W, 160), pygame.SRCALPHA)
        overlay.fill((0, 0, 30, 180))
        screen.blit(overlay, (0, 0))

        # 标题
        t = self._font.render("Journey Complete!", True, (255, 240, 100))
        screen.blit(t, t.get_rect(center=(W // 2, 40)))

        # 统计
        stats = [
            f"Words learned at supermarket: {len(state.purchased)} / 8",
            f"Forest animals met: {len(state.interacted_animals)} / 9",
        ]
        for i, s in enumerate(stats):
            st = self._small.render(s, True, (220, 220, 255))
            screen.blit(st, st.get_rect(center=(W // 2, 85 + i * 28)))

        # 奖章
        gold   = sum(1 for v in state.medals.values() if v == "gold")
        silver = sum(1 for v in state.medals.values() if v == "silver")
        bronze = sum(1 for v in state.medals.values() if v == "bronze")
        if gold + silver + bronze > 0:
            medal_t = self._small.render(
                f"Challenge Medals —  ★ Gold:{gold}  ☆ Silver:{silver}  ◆ Bronze:{bronze}",
                True, (255, 210, 80)
            )
            screen.blit(medal_t, medal_t.get_rect(center=(W // 2, 142)))

        # 返回按钮
        color = (200, 100, 100) if self._hover else (180, 80, 80)
        pygame.draw.rect(screen, color, self.back_btn, border_radius=28)
        pygame.draw.rect(screen, (120, 40, 40), self.back_btn, 3, border_radius=28)
        bt = self._font.render("Play Again", True, (255, 255, 255))
        screen.blit(bt, bt.get_rect(center=self.back_btn.center))
