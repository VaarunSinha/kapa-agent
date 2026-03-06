from django.contrib import admin
from .models import Issue, Research, Question, Fix


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "coverage_gap", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["title", "description"]


@admin.register(Research)
class ResearchAdmin(admin.ModelAdmin):
    list_display = ["id", "issue", "status", "confidence_score", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["summary"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["id", "research", "question_type"]
    list_filter = ["question_type"]
    search_fields = ["question_text"]


@admin.register(Fix)
class FixAdmin(admin.ModelAdmin):
    list_display = ["id", "issue", "file_path", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["file_path", "summary"]
