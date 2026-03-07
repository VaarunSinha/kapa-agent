"""URLs for /github/ prefix (setup callback only)."""
from django.urls import path
from . import views

urlpatterns = [
    path("setup", views.github_setup_view, name="setup"),
]
