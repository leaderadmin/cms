from django.urls import path

from .views import ProductDetailView, ProductListView, ProductMetadataView, ProductPublishView, ProductTagDetailView, ProductTagListView

urlpatterns = [
    path("metadata/", ProductMetadataView.as_view(), name="product-metadata"),
    path("metadata/<int:metadata_id>/", ProductMetadataView.as_view(), name="product-metadata-detail"),
    path("tags/", ProductTagListView.as_view(), name="product-tag-list"),
    path("tags/<int:tag_id>/", ProductTagDetailView.as_view(), name="product-tag-detail"),
    path("", ProductListView.as_view(), name="product-list"),
    path("<int:product_id>/", ProductDetailView.as_view(), name="product-detail"),
    path("<int:product_id>/publish/", ProductPublishView.as_view(), name="product-publish"),
]
