import io
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from PIL import Image, ImageDraw, ImageFont
from .verdict import calculate_verdict


def _font(size):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


@login_required
def verdict_image(request):
    v = calculate_verdict(request.user)
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), "#0f172a")
    draw = ImageDraw.Draw(img)

    # градиентная полоса снизу
    for i in range(H - 20, H):
        t = (i - (H - 20)) / 20
        color = (
            int(124 * (1 - t) + 13 * t),
            int(58 * (1 - t) + 148 * t),
            int(237 * (1 - t) + 136 * t),
        )
        draw.rectangle([0, i, W, i + 1], fill=color)

    draw.text((60, 60), "MoodMap", font=_font(48), fill="#94a3b8")
    draw.text((60, 160), f"Я на {v['percent']}%", font=_font(72), fill="#e2e8f0")
    # обрезаем длинный текст вердикта по словам
    words = v["text"].split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > 40:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    y = 280
    for line in lines[:4]:
        draw.text((60, y), line, font=_font(36), fill="#cbd5e1")
        y += 50

    stats = f"Мест: {v['places_count']}  •  Дней: {v['unique_days']}  •  Средний балл: {v['avg_mood']}"
    draw.text((60, H - 100), stats, font=_font(28), fill="#94a3b8")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return HttpResponse(buf.getvalue(), content_type="image/png")