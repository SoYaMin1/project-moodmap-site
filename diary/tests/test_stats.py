import pytest
from django.contrib.auth.models import User
from diary.models import Mood, Entry
from diary.stats import get_stats


@pytest.mark.django_db
def test_stats_shape():
    u = User.objects.create_user("a", password="x")
    m = Mood.objects.create(score=7, emoji="😄", name="Отлично", color="#16a34a")
    Entry.objects.create(user=u, mood=m, latitude=1, longitude=1)
    s = get_stats(u, "all")
    assert s["kpi"]["total"] == 1
    assert len(s["distribution"]) == 1
    assert len(s["points"]) == 1