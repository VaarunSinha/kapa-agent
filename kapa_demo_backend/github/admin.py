from django.contrib import admin
from django.utils.html import escape
from django.utils.safestring import mark_safe
from .models import GitHubInstallation


@admin.register(GitHubInstallation)
class GitHubInstallationAdmin(admin.ModelAdmin):
    list_display = (
        "installation_id",
        "owner",
        "repository_name",
        "source_status",
        "buckets_summary",
        "installed_at",
    )
    search_fields = ("owner", "repository_name")
    list_filter = ("source_status",)
    readonly_fields = ("installed_at", "understanding_directories", "buckets_display", "indexed_tree_display", "indexed_paths")
    fieldsets = (
        (None, {"fields": ("installation_id", "owner", "repository_name", "installed_at")}),
        ("Source & indexing", {"fields": ("source_status", "chroma_collection_name", "raw_tree")}),
        ("Understanding", {"fields": ("understanding",)}),
        ("Buckets (path → docs/backend/frontend)", {"fields": ("buckets_display", "understanding_directories")}),
        ("Indexed tree (files in Chroma)", {"fields": ("indexed_tree_display", "indexed_paths")}),
        ("Style", {"fields": ("style_md",)}),
    )

    @admin.display(description="Buckets")
    def buckets_summary(self, obj):
        if not obj.understanding_directories:
            return "—"
        by_bucket = {}
        for d in obj.understanding_directories:
            if isinstance(d, dict):
                b = (d.get("bucket") or "other").strip().lower()
                by_bucket[b] = by_bucket.get(b, 0) + 1
        return ", ".join(f"{b}: {n}" for b, n in sorted(by_bucket.items()))

    def buckets_display(self, obj):
        if not obj.understanding_directories:
            return "No directory mapping (run Connect Source Code / index to populate)."
        lines = []
        for d in obj.understanding_directories:
            if isinstance(d, dict):
                path = d.get("path") or ""
                purpose = (d.get("purpose") or "").strip()
                bucket = (d.get("bucket") or "other").strip()
                line = f"• {path} → {bucket}" + (f" — {purpose}" if purpose else "")
                lines.append(escape(line))
        return mark_safe("<br>".join(lines)) if lines else "—"

    buckets_display.short_description = "Path → bucket"

    def indexed_tree_display(self, obj):
        if not getattr(obj, "indexed_paths", None):
            return "No indexed tree (run Connect Source Code / index to populate)."
        lines = []
        for item in obj.indexed_paths:
            if isinstance(item, dict):
                path = item.get("path") or ""
                bucket = (item.get("bucket") or "other").strip()
                lines.append(escape(f"{path} → {bucket}"))
        return mark_safe("<br>".join(lines)) if lines else "—"

    indexed_tree_display.short_description = "Indexed paths (path → bucket)"
