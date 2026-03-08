import uuid
from django.db import models


class Issue(models.Model):
    STATUS_CHOICES = [
        ("created", "Created"),
        ("researching", "Researching"),
        ("questions_pending", "Questions Pending"),
        ("research_complete", "Research Complete"),
        ("research_failed", "Research Failed"),
        ("fix_proposed", "Fix Proposed"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coverage_gap = models.ForeignKey(
        "data.CoverageGap",
        on_delete=models.CASCADE,
        related_name="issues",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    research_goal = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Research(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="research_list",
    )
    summary = models.TextField(blank=True)
    files_analyzed = models.JSONField(default=list, blank=True)
    coverage_gap_description = models.TextField(blank=True, null=True)
    recommended_changes = models.TextField(blank=True, null=True)
    confidence_score = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Research for {self.issue.title}"


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ("text", "Text"),
        ("textarea", "Textarea"),
        ("choice", "Choice"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    research = models.ForeignKey(
        Research,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    choices = models.JSONField(blank=True, null=True)
    answer = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.question_text[:50]


class Fix(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("review", "Review"),
        ("approved", "Approved"),
        ("published", "Published"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="fixes",
    )
    file_path = models.CharField(max_length=1024, blank=True)
    patch = models.TextField(blank=True)
    files = models.JSONField(default=list, blank=True)  # [{"path": str, "content": str}, ...]
    summary = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    branch_name = models.CharField(max_length=255, blank=True, null=True)
    pr_url = models.URLField(max_length=512, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.file_path} ({self.status})"
