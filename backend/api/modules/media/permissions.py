MEDIA_READ = "media.read"
MEDIA_UPLOAD = "media.upload"
MEDIA_DELETE = "media.delete"
MEDIA_FOLDER_CREATE = "media.folder.create"

DECLARED_PERMISSIONS = (
    {"code": MEDIA_READ, "module": "media", "route": "GET /api/media/"},
    {"code": MEDIA_UPLOAD, "module": "media", "route": "POST /api/media/upload/"},
    {"code": MEDIA_DELETE, "module": "media", "route": "DELETE /api/media/<id>/"},
    {"code": MEDIA_FOLDER_CREATE, "module": "media", "route": "POST /api/media/folders/"},
)
