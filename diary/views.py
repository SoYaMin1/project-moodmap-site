from django.shortcuts import render

# Create your views here.
import json
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Entry, Mood
from .verdict import calculate_verdict, favourite_place, happiest_month, streak_days
from .stats import get_stats, invalidate_user_cache
from .mood_theme import get_theme



from .mood_theme import get_theme

@login_required
def dashboard(request):
    moods = Mood.objects.all()
    verdict = calculate_verdict(request.user)
    fav = favourite_place(request.user)
    month = happiest_month(request.user)
    streak = streak_days(request.user)

    entries = list(
        Entry.objects.filter(user=request.user).select_related("mood")
    )
    theme = get_theme(entries)

    context = {
        "moods": moods,
        # 👇 ВАЖНО: список словарей, а не json.dumps(...)
        "moods_json": [
            {
                "id": m.id,
                "score": m.score,
                "emoji": m.emoji,
                "name": m.name,
                "color": m.color,
            }
            for m in moods
        ],
        "verdict": verdict,
        "fav": fav,
        "happy_month": month,
        "streak": streak,
        "theme": theme,
    }
    return render(request, "diary/dashboard.html", context)
@login_required

@require_POST
def create_entry(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid json"}, status=400)

    mood = get_object_or_404(Mood, id=data.get("mood_id"))
    try:
        lat = float(data["latitude"])
        lng = float(data["longitude"])
    except (KeyError, TypeError, ValueError):
        return JsonResponse({"error": "coords required"}, status=400)

    date_str = data.get("date")
    date = timezone.localdate()
    if date_str:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    entry = Entry.objects.create(
        user=request.user,
        mood=mood,
        title=(data.get("title") or "")[:128],
        note=data.get("note") or "",
        latitude=lat,
        longitude=lng,
        date=date,
    )
    invalidate_user_cache(request.user)
    return JsonResponse({"id": entry.id, "ok": True})


@login_required
@require_POST
def delete_entry(request, pk):
    Entry.objects.filter(pk=pk, user=request.user).delete()
    invalidate_user_cache(request.user)
    return JsonResponse({"ok": True})

def public_profile(request, username):
    user = get_object_or_404(User, username=username)
    entries = list(
        Entry.objects.filter(user=user).select_related("mood")[:200]
    )
    verdict = calculate_verdict(user)
    theme = get_theme(entries)   # 👈 должно быть
    return render(
        request,
        "diary/public_profile.html",
        {
            "profile_user": user,
            "entries": entries,
            "verdict": verdict,
            "theme": theme,       # 👈 должно быть
        },
    )

def export_geojson(request, username):
    user = get_object_or_404(User, username=username)
    features = []
    for e in Entry.objects.filter(user=user).select_related("mood"):
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [e.longitude, e.latitude]},
            "properties": {
                "date": e.date.isoformat(),
                "mood": e.mood.name,
                "score": e.mood.score,
                "emoji": e.mood.emoji,
                "note": e.note,
                "title": e.title,
            },
        })
    data = {"type": "FeatureCollection", "features": features}
    resp = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type="application/geo+json",
    )
    resp["Content-Disposition"] = f'attachment; filename="{username}.geojson"'
    return resp