from pathlib import Path

from .permissions import MEDIA_DELETE, MEDIA_READ, MEDIA_UPLOAD


def serialize_media(media, request):
    return {
        "id": media.id,
        "name": media.original_name,
        "size": media.size,
        "content_type": media.content_type,
        "uploaded_by": media.uploaded_by.username if media.uploaded_by else None,
        "created_at": media.created_at.isoformat(),
        "download_url": request.build_absolute_uri(f"/api/media/{media.id}/download/"),
        "extension": Path(media.original_name).suffix.lower().lstrip("."),
        "folder_id": media.folder_id,
    }


def serialize_folder(folder):
    return {"id": folder.id, "name": folder.name, "parent_id": folder.parent_id, "file_count": folder.files.count()}
