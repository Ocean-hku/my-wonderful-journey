"""场景管理器：注册、切换、过渡效果"""
import pygame
from scenes.scene_base import SceneBase


class SceneManager:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self._scenes: dict[str, type] = {}
        self._current: SceneBase | None = None
        self._current_name: str = ""

        # 淡入淡出
        self._fade_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        self._fade_alpha: float = 0
        self._fade_dir: int = 0      # 1=淡出 -1=淡入 0=无
        self._fade_speed: float = 400  # alpha/s
        self._next_scene: str = ""
        self._next_kwargs: dict = {}

    def register(self, name: str, scene_class: type):
        self._scenes[name] = scene_class

    def switch(self, name: str, fade=True, **kwargs):
        if fade:
            self._fade_dir = 1
            self._fade_alpha = 0
            self._next_scene = name
            self._next_kwargs = kwargs
        else:
            self._do_switch(name, **kwargs)

    def _do_switch(self, name: str, **kwargs):
        if self._current:
            self._current.on_exit()
        cls = self._scenes[name]
        self._current = cls(self)
        self._current_name = name
        self._current.on_enter(**kwargs)
        # 淡入
        self._fade_dir = -1
        self._fade_alpha = 255

    @property
    def current_name(self) -> str:
        return self._current_name

    def handle_event(self, event: pygame.event.Event):
        if self._fade_dir == 1:   # 淡出中，不响应交互
            return
        if self._current:
            self._current.handle_event(event)

    def update(self, dt: float):
        if self._fade_dir != 0:
            self._fade_alpha += self._fade_dir * self._fade_speed * dt
            if self._fade_dir == 1 and self._fade_alpha >= 255:
                self._fade_alpha = 255
                self._fade_dir = 0
                self._do_switch(self._next_scene, **self._next_kwargs)
            elif self._fade_dir == -1 and self._fade_alpha <= 0:
                self._fade_alpha = 0
                self._fade_dir = 0
        if self._current:
            self._current.update(dt)

    def draw(self):
        if self._current:
            self._current.draw(self.screen)
        # 淡入淡出遮罩
        if self._fade_alpha > 0:
            self._fade_surface.fill((0, 0, 0, int(self._fade_alpha)))
            self.screen.blit(self._fade_surface, (0, 0))
