"""
一次性资源同步脚本
将 ../场景图/*.PNG 复制到 assets/images/
将 ../音频/**/*.mp3 复制到 assets/audio/（保留子目录结构）
并生成占位音效文件（correct.mp3 / wrong.mp3）

运行方式：
    python setup_assets.py
"""
import os
import shutil

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
GAME_ROOT   = os.path.dirname(SCRIPT_DIR)    # 游戏/
SRC_IMAGES  = os.path.join(GAME_ROOT, "场景图")
SRC_AUDIO   = os.path.join(GAME_ROOT, "音频")
DST_IMAGES  = os.path.join(SCRIPT_DIR, "assets", "images")
DST_AUDIO   = os.path.join(SCRIPT_DIR, "assets", "audio")

os.makedirs(DST_IMAGES, exist_ok=True)
os.makedirs(DST_AUDIO,  exist_ok=True)


def sync_images():
    count = 0
    for f in os.listdir(SRC_IMAGES):
        if f.upper().endswith(".PNG"):
            src = os.path.join(SRC_IMAGES, f)
            dst = os.path.join(DST_IMAGES, f)
            if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
                shutil.copy2(src, dst)
                count += 1
    print(f"[Images] Synced {count} file(s) → {DST_IMAGES}")


def sync_audio():
    """将音频目录树复制到 assets/audio/，保留子目录"""
    count = 0
    # 根目录的 mp3
    for f in os.listdir(SRC_AUDIO):
        fp = os.path.join(SRC_AUDIO, f)
        if os.path.isfile(fp) and f.lower().endswith(".mp3"):
            dst = os.path.join(DST_AUDIO, f)
            if not os.path.exists(dst) or os.path.getmtime(fp) > os.path.getmtime(dst):
                shutil.copy2(fp, dst)
                count += 1

    # 子目录递归
    for root, dirs, files in os.walk(SRC_AUDIO):
        rel = os.path.relpath(root, SRC_AUDIO)
        dst_dir = os.path.join(DST_AUDIO, rel) if rel != "." else DST_AUDIO
        os.makedirs(dst_dir, exist_ok=True)
        for f in files:
            if f.lower().endswith(".mp3"):
                src = os.path.join(root, f)
                dst = os.path.join(dst_dir, f)
                if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
                    shutil.copy2(src, dst)
                    count += 1

    print(f"[Audio]  Synced {count} file(s) → {DST_AUDIO}")


def create_word_audio_symlinks():
    """将 采购清单-单词发音/*.mp3 同时复制到 assets/audio/word/ 便于统一路径"""
    word_src = os.path.join(SRC_AUDIO, "2采购清单", "采购清单-单词发音")
    word_dst = os.path.join(DST_AUDIO, "word")
    os.makedirs(word_dst, exist_ok=True)
    count = 0
    if os.path.isdir(word_src):
        for f in os.listdir(word_src):
            if f.lower().endswith(".mp3"):
                src = os.path.join(word_src, f)
                dst = os.path.join(word_dst, f)
                if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
                    shutil.copy2(src, dst)
                    count += 1
    print(f"[Word audio] {count} file(s) → {word_dst}")


def create_placeholder_sfx():
    """用 numpy+wave 生成简单音效占位文件"""
    sfx_dir = os.path.join(DST_AUDIO, "sfx")
    os.makedirs(sfx_dir, exist_ok=True)
    try:
        import numpy as np
        import wave, struct

        def make_tone(path, freq=880, duration=0.15, volume=0.4):
            if os.path.exists(path):
                return
            sample_rate = 44100
            n = int(sample_rate * duration)
            t = [i / sample_rate for i in range(n)]
            # 简单正弦 + 淡出
            samples = []
            for i, ti in enumerate(t):
                fade = 1.0 - i / n
                val = int(volume * fade * 32767 * (
                    __import__("math").sin(2 * __import__("math").pi * freq * ti)
                ))
                samples.append(val)
            with wave.open(path, "w") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(struct.pack(f"<{n}h", *samples))

        make_tone(os.path.join(sfx_dir, "correct.mp3"), freq=1047, duration=0.2)  # C6
        make_tone(os.path.join(sfx_dir, "wrong.mp3"),   freq=220,  duration=0.2)  # A3
        print("[SFX]    Placeholder sfx created (WAV in .mp3 container)")
    except Exception as e:
        print(f"[SFX]    Skipped placeholder sfx: {e}")


if __name__ == "__main__":
    print("=== Asset Setup ===")
    sync_images()
    sync_audio()
    create_word_audio_symlinks()
    create_placeholder_sfx()
    print("=== Done. Run:  python main.py ===")
