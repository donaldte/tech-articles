from django.urls import path

from . import views
from .views import ArticleDetailView

app_name = "common"

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("articles/", views.ArticlesListView.as_view(), name="articles_list"),
    path("articles/detail/", ArticleDetailView.as_view(), name="article_detail"),
]
