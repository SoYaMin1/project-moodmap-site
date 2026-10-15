from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.utils import timezone


class Mood(models.Model):
    """Справочник из 10 улыбок (фикстура)."""
    score = models.PositiveSmallIntegerField(unique=True)  # 1..10
    emoji = models.CharField(max_length=8)
    name = models.CharField(max_length=64)
    color = models.CharField(max_length=16)

    class Meta:
        ordering = ["score"]

    def __str__(self):
        return f"{self.score} {self.emoji} {self.name}"


class Entry(models.Model):
    """Запись: место + настроение + дата."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="entries"
    )
    mood = models.ForeignKey(Mood, on_delete=models.PROTECT, related_name="entries")
    title = models.CharField(max_length=128, blank=True)
    note = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    date = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["user", "mood"]),
        ]

    def __str__(self):
        return f"{self.user} @ {self.date} — {self.mood.emoji}"

    @property
    def lat(self):
        return self.latitude

    @property
    def lng(self):
        return self.longitude