from math import radians, sin, cos, asin, sqrt
from django.db.models import Avg
from django.core.cache import cache
from .models import Entry

EARTH_R = 6371.0


def _haversine(lat1, lon1, lat2, lon2):
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * EARTH_R * asin(sqrt(a))


def calculate_geo_spread(entries):
    """Максимальная дистанция между любыми двумя точками (по центрам)."""
    pts = [(e.latitude, e.longitude) for e in entries]
    if len(pts) < 2:
        return 0.0
    # bounding-box хаба: сравним каждую точку с "центром масс"
    lat_c = sum(p[0] for p in pts) / len(pts)
    lon_c = sum(p[1] for p in pts) / len(pts)
    return max(_haversine(lat_c, lon_c, la, lo) for la, lo in pts) * 2


def calculate_verdict(user):
    entries = list(Entry.objects.filter(user=user).select_related("mood"))
    places_count = len(entries)
    unique_days = len({e.date for e in entries})
    avg_mood = (
        sum(e.mood.score for e in entries) / places_count if places_count else 0
    )
    geo_spread = calculate_geo_spread(entries)

    if places_count > 30 and geo_spread > 100:
        text = "🧭 Ты настоящий путешественник! Тебе мало одного города."
        pct = min(100, 60 + places_count // 2)
    elif places_count > 10 and avg_mood >= 7:
        text = "😄 Ты любишь открывать новое, и оно отвечает тебе взаимностью."
        pct = min(100, 50 + int(avg_mood * 3))
    elif places_count < 5 and avg_mood < 5:
        text = "🏠 Похоже, ты домосед. И это тоже классно — уют важнее."
        pct = 30
    else:
        text = "🙂 Ты где-то посередине: ценишь и дом, и дорогу."
        pct = 55

    return {
        "text": text,
        "percent": pct,
        "places_count": places_count,
        "unique_days": unique_days,
        "avg_mood": round(avg_mood, 1),
        "geo_spread": round(geo_spread, 1),
    }


def favourite_place(user):
    e = (
        Entry.objects.filter(user=user)
        .select_related("mood")
        .order_by("-mood__score", "-date")
        .first()
    )
    return e


def happiest_month(user):
    from django.db.models.functions import TruncMonth
    row = (
        Entry.objects.filter(user=user)
        .annotate(m=TruncMonth("date"))
        .values("m")
        .annotate(avg=Avg("mood__score"))
        .order_by("-avg")
        .first()
    )
    return row


def streak_days(user):
    """Сколько дней подряд (включая сегодня/вчера) идут записи."""
    from datetime import timedelta
    from django.utils import timezone
    dates = set(
        Entry.objects.filter(user=user).values_list("date", flat=True).distinct()
    )
    if not dates:
        return 0
    today = timezone.localdate()
    start = today if today in dates else today - timedelta(days=1)
    if start not in dates:
        return 0
    n, cur = 0, start
    while cur in dates:
        n += 1
        cur -= timedelta(days=1)
    return n