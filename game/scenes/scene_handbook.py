"""第四幕：旅行手册 —— 3页翻页，每页介绍3只动物，翻完后出发"""
import pygame
from scenes.scene_base import SceneBase
from utils import asset_loader, audio_manager
from utils.asset_loader import get_font
from data.words_data import FOREST_ANIMALS
from components.dialogue_box import DialogueBox

W, H = 960, 540

# 手册3页，每页3只动物
HANDBOOK_PAGES = [
    FOREST_ANIMALS[0:3],   # fox, horse, pig
    FOREST_ANIMALS[3:6],   # sheep, elephant, tiger
    FOREST_ANIMALS[6:9],   # parrot, giraffe, monkey
]
PAGE_IMAGES = ["9动物手册.PNG", "10动物手册.PNG", "11动物手册.PNG"]


class SceneHandbook(SceneBase):
    def on_enter(self, **kwargs):
        audio_manager.play_bgm("主场景BGM.mp3")
        self._font   = get_font(28, bold=True)
        self._small  = get_font(18)
        self._medium = get_font(22)

        self._page = 0          # 0~2
        self._anim_offset = 0   # 翻页动画偏移（像素，向左滑出）
        self._animating = False
        self._anim_dir = 1      # 1=向右翻 -1=向左
        self._anim_timer = 0.0
        ANIM_DUR = 0.3
        self._anim_dur = ANIM_DUR

        self._dialogue = DialogueBox(None)

        # 导航按钮
        self.prev_btn = pygame.Rect(30, H // 2 - 28, 56, 56)
        self.next_btn = pygame.Rect(W - 86, H // 2 - 28, 56, 56)
        self.go_btn   = pygame.Rect(W // 2 - 100, H - 72, 200, 52)

        # 每页3个动物发音按钮
        self.animal_sound_btns = [
            pygame.Rect(140 + i * 240, H - 130, 120, 36)
            for i in range(3)
        ]

        self._show_page(0)

    def _show_page(self, page):
        self._page = page
        animals = HANDBOOK_PAGES[page]
        lines = []
        for a in animals:
            lines.append({
                "text": f'{a["word"].upper()} - {a["zh"]}',
                "speaker": "Handbook",
            })
        self._dialogue.show_sequence(lines)
        # 自动播放第一只动物的手册语音
        audio_manager.play_voice(animals[0]["handbook_audio"])

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            self._dialogue.handle_event(event)

            if self._animating:
                return

            # 上一页
            if self.prev_btn.collidepoint(pos) and self._page > 0:
                self._start_anim(-1, self._page - 1)
                return

            # 下一页（未到末页）
            if self.next_btn.collidepoint(pos) and self._page < len(HANDBOOK_PAGES) - 1:
                self._start_anim(1, self._page + 1)
                return

            # 动物发音按钮
            animals = HANDBOOK_PAGES[self._page]
            for i, btn in enumerate(self.animal_sound_btns):
                if btn.collidepoint(pos) and i < len(animals):
                    audio_manager.play_voice(animals[i]["handbook_audio"])
                    audio_manager.play_voice(animals[i]["word_audio"])
                    return

            # 出发按钮（最后一页）
            if self._page == len(HANDBOOK_PAGES) - 1:
                if self.go_btn.collidepoint(pos):
                    audio_manager.play_voice("4森林动物手册/出发 父.mp3")
                    self.manager.switch("forest", fade=True)

    def _start_anim(self, direction, next_page):
        self._animating = True
        self._anim_dir = direction
        self._anim_timer = 0.0
        self._next_page = next_page

    def update(self, dt):
        self._dialogue.update(dt)
        if self._animating:
            self._anim_timer += dt
            if self._anim_timer >= self._anim_dur:
                self._animating = False
                self._show_page(self._next_page)

    def draw(self, screen):
        self._dialogue.screen = screen

        # 翻页滑动效果
        if self._animating:
            progress = self._anim_timer / self._anim_dur
            offset = int(self._anim_dir * W * progress)
            # 当前页滑出
            bg_cur = asset_loader.get_image(PAGE_IMAGES[self._page], (W, H))
            screen.blit(bg_cur, (-offset, 0))
            # 下一页滑入
            bg_next = asset_loader.get_image(PAGE_IMAGES[self._next_page], (W, H))
            screen.blit(bg_next, (W * self._anim_dir - offset, 0))
        else:
            bg = asset_loader.get_image(PAGE_IMAGES[self._page], (W, H))
            screen.blit(bg, (0, 0))

        # 页码
        pt = self._small.render(f"Page {self._page + 1} / {len(HANDBOOK_PAGES)}", True, (255, 255, 255))
        screen.blit(pt, pt.get_rect(center=(W // 2, 22)))

        # 动物卡片（每页3个）
        animals = HANDBOOK_PAGES[self._page]
        for i, a in enumerate(animals):
            x_center = 160 + i * 240
            # 名称
            wt = self._font.render(a["word"].upper(), True, (255, 255, 255))
            shadow = self._font.render(a["word"].upper(), True, (0, 0, 0))
            screen.blit(shadow, shadow.get_rect(center=(x_center + 2, 82)))
            screen.blit(wt, wt.get_rect(center=(x_center, 80)))
            # 中文
            zt = self._small.render(a["zh"], True, (255, 230, 150))
            screen.blit(zt, zt.get_rect(center=(x_center, 108)))
            # 发音按钮
            btn = self.animal_sound_btns[i]
            pygame.draw.rect(screen, (100, 180, 255), btn, border_radius=18)
            pygame.draw.rect(screen, (40, 100, 200), btn, 2, border_radius=18)
            st = self._small.render("🔊 Listen", True, (20, 20, 80))
            screen.blit(st, st.get_rect(center=btn.center))

        # 翻页按钮
        if self._page > 0:
            self._draw_arrow(screen, self.prev_btn, "◀")
        if self._page < len(HANDBOOK_PAGES) - 1:
            self._draw_arrow(screen, self.next_btn, "▶")

        # 出发按钮（最后一页）
        if self._page == len(HANDBOOK_PAGES) - 1:
            pygame.draw.rect(screen, (80, 200, 100), self.go_btn, border_radius=26)
            pygame.draw.rect(screen, (30, 120, 50), self.go_btn, 3, border_radius=26)
            gt = get_font(24, bold=True).render("Let's Go! →", True, (255, 255, 255))
            screen.blit(gt, gt.get_rect(center=self.go_btn.center))

        self._dialogue.draw(screen)

    def _draw_arrow(self, screen, rect, label):
        mouse = pygame.mouse.get_pos()
        color = (200, 220, 255) if rect.collidepoint(mouse) else (160, 180, 230)
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, (80, 100, 180), rect, 2, border_radius=10)
        font = get_font(28, bold=True)
        t = font.render(label, True, (40, 40, 120))
        screen.blit(t, t.get_rect(center=rect.center))
