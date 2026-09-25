#!/usr/bin/env python3
"""Собирает обложку лендинга og-cover.png (1200×630) для соцсетей и мессенджеров.

    python3 make-cover.py --version 1.3.2 \
        --shot "/tmp/selfcrm-shots/dark/Главный экран (темный).png" \
        --out og-cover.png

Геометрия (совпадает с README, менять вместе с ним):
    * фон — вертикальный градиент от primary (#2563EB) к #0B1220;
    * телефон — 270×560 в точке (883, 35), внешнее скругление 26, рамка #27272A
      с обводкой #585860;
    * кадр приложения — 250×540 в точке (893, 45), скругление 17;
    * тексты — DejaVu Sans (есть кириллица), размеры подобраны по прежним обложкам.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1200, 630
GRADIENT_TOP = (37, 99, 235)     # --primary приложения
GRADIENT_BOTTOM = (11, 18, 32)   # #0B1220

FRAME = (883, 35, 270, 560, 26, (39, 39, 42), (88, 88, 96))
SHOT = (893, 45, 250, 540, 17)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Тексты: (x, y, текст, размер, шрифт, цвет). y — верх строки для draw.text.
LINES = [
    (75, 151, "SelfCRM", 75, FONT_BOLD, (255, 255, 255)),
    (75, 263, "Минималистичная личная CRM", 35, FONT_REGULAR, (219, 234, 254)),
    (75, 384, "Клиенты · Заказы · Товары · Склад", 26, FONT_BOLD, (255, 255, 255)),
    (75, 425, "Работает офлайн · Бесплатно · Открытый код", 24, FONT_REGULAR, (191, 219, 254)),
]


def gradient(width: int, height: int) -> Image.Image:
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / (height - 1)
        color = tuple(
            int(top + (bottom - top) * t)
            for top, bottom in zip(GRADIENT_TOP, GRADIENT_BOTTOM)
        )
        draw.line([(0, y), (width, y)], fill=color)
    return image


def rounded(image: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, image.size[0] - 1, image.size[1] - 1], radius=radius, fill=255)
    result = image.convert("RGBA")
    result.putalpha(mask)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Обложка SelfCRM 1200×630")
    parser.add_argument("--version", required=True, help="версия строкой, например 1.3.2")
    parser.add_argument("--shot", required=True, help="PNG главного экрана (любой размер)")
    parser.add_argument("--out", default="og-cover.png", help="куда сохранить обложку")
    args = parser.parse_args()

    cover = gradient(WIDTH, HEIGHT).convert("RGBA")

    # Телефон: рамка со скруглением, внутри — кадр главного экрана.
    x, y, box_w, box_h, frame_radius, frame_fill, frame_edge = FRAME
    draw = ImageDraw.Draw(cover)
    draw.rounded_rectangle(
        [x, y, x + box_w - 1, y + box_h - 1],
        radius=frame_radius,
        fill=frame_fill,
        outline=frame_edge,
        width=1,
    )

    shot_x, shot_y, shot_w, shot_h, shot_radius = SHOT
    shot = Image.open(args.shot).convert("RGB").resize((shot_w, shot_h), Image.LANCZOS)
    cover.alpha_composite(rounded(shot, shot_radius), (shot_x, shot_y))

    draw = ImageDraw.Draw(cover)
    lines = LINES + [(75, 486, f"v{args.version} · Android и Telegram", 22, FONT_REGULAR, (147, 197, 253))]
    for line_x, line_y, text, size, path, color in lines:
        draw.text((line_x, line_y), text, font=ImageFont.truetype(path, size), fill=color)

    out = Path(args.out)
    cover.convert("RGB").save(out, optimize=True)
    print(f"Готово: {out} ({out.stat().st_size} байт, {WIDTH}×{HEIGHT})")


if __name__ == "__main__":
    main()
