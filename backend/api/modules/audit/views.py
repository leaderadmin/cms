from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import CanReadActivityLogs
from .serializers import ActivityLogSerializer
from ...models import ActivityLog


class ActivityLogListView(APIView):
    permission_classes = [CanReadActivityLogs]

    @extend_schema(
        parameters=[
            OpenApiParameter("limit", OpenApiTypes.INT, OpenApiParameter.QUERY, default=50),
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, default=1),
            OpenApiParameter("path", OpenApiTypes.STR, OpenApiParameter.QUERY),
            OpenApiParameter("status_code", OpenApiTypes.INT, OpenApiParameter.QUERY),
            OpenApiParameter("action", OpenApiTypes.STR, OpenApiParameter.QUERY),
            OpenApiParameter("level", OpenApiTypes.STR, OpenApiParameter.QUERY),
            OpenApiParameter("username", OpenApiTypes.STR, OpenApiParameter.QUERY),
        ],
        responses=ActivityLogSerializer(many=True),
    )
    def get(self, request):
        try:
            requested_limit = int(request.query_params.get("limit", 50))
        except (TypeError, ValueError):
            requested_limit = 50
        limit = min(max(requested_limit, 1), 100)
        try:
            page = max(int(request.query_params.get("page", 1)), 1)
        except (TypeError, ValueError):
            page = 1
        logs = ActivityLog.objects.select_related("user").all()
        path = request.query_params.get("path")
        status_code = request.query_params.get("status_code")
        action = request.query_params.get("action")
        level = request.query_params.get("level")
        username = request.query_params.get("username")
        if path:
            logs = logs.filter(path__icontains=path)
        if status_code:
            logs = logs.filter(status_code=status_code)
        if action:
            logs = logs.filter(action__icontains=action)
        if level:
            logs = logs.filter(level=level.upper())
        if username:
            logs = logs.filter(user__username__icontains=username)
        count = logs.count()
        start = (page - 1) * limit
        results = logs[start:start + limit]
        return Response({
            "results": ActivityLogSerializer(results, many=True).data,
            "count": count,
            "page": page,
            "page_size": limit,
            "total_pages": max((count + limit - 1) // limit, 1),
        })