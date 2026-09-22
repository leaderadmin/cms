from django.core.files.storage import default_storage
from django.core.mail import EmailMessage, get_connection
from django.http import FileResponse
from django.urls import reverse
from mimetypes import guess_type
from django.db import transaction
from smtplib import SMTPException
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ...models import EmailConfiguration, EmailTemplate, SystemSettings
from .serializers import EmailConfigurationSerializer, EmailTemplateSerializer, SystemSettingsSerializer


def system_settings():
    return SystemSettings.objects.first() or SystemSettings.objects.create()


class SystemSettingsView(APIView):
    def get(self, request):
        return Response(SystemSettingsSerializer(system_settings()).data)

    @transaction.atomic
    def put(self, request):
        item = system_settings()
        serializer = SystemSettingsSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SystemLogoView(APIView):
    permission_classes = []

    def get(self, request):
        item = system_settings()
        if not item.logo_file:
            return Response({"detail": "No logo has been uploaded."}, status=status.HTTP_404_NOT_FOUND)
        content_type = guess_type(item.logo_file.name)[0] or "application/octet-stream"
        return FileResponse(item.logo_file.open("rb"), content_type=content_type)

    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        uploaded = request.FILES.get("logo")
        if not uploaded:
            return Response({"detail": "A logo file is required."}, status=status.HTTP_400_BAD_REQUEST)
        allowed_types = {"image/png", "image/jpeg", "image/gif", "image/webp", "image/svg+xml"}
        if uploaded.content_type not in allowed_types:
            return Response({"detail": "Logo must be a PNG, JPG, GIF, WEBP, or SVG image."}, status=status.HTTP_400_BAD_REQUEST)
        if uploaded.size > 5 * 1024 * 1024:
            return Response({"detail": "Logo must be smaller than 5 MB."}, status=status.HTTP_400_BAD_REQUEST)
        item = system_settings()
        old_name = item.logo_file.name
        item.logo_file = uploaded
        item.logo_url = f"{item.api_domain.rstrip('/')}{reverse('system-logo')}" if item.api_domain else ""
        item.save(update_fields=("logo_file", "logo_url", "updated_at"))
        if old_name and old_name != item.logo_file.name and default_storage.exists(old_name):
            default_storage.delete(old_name)
        return Response(SystemSettingsSerializer(item).data)


def configuration():
    return EmailConfiguration.objects.first() or EmailConfiguration.objects.create()


class EmailConfigurationView(APIView):
    def get(self, request):
        return Response(EmailConfigurationSerializer(configuration()).data)

    @transaction.atomic
    def put(self, request):
        item = configuration()
        serializer = EmailConfigurationSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if "password" not in request.data:
            serializer.validated_data.pop("password", None)
        serializer.save()
        return Response(EmailConfigurationSerializer(item).data)


class EmailTestView(APIView):
    def post(self, request):
        recipient = request.data.get("recipient", "").strip()
        if not recipient:
            return Response({"detail": "recipient is required"}, status=status.HTTP_400_BAD_REQUEST)
        config = configuration()
        if not config.enabled or not config.host or not config.from_email:
            return Response({"detail": "Email configuration is incomplete or disabled"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            connection = get_connection(host=config.host, port=config.port, username=config.username, password=config.password, use_tls=config.encryption == "tls", use_ssl=config.encryption == "ssl", fail_silently=False)
            EmailMessage("Startup Backoffice test email", "SMTP configuration is working.", config.from_email, [recipient], connection=connection).send()
        except (OSError, SMTPException) as exc:
            return Response({"detail": f"SMTP delivery failed: {exc}"}, status=status.HTTP_502_BAD_GATEWAY)
        return Response({"detail": "Test email sent"})


class EmailTemplateListView(APIView):
    def get(self, request):
        return Response(EmailTemplateSerializer(EmailTemplate.objects.all(), many=True).data)

    def post(self, request):
        serializer = EmailTemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save() and serializer.data, status=status.HTTP_201_CREATED)


class EmailTemplateDetailView(APIView):
    def put(self, request, pk):
        item = EmailTemplate.objects.get(pk=pk)
        serializer = EmailTemplateSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        EmailTemplate.objects.filter(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
