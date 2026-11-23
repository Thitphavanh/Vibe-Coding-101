from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from .models import Category, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "post_count")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="จำนวนบทความ")
    def post_count(self, obj):
        return obj.posts.count()


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ("content",)
    list_display = (
        "title",
        "category",
        "author",
        "status",
        "is_featured",
        "views",
        "published_at",
    )
    list_filter = ("status", "is_featured", "category", "created_at")
    search_fields = ("title", "summary", "content")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("status", "is_featured")
    date_hierarchy = "created_at"
    readonly_fields = ("views", "created_at", "updated_at")

    fieldsets = (
        ("ข้อมูลหลัก", {
            "fields": ("title", "slug", "category", "author"),
        }),
        ("เนื้อหา", {
            "fields": ("summary", "content", "thumbnail"),
        }),
        ("การเผยแพร่", {
            "fields": ("status", "is_featured", "published_at"),
        }),
        ("ข้อมูลระบบ", {
            "fields": ("views", "created_at", "updated_at"),
        }),
    )


admin.site.site_header = "Vibe Coding 101 — Blog Admin"
