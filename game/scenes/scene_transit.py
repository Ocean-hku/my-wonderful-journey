"""过渡场景：显示过渡图片，停留2秒后自动切换"""
import pygame
from scenes.scene_base import SceneBase
from utils import asset_loader

W, H = 960, 540
TRANSIT_DURATION = 2.0


class SceneTransit(SceneBase):
    def on_enter(self, image="3从家去超市.PNG", next_scene="shopping_list", **kwargs):
        self._image = image
        self._next = next_scene
        self._next_kwargs = kwargs
        self._timer = 0.0

    def update(self, dt):
        self._timer += dt
        if self._timer >= TRANSIT_DURATION:
            self.manager.switch(self._next, fade=True, **self._next_kwargs)

    def draw(self, screen):
        bg = asset_loader.get_image(self._image, (W, H))
        screen.blit(bg, (0, 0))
