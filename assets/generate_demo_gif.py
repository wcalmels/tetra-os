"""Generate TETRA OS demo GIF for README and GitHub."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 960, 540
FRAMES = 48
DURATION_MS = 90
OUT = Path(__file__).parent / "demo.gif"

BG_TOP = (102, 126, 234)
BG_BOT = (118, 75, 162)
TIER_COLORS = [
    (56, 189, 248, 220),
    (52, 211, 153, 220),
    (251, 191, 36, 220),
]
TIER_LABELS = [
    "Tier 1 — Base Optimization",
    "Tier 2 — Science Modules",
    "Tier 3 — Meta-Discovery",
]
TIER_SUB = [
    "GD · GA · PSO · SA · DE",
    "Drugs · Materials · Energy",
    "Laws · Algorithms · Meta³",
]


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_color(c1: tuple[int, ...], c2: tuple[int, ...], t: float) -> tuple[int, int, int]:
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def gradient_bg() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT))
    px = img.load()
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        col = lerp_color(BG_TOP, BG_BOT, t)
        for x in range(WIDTH):
            px[x, y] = col
    return img


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def ease_out(t: float) -> float:
    return 1 - (1 - t) ** 3


def draw_frame(frame_idx: int) -> Image.Image:
    t_global = frame_idx / (FRAMES - 1)
    base = gradient_bg().convert("RGBA")
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    title_font = font(46, bold=True)
    sub_font = font(18)
    tier_font = font(20, bold=True)
    small_font = font(14)

    # Title pulse
    pulse = 0.92 + 0.08 * math.sin(t_global * math.pi * 4)
    title = "TETRA OS"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text(
        ((WIDTH - tw) // 2, 28),
        title,
        fill=(255, 255, 255, int(255 * pulse)),
        font=title_font,
    )
    subtitle = "Self-Improving Scientific Discovery"
    sb = draw.textbbox((0, 0), subtitle, font=sub_font)
    sw = sb[2] - sb[0]
    draw.text(((WIDTH - sw) // 2, 82), subtitle, fill=(230, 230, 255, 220), font=sub_font)

    # Animated convergence curve (right side)
    cx0, cy0 = 560, 360
    cw, ch = 360, 150
    draw.rounded_rectangle(
        (cx0, cy0 - ch - 20, cx0 + cw, cy0 + 10),
        radius=14,
        fill=(255, 255, 255, 35),
        outline=(255, 255, 255, 70),
        width=2,
    )
    draw.text((cx0 + 16, cy0 - ch - 8), "Optimization convergence", fill=(255, 255, 255, 200), font=small_font)

    n_pts = 40
    xs = np.linspace(0, 1, n_pts)
    ys = np.exp(-3.5 * xs) + 0.02 * np.sin(xs * 18)
    visible = int(lerp(4, n_pts, ease_out(min(1.0, t_global * 1.4))))
    points = []
    for i in range(visible):
        x = cx0 + 20 + xs[i] * (cw - 40)
        y = cy0 - 15 - ys[i] * (ch - 30)
        points.append((x, y))
    if len(points) >= 2:
        draw.line(points, fill=(52, 211, 153, 255), width=3)
    if points:
        draw.ellipse(
            (points[-1][0] - 5, points[-1][1] - 5, points[-1][0] + 5, points[-1][1] + 5),
            fill=(251, 191, 36, 255),
        )
    metric = f"obj = {ys[min(visible - 1, n_pts - 1)]:.2e}"
    draw.text((cx0 + cw - 130, cy0 - 5), metric, fill=(52, 211, 153, 230), font=small_font)

    # Three tiers — sequential reveal
    box_w, box_h = 500, 72
    x0 = (WIDTH - box_w) // 2 - 40
    y_start = 145
    gap = 18

    for i, (label, sub, color) in enumerate(zip(TIER_LABELS, TIER_SUB, TIER_COLORS)):
        reveal = ease_out(max(0.0, min(1.0, (t_global - i * 0.18) / 0.45)))
        if reveal <= 0:
            continue
        y = y_start + i * (box_h + gap)
        slide = int((1 - reveal) * 40)
        alpha = int(color[3] * reveal)
        glow = int(90 * reveal)
        draw.rounded_rectangle(
            (x0 + slide, y, x0 + box_w + slide, y + box_h),
            radius=12,
            fill=(color[0], color[1], color[2], alpha),
            outline=(255, 255, 255, int(120 * reveal)),
            width=2,
        )
        draw.text((x0 + 18 + slide, y + 14), label, fill=(255, 255, 255, int(255 * reveal)), font=tier_font)
        draw.text((x0 + 18 + slide, y + 42), sub, fill=(240, 240, 255, int(200 * reveal)), font=small_font)

        # Connector line to next tier
        if i < 2 and reveal > 0.8:
            ly = y + box_h + 2
            draw.line(
                (x0 + box_w // 2 + slide, ly, x0 + box_w // 2 + slide, ly + gap - 4),
                fill=(255, 255, 255, int(160 * reveal)),
                width=2,
            )

    # Rotating particles
    for k in range(14):
        ang = t_global * math.pi * 2 + k * 0.45
        r = 120 + 18 * math.sin(t_global * 6 + k)
        px = WIDTH // 2 + math.cos(ang) * r
        py = HEIGHT // 2 + 40 + math.sin(ang) * r * 0.35
        rad = 3 + (k % 3)
        draw.ellipse(
            (px - rad, py - rad, px + rad, py + rad),
            fill=(255, 255, 255, int(50 + 40 * math.sin(t_global * 8 + k))),
        )

    # Footer
    footer = "Walter Calmels · github.com/wcalmels/tetra-os"
    fb = draw.textbbox((0, 0), footer, font=small_font)
    fw = fb[2] - fb[0]
    draw.text(((WIDTH - fw) // 2, HEIGHT - 34), footer, fill=(255, 255, 255, 170), font=small_font)

    return Image.alpha_composite(base, overlay).convert("P", palette=Image.Palette.ADAPTIVE)


def main() -> None:
    frames = [draw_frame(i) for i in range(FRAMES)]
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=DURATION_MS,
        loop=0,
        optimize=True,
    )
    size_kb = OUT.stat().st_size / 1024
    print(f"Created {OUT} ({size_kb:.0f} KB, {FRAMES} frames)")


if __name__ == "__main__":
    main()
