"""所有场景的基类"""
import pygame


class SceneBase:
    def __init__(self, manager):
        self.manager = manager   # SceneManager 引用

    def on_enter(self, **kwargs):
        """场景进入时调用，kwargs 为切换参数"""
        pass

    def on_exit(self):
        """场景退出时调用"""
        pass

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt: float):
        """dt 单位秒"""
        pass

    def draw(self, screen: pygame.Surface):
        pass
