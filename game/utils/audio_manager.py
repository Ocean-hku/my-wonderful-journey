"""音频管理器：BGM切换、音效、单词发音"""
import pygame
import os
from utils.asset_loader import get_audio_path

pygame.mixer.pre_init(44100, -16, 2, 512)

_current_bgm: str = ""
_sfx_cache: dict = {}
_voice_channel: pygame.mixer.Channel = None


def init():
    global _voice_channel
    pygame.mixer.init()
    pygame.mixer.set_num_channels(8)
    _voice_channel = pygame.mixer.Channel(7)


def play_bgm(filename: str, loops=-1):
    """filename 相对于 assets/audio/"""
    global _current_bgm
    if filename == _current_bgm:
        return
    path = get_audio_path(filename)
    if not os.path.exists(path):
        return
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(loops)
    _current_bgm = filename


def stop_bgm():
    global _current_bgm
    pygame.mixer.music.stop()
    _current_bgm = ""


def play_sfx(filename: str, volume=0.8):
    """播放音效，filename 相对于 assets/audio/"""
    path = get_audio_path(filename)
    if not os.path.exists(path):
        _beep(filename)
        return
    if path not in _sfx_cache:
        _sfx_cache[path] = pygame.mixer.Sound(path)
    snd = _sfx_cache[path]
    snd.set_volume(volume)
    snd.play()


def play_voice(filename: str, volume=1.0):
    """在专属语音通道播放，可打断上一条语音"""
    global _voice_channel
    if _voice_channel is None:
        return
    path = get_audio_path(filename)
    if not os.path.exists(path):
        return
    if path not in _sfx_cache:
        _sfx_cache[path] = pygame.mixer.Sound(path)
    snd = _sfx_cache[path]
    snd.set_volume(volume)
    _voice_channel.stop()
    _voice_channel.play(snd)


def is_voice_playing() -> bool:
    if _voice_channel is None:
        return False
    return _voice_channel.get_busy()


def _beep(tag=""):
    """无音频文件时生成简单提示音"""
    try:
        import numpy as np
        sample_rate = 44100
        freq = 880 if "correct" in tag else 440
        t = np.linspace(0, 0.15, int(sample_rate * 0.15), endpoint=False)
        wave = (np.sin(2 * np.pi * freq * t) * 16000).astype(np.int16)
        stereo = np.column_stack([wave, wave])
        snd = pygame.sndarray.make_sound(stereo)
        snd.set_volume(0.3)
        snd.play()
    except Exception:
        pass
