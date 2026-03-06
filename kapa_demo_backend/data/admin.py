from django.contrib import admin
from .models import CoverageGap


@admin.register(CoverageGap)
class CoverageGapAdmin(admin.ModelAdmin):
    list_display = ["title", "conversation_count", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["title", "finding"]
