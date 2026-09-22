from pathlib import Path

from django.conf import settings
from django.db.models import Q
from django.http import FileResponse
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from ..auth.permissions import HasRoutePermission
from .permissions import MEDIA_DELETE, MEDIA_FOLDER_CREATE, MEDIA_READ, MEDIA_UPLOAD
from .serializers import serialize_folder, serialize_media
from ...models import MediaFile, MediaFolder


class MediaFolderListCreateView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": MEDIA_READ, "POST": MEDIA_FOLDER_CREATE}

    def get(self, request):
        return Response([serialize_folder(folder) for folder in MediaFolder.objects.all()])

    def post(self, request):
        name = str(request.data.get("name", "")).strip()
        if not name or len(name) > 120:
            return Response({"detail": "Folder name must contain 1 to 120 characters."}, status=status.HTTP_400_BAD_REQUEST)
        parent_id = request.data.get("parent_id")
        parent = None
        if parent_id:
            try:
                parent = MediaFolder.objects.get(pk=parent_id)
            except MediaFolder.DoesNotExist:
                return Response({"detail": "Parent folder not found."}, status=status.HTTP_400_BAD_REQUEST)
        if MediaFolder.objects.filter(parent=parent, name=name).exists():
            return Response({"detail": "A folder with this name already exists here."}, status=status.HTTP_400_BAD_REQUEST)
        folder = MediaFolder.objects.create(name=name, parent=parent, created_by=request.user)
        return Response(serialize_folder(folder), status=status.HTTP_201_CREATED)


class MediaFolderDeleteView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = MEDIA_DELETE

    def delete(self, request, folder_id):
        try:
            folder = MediaFolder.objects.get(pk=folder_id)
        except MediaFolder.DoesNotExist:
            return Response({"detail": "Folder not found."}, status=status.HTTP_404_NOT_FOUND)
        folder.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MediaListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = MEDIA_READ

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        files = MediaFile.objects.select_related("uploaded_by", "folder")
        folder_id = request.query_params.get("folder_id")
        if folder_id:
            files = files.filter(folder_id=folder_id)
        if query:
            files = files.filter(Q(original_name__icontains=query) | Q(content_type__icontains=query))
        return Response([serialize_media(media, request) for media in files[:200]])


class MediaUploadView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = MEDIA_UPLOAD
    parser_classes = [MultiPartParser]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "media_upload"

    def post(self, request):
        uploads = request.FILES.getlist("files") or ([request.FILES["file"]] if "file" in request.FILES else [])
        if not uploads:
            return Response({"detail": "Select at least one file."}, status=status.HTTP_400_BAD_REQUEST)

        folder = None
        folder_id = request.data.get("folder_id")
        if folder_id:
            try:
                folder = MediaFolder.objects.get(pk=folder_id)
            except MediaFolder.DoesNotExist:
                return Response({"detail": "Folder not found."}, status=status.HTTP_400_BAD_REQUEST)
        created = []
        for uploaded in uploads:
            extension = Path(uploaded.name).suffix.lower().lstrip(".")
            if extension not in settings.MEDIA_ALLOWED_EXTENSIONS:
                return Response(
                    {"detail": f"File type .{extension or 'unknown'} is not allowed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if uploaded.size > settings.MEDIA_MAX_UPLOAD_BYTES:
                return Response(
                    {"detail": f"Each file must be smaller than {settings.MEDIA_MAX_UPLOAD_BYTES} bytes."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        for uploaded in uploads:
            original_name = Path(uploaded.name).name[:255]
            media = MediaFile.objects.create(
                file=uploaded,
                original_name=original_name,
                content_type=uploaded.content_type or "application/octet-stream",
                size=uploaded.size,
                uploaded_by=request.user,
                folder=folder,
            )
            created.append(serialize_media(media, request))
        return Response(created, status=status.HTTP_201_CREATED)


class MediaDownloadView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = MEDIA_READ

    def get(self, request, media_id):
        try:
            media = MediaFile.objects.get(pk=media_id)
            handle = media.file.open("rb")
        except (MediaFile.DoesNotExist, FileNotFoundError, OSError):
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)
        return FileResponse(handle, as_attachment=True, filename=media.original_name, content_type=media.content_type)


class MediaPreviewView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = MEDIA_READ

    def get(self, request, media_id):
        try:
            media = MediaFile.objects.get(pk=media_id)
            if not media.content_type.startswith("image/"):
                return Response({"detail": "Only image files can be previewed."}, status=status.HTTP_400_BAD_REQUEST)
            handle = media.file.open("rb")
        except (MediaFile.DoesNotExist, FileNotFoundError, OSError):
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)
        return FileResponse(handle, as_attachment=False, content_type=media.content_type)


class MediaDeleteView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = MEDIA_DELETE

    def delete(self, request, media_id):
        try:
            media = MediaFile.objects.get(pk=media_id)
        except MediaFile.DoesNotExist:
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)
        media.file.delete(save=False)
        media.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
