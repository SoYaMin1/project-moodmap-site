import pytest
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from diary.models import Mood, Entry
from diary.verdict import calculate_verdict, streak_days


@pytest.fixture
def user(db):
    return User.objects.create_user("u", password="x")


@pytest.fixture
def moods(db):
    return [Mood.objects.create(score=i, emoji="🙂", name=str(i), color="#000") for i in range(1, 11)]


@pytest.mark.django_db
def test_domosed(user, moods):
    for i in range(3):
        Entry.objects.create(user=user, mood=moods[0], latitude=55, longitude=37,
                             date=timezone.localdate() - timedelta(days=i))
    v = calculate_verdict(user)
    assert "домосед" in v["text"]


@pytest.mark.django_db
def test_traveller(user, moods):
    for i in range(35):
        Entry.objects.create(
            user=user, mood=moods[9],
            latitude=55 + (i % 10), longitude=37 + (i % 10),
            date=timezone.localdate() - timedelta(days=i),
        )
    v = calculate_verdict(user)
    assert "путешественник" in v["text"]


@pytest.mark.django_db
def test_streak(user, moods):
    today = timezone.localdate()
    for i in range(4):
        Entry.objects.create(user=user, mood=moods[5], latitude=55, longitude=37,
                             date=today - timedelta(days=i))
    assert streak_days(user) == 4