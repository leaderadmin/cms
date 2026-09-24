from django.urls import path
from .views import FAQCategoryDetailView, FAQCategoryListView, FAQQuestionDetailView, FAQQuestionListView
urlpatterns = [path("categories/", FAQCategoryListView.as_view()), path("categories/<int:category_id>/", FAQCategoryDetailView.as_view()), path("questions/", FAQQuestionListView.as_view()), path("questions/<int:question_id>/", FAQQuestionDetailView.as_view())]