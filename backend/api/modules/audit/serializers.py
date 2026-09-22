from rest_framework import serializers

from ...models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    user_id = serializers.IntegerField(read_only=True, allow_null=True)
    user_name = serializers.SerializerMethodField()
    http_method = serializers.CharField(source="method", read_only=True)
    http_path = serializers.CharField(source="path", read_only=True)
    http_status = serializers.IntegerField(source="status_code", read_only=True)

    class Meta:
        model = ActivityLog
        fields = (
            "id",
            "timestamp",
            "level",
            "service",
            "module",
            "environment",
            "host",
            "message",
            "trace_id",
            "request_id",
            "session_id",
            "user_id",
            "user_name",
            "username",
            "action",
            "entity_type",
            "entity_id",
            "method",
            "path",
            "status_code",
            "http_method",
            "http_path",
            "http_status",
            "error_code",
            "error_type",
            "stack_trace",
            "changed_fields",
            "duration_ms",
            "ip_address",
            "user_agent",
            "portal_id",
            "tags",
            "created_at",
        )

    def get_username(self, activity_log):
        return activity_log.user.username if activity_log.user else None

    def get_user_name(self, activity_log):
        return activity_log.user.username if activity_log.user else None