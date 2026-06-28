import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from metadata_tools import COPYRIGHT_NAME, get_create_time

_FONT_PATHS = [
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def _load_font(size):
    for path in _FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def apply_watermark(filepath):
    try:
        year = get_create_time(filepath).strftime("%Y")
    except Exception:
        year = str(datetime.now().year)

    text = f"© {year} {COPYRIGHT_NAME}"

    img = Image.open(filepath)
    img_format = img.format or "JPEG"
    exif_bytes = img.info.get("exif", b"")

    base = img.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    w, h = base.size
    font_size = max(14, w // 50)
    font = _load_font(font_size)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    padding = max(12, w // 80)

    x = w - text_w - padding
    y = h - text_h - padding

    stroke = max(1, font_size // 18)
    draw.text(
        (x, y), text, font=font,
        fill=(255, 255, 255, 220),
        stroke_width=stroke,
        stroke_fill=(0, 0, 0, 180),
    )

    result = Image.alpha_composite(base, overlay)

    save_kwargs = {}
    if exif_bytes:
        save_kwargs["exif"] = exif_bytes
    if img_format in ("JPEG", "WEBP"):
        result = result.convert("RGB")
        if img_format == "JPEG":
            save_kwargs["quality"] = 95

    result.save(filepath, img_format, **save_kwargs)
