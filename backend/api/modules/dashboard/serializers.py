import json
from rest_framework import serializers


class HealthResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    redis = serializers.CharField()


class StatsResponseSerializer(serializers.Serializer):
    visits = serializers.IntegerField()
    last_cron_run = serializers.JSONField(allow_null=True)


def serialize_health(status, redis_status):
    return {
        "status": status,
        "redis": redis_status,
    }


def serialize_stats(visits, last_job):
    return {
        "visits": visits,
        "last_cron_run": json.loads(last_job) if last_job else None,
    }
