from django.urls import path
from . import views, api, share

app_name = "diary"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/entries/", views.create_entry, name="create_entry"),
    path("api/entries/<int:pk>/delete/", views.delete_entry, name="delete_entry"),
    path("api/stats/", api.stats_api, name="stats"),
    path("api/verdict.png", share.verdict_image, name="verdict_image"),
    path("u/<str:username>/", views.public_profile, name="public_profile"),
    path("u/<str:username>/geojson/", views.export_geojson, name="geojson"),
]