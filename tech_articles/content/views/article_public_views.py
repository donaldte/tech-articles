"""
Public-facing article views for displaying articles to end users.

This module contains views for:
- Article detail page with pagination support
- Article preview page (for premium content)
- Interactive API endpoints (claps, likes, comments)
"""
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from tech_articles.content.models import Article, Clap, Comment, CommentLike, Like
from tech_articles.utils.enums import ArticleStatus, ArticleAccessType

logger = logging.getLogger(__name__)


class ArticleDetailView(TemplateView):
    """
    Unified article detail/preview view with access control and pagination support.
    
    Access logic:
    - Unauthenticated + Premium → Show preview template
    - Unauthenticated + Free → Show full detail template
    - Authenticated + Free → Show full detail (all users)
    - Authenticated + Premium + Active subscription → Show full detail
    - Authenticated + Premium + Article purchased → Show full detail
    - Authenticated + Premium + No subscription/purchase → Show preview
    
    Pagination:
    - Articles can have multiple pages (ArticlePage model)
    - URL parameter ?page=N determines which page to display
    - Navigation buttons (prev/next) are shown
    - Comments section only appears on the last page
    """

    def get_template_names(self):
        """Return appropriate template based on access control."""
        article = self.get_article()
        if self.user_has_access(article):
            return ["tech-articles/home/pages/articles/article_detail.html"]
        return ["tech-articles/home/pages/articles/article_preview.html"]
    
    def get_article(self):
        """Get article by slug from URL or return None."""
        slug = self.request.GET.get('slug') or self.kwargs.get('slug')
        if not slug:
            return None
        try:
            return Article.objects.prefetch_related('categories', 'tags', 'pages').get(
                slug=slug,
                status=ArticleStatus.PUBLISHED
            )
        except Article.DoesNotExist:
            return None
    
    def user_has_access(self, article):
        """
        Determine if the current user has access to the full article.
        
        Returns True if:
        - Article is free (access_type='free')
        - User has active subscription (any plan)
        - User has purchased this specific article
        """
        if not article:
            return False
        
        # Free articles are accessible to everyone
        if article.access_type == ArticleAccessType.FREE:
            return True
        
        # Premium articles require authentication + (subscription OR purchase)
        if not self.request.user.is_authenticated:
            return False
        
        # Check if user has active subscription (from context processor)
        if getattr(self.request, 'has_active_subscription', False):
            return True
        
        # Check if user purchased this article (from context processor)
        purchased_ids = getattr(self.request, 'purchased_article_ids', set())
        if article.id in purchased_ids:
            return True
        
        return False
    
    def get_context_data(self, **kwargs):
        """Add article data, pagination info, and interaction counts to context."""
        context = super().get_context_data(**kwargs)
        article = self.get_article()
        
        if not article:
            # Redirect to 404 or articles list
            context['article'] = None
            return context
        
        context['article'] = article
        context['has_access'] = self.user_has_access(article)
        
        # Get interaction counts
        context['clap_count'] = Clap.objects.filter(article=article).count()
        context['like_count'] = Like.objects.filter(article=article).count()
        context['comment_count'] = Comment.objects.filter(article=article).count()
        
        # Check if current user has liked (for authenticated users)
        context['user_has_liked'] = False
        if self.request.user.is_authenticated:
            context['user_has_liked'] = Like.objects.filter(
                article=article,
                user=self.request.user
            ).exists()
        
        # Pagination logic for multi-page articles
        pages = list(article.pages.all().order_by('page_number'))
        total_pages = len(pages)
        
        # Get current page number from query param (default to 1)
        try:
            current_page = int(self.request.GET.get('page', 1))
        except (ValueError, TypeError):
            current_page = 1
        
        # Ensure page number is valid
        current_page = max(1, min(current_page, total_pages if total_pages > 0 else 1))
        
        context['total_pages'] = total_pages
        context['current_page'] = current_page
        context['has_multiple_pages'] = total_pages > 1
        context['is_last_page'] = current_page == total_pages if total_pages > 0 else True
        context['has_next_page'] = current_page < total_pages
        context['has_prev_page'] = current_page > 1
        context['next_page'] = current_page + 1 if context['has_next_page'] else None
        context['prev_page'] = current_page - 1 if context['has_prev_page'] else None
        
        # Get the current page content
        if pages and 0 < current_page <= total_pages:
            context['current_page_content'] = pages[current_page - 1]
        else:
            context['current_page_content'] = None
        
        # Get comments (only if user has access and on last page)
        if context['has_access'] and context['is_last_page']:
            context['comments'] = Comment.objects.filter(
                article=article
            ).select_related('user').prefetch_related('likes').order_by('-created_at')[:50]
        else:
            context['comments'] = []
        
        return context


class ArticlePreviewView(TemplateView):
    """
    DEPRECATED: Use ArticleDetailView instead.
    
    This view is kept for backward compatibility but redirects to ArticleDetailView.
    The unified ArticleDetailView now handles both preview and detail based on access control.
    """

    def get(self, request, *args, **kwargs):
        """Redirect to ArticleDetailView."""
        from django.shortcuts import redirect
        slug = request.GET.get('slug')
        if slug:
            return redirect('content:article_detail', slug=slug)
        return redirect('common:articles_list')


# ============================================================================
# Interactive Article APIs (Claps, Likes, Comments)
# ============================================================================

class ArticleClapApiView(View):
    """
    API endpoint for adding claps to an article.
    Anyone can clap (authenticated or anonymous), but limited to 50 claps per user/session.
    """
    http_method_names = ["post"]
    
    def post(self, request, article_id):
        """Add a clap to the article."""
        try:
            article = Article.objects.get(id=article_id, status=ArticleStatus.PUBLISHED)
        except Article.DoesNotExist:
            return JsonResponse({"error": "Article not found"}, status=404)
        
        # Get or create clap record
        if request.user.is_authenticated:
            clap, created = Clap.objects.get_or_create(
                article=article,
                user=request.user,
                defaults={'count': 1}
            )
        else:
            # Use session key for anonymous users
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            
            clap, created = Clap.objects.get_or_create(
                article=article,
                session_key=session_key,
                defaults={'count': 1}
            )
        
        # Increment count (max 50)
        if not created and clap.count < 50:
            clap.count += 1
            clap.save()
        elif not created and clap.count >= 50:
            return JsonResponse({
                "error": "Maximum claps reached (50)",
                "count": clap.count,
                "total": Clap.objects.filter(article=article).count()
            }, status=400)
        
        # Return total clap count for this article
        total_claps = Clap.objects.filter(article=article).count()
        return JsonResponse({
            "success": True,
            "count": clap.count,
            "total": total_claps
        })


class ArticleLikeApiView(LoginRequiredMixin, View):
    """
    API endpoint for toggling likes on an article.
    Only authenticated users can like articles.
    """
    http_method_names = ["post"]
    
    def post(self, request, article_id):
        """Toggle like on the article."""
        try:
            article = Article.objects.get(id=article_id, status=ArticleStatus.PUBLISHED)
        except Article.DoesNotExist:
            return JsonResponse({"error": "Article not found"}, status=404)
        
        # Toggle like
        like, created = Like.objects.get_or_create(
            article=article,
            user=request.user
        )
        
        if not created:
            # Unlike
            like.delete()
            liked = False
        else:
            # Liked
            liked = True
        
        # Return total like count
        total_likes = Like.objects.filter(article=article).count()
        return JsonResponse({
            "success": True,
            "liked": liked,
            "total": total_likes
        })


class ArticleCommentApiView(LoginRequiredMixin, View):
    """
    API endpoint for creating and retrieving comments on an article.
    Only authenticated users can comment.
    """
    http_method_names = ["post", "get"]
    
    def get(self, request, article_id):
        """Get comments for an article."""
        try:
            article = Article.objects.get(id=article_id, status=ArticleStatus.PUBLISHED)
        except Article.DoesNotExist:
            return JsonResponse({"error": "Article not found"}, status=404)
        
        comments = Comment.objects.filter(article=article).select_related('user').order_by('-created_at')[:50]
        result = []
        for comment in comments:
            likes_count = CommentLike.objects.filter(comment=comment).count()
            user_liked = CommentLike.objects.filter(
                comment=comment,
                user=request.user
            ).exists() if request.user.is_authenticated else False
            
            result.append({
                "id": str(comment.id),
                "content": comment.content,
                "user": {
                    "username": comment.user.username,
                    "name": comment.user.get_full_name() or comment.user.username,
                },
                "created_at": comment.created_at.isoformat(),
                "is_edited": comment.is_edited,
                "likes_count": likes_count,
                "user_liked": user_liked,
            })
        
        return JsonResponse({"comments": result, "total": len(result)})
    
    def post(self, request, article_id):
        """Create a new comment on the article."""
        try:
            article = Article.objects.get(id=article_id, status=ArticleStatus.PUBLISHED)
        except Article.DoesNotExist:
            return JsonResponse({"error": "Article not found"}, status=404)
        
        # Get comment content from request
        import json
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
        except json.JSONDecodeError:
            content = request.POST.get('content', '').strip()
        
        if not content:
            return JsonResponse({"error": "Comment content is required"}, status=400)
        
        if len(content) > 2000:
            return JsonResponse({"error": "Comment too long (max 2000 characters)"}, status=400)
        
        # Create comment
        comment = Comment.objects.create(
            article=article,
            user=request.user,
            content=content
        )
        
        return JsonResponse({
            "success": True,
            "comment": {
                "id": str(comment.id),
                "content": comment.content,
                "user": {
                    "username": comment.user.username,
                    "name": comment.user.get_full_name() or comment.user.username,
                },
                "created_at": comment.created_at.isoformat(),
                "is_edited": comment.is_edited,
                "likes_count": 0,
                "user_liked": False,
            }
        }, status=201)


class CommentLikeApiView(LoginRequiredMixin, View):
    """
    API endpoint for toggling likes on comments.
    Only authenticated users can like comments.
    """
    http_method_names = ["post"]
    
    def post(self, request, comment_id):
        """Toggle like on a comment."""
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({"error": "Comment not found"}, status=404)
        
        # Toggle like
        comment_like, created = CommentLike.objects.get_or_create(
            comment=comment,
            user=request.user
        )
        
        if not created:
            # Unlike
            comment_like.delete()
            liked = False
        else:
            # Liked
            liked = True
        
        # Return total like count
        total_likes = CommentLike.objects.filter(comment=comment).count()
        return JsonResponse({
            "success": True,
            "liked": liked,
            "total": total_likes
        })
