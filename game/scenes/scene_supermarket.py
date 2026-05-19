"""
第三幕：超市采购
- 点击正确商品 → 弹出拼写面板
- 点击错误商品 → 播放"不需要"语音
- 全部购齐 → 过渡回家再去森林
"""
import pygame
import random
from scenes.scene_base import SceneBase
from utils import asset_loader, audio_manager
from utils.asset_loader import get_font
from data.words_data import SHOPPING_ITEMS
from game_state import state
from components.spelling_panel import SpellingPanel
from components.dialogue_box import DialogueBox

W, H = 960, 540

# 干扰物品（中文名，点击时说"不需要"）
DECOYS = ["wallet", "palette", "book", "cookie", "wine"]

# 超市货架上的点击热区（相对960x540，按场景图5实际位置标定）
# pygame.Rect(left, top, width, height)，坐标来源：(left, right, top, bottom)
ITEM_ZONES = [
    pygame.Rect(470, 450, 40,  40),   # backpack  背包
    pygame.Rect(565, 524, 98,  41),   # apple     苹果
    pygame.Rect(427, 487, 26,  33),   # bandage   创可贴
    pygame.Rect(430, 450, 34,  38),   # bottle    水壶
    pygame.Rect(560, 481, 175, 39),   # cake      蛋糕
    pygame.Rect(385, 486, 40,  29),   # compass   指南针
    pygame.Rect(560, 434, 175, 46),   # lollipop  棒棒糖
    pygame.Rect(385, 516, 25,  46),   # umbrella  雨伞
]

# 干扰物品热区（点击播放"不需要"，顺序对应 DECOYS 列表）
DECOY_ZONES = [
    pygame.Rect(383, 450, 42,  35),   # palette  画板
    pygame.Rect(455, 491, 40,  29),   # wallet   钱包
    pygame.Rect(420, 521, 95,  44),   # book     书
    pygame.Rect(560, 403, 175, 29),   # cookie   饼干
    pygame.Rect(668, 521, 67,  44),   # wine     酒
]


class SceneSupermarket(SceneBase):
    def on_enter(self, **kwargs):
        audio_manager.play_bgm("主场景BGM.mp3")
        self._font  = get_font(22, bold=True)
        self._small = get_font(17)

        self._items = SHOPPING_ITEMS
        self._spelling: SpellingPanel | None = None
        self._dialogue = DialogueBox(None)

        # 已购买（从全局状态恢复，支持重进场景）
        # 注意：此处重置，让玩家每次进超市都需重新购买
        state.purchased = []

        self._wrong_flash_timer = 0.0
        self._wrong_flash_item = -1

    def _open_spelling(self, item_idx: int):
        item = self._items[item_idx]
        self._spelling = SpellingPanel(
            None, item["word"], item["image"],
            on_correct=lambda: self._on_correct(item["word"]),
            on_wrong=self._on_wrong_spell,
            colorblind_mode=state.colorblind_mode,
        )

    def _on_correct(self, word: str):
        if word not in state.purchased:
            state.purchased.append(word)
        audio_manager.play_voice("3超市/采购完成 母.mp3" if state.all_purchased else "3超市/采购完成 父.mp3")
        if state.all_purchased:
            self._dialogue.show(
                "Great job! We got everything! Let's head home!",
                speaker="Mom",
                on_done=self._go_home,
            )

    def _on_wrong_spell(self):
        audio_manager.play_voice("3超市/再试试 母.mp3")

    def _play_wrong(self):
        audio_manager.play_voice("3超市/不需要 母.mp3")
        self._dialogue.show("We don't need that!", speaker="Mom")

    def _go_home(self):
        # 先过渡"回家"，再从家出发去森林（SceneTransit 只支持单跳，故用两段）
        self.manager.switch("transit", fade=True,
                            image="7从超市回家.PNG",
                            next_scene="transit2")

    def update(self, dt):
        if self._spelling:
            self._spelling.update(dt)
            if self._spelling.done:
                self._spelling = None
                if state.all_purchased:
                    pygame.time.set_timer(pygame.USEREVENT + 10, 800, loops=1)
        self._dialogue.update(dt)
        if self._wrong_flash_timer > 0:
            self._wrong_flash_timer -= dt

    def handle_event(self, event):
        if event.type == pygame.USEREVENT + 10:
            self._go_home()
            return
        if self._spelling and not self._spelling.done:
            self._spelling.handle_event(event)
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            self._dialogue.handle_event(event)
            for i, zone in enumerate(ITEM_ZONES):
                if zone.collidepoint(pos):
                    item = self._items[i]
                    if item["word"] not in state.purchased:
                        self._open_spelling(i)
                    return
            for zone in DECOY_ZONES:
                if zone.collidepoint(pos):
                    self._play_wrong()
                    return

    def draw(self, screen):
        if self._dialogue:
            self._dialogue.screen = screen
        bg = asset_loader.get_image("5超市.PNG", (W, H))
        screen.blit(bg, (0, 0))

        # 已购买：在对应物品热区覆盖半透明绿色块
        for item, zone in zip(self._items, ITEM_ZONES):
            if item["word"] in state.purchased:
                overlay = pygame.Surface((zone.width, zone.height), pygame.SRCALPHA)
                overlay.fill((60, 200, 60, 160))
                screen.blit(overlay, (zone.x, zone.y))

        # 购买进度
        prog = self._small.render(
            f"Collected: {len(state.purchased)} / {len(self._items)}", True, (255, 255, 255)
        )
        prog_bg = pygame.Surface((prog.get_width() + 20, 30), pygame.SRCALPHA)
        prog_bg.fill((0, 0, 0, 140))
        screen.blit(prog_bg, (10, 10))
        screen.blit(prog, (20, 15))

        if self._spelling and not self._spelling.done:
            self._spelling.screen = screen
            self._spelling.draw(screen)

        self._dialogue.draw(screen)
