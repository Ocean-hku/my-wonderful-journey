"""全局游戏状态，场景间共享"""


class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        # 色盲模式: 'normal' / 'deuteranopia' / 'protanopia' / 'tritanopia'
        self.colorblind_mode: str = "normal"

        # 已购买物品列表（word字符串）
        self.purchased: list = []

        # 已互动动物列表（word字符串）
        self.interacted_animals: list = []

        # 挑战模式奖章 {word: 'gold'/'silver'/'bronze'/None}
        self.medals: dict = {}

        # 挑战模式分数
        self.challenge_score: int = 0
        self.challenge_total: int = 0

        # 音量
        self.bgm_volume: float = 0.5
        self.sfx_volume: float = 0.8

        # 当前选择的朗读者 'dad'/'mom'  (某些场景双声道)
        self.narrator: str = "mom"

    # ── 快捷属性 ──────────────────────────────────────────────
    @property
    def all_purchased(self) -> bool:
        return len(self.purchased) >= 8

    @property
    def all_interacted(self) -> bool:
        return len(self.interacted_animals) >= 9


# 全局单例
state = GameState()
