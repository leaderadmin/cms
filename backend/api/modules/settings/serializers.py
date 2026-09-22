from rest_framework import serializers
from django.urls import reverse

from ...models import EmailConfiguration, EmailTemplate, SystemSettings


class SystemSettingsSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    def get_logo_url(self, obj):
        if obj.logo_file:
            path = reverse("system-logo")
            return f"{obj.api_domain.rstrip('/')}{path}" if obj.api_domain else path
        return obj.logo_url

    class Meta:
        model = SystemSettings
        fields = ("system_name", "api_domain", "backoffice_domain", "logo_url", "favicon_url", "description", "website_url", "support_email", "version", "footer_text", "updated_at")
        read_only_fields = ("updated_at",)


class EmailConfigurationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password_configured = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EmailConfiguration
        fields = ("provider", "host", "port", "username", "password", "password_configured", "encryption", "from_name", "from_email", "reply_to", "enabled")

    def get_password_configured(self, obj):
        return bool(obj.password)


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ("id", "key", "name", "subject", "html_body", "text_body", "variables", "active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")
