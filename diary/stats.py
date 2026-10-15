from datetime import timedelta
from django.core.cache import cache
from django.db.models import Count, Avg
from django.utils import timezone
from .models import Entry


def _range_from_param(param):
    today = timezone.localdate()
    if param == "week":
        return today - timedelta(days=7)
    if param == "month":
        return today - timedelta(days=30)
    if param == "year":
        return today - timedelta(days=365)
    return None  # всё


def get_stats(user, period="all"):
    key = f"stats:{user.id}:{period}"
    cached = cache.get(key)
    if cached:
        return cached

    start = _range_from_param(period)
    qs = Entry.objects.filter(user=user)
    if start:
        qs = qs.filter(date__gte=start)

    # ── KPI
    kpi_qs = qs.aggregate(total=Count("id"), avg=Avg("mood__score"))
    unique_days = qs.values("date").distinct().count()

    # ── 1. Линия: score по дням (группируем напрямую по DateField)
    line = list(
        qs.values("date")
        .annotate(avg=Avg("mood__score"), cnt=Count("id"))
        .order_by("date")
    )

    # ── 2. Doughnut: распределение оценок
    dist = list(
        qs.values("mood__score", "mood__emoji", "mood__name", "mood__color")
        .annotate(cnt=Count("id"))
        .order_by("mood__score")
    )

    # ── 3. Bar по дням
    days = list(
        qs.values("date")
        .annotate(cnt=Count("id"))
        .order_by("date")
    )

    # ── 4. Точки для карты
    points = list(
        qs.values(
            "id", "latitude", "longitude", "date",
            "mood__score", "mood__emoji", "mood__color",
            "title", "note",
        )
    )

    data = {
        "kpi": {
            "total": kpi_qs["total"] or 0,
            "avg": round(kpi_qs["avg"] or 0, 1),
            "unique_days": unique_days,
        },
        "line": [
            {"date": r["date"].isoformat(), "avg": r["avg"], "cnt": r["cnt"]}
            for r in line
        ],
        "distribution": [
            {
                "score": r["mood__score"],
                "emoji": r["mood__emoji"],
                "name": r["mood__name"],
                "color": r["mood__color"],
                "cnt": r["cnt"],
            }
            for r in dist
        ],
        # ключ называется "months" для совместимости с charts.js,
        # но содержит по дням: {"month": "2026-10-15", "cnt": 3}
        "months": [
            {"month": r["date"].isoformat(), "cnt": r["cnt"]}
            for r in days
        ],
        "points": [
            {
                **{k: v for k, v in p.items() if k != "date"},
                "date": p["date"].isoformat(),
            }
            for p in points
        ],
    }

    cache.set(key, data, 300)
    return data


def invalidate_user_cache(user):
    for p in ("week", "month", "year", "all"):
        cache.delete(f"stats:{user.id}:{p}")