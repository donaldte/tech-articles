from allauth.urls import build_provider_urlpatterns
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.i18n import set_language, JavaScriptCatalog

# ============================================================================
# INTERNATIONALIZED URLS (With i18n prefix)
# ============================================================================
urlpatterns = i18n_patterns(
    # Admin
    path(settings.ADMIN_URL, admin.site.urls),
    path("django-admin/home/", admin.site.index, name="django_admin"),
    # Common pages (home, about, etc.)
    path("", include("tech_articles.common.urls", namespace="common")),
    # Dashboard pages
    path("dashboard/", include("tech_articles.dashboard.urls", namespace="dashboard")),
    # Custom accounts (replace default allauth UI)
    path("accounts/", include("tech_articles.accounts.urls", namespace="accounts")),
    # Optional: keep socialaccount urls for OAuth callback handling
    path("accounts/social/", include("allauth.socialaccount.urls")),
    path("accounts/social/", include(build_provider_urlpatterns())),
    # Content management (categories, tags, articles) - dashboard area
    path("content/", include("tech_articles.content.urls", namespace="content_manage")),
    # Billing management (Plan, Coupon, Subscription, Transaction)
    path("billing/", include("tech_articles.billing.urls", namespace="billing")),
    # Resources management
    path("resources/", include("tech_articles.resources.urls", namespace="resources")),
    # Newsletter management
    path(
        "newsletter/", include("tech_articles.newsletter.urls", namespace="newsletter")
    ),
    # Appointments management
    path(
        "appointments/",
        include("tech_articles.appointments.urls", namespace="appointments"),
    ),
    # Analytics
    path("analytics/", include("tech_articles.analytics.urls", namespace="analytics")),
)


# ============================================================================
# LANGUAGE SWITCHING (Non-internationalized)
# ============================================================================
urlpatterns += [
    path("i18n/set-language/", set_language, name="set_language"),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
]

# ============================================================================
# MEDIA FILES
# ============================================================================
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ============================================================================
# DEBUG URLS (Development only)
# ============================================================================
if settings.DEBUG:
    # Error pages
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]

    # Debug Toolbar
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            *urlpatterns,
        ]
