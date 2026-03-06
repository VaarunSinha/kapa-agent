from django.urls import path
from . import views

app_name = "data"

urlpatterns = [
    path("coverage-gaps", views.CoverageGapListAPIView.as_view(), name="coverage-gap-list"),
]
