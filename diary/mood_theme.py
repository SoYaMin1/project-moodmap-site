"""
Определяет визуальную тему сайта в зависимости от того,
насколько юзер путешественник и насколько он счастлив.
"""


def get_theme(entries):
    """
    entries: список Entry (уже с select_related('mood')).
    Возвращает dict с параметрами темы для шаблона.
    """
    count = len(entries)
    if count == 0:
        return {
            "level": "empty",
            "avg": 0,
            "sun": False,
            "clouds": True,
            "birds": False,
            "label": "Начни отмечать места — и небо оживёт ✨",
        }

    avg = sum(e.mood.score for e in entries) / count

    # ПРАВИЛО: если средний балл >= 6 — появляется солнце и птицы
    sun = avg >= 6
    birds = avg >= 6 and count >= 5
    clouds = True

    if count < 5 and avg < 5:
        level = "homebody"
        label = "🏠 Уютный домосед — небо тихое, облака мягкие"
    elif avg < 6:
        level = "balanced"
        label = "🌤️ Ты где-то посередине: ценишь и дом, и дорогу"
    else:
        level = "traveler"
        label = "☀️ Ты путешественник! Небо светит для тебя"

    return {
        "level": level,
        "avg": round(avg, 1),
        "sun": sun,
        "clouds": clouds,
        "birds": birds,
        "label": label,
    }