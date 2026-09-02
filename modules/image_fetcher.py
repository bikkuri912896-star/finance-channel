import hashlib
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
import config


def _gradient_path(seed: str) -> Path:
    h = hashlib.md5(seed.encode()).hexdigest()
    return config.IMAGE_CACHE_DIR / f"grad_{h}.jpg"


def _make_gradient(seed: str) -> Path:
    cache = _gradient_path(seed)
    if cache.exists():
        return cache

    rng = random.Random(seed)
    W, H = config.VIDEO_WIDTH, config.VIDEO_HEIGHT

    # Palette sets — professional finance look
    palettes = [
        [(8, 18, 38),  (12, 40, 80)],   # deep navy
        [(6, 30, 55),  (10, 60, 100)],  # midnight blue
        [(5, 20, 45),  (8, 45, 70)],    # dark ocean
        [(10, 18, 35), (20, 55, 90)],   # cobalt
    ]
    c1, c2 = rng.choice(palettes)

    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    # Vertical gradient
    for y in range(H):
        t = y / H
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Subtle grid lines — evoke financial charts
    grid_color = (255, 255, 255, 12)
    grid_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grid_draw = ImageDraw.Draw(grid_img)
    for x in range(0, W, 90):
        grid_draw.line([(x, 0), (x, H)], fill=grid_color, width=1)
    for y in range(0, H, 90):
        grid_draw.line([(0, y), (W, y)], fill=grid_color, width=1)
    img = Image.alpha_composite(img.convert("RGBA"), grid_img).convert("RGB")

    # Soft radial glow in upper-center
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gx, gy = W // 2, H // 3
    for r in range(400, 0, -20):
        alpha = max(0, int(30 * (1 - r / 400)))
        bbox = [gx - r, gy - r, gx + r, gy + r]
        ImageDraw.Draw(glow).ellipse(bbox, fill=(16, 185, 129, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

    config.IMAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    img.save(str(cache), "JPEG", quality=90)
    return cache


def fetch_images(topic: dict, count: int = 4) -> list[Path]:
    word = topic.get("word", "finance")
    paths = []
    for i in range(count):
        seed = f"{word}_{i}"
        p = _make_gradient(seed)
        if p:
            paths.append(p)
    return paths
