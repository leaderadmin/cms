from django.urls import path

from .views import DraftPageView, PageComponentDefinitionDetailView, PageComponentDefinitionListView, PageComponentDetailView, PageComponentListView, PageDetailView, PageListView, PageTemplateDetailView, PageTemplateListView, PreviewContentView, PublishPageView, PublishedPageView

urlpatterns = [
    path("", PageListView.as_view(), name="page-list"),
    path("templates/", PageTemplateListView.as_view(), name="page-template-list"),
    path("templates/<int:template_id>/", PageTemplateDetailView.as_view(), name="page-template-detail"),
    path("components/", PageComponentListView.as_view(), name="page-component-list"),
    path("components/<int:component_id>/", PageComponentDetailView.as_view(), name="page-component-detail"),
    path("component-definitions/", PageComponentDefinitionListView.as_view(), name="page-component-definition-list"),
    path("component-definitions/<int:component_id>/", PageComponentDefinitionDetailView.as_view(), name="page-component-definition-detail"),
    path("<slug:slug>/draft/", DraftPageView.as_view(), name="page-draft"),
    path("<slug:slug>/publish/", PublishPageView.as_view(), name="page-publish"),
    path("<slug:slug>/preview-content/", PreviewContentView.as_view(), name="page-preview-content"),
    path("<slug:slug>/", PublishedPageView.as_view(), name="page-published"),
    path("<int:page_id>/", PageDetailView.as_view(), name="page-detail"),
]
