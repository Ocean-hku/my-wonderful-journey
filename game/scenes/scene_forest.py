"""
第五幕：森林动物交互
- 9只动物依次出现，点击动物 → 父母提示对话 → 拼写测试 → 动物台词 → 下一只
- 全部互动完成 → 结算画面
"""
import pygame
from scenes.scene_base import SceneBase
from utils import asset_loader, audio_manager
from utils.asset_loader import get_font
from data.words_data import FOREST_ANIMALS
from game_state import state
from components.spelling_panel import SpellingPanel
from components.dialogue_box import DialogueBox

W, H = 960, 540

# 动物点击区域（依次排列，可微调）
ANIMAL_CLICK_ZONES = [
    pygame.Rect(60,  160, 140, 160),   # fox
    pygame.Rect(220, 160, 140, 160),   # horse
    pygame.Rect(380, 160, 140, 160),   # pig
    pygame.Rect(540, 160, 140, 160),   # sheep
    pygame.Rect(700, 160, 140, 160),   # elephant
    pygame.Rect(60,  330, 140, 160),   # tiger
    pygame.Rect(220, 330, 140, 160),   # parrot
    pygame.Rect(380, 330, 140, 160),   # giraffe
    pygame.Rect(540, 330, 140, 160),   # monkey
]

PHASE_IDLE     = "idle"
PHASE_DIALOGUE = "dialogue"
PHASE_SPELLING = "spelling"
PHASE_ANIMAL   = "animal_lines"


class SceneForest(SceneBase):
    def on_enter(self, **kwargs):
        audio_manager.play_bgm("5森林动物交互/森林场景BGM.mp3")
        self._font  = get_font(22, bold=True)
        self._small = get_font(17)

        self._animals = FOREST_ANIMALS
        state.interacted_animals = []

        self._current_idx  = -1   # 当前交互的动物下标
        self._phase = PHASE_IDLE
        self._frame = 0            # 当前动物帧
        self._frame_timer = 0.0
        self._line_idx = 0         # 动物台词下标

        self._spelling: SpellingPanel | None = None
        self._dialogue = DialogueBox(None)

        self._all_done = False
        self._done_timer = 0.0

    def handle_event(self, event):
        if self._all_done:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self._phase == PHASE_DIALOGUE:
                self._dialogue.handle_event(event)
                return

            if self._phase == PHASE_ANIMAL:
                self._dialogue.handle_event(event)
                return

            if self._phase == PHASE_IDLE:
                for i, zone in enumerate(ANIMAL_CLICK_ZONES):
                    if zone.collidepoint(pos):
                        animal = self._animals[i]
                        if animal["word"] not in state.interacted_animals:
                            self._start_interaction(i)
                        return

        if self._phase == PHASE_SPELLING and self._spelling:
            self._spelling.handle_event(event)

    def _start_interaction(self, idx: int):
        self._current_idx = idx
        self._frame = 0
        self._phase = PHASE_DIALOGUE
        animal = self._animals[idx]

        # 父母提示对话
        intro = animal["interact_audio"]
        voice = intro.get("mom") or intro.get("dad")
        if voice:
            audio_manager.play_voice(voice)

        self._dialogue.show_sequence([
            {"text": f'Look! It\'s a {animal["word"].upper()}! Can you spell it?',
             "speaker": "Mom"},
        ], on_done=self._start_spelling)

    def _start_spelling(self):
        animal = self._animals[self._current_idx]
        self._phase = PHASE_SPELLING
        self._spelling = SpellingPanel(
            None, animal["word"], animal["frames"][0],
            on_correct=self._on_correct,
            on_wrong=self._on_wrong,
            colorblind_mode=state.colorblind_mode,
        )

    def _on_correct(self):
        animal = self._animals[self._current_idx]
        if animal["word"] not in state.interacted_animals:
            state.interacted_animals.append(animal["word"])
        self._phase = PHASE_ANIMAL
        self._line_idx = 0
        self._play_animal_line()

    def _on_wrong(self):
        audio_manager.play_voice("3超市/再试试 母.mp3")

    def _play_animal_line(self):
        animal = self._animals[self._current_idx]
        lines = animal.get("animal_lines", [])
        if self._line_idx < len(lines):
            audio_manager.play_voice(lines[self._line_idx])
            self._dialogue.show(
                f"({animal['zh']} says something...)",
                speaker=animal["zh"],
                on_done=self._next_line,
            )
        else:
            self._finish_interaction()

    def _next_line(self):
        self._line_idx += 1
        self._play_animal_line()

    def _finish_interaction(self):
        self._phase = PHASE_IDLE
        self._current_idx = -1
        self._spelling = None
        if state.all_interacted:
            audio_manager.play_voice("5森林动物交互/森林旅行结束 母.mp3")
            self._all_done = True
            self._done_timer = 3.0

    def update(self, dt):
        self._dialogue.update(dt)
        if self._spelling:
            self._spelling.update(dt)
            if self._spelling.done and self._phase == PHASE_SPELLING:
                # 拼写完成（correct回调已处理）
                pass

        # 当前动物帧动画
        if self._current_idx >= 0 and self._phase != PHASE_IDLE:
            self._frame_timer += dt
            if self._frame_timer >= 0.4:
                self._frame_timer = 0.0
                animal = self._animals[self._current_idx]
                self._frame = (self._frame + 1) % len(animal["frames"])

        if self._all_done:
            self._done_timer -= dt
            if self._done_timer <= 0:
                self.manager.switch("result", fade=True)

    def draw(self, screen):
        self._dialogue.screen = screen

        # 森林背景（用第一只动物的第1帧作为背景底图）
        # 实际主背景是第五幕的框架图，这里复用最后一个动物的帧作背景示意
        # 具体位置由各动物帧图本身决定
        bg = asset_loader.get_image("8从家去森林.PNG", (W, H))
        screen.blit(bg, (0, 0))

        # 绘制每只动物（已互动的显示正确帧，未互动显示第1帧）
        for i, (animal, zone) in enumerate(zip(self._animals, ANIMAL_CLICK_ZONES)):
            interacted = animal["word"] in state.interacted_animals
            is_active  = (i == self._current_idx)

            if is_active:
                frame_img = animal["frames"][self._frame]
            else:
                frame_img = animal["frames"][0]

            img = asset_loader.get_image(frame_img, (zone.width, zone.height))
            screen.blit(img, zone.topleft)

            # 已互动打勾
            if interacted and not is_active:
                font = get_font(28)
                check = font.render("✓", True, (60, 220, 60))
                screen.blit(check, (zone.right - 24, zone.top))
            elif not interacted:
                # 未互动闪烁边框提示
                pygame.draw.rect(screen, (255, 230, 80), zone, 2, border_radius=8)

        # 进度
        prog_t = self._small.render(
            f"Animals met: {len(state.interacted_animals)} / {len(self._animals)}",
            True, (255, 255, 255)
        )
        prog_bg = pygame.Surface((prog_t.get_width() + 20, 28), pygame.SRCALPHA)
        prog_bg.fill((0, 0, 0, 140))
        screen.blit(prog_bg, (10, 10))
        screen.blit(prog_t, (20, 14))

        # 当前动物大图（交互中）
        if self._current_idx >= 0 and self._phase in (PHASE_DIALOGUE, PHASE_ANIMAL):
            animal = self._animals[self._current_idx]
            big_img = asset_loader.get_image(animal["frames"][self._frame], (380, 340))
            screen.blit(big_img, big_img.get_rect(center=(W // 2, H // 2 - 30)))

        if self._spelling and not self._spelling.done and self._phase == PHASE_SPELLING:
            self._spelling.screen = screen
            animal = self._animals[self._current_idx]
            self._spelling.bg_image = animal["frames"][0]
            self._spelling.draw(screen)

        self._dialogue.draw(screen)

        if self._all_done:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(min(180, (3.0 - self._done_timer) / 3.0 * 200))))
            screen.blit(overlay, (0, 0))
            font = get_font(40, bold=True)
            t = font.render("What a wonderful journey!", True, (255, 240, 120))
            screen.blit(t, t.get_rect(center=(W // 2, H // 2)))
