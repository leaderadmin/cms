from django.urls import path

from .views import EntityCatalogView, EntityDetailView, EntityListCreateView, SchemaCatalogView, SchemaColumnView, SchemaTableView

urlpatterns = [
    path("", SchemaCatalogView.as_view()),
    path("schema/<str:table_name>/", SchemaTableView.as_view()),
    path("schema/<str:table_name>/columns/<str:column_name>/", SchemaColumnView.as_view()),
    path("<slug:slug>/", EntityListCreateView.as_view()),
    path("<slug:slug>/<int:pk>/", EntityDetailView.as_view()),
]