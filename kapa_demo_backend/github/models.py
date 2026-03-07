from django.db import models


class GitHubInstallation(models.Model):
    """Stores GitHub App installation and linked repo; understanding = generated repo understanding markdown."""

    installation_id = models.BigIntegerField(unique=True)
    repository_name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    installed_at = models.DateTimeField(auto_now_add=True)
    understanding = models.TextField(blank=True, null=True)
    raw_tree = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-installed_at"]

    def __str__(self):
        return f"{self.owner}/{self.repository_name} (installation {self.installation_id})"
