from django.urls import path
from . import views

app_name = "github"

urlpatterns = [
    path("webhook", views.GitHubWebhookView.as_view(), name="webhook"),
    path("installation", views.GitHubInstallationAPIView.as_view(), name="installation"),
]
