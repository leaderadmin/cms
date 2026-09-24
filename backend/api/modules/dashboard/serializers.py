import json
from rest_framework import serializers


class HealthResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    redis = serializers.CharField()


class StatsResponseSerializer(serializers.Serializer):
    visits = serializers.IntegerField()
    last_cron_run = serializers.JSONField(allow_null=True)
    visits_by_day = serializers.ListField(child=serializers.DictField())
    activity_by_day = serializers.ListField(child=serializers.DictField())
    content_counts = serializers.DictField()


def serialize_health(status, redis_status):
    return {
        "status": status,
        "redis": redis_status,
    }


def serialize_stats(visits, last_job, visits_by_day, activity_by_day, content_counts):
    return {
        "visits": visits,
        "last_cron_run": json.loads(last_job) if last_job else None,
        "visits_by_day": visits_by_day,
        "activity_by_day": activity_by_day,
        "content_counts": content_counts,
    }
