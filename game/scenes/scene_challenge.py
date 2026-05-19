"""
挑战模式：
- 3档难度：Easy(60s) / Medium(45s) / Hard(30s)
- 随机从17词抽10题
- 每题展示单词图片，玩家拼写
- 计分：60~100分=金，40~59=银，1~39=铜
- 奖章存入 state.medals
"""
import pygame
import random
from scenes.scene_base import SceneBase
from utils import asset_loader, audio_manager
from utils.asset_loader import get_font
from data.words_data import ALL_WORDS
from game_state import state
from components.spelling_panel import SpellingPanel

W, H = 960, 540

DIFFICULTY = {
    "Easy":   {"time": 60,  "label": "Easy   (60s)"},
    "Medium": {"time": 45,  "label": "Medium (45s)"},
    "Hard":   {"time": 30,  "label": "Hard   (30s)"},
}
DIFF_KEYS = ["Easy", "Medium", "Hard"]
TOTAL_Q = 10

PHASE_SELECT  = "select"
PHASE_PLAY    = "play"
PHASE_RESULT  = "result"


class SceneChallenge(SceneBase):
    def on_enter(self, **kwargs):
        audio_manager.play_bgm("主场景BGM.mp3")
        self._font   = get_font(30, bold=True)
        self._medium = get_font(22, bold=True)
        self._small  = get_font(18)

        self._phase = PHASE_SELECT
        self._diff  = "Easy"
        self._questions: list = []
        self._q_idx  = 0
        self._score  = 0
        self._time_left = 0.0
        self._spelling: SpellingPanel | None = None

        # 难度选择按钮
        self._diff_btns = {}
        for i, key in enumerate(DIFF_KEYS):
            self._diff_btns[key] = pygame.Rect(W // 2 - 140, 200 + i * 80, 280, 60)

        self.start_btn = pygame.Rect(W // 2 - 110, 460, 220, 54)
        self.back_btn  = pygame.Rect(20, 20, 110, 38)
        self.exit_btn  = pygame.Rect(20, 20, 110, 38)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self._phase == PHASE_SELECT:
                for key, rect in self._diff_btns.items():
                    if rect.collidepoint(pos):
                        self._diff = key
                        return
                if self.start_btn.collidepoint(pos):
                    self._start_game()
                    return
                if self.back_btn.collidepoint(pos):
                    self.manager.switch("living_room", fade=True)
                    return

            elif self._phase == PHASE_PLAY:
                if self._spelling and not self._spelling.done:
                    self._spelling.handle_event(event)

            elif self._phase == PHASE_RESULT:
                if self.exit_btn.collidepoint(pos):
                    self.manager.switch("living_room", fade=True)

    def _start_game(self):
        self._questions = random.sample(ALL_WORDS, TOTAL_Q)
        self._q_idx  = 0
        self._score  = 0
        self._time_left = float(DIFFICULTY[self._diff]["time"])
        self._pending_next = 0.0
        self._phase = PHASE_PLAY
        self._load_question()

    def _load_question(self):
        if self._q_idx >= len(self._questions):
            self._finish()
            return
        q = self._questions[self._q_idx]
        # 图片：优先高级图
        adv_img = q.get("challenge_img_adv", q.get("challenge_img", ""))
        self._spelling = SpellingPanel(
            None, q["word"], adv_img,
            on_correct=self._on_correct,
            on_wrong=lambda: None,
            colorblind_mode=state.colorblind_mode,
            challenge_mode=True,
        )
        audio_manager.play_voice(q["word_audio"])

    def _on_correct(self):
        self._score += 1
        self._q_idx += 1
        self._pending_next = 0.6   # 延迟0.6秒加载下一题

    def _finish(self):
        self._phase = PHASE_RESULT
        pct = self._score / TOTAL_Q * 100
        if pct >= 60:
            medal = "gold"
        elif pct >= 40:
            medal = "silver"
        elif pct >= 10:
            medal = "bronze"
        else:
            medal = None
        # 存入全局奖章（以本局最高分更新）
        for q in self._questions:
            old = state.medals.get(q["word"])
            ranks = [None, "bronze", "silver", "gold"]
            if medal and (old is None or ranks.index(medal) > ranks.index(old)):
                state.medals[q["word"]] = medal
        self._medal = medal
        state.challenge_score = self._score
        state.challenge_total = TOTAL_Q

    def update(self, dt):
        if self._phase == PHASE_PLAY:
            self._time_left -= dt
            if self._time_left <= 0:
                self._time_left = 0
                self._finish()
                return
            # 答对后延迟切题
            if self._pending_next > 0:
                self._pending_next -= dt
                if self._pending_next <= 0:
                    self._pending_next = 0
                    self._spelling = None
                    self._load_question()
                return
            if self._spelling:
                self._spelling.update(dt)
                if self._spelling.done and not self._pending_next:
                    # 超时未答，强制切下一题
                    self._q_idx += 1
                    self._spelling = None
                    self._load_question()

    def _poll_timer_event(self):
        return None

    def draw(self, screen):
        if self._phase == PHASE_SELECT:
            self._draw_select(screen)
        elif self._phase == PHASE_PLAY:
            self._draw_play(screen)
        elif self._phase == PHASE_RESULT:
            self._draw_result(screen)

    # ── 选择难度 ─────────────────────────────────────────────────
    def _draw_select(self, screen):
        screen.fill((20, 20, 50))
        t = self._font.render("Challenge Mode", True, (255, 220, 80))
        screen.blit(t, t.get_rect(center=(W // 2, 120)))
        sub = self._small.render("Spell 10 words as fast as you can!", True, (200, 200, 255))
        screen.blit(sub, sub.get_rect(center=(W // 2, 160)))

        for key, rect in self._diff_btns.items():
            selected = (self._diff == key)
            color = (80, 160, 240) if selected else (50, 80, 140)
            border = (200, 230, 255) if selected else (80, 100, 180)
            pygame.draw.rect(screen, color, rect, border_radius=20)
            pygame.draw.rect(screen, border, rect, 3, border_radius=20)
            lt = self._medium.render(DIFFICULTY[key]["label"], True, (255, 255, 255))
            screen.blit(lt, lt.get_rect(center=rect.center))

        # 开始
        pygame.draw.rect(screen, (80, 200, 100), self.start_btn, border_radius=27)
        pygame.draw.rect(screen, (30, 130, 50), self.start_btn, 3, border_radius=27)
        st = self._font.render("Start!", True, (255, 255, 255))
        screen.blit(st, st.get_rect(center=self.start_btn.center))

        # 返回
        pygame.draw.rect(screen, (180, 80, 80), self.back_btn, border_radius=10)
        bt = self._small.render("← Back", True, (255, 255, 255))
        screen.blit(bt, bt.get_rect(center=self.back_btn.center))

    # ── 答题中 ───────────────────────────────────────────────────
    def _draw_play(self, screen):
        if self._spelling and not self._spelling.done:
            self._spelling.screen = screen
            self._spelling.draw(screen)
        else:
            screen.fill((20, 20, 50))

        # HUD
        hud_bg = pygame.Surface((W, 46), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 160))
        screen.blit(hud_bg, (0, 0))

        t_time = self._small.render(f"Time: {int(self._time_left)}s", True, (255, 200, 80))
        screen.blit(t_time, (20, 12))

        t_q = self._small.render(
            f"Q {min(self._q_idx + 1, TOTAL_Q)} / {TOTAL_Q}  |  Score: {self._score}",
            True, (200, 230, 255)
        )
        screen.blit(t_q, t_q.get_rect(midright=(W - 20, 22)))

        # 时间条
        bar_w = int((self._time_left / DIFFICULTY[self._diff]["time"]) * (W - 40))
        bar_color = (80, 220, 80) if self._time_left > 15 else (220, 100, 80)
        pygame.draw.rect(screen, bar_color, pygame.Rect(20, 40, bar_w, 6), border_radius=3)

    # ── 结算 ─────────────────────────────────────────────────────
    def _draw_result(self, screen):
        screen.fill((20, 20, 50))

        t = self._font.render("Challenge Complete!", True, (255, 220, 80))
        screen.blit(t, t.get_rect(center=(W // 2, 100)))

        score_t = self._medium.render(
            f"Score: {self._score} / {TOTAL_Q}  ({int(self._score/TOTAL_Q*100)}%)",
            True, (200, 230, 255)
        )
        screen.blit(score_t, score_t.get_rect(center=(W // 2, 180)))

        # 奖章
        medal = getattr(self, "_medal", None)
        if medal == "gold":
            m_text, m_color = "★ GOLD MEDAL ★",    (255, 215, 0)
        elif medal == "silver":
            m_text, m_color = "☆ SILVER MEDAL ☆", (192, 192, 210)
        elif medal == "bronze":
            m_text, m_color = "◆ BRONZE MEDAL ◆", (205, 127, 50)
        else:
            m_text, m_color = "Keep Trying!",       (180, 180, 180)

        big = get_font(44, bold=True)
        mt = big.render(m_text, True, m_color)
        screen.blit(mt, mt.get_rect(center=(W // 2, 280)))

        # 返回按钮
        pygame.draw.rect(screen, (80, 140, 220), self.exit_btn, border_radius=10)
        et = self._small.render("← Back", True, (255, 255, 255))
        screen.blit(et, et.get_rect(center=self.exit_btn.center))
