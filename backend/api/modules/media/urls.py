from django.urls import path

from .views import MediaDeleteView, MediaDownloadView, MediaFolderDeleteView, MediaFolderListCreateView, MediaListView, MediaPreviewView, MediaUploadView

urlpatterns = [
    path("", MediaListView.as_view(), name="media-list"),
    path("upload/", MediaUploadView.as_view(), name="media-upload"),
    path("folders/", MediaFolderListCreateView.as_view(), name="media-folders"),
    path("folders/<int:folder_id>/", MediaFolderDeleteView.as_view(), name="media-folder-delete"),
    path("<int:media_id>/download/", MediaDownloadView.as_view(), name="media-download"),
    path("<int:media_id>/preview/", MediaPreviewView.as_view(), name="media-preview"),
    path("<int:media_id>/", MediaDeleteView.as_view(), name="media-delete"),
]
