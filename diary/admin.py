from django.contrib import admin

from django.contrib import admin
from .models import Mood, Entry


@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ("score", "emoji", "name", "color")
    ordering = ("score",)


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "mood", "title", "latitude", "longitude")
    list_filter = ("mood", "date")
    search_fields = ("title", "note", "user__username")
    autocomplete_fields = ()