from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from tech_articles.content.models import FeaturedArticles, TableOfContents, ArticlePage, LATEST_ARTICLES_CACHE_KEY, \
    Article
from tech_articles.utils.constants import FEATURED_ARTICLES_UUID

CACHE_KEY = f"featured_articles:{FEATURED_ARTICLES_UUID}"


@receiver(post_save, sender=FeaturedArticles)
def clear_featured_cache_on_save(sender, instance, **kwargs):
    """Clear cache when FeaturedArticles is saved."""
    cache.delete(CACHE_KEY)


@receiver(post_delete, sender=FeaturedArticles)
def clear_featured_cache_on_delete(sender, instance, **kwargs):
    """Clear cache when FeaturedArticles is deleted."""
    cache.delete(CACHE_KEY)


@receiver(post_save, sender=FeaturedArticles)
def clear_featured_articles_cache_on_save(sender, instance, **kwargs):
    """Clear the featured articles cache when the configuration changes."""
    try:
        cache.delete(FeaturedArticles.CACHE_KEY)
    except Exception:
        pass


@receiver(post_delete, sender=FeaturedArticles)
def clear_featured_articles_cache_on_delete(sender, instance, **kwargs):
    """Clear cache when the FeaturedArticles instance is deleted."""
    try:
        cache.delete(FeaturedArticles.CACHE_KEY)
    except Exception:
        pass



@receiver(post_save, sender=ArticlePage)
def auto_generate_toc(sender, instance, **kwargs):
    """Auto-generate TOC when article page is saved."""
    from tech_articles.content.services.toc_generator import TOCGenerator

    try:
        toc = TableOfContents.objects.get(article=instance.article)
        if toc.is_auto_generated:
            structure = TOCGenerator.generate_from_article(instance.article)
            toc.structure = structure
            toc.save(update_fields=["structure", "updated_at"])
    except TableOfContents.DoesNotExist:
        pass


@receiver(post_save, sender=Article)
def clear_latest_articles_cache_on_save(sender, instance, **kwargs):
    """Invalidate the latest-articles cache whenever an Article is saved."""
    try:
        cache.delete(LATEST_ARTICLES_CACHE_KEY)
    except Exception:
        pass


@receiver(post_delete, sender=Article)
def clear_latest_articles_cache_on_delete(sender, instance, **kwargs):
    """Invalidate the latest-articles cache whenever an Article is deleted."""
    try:
        cache.delete(LATEST_ARTICLES_CACHE_KEY)
    except Exception:
        pass



