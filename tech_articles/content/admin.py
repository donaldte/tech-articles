# Register your models here.
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from tech_articles.content.models import (
    Article,
    ArticlePage,
    Category,
    Clap,
    Comment,
    CommentLike,
    FeaturedArticles,
    Like,
    Tag,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model."""
    list_display = ['name', 'slug', 'is_active', 'sort_order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['sort_order', 'name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface for Tag model."""
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin interface for Article model."""
    list_display = ['title', 'language', 'status', 'difficulty', 'access_type', 'published_at', 'created_at']
    list_filter = ['status', 'language', 'difficulty', 'access_type', 'created_at', 'published_at']
    search_fields = ['title', 'slug', 'summary']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['categories', 'tags']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(ArticlePage)
class ArticlePageAdmin(admin.ModelAdmin):
    """Admin interface for ArticlePage model."""
    list_display = ['article', 'page_number', 'title', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'article__title']
    ordering = ['article', 'page_number']


@admin.register(FeaturedArticles)
class FeaturedArticlesAdmin(admin.ModelAdmin):
    """Admin interface for FeaturedArticles model."""
    list_display = ['id', 'first_feature', 'second_feature', 'third_feature', 'updated_at']
    fields = ['first_feature', 'second_feature', 'third_feature']
    
    def has_add_permission(self, request):
        """Only allow one instance of FeaturedArticles."""
        return not FeaturedArticles.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of the configuration."""
        return False


@admin.register(Clap)
class ClapAdmin(admin.ModelAdmin):
    """Admin interface for Clap model."""
    list_display = ['article', 'user', 'session_key', 'count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['article__title', 'user__username', 'session_key']
    ordering = ['-created_at']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Admin interface for Like model."""
    list_display = ['article', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['article__title', 'user__username']
    ordering = ['-created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment model."""
    list_display = ['article', 'user', 'content_preview', 'is_edited', 'created_at']
    list_filter = ['is_edited', 'created_at']
    search_fields = ['article__title', 'user__username', 'content']
    ordering = ['-created_at']

    def content_preview(self, obj):
        """Show first 50 characters of comment."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = _('Content')


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    """Admin interface for CommentLike model."""
    list_display = ['comment', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comment__content', 'user__username']
    ordering = ['-created_at']

