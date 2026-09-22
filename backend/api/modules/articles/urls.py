from django.urls import path

from .views import ArticleCategoryDetailView, ArticleCategoryListView, ArticleDetailView, ArticleListView, ArticlePublishView, ArticleTagDetailView, ArticleTagListView

urlpatterns = [
    path("", ArticleListView.as_view(), name="article-list"),
    path("categories/", ArticleCategoryListView.as_view(), name="article-category-list"),
    path("categories/<int:category_id>/", ArticleCategoryDetailView.as_view(), name="article-category-detail"),
    path("tags/", ArticleTagListView.as_view(), name="article-tag-list"),
    path("tags/<int:tag_id>/", ArticleTagDetailView.as_view(), name="article-tag-detail"),
    path("<int:article_id>/", ArticleDetailView.as_view(), name="article-detail"),
    path("<int:article_id>/publish/", ArticlePublishView.as_view(), name="article-publish"),
]