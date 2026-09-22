from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import OpenApiExample, extend_schema

from ..auth.permissions import HasRoutePermission
from .permissions import DASHBOARD_STATS
from .serializers import HealthResponseSerializer, StatsResponseSerializer, serialize_health, serialize_stats
from .services import _dashboard_service


@extend_schema(
    responses=HealthResponseSerializer,
    examples=[
        OpenApiExample(
            "Healthy API",
            response_only=True,
            value={"status": "ok", "redis": "ok"},
        )
    ],
)
@api_view(["GET"])
def health(request):
    return JsonResponse(serialize_health("ok", _dashboard_service.get_health()))


@extend_schema(
    responses=StatsResponseSerializer,
    examples=[
        OpenApiExample(
            "Dashboard stats",
            response_only=True,
            value={
                "visits": 42,
                "last_cron_run": {"status": "ok", "processed_at": "2026-09-16T12:00:00Z"},
            },
        )
    ],
)
@api_view(["GET"])
@permission_classes([HasRoutePermission])
def stats(request):
    data = _dashboard_service.get_stats()
    return JsonResponse(serialize_stats(data["visits"], data["last_job"]))


stats.required_permission = DASHBOARD_STATS
stats.cls.required_permission = DASHBOARD_STATS
