from django.contrib import admin
from .models import GitHubInstallation


@admin.register(GitHubInstallation)
class GitHubInstallationAdmin(admin.ModelAdmin):
    list_display = ("installation_id", "owner", "repository_name", "installed_at")
    search_fields = ("owner", "repository_name")
    readonly_fields = ("installed_at",)
