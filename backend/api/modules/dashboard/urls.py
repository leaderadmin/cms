from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health, name="dashboard-health"),
    path("stats/", views.stats, name="dashboard-stats"),
]
