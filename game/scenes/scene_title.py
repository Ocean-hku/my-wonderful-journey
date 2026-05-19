"""第零幕：标题画面"""
import pygame
from scenes.scene_base import SceneBase
from utils import asset_loader, audio_manager
from utils.asset_loader import get_font

W, H = 960, 540


class SceneTitle(SceneBase):
    def on_enter(self, **kwargs):
        audio_manager.play_bgm("主场景BGM.mp3")
        self._font = get_font(32, bold=True)
        self._small = get_font(20)

        # 进入按钮
        self.start_rect = pygame.Rect(W // 2 - 110, 400, 220, 60)
        self._hover = False
        self._alpha = 0
        self._fade_in = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 点击任意位置均可进入（兼容不同背景图布局）
            self.manager.switch("living_room", fade=True)
        if event.type == pygame.MOUSEMOTION:
            self._hover = self.start_rect.collidepoint(event.pos)

    def update(self, dt):
        if self._fade_in and self._alpha < 255:
            self._alpha = min(255, self._alpha + 300 * dt)

    def draw(self, screen):
        bg = asset_loader.get_image("1开始页.PNG", (W, H))
        screen.blit(bg, (0, 0))

        # 开始按钮
        color = (255, 230, 80) if self._hover else (240, 200, 50)
        pygame.draw.rect(screen, color, self.start_rect, border_radius=30)
        pygame.draw.rect(screen, (180, 140, 0), self.start_rect, 3, border_radius=30)
        txt = self._font.render("START", True, (80, 40, 0))
        screen.blit(txt, txt.get_rect(center=self.start_rect.center))

        # 淡入遮罩
        if self._alpha < 255:
            mask = pygame.Surface((W, H))
            mask.set_alpha(255 - int(self._alpha))
            mask.fill((0, 0, 0))
            screen.blit(mask, (0, 0))
