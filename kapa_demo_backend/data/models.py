import uuid
from django.db import models


class CoverageGap(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("to_review", "To Review"),
        ("resolved", "Resolved"),
        ("acted", "Acted"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    conversation_count = models.IntegerField()
    finding = models.TextField()
    suggestion = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
