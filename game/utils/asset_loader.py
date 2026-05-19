"""统一资源加载器，带缓存，所有图片统一从 assets/images/ 读取"""
import pygame
import os

_cache: dict = {}
_font_cache: dict = {}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, "assets", "images")
AUDIO_DIR  = os.path.join(BASE_DIR, "assets", "audio")

# 尝试找到系统中可用的中英文字体文件，避免使用 SysFont（Python3.13 有 bug）
def _find_font_file() -> str | None:
    candidates = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\tahoma.ttf",
        r"C:\Windows\Fonts\verdana.ttf",
        r"C:\Windows\Fonts\msyh.ttc",   # 微软雅黑
        r"C:\Windows\Fonts\simsun.ttc",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

_FONT_FILE = _find_font_file()

def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    """获取缓存字体，兼容 Python 3.13 + pygame 2.6（避免 SysFont bug）"""
    key = (size, bold)
    if key not in _font_cache:
        if _FONT_FILE:
            f = pygame.font.Font(_FONT_FILE, size)
            f.bold = bold
        else:
            f = pygame.font.Font(None, size)  # pygame 内置位图字体
        _font_cache[key] = f
    return _font_cache[key]

def get_image(filename: str, size=None) -> pygame.Surface:
    """加载并缓存图片。filename 可含子目录，如 'bg_title.png'"""
    key = (filename, size)
    if key not in _cache:
        path = os.path.join(IMAGES_DIR, filename)
        if not os.path.exists(path):
            # 生成纯色占位图
            surf = pygame.Surface(size or (960, 540))
            surf.fill((40, 40, 60))
            font = get_font(20)
            label = font.render(f"[{filename}]", True, (200, 200, 200))
            surf.blit(label, (10, 10))
            _cache[key] = surf
            return surf
        surf = pygame.image.load(path).convert_alpha()
        if size:
            surf = pygame.transform.scale(surf, size)
        _cache[key] = surf
    return _cache[key]

def get_audio_path(relative: str) -> str:
    """返回音频文件的完整路径"""
    return os.path.join(AUDIO_DIR, relative)

def clear_cache():
    _cache.clear()
